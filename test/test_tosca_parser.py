
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


from helpers import *
import unittest
import os
from tosca.parser import TOSCA_Parser

class TOSCA_Parser_Test(unittest.TestCase):

    def test_get_tosca_models_by_name(self):
        """
        [TOSCA_Parser] get_tosca_models_by_name: should extract models from the TOSCA recipe and store them in a dict
        """
        class FakeNode:
            def __init__(self, name):
                self.name = name

        class FakeTemplate:
            nodetemplates = [
                FakeNode('model1'),
                FakeNode('model2')
            ]


        res = TOSCA_Parser.get_tosca_models_by_name(FakeTemplate)
        self.assertIsInstance(res['model1'], FakeNode)
        self.assertIsInstance(res['model2'], FakeNode)

        self.assertEqual(res['model1'].name, 'model1')
        self.assertEqual(res['model2'].name, 'model2')

    def test_populate_dependencies(self):
        """
        [TOSCA_Parser] populate_dependencies: if a recipe has dependencies, it should find the ID of the requirements and add it to the model
        """
        class FakeRecipe:
            requirements = [
                {
                    'site': {
                        'node': 'site_onlab',
                        'relationship': 'tosca.relationship.BelongsToOne'
                    }
                }
            ]

        class FakeSite:
            id = 1
            name = 'onlab'

        class FakeModel:
            name = 'test@opencord.org'

        saved_models = {
            'site_onlab': FakeSite
        }

        model = TOSCA_Parser.populate_dependencies(FakeModel, FakeRecipe.requirements, saved_models)
        self.assertEqual(model.site_id, 1)

    def test_get_ordered_models_template(self):
        """
        [TOSCA_Parser] get_ordered_models_template: Create a list of templates based on topsorted models
        """
        ordered_models = ['foo', 'bar']

        templates = {
            'foo': 'foo_template',
            'bar': 'bar_template'
        }

        ordered_templates = TOSCA_Parser.get_ordered_models_template(ordered_models, templates)

        self.assertEqual(ordered_templates[0], 'foo_template')
        self.assertEqual(ordered_templates[1], 'bar_template')

    def test_topsort_dependencies(self):
        """
        [TOSCA_Parser] topsort_dependencies: Create a list of models based on dependencies
        """
        class FakeTemplate:
            def __init__(self, name, deps):
                self.name = name
                self.dependencies_names =  deps


        templates = {
            'deps': FakeTemplate('deps', ['main']),
            'main': FakeTemplate('main', []),
        }

        sorted = TOSCA_Parser.topsort_dependencies(templates)

        self.assertEqual(sorted[0], 'main')
        self.assertEqual(sorted[1], 'deps')

    def test_compute_dependencies(self):
        """
        [TOSCA_Parser] compute_dependencies: augment the TOSCA nodetemplate with information on requirements (aka related models)
        """

        parser = TOSCA_Parser('', 'user', 'pass')

        class FakeNode:
            def __init__(self, name, requirements):
                self.name = name
                self.requirements = requirements

        main = FakeNode('main', [])
        dep = FakeNode('dep', [{'relation': {'node': 'main'}}])

        models_by_name = {
            'main': main,
            'dep': dep
        }

        class FakeTemplate:
            nodetemplates = [dep, main]

        parser.compute_dependencies(FakeTemplate, models_by_name)

        templates = FakeTemplate.nodetemplates
        augmented_dep = templates[0]
        augmented_main = templates[1]

        self.assertIsInstance(augmented_dep.dependencies[0], FakeNode)
        self.assertEqual(augmented_dep.dependencies[0].name, 'main')
        self.assertEqual(augmented_dep.dependencies_names[0], 'main')

        self.assertEqual(len(augmented_main.dependencies), 0)
        self.assertEqual(len(augmented_main.dependencies_names), 0)

    def test_populate_model(self):
        """
        [TOSCA_Parser] populate_model: augment the GRPC model with data from TOSCA
        """
        class FakeModel:
            pass

        data = {
            'name': 'test',
            'foo': 'bar',
            'number': 1
        }

        model = TOSCA_Parser.populate_model(FakeModel, data)

        self.assertEqual(model.name, 'test')
        self.assertEqual(model.foo, 'bar')
        self.assertEqual(model.number, 1)

    def test_populate_model_error(self):
        """
        [TOSCA_Parser] populate_model: should print a meaningful error message
        """

        class FakeModel:

            model_name = "FakeModel"

            def __setattr__(self, name, value):
                if name == 'foo':
                    raise TypeError('reported exception')
                else:
                    super(FakeModel, self).__setattr__(name, value)

        data = {
            'name': 'test',
            'foo': None,
            'number': 1
        }


        model = FakeModel()

        with self.assertRaises(Exception) as e:
            model = TOSCA_Parser.populate_model(model, data)
        self.assertEqual(e.exception.message, 'Failed to set None on field foo for class FakeModel, Exception was: "reported exception"')

    def test_translate_exception(self):
        """
        [TOSCA_Parser] translate_exception: convert a TOSCA Parser exception in a user readable string
        """
        e = TOSCA_Parser._translate_exception("Non tosca exception")
        self.assertEqual(e, "Non tosca exception")

        e = TOSCA_Parser._translate_exception("""        
MissingRequiredFieldError: some message
    followed by unreadable
    and mystic
        python error
        starting at line
            38209834 of some file
UnknownFieldError: with some message
    followed by useless things
ImportError: with some message
    followed by useless things
InvalidTypeError: with some message
    followed by useless things
TypeMismatchError: with some message
    followed by useless things
        """)
        self.assertEqual(e, """MissingRequiredFieldError: some message
UnknownFieldError: with some message
ImportError: with some message
InvalidTypeError: with some message
TypeMismatchError: with some message
""")
