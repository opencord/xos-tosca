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