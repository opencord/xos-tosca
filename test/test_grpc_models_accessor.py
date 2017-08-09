
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


import unittest
from mock import patch, MagicMock
from grpc_client.models_accessor import GRPCModelsAccessor
from grpc_client.resources import RESOURCES

class FakeObj:
    new = None
    filter = None

class FakeResource:
    objects = FakeObj

class FakeModel:
    pass

class FakeExistingModel:
    pass

mock_resources = {
    'username~pass': {
        'test-model': FakeResource
    }
}

USERNAME = 'username'
PASSWORD = 'pass'

class GRPCModelsAccessor_Create_or_update_Test(unittest.TestCase):

    def test_unkown_user(self):
        """
        [GRPCModelsAccessor] get_model_from_classname: If a user does not have orm classes, raise
        """
        data = {
            "name": "test"
        }
        with self.assertRaises(Exception) as e:
            GRPCModelsAccessor.get_model_from_classname('i-do-not-exists', data, USERNAME, PASSWORD)
        self.assertEqual(e.exception.message, "[XOS-TOSCA] User 'username' does not have ready resources")

    @patch.dict(RESOURCES, mock_resources, clear=True)
    def test_unkown_module(self):
        """
        [GRPCModelsAccessor] get_model_from_classname: If a model is not know by the grpc api, raise
        """
        data = {
            "name": "test"
        }
        with self.assertRaises(Exception) as e:
            GRPCModelsAccessor.get_model_from_classname('i-do-not-exists', data, USERNAME, PASSWORD)
        self.assertEqual(e.exception.message, "[XOS-TOSCA] The model you are trying to create (name: test, class: i-do-not-exists) is not know by xos-core")

    @patch.object(FakeResource.objects, "filter")
    @patch.object(FakeResource.objects, "new", MagicMock(return_value=FakeModel))
    def test_new_model(self, mock_filter):
        """
        [GRPCModelsAccessor] get_model_from_classname: should create a new model
        """
        data = {
            "name": "test"
        }
        with patch.dict(RESOURCES, mock_resources, clear=True):
            model = GRPCModelsAccessor.get_model_from_classname('test-model', data, USERNAME, PASSWORD)
            mock_filter.assert_called_with(name="test")
            self.assertEqual(model, FakeModel)

    @patch.object(FakeResource.objects, "filter", MagicMock(return_value=[FakeExistingModel]))
    def test_existing_model(self):
        """
        [GRPCModelsAccessor] get_model_from_classname: should update an existing model
        """
        data = {
            "name": "test"
        }
        with patch.dict(RESOURCES, mock_resources, clear=True):
            model = GRPCModelsAccessor.get_model_from_classname('test-model', data, USERNAME, PASSWORD)
            self.assertEqual(model, FakeExistingModel)

    @patch.object(FakeResource.objects, "filter", MagicMock(return_value=['a', 'b']))
    def test_multiple_models(self):
        """
        [GRPCModelsAccessor] get_model_from_classname: should raise an exception if multiple instances are found
        """
        data = {
            "name": "test"
        }
        with patch.dict(RESOURCES, mock_resources, clear=True):
            with self.assertRaises(Exception) as e:
                GRPCModelsAccessor.get_model_from_classname('test-model', data, USERNAME, PASSWORD)
            self.assertEqual(e.exception.message, "[XOS-Tosca] Model test has multiple instances, I can't handle it")

    @patch.dict(RESOURCES, mock_resources, clear=True)
    @patch.object(FakeResource.objects, "filter")
    @patch.object(FakeResource.objects, "new")
    def test_find_model_without_name_property(self, mock_new, mock_filter):
        """
        [GRPCModelsAccessor] get_model_from_classname: should lookup a model by the first property
        """
        data = {
            'foo': 'bar',
            'something': 'else'
        }
        GRPCModelsAccessor.get_model_from_classname('test-model', data, USERNAME, PASSWORD)
        mock_filter.assert_called_with(foo="bar")
        mock_new.assert_called()

if __name__ == '__main__':
    unittest.main()