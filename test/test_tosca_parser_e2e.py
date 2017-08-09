
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
from tosca.parser import TOSCA_Parser
from grpc_client.resources import RESOURCES

class FakeObj:
    new = None
    filter = None

class FakeModel:
    save = None
    delete = None
    is_new = False
    id = 1

class FakeGuiExt:
    objects = FakeObj

class FakeSite:
    objects = FakeObj

class FakeUser:
    objects = FakeObj

USERNAME = "username"
PASSWORD = "pass"

mock_resources = {}
mock_resources["%s~%s" % (USERNAME, PASSWORD)] = {
    'XOSGuiExtension': FakeGuiExt,
    'Site': FakeSite,
    'User': FakeUser
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

        parser = TOSCA_Parser(recipe, USERNAME, PASSWORD)

        parser.execute()

        # checking that the model has been saved
        mock_save.assert_called()

        self.assertIsNotNone(parser.templates_by_model_name['test'])
        self.assertEqual(parser.ordered_models_name, ['test'])

        # check that the model was saved with the expected values
        saved_model = parser.saved_model_by_name['test']
        self.assertEqual(saved_model.name, 'test')
        self.assertEqual(saved_model.files, '/spa/extensions/test/vendor.js, /spa/extensions/test/app.js')

    @patch.dict(RESOURCES, mock_resources, clear=True)
    @patch.object(FakeGuiExt.objects, 'filter', MagicMock(return_value=[FakeModel]))
    @patch.object(FakeModel, 'delete')
    def test_basic_deletion(self, mock_delete):
        """
        [TOSCA_Parser] Should delete models defined in a TOSCA recipe
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

        parser = TOSCA_Parser(recipe, USERNAME, PASSWORD, delete=True)

        parser.execute()

        # checking that the model has been saved
        mock_delete.assert_called()

        self.assertIsNotNone(parser.templates_by_model_name['test'])
        self.assertEqual(parser.ordered_models_name, ['test'])

    @patch.dict(RESOURCES, mock_resources, clear=True)
    @patch.object(FakeSite.objects, 'filter', MagicMock(return_value=[FakeModel]))
    @patch.object(FakeUser.objects, 'filter', MagicMock(return_value=[FakeModel]))
    @patch.object(FakeModel, 'save')
    def test_related_models_creation(self, mock_save):
        """
        [TOSCA_Parser] Should save related models defined in a TOSCA recipe
        """

        recipe = """
tosca_definitions_version: tosca_simple_yaml_1_0

description: Create a new site with one user

imports:
   - custom_types/user.yaml
   - custom_types/site.yaml

topology_template:
  node_templates:

    # Site
    site_onlab:
      type: tosca.nodes.Site
      properties:
        name: Open Networking Lab
        site_url: http://onlab.us/
        hosts_nodes: True

    # User
    user_test:
      type: tosca.nodes.User
      properties:
        username: test@opencord.org
        email: test@opencord.org
        password: mypwd
        firstname: User
        lastname: Test
        is_admin: True
      requirements:
        - site:
            node: site_onlab
            relationship: tosca.relationships.BelongsToOne
"""

        parser = TOSCA_Parser(recipe, USERNAME, PASSWORD)

        parser.execute()

        self.assertEqual(mock_save.call_count, 2)

        self.assertIsNotNone(parser.templates_by_model_name['site_onlab'])
        self.assertIsNotNone(parser.templates_by_model_name['user_test'])
        self.assertEqual(parser.ordered_models_name, ['site_onlab', 'user_test'])

        # check that the model was saved with the expected values
        saved_site = parser.saved_model_by_name['site_onlab']
        self.assertEqual(saved_site.name, 'Open Networking Lab')

        saved_user = parser.saved_model_by_name['user_test']
        self.assertEqual(saved_user.firstname, 'User')
        self.assertEqual(saved_user.site_id, 1)

    @patch.dict(RESOURCES, mock_resources, clear=True)
    @patch.object(FakeSite.objects, 'filter', MagicMock(return_value=[]))
    def test_must_exist_fail(self):
        """
        [TOSCA_Parser] Should throw an error if an object with 'must_exist' does not exist
        """
        recipe = """
        tosca_definitions_version: tosca_simple_yaml_1_0

        description: Create a new site with one user

        imports:
           - custom_types/user.yaml
           - custom_types/site.yaml

        topology_template:
          node_templates:

            # Site
            site_onlab:
              type: tosca.nodes.Site
              properties:
                name: Open Networking Lab
                must-exist: True
        """

        parser = TOSCA_Parser(recipe, USERNAME, PASSWORD)

        with self.assertRaises(Exception) as e:
            parser.execute()

        self.assertEqual(e.exception.message, "[XOS-TOSCA] Model Site:Open Networking Lab has property 'must-exist' but cannot be found")
