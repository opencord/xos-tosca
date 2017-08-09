
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


from resources import RESOURCES

class GRPCModelsAccessor:
    """
    This class provide the glue between the models managed by TOSCA and the ones living in xos-core
    """

    @staticmethod
    def get_model_from_classname(class_name, data, username, password):
        """
        Give a Model Class Name and some data, check if that exits or instantiate a new one
        """

        if data.get('name'):
            used_key = 'name'
        else:
            # FIXME apparently we're not matching model without a name field
            used_key = data.keys()[0]

        key = "%s~%s" % (username, password)
        if not key in RESOURCES:
            raise Exception("[XOS-TOSCA] User '%s' does not have ready resources" % username)
        if class_name not in RESOURCES[key]:
            raise Exception('[XOS-TOSCA] The model you are trying to create (%s: %s, class: %s) is not know by xos-core' % (used_key, data[used_key], class_name))

        cls = RESOURCES[key][class_name]
        models = cls.objects.filter(**{used_key: data[used_key]})

        if len(models) == 1:
            print "[XOS-Tosca] Model %s already exist, retrieving instance..." % data[used_key]
            model = models[0]
        elif len(models) == 0:

            if 'must-exist' in data and data['must-exist']:
                raise Exception("[XOS-TOSCA] Model %s:%s has property 'must-exist' but cannot be found" % (class_name, data[used_key]))

            model = cls.objects.new()
            print "[XOS-Tosca] Model %s is new, creating new instance..." % data[used_key]
        else:
            raise Exception("[XOS-Tosca] Model %s has multiple instances, I can't handle it" % data[used_key])
        return model