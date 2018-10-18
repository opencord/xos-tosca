
# Copyright 2017-present Open Networking Foundation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


import os
from tempfile import NamedTemporaryFile
from xosconfig import Config
from multistructlog import create_logger
log = create_logger(Config().get('logging'))

from toscaparser.tosca_template import ToscaTemplate, ValidationError
from default import TOSCA_RECIPES_DIR
from grpc_client.resources import RESOURCES
from grpc_client.models_accessor import GRPCModelsAccessor
from grpc._channel import _Rendezvous
import json
import traceback

class TOSCA_Parser:

    def compute_dependencies(self, template, models_by_name):
        """
        NOTE this method is augmenting self.template, isn't there a more explicit way to achieve it?
        """
        for nodetemplate in template.nodetemplates:
            nodetemplate.dependencies = []
            nodetemplate.dependencies_names = []
            for reqs in nodetemplate.requirements:
                for (k,v) in reqs.items():
                    name = v["node"]
                    if (name in models_by_name):
                        nodetemplate.dependencies.append(models_by_name[name])
                        nodetemplate.dependencies_names.append(name)

                    # go another level deep, as our requirements can have requirements...
                    # NOTE do we still need to go deep?
                    for sd_req in v.get("requirements",[]):
                        for (sd_req_k, sd_req_v) in sd_req.items():
                            name = sd_req_v["node"]
                            if (name in models_by_name):
                                nodetemplate.dependencies.append(models_by_name[name])
                                nodetemplate.dependencies_names.append(name)

    @staticmethod
    def topsort_dependencies(g):

        # Get set of all nodes, including those without outgoing edges
        keys = set(g.keys())
        values = set({})
        for v in g.values():
            values = values | set(v.dependencies_names)

        all_nodes = list(keys | values)
        steps = all_nodes


        # Final order
        order = []

        # DFS stack, not using recursion
        stack = []

        # Unmarked set
        unmarked = all_nodes

        # visiting = [] - skip, don't expect 1000s of nodes, |E|/|V| is small

        while unmarked:
            stack.insert(0, unmarked[0])  # push first unmarked

            while (stack):
                n = stack[0]
                add = True
                try:
                    for m in g[n].dependencies_names:
                        if (m in unmarked):
                            add = False
                            stack.insert(0, m)
                except KeyError:
                    pass
                if (add):
                    if (n in steps and n not in order):
                        order.append(n)
                    item = stack.pop(0)
                    try:
                        unmarked.remove(item)
                    except ValueError:
                        pass

        noorder = list(set(steps) - set(order))
        return order + noorder

    @staticmethod
    def populate_model(model, data):
        for k,v in data.iteritems():
            # NOTE must-exists is a TOSCA implementation choice, remove it before saving the model
            if k != "must-exist":
                try:
                    setattr(model, k, v)
                except TypeError, e:
                    raise Exception('Failed to set %s on field %s for class %s, Exception was: "%s"' % (v, k, model.model_name, e))
        return model

    @staticmethod
    def _translate_exception(msg):
        readable = []
        for line in msg.splitlines():
            if line.strip().startswith('MissingRequiredFieldError') or \
                    line.strip().startswith('UnknownFieldError') or \
                    line.strip().startswith('ImportError') or \
                    line.strip().startswith('InvalidTypeError') or \
                    line.strip().startswith('TypeMismatchError'):
                readable.append(line)

        if len(readable) > 0:
            return '\n'.join(readable) + '\n'
        else:
            return msg

    @staticmethod
    def get_tosca_models_by_name(template):
        models_by_name = {}
        for node in template.nodetemplates:
            models_by_name[node.name] = node
        return models_by_name

    @staticmethod
    def get_ordered_models_template(ordered_models_name, templates_by_model_name):
        ordered_models_templates = []
        for name in ordered_models_name:
            if name in templates_by_model_name:
                ordered_models_templates.append(templates_by_model_name[name])
        return ordered_models_templates

    @staticmethod
    def populate_dependencies(model, requirements, saved_models):
        for dep in requirements:
            class_name = dep.keys()[0]
            related_model = saved_models[dep[class_name]['node']]
            setattr(model, "%s_id" % class_name, related_model.id)
        return model

    @staticmethod
    def add_dependencies(data, requirements, saved_models):
        for dep in requirements:
            class_name = dep.keys()[0]
            related_model = saved_models[dep[class_name]['node']]
            data["%s_id" % class_name] = related_model.id
        return data

    def __init__(self, recipe, username, password, **kwargs):

        self.delete = False
        if 'delete' in kwargs:
            self.delete = True

        # store username/password combination to read resources
        self.username = username
        self.password = password

        # the template returned by TOSCA-Parser
        self.template = None
        # dictionary containing the models in the recipe and their template
        self.templates_by_model_name = None
        # list of models ordered by requirements
        self.ordered_models_name = []
        # dictionary containing the saved model
        self.saved_model_by_name = {}

        self.ordered_models_template = []

        self.recipe = recipe

    def execute(self):

        try:
            # [] save the recipe to a tmp file
            with NamedTemporaryFile(delete=False, suffix=".yaml", dir=TOSCA_RECIPES_DIR) as recipe_file:
                try:
                    recipe_file.write(self.recipe)
                    recipe_file.close()

                    # [] parse the recipe with TOSCA Parse
                    self.template = ToscaTemplate(recipe_file.name)
                finally:
                    # [] Make sure the temporary file is cleaned up
                    os.remove(recipe_file.name)

            # [] get all models in the recipe
            self.templates_by_model_name = self.get_tosca_models_by_name(self.template)
            # [] compute requirements
            self.compute_dependencies(self.template, self.templates_by_model_name)
            # [] topsort requirements
            self.ordered_models_name = self.topsort_dependencies(self.templates_by_model_name)
            # [] topsort templates
            self.ordered_models_template = self.get_ordered_models_template(self.ordered_models_name, self.templates_by_model_name)

            for recipe in self.ordered_models_template:
                try:
                    # get properties from tosca
                    if not 'properties' in recipe.templates[recipe.name]:
                        data = {}
                    else:
                        data = recipe.templates[recipe.name]['properties']
                        if data == None:
                            data = {}
                    # [] get model by class name
                    class_name = recipe.type.replace("tosca.nodes.", "")

                    # augemnt data with relations
                    data = self.add_dependencies(data, recipe.requirements, self.saved_model_by_name)

                    model = GRPCModelsAccessor.get_model_from_classname(class_name, data, self.username, self.password)
                    # [] populate model with data
                    model = self.populate_model(model, data)
                    # [] check if the model has requirements
                    # [] if it has populate them
                    model = self.populate_dependencies(model, recipe.requirements, self.saved_model_by_name)
                    # [] save, update or delete

                    reference_only = False
                    if 'must-exist' in data:
                        reference_only = True

                    if self.delete and not model.is_new and not reference_only:
                        log.info("[XOS-Tosca] Deleting model %s[%s]" % (class_name, model.id))
                        model.delete()
                    elif not self.delete:
                        log.info("[XOS-Tosca] Saving model %s[%s]" % (class_name, model.id))
                        model.save()


                    self.saved_model_by_name[recipe.name] = model
                except Exception, e:
                    log.exception("[XOS-TOSCA] Failed to save model: %s [%s]" % (class_name, recipe.name))
                    raise e

        except ValidationError as e:
            if e.message:
                exception_msg = TOSCA_Parser._translate_exception(e.message)
            else:
                exception_msg = TOSCA_Parser._translate_exception(str(e))
            raise Exception(exception_msg)

        except _Rendezvous, e:
            try:
                details = json.loads(e._state.details)
                exception_msg = details["error"]
                if "specific_error" in details:
                    exception_msg = "%s: %s" % (exception_msg, details["specific_error"])
            except Exception:
                exception_msg = e._state.details
            raise Exception(exception_msg)
        except Exception, e:
            log.exception(e)
            raise Exception(e)


