import sys, os
import unittest
from mock import patch, MagicMock
from tosca.parser import TOSCA_Parser

class FakeObj:
    new = None
    filter = None

class FakeResource:
    objects = FakeObj

class FakeModel:
    save = None

class TOSCA_Parser_Create_or_update_Test(unittest.TestCase):

    @patch.object(FakeResource.objects, "filter")
    @patch.object(FakeResource.objects, "new", MagicMock(return_value=FakeModel))
    @patch.object(FakeModel, "save")
    def test_new_model(self, mock_save, mock_filter):
        """
        [TOSCA_Parser] create_or_update: should create a new model
        """
        data = {
            "name": "test"
        }

        TOSCA_Parser.creat_or_update(FakeResource, data)
        mock_filter.assert_called_with(name="test")
        mock_save.assert_called_once()

    @patch.object(FakeResource.objects, "filter", MagicMock(return_value=[FakeModel]))
    @patch.object(FakeModel, "save")
    def test_existing_model(self, mock_save):
        """
        [TOSCA_Parser] create_or_update: should update an existing model
        """
        data = {
            "name": "test"
        }

        TOSCA_Parser.creat_or_update(FakeResource, data)
        mock_save.assert_called_once()

    @patch.object(FakeResource.objects, "filter", MagicMock(return_value=['a', 'b']))
    def test_multiple_models(self):
        """
        [TOSCA_Parser] create_or_update: should raise an exception if multiple instances are found
        """
        data = {
            "name": "test"
        }
        with self.assertRaises(Exception) as e:
            TOSCA_Parser.creat_or_update(FakeResource, data)
        self.assertEqual(e.exception.message, "[XOS-Tosca] Model test has multiple instances, I can't handle it")

    @patch.object(FakeResource.objects, "new", MagicMock(return_value=FakeModel))
    @patch.object(FakeResource.objects, "filter")
    @patch.object(FakeModel, "save")
    def test_find_model_without_name_property(self, mock_save, mock_filter):
        """
        [TOSCA_Parser] create_or_update: should lookup a model by the first property
        """
        data = {
            'foo': 'bar',
            'something': 'else'
        }
        TOSCA_Parser.creat_or_update(FakeResource, data)
        mock_filter.assert_called_with(foo="bar")
        mock_save.assert_called_once()

if __name__ == '__main__':
    unittest.main()