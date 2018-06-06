
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
from mock import patch, MagicMock
from grpc_client.models_accessor import GRPCModelsAccessor
from grpc_client.resources import RESOURCES
from grpc_client.KEYS import TOSCA_KEYS

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
        'test-model': FakeResource,
        'single-key': FakeResource,
        'double-key': FakeResource,
        'one-of-key': FakeResource
    }
}

mock_keys = {
    'i-do-not-exists': ['name'],
    'test-model': ['name'],
    'empty-key': [],
    'single-key': ['fake_key'],
    'double-key': ['key_1', 'key_2'],
    'one-of-key': ['key_1', ['key_2', 'key_3']],
}

USERNAME = 'username'
PASSWORD = 'pass'

class GRPCModelsAccessor_Create_or_update_Test(unittest.TestCase):

    @patch.dict(TOSCA_KEYS, mock_keys, clear=True)
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
    @patch.dict(TOSCA_KEYS, mock_keys, clear=True)
    def test_unkown_module(self):
        """
        [GRPCModelsAccessor] get_model_from_classname: If a model is not know by the grpc api, raise
        """
        data = {
            "name": "test"
        }
        with self.assertRaises(Exception) as e:
            GRPCModelsAccessor.get_model_from_classname('i-do-not-exists', data, USERNAME, PASSWORD)
        self.assertEqual(e.exception.message, "[XOS-TOSCA] The model you are trying to create (class: i-do-not-exists, properties, {'name': 'test'}) is not know by xos-core")

    def test_unkown_tosca_key(self):
        """
        [GRPCModelsAccessor] get_model_from_classname: If a model does not have a tosca_key, raise
        """
        data = {
            "name": "test"
        }
        with self.assertRaises(Exception) as e:
            GRPCModelsAccessor.get_model_from_classname('no-key', data, USERNAME, PASSWORD)
        self.assertEqual(e.exception.message, "[XOS-TOSCA] Model no-key doesn't have a tosca_key specified")

    @patch.dict(TOSCA_KEYS, mock_keys, clear=True)
    def test_empty_tosca_key(self):
        """
        [GRPCModelsAccessor] get_model_from_classname: If a model does not have a tosca_key, raise
        """
        data = {
            "name": "test"
        }
        with self.assertRaises(Exception) as e:
            GRPCModelsAccessor.get_model_from_classname('empty-key', data, USERNAME, PASSWORD)
        self.assertEqual(e.exception.message, "[XOS-TOSCA] Model empty-key doesn't have a tosca_key specified")

    @patch.dict(TOSCA_KEYS, mock_keys, clear=True)
    def test_tosca_key_are_defined(self):
        """
        [GRPCModelsAccessor] get_model_from_classname: a model should have a property for it's tosca_key
        """
        data = {
            "name": "test",
        }
        with self.assertRaises(Exception) as e:
            GRPCModelsAccessor.get_model_from_classname('single-key', data, USERNAME, PASSWORD)
        self.assertEqual(e.exception.message, "[XOS-TOSCA] Model single-key doesn't have a property for the specified tosca_key ('fake_key')")

    @patch.object(FakeResource.objects, "filter")
    @patch.object(FakeResource.objects, "new", MagicMock(return_value=FakeModel))
    @patch.dict(TOSCA_KEYS, mock_keys, clear=True)
    def test_composite_key(self, mock_filter):
        """
        [GRPCModelsAccessor] get_model_from_classname: should use a composite key to lookup a model
        """
        data = {
            "name": "test",
            "key_1": "key1",
            "key_2": "key2"
        }
        with patch.dict(RESOURCES, mock_resources, clear=True):
            model = GRPCModelsAccessor.get_model_from_classname('double-key', data, USERNAME, PASSWORD)
            mock_filter.assert_called_with(key_1="key1", key_2="key2")
            self.assertEqual(model, FakeModel)

    @patch.object(FakeResource.objects, "filter")
    @patch.object(FakeResource.objects, "new", MagicMock(return_value=FakeModel))
    @patch.dict(TOSCA_KEYS, mock_keys, clear=True)
    def test_one_of_key(self, mock_filter):
        """
        [GRPCModelsAccessor] get_model_from_classname: should use a composite with one_of key to lookup a model
        """
        # NOTE it should be valid for items with either one of the keys
        data2 = {
            "name": "test",
            "key_1": "key1",
            "key_2": "key2"
        }
        with patch.dict(RESOURCES, mock_resources, clear=True):
            model = GRPCModelsAccessor.get_model_from_classname('one-of-key', data2, USERNAME, PASSWORD)
            mock_filter.assert_called_with(key_1="key1", key_2="key2")
            self.assertEqual(model, FakeModel)

        data3 = {
            "name": "test",
            "key_1": "key1",
            "key_3": "key3"
        }
        with patch.dict(RESOURCES, mock_resources, clear=True):
            model = GRPCModelsAccessor.get_model_from_classname('one-of-key', data3, USERNAME, PASSWORD)
            mock_filter.assert_called_with(key_1="key1", key_3="key3")
            self.assertEqual(model, FakeModel)

    @patch.object(FakeResource.objects, "filter")
    @patch.object(FakeResource.objects, "new", MagicMock(return_value=FakeModel))
    @patch.dict(TOSCA_KEYS, mock_keys, clear=True)
    def test_one_of_key_error(self, mock_filter):
        data = {
            "name": "test",
            "key_1": "key1"
        }
        with self.assertRaises(Exception) as e:
            GRPCModelsAccessor.get_model_from_classname('one-of-key', data, USERNAME, PASSWORD)
        self.assertEqual(e.exception.message, "[XOS-TOSCA] Model one-of-key doesn't have a property for the specified tosca_key_one_of (['key_2', 'key_3'])")

    @patch.object(FakeResource.objects, "filter")
    @patch.object(FakeResource.objects, "new", MagicMock(return_value=FakeModel))
    @patch.dict(TOSCA_KEYS, mock_keys, clear=True)
    def test_new_model(self, mock_filter):
        """
        [GRPCModelsAccessor] get_model_from_classname: should create a new model
        """
        data = {
            "name": "test",
            "fake_key": "key"
        }
        with patch.dict(RESOURCES, mock_resources, clear=True):
            model = GRPCModelsAccessor.get_model_from_classname('single-key', data, USERNAME, PASSWORD)
            mock_filter.assert_called_with(fake_key="key")
            self.assertEqual(model, FakeModel)

    @patch.object(FakeResource.objects, "filter", MagicMock(return_value=[FakeExistingModel]))
    @patch.dict(TOSCA_KEYS, mock_keys, clear=True)
    def test_existing_model(self):
        """
        [GRPCModelsAccessor] get_model_from_classname: should update an existing model
        """
        data = {
            "name": "test",
            "fake_key": "key"
        }
        with patch.dict(RESOURCES, mock_resources, clear=True):
            model = GRPCModelsAccessor.get_model_from_classname('single-key', data, USERNAME, PASSWORD)
            self.assertEqual(model, FakeExistingModel)

    @patch.object(FakeResource.objects, "filter", MagicMock(return_value=['a', 'b']))
    @patch.dict(TOSCA_KEYS, mock_keys, clear=True)
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
            self.assertEqual(e.exception.message, "[XOS-Tosca] Model of class test-model and properties {'name': 'test'} has multiple instances, I can't handle it")

if __name__ == '__main__':
    unittest.main()