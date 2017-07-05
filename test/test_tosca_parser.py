import unittest
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
            pass


        res = TOSCA_Parser.get_tosca_models_by_name(FakeTemplate)
        self.assertIsInstance(res['model1'], FakeNode)
        self.assertIsInstance(res['model2'], FakeNode)

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