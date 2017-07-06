import unittest
from mock import patch, MagicMock
from tosca.parser import TOSCA_Parser
from grpc_client.resources import RESOURCES

class FakeObj:
    new = None
    filter = None

class FakeGuiExt:
    objects = FakeObj

class FakeModel:
    save = None

mock_resources = {
    'XOSGuiExtension': FakeGuiExt
}

class TOSCA_Parser_E2E(unittest.TestCase):

    @patch.dict(RESOURCES, mock_resources, clear=True)
    @patch.object(FakeGuiExt.objects, 'filter', MagicMock(return_value=[FakeModel]))
    @patch.object(FakeModel, 'save')
    def test_basic_creation(self, mock_save):
        """
        [TOSCA_Parser] Should save models defined in a TOSCA recipe
        """
        recipe = """
tosca_definitions_version: tosca_simple_yaml_1_0

description: Persist xos-sample-gui-extension

imports:
   - custom_types/xosguiextension.yaml

topology_template:
  node_templates:

    # UI Extension
    test:
      type: tosca.nodes.XOSGuiExtension
      properties:
        name: test
        files: /spa/extensions/test/vendor.js, /spa/extensions/test/app.js
"""

        parser = TOSCA_Parser(recipe)

        parser.execute()

        # checking that the model has been saved
        mock_save.assert_called()

        self.assertIsNotNone(parser.templates_by_model_name['test'])
        self.assertEqual(parser.ordered_models_name, ['test'])

        # check that the model was saved with the expected values
        saved_model = parser.saved_model_by_name['test']
        self.assertEqual(saved_model.name, 'test')
        self.assertEqual(saved_model.files, '/spa/extensions/test/vendor.js, /spa/extensions/test/app.js')
