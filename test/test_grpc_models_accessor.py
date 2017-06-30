import unittest
from mock import patch, MagicMock
from grpc_client.models_accessor import GRPCModelsAccessor
import grpc_client.resources

class FakeObj:
    new = None
    filter = None

class FakeResource:
    objects = FakeObj

class FakeModel:
    save = None

mock_resources = {
    'test-model': FakeResource
}

class GRPCModelsAccessor_Create_or_update_Test(unittest.TestCase):

    def test_unkown_module(self):
        """
        [GRPCModelsAccessor] get_model_from_classname: If a model is not know by the grpc api, raise
        """
        with self.assertRaises(Exception) as e:
            GRPCModelsAccessor.get_model_from_classname('i-do-not-exists', {})
        self.assertEqual(e.exception.message, "[XOS-TOSCA] The model your tring to create (i-do-not-exists) is not know by xos-core")

    @patch.object(grpc_client.resources, 'RESOURCES', MagicMock(return_value=mock_resources))
    @patch.object(FakeResource.objects, "filter")
    @patch.object(FakeResource.objects, "new", MagicMock(return_value=FakeModel))
    def _test_new_model(self, mock_filter):
        """
        [GRPCModelsAccessor] get_model_from_classname: should create a new model
        """
        data = {
            "name": "test"
        }

        model = GRPCModelsAccessor.get_model_from_classname('test-model', data)
        mock_filter.assert_called_with(name="test")

    @patch.object(FakeResource.objects, "filter", MagicMock(return_value=[FakeModel]))
    @patch.object(FakeModel, "save")
    def _test_existing_model(self, mock_save):
        """
        [GRPCModelsAccessor] get_model_from_classname: should update an existing model
        """
        data = {
            "name": "test"
        }

        GRPCModelsAccessor.get_model_from_classname(FakeResource, data)
        mock_save.assert_called_once()

    @patch.object(FakeResource.objects, "filter", MagicMock(return_value=['a', 'b']))
    def _test_multiple_models(self):
        """
        [GRPCModelsAccessor] get_model_from_classname: should raise an exception if multiple instances are found
        """
        data = {
            "name": "test"
        }
        with self.assertRaises(Exception) as e:
            GRPCModelsAccessor.get_model_from_classname(FakeResource, data)
        self.assertEqual(e.exception.message, "[XOS-Tosca] Model test has multiple instances, I can't handle it")

    @patch.object(FakeResource.objects, "new", MagicMock(return_value=FakeModel))
    @patch.object(FakeResource.objects, "filter")
    @patch.object(FakeModel, "save")
    def _test_find_model_without_name_property(self, mock_save, mock_filter):
        """
        [GRPCModelsAccessor] get_model_from_classname: should lookup a model by the first property
        """
        data = {
            'foo': 'bar',
            'something': 'else'
        }
        GRPCModelsAccessor.get_model_from_classname(FakeResource, data)
        mock_filter.assert_called_with(foo="bar")
        mock_save.assert_called_once()

if __name__ == '__main__':
    unittest.main()