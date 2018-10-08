
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
from xosgenx.generator import XOSProcessor, XOSProcessorArgs

current_dir = os.path.dirname(os.path.realpath(__file__))
OUTPUT_DIR = os.path.join(current_dir, 'out');
print OUTPUT_DIR

class TOSCA_Generator_Test(unittest.TestCase):

    def test_generate_basic_tosca(self):
        """
        [TOSCA_xtarget] Should generate a basic TOSCA recipe
        """
        xproto = \
            """
            option app_label = "core";

            message XOSGuiExtension (XOSBase) {
                 option verbose_name="XOS GUI Extension";
                 option description="This model holds the instruction to load an extension in the GUI";
                 required string name = 1 [max_length = 200, content_type = "stripped", blank = False, help_text = "Name of the GUI Extensions", null = False, db_index = False];
                 required string files = 2 [max_length = 1024, content_type = "stripped", blank = False, help_text = "List of comma separated file composing the view", null = False, db_index = False];
            }
            """
        args = XOSProcessorArgs(inputs = xproto,
                                target = os.path.join(current_dir, '../src/tosca/xtarget/tosca.xtarget'),
                                output = OUTPUT_DIR,
                                write_to_file = "single",
                                dest_file = "basic.yaml",
                                quiet = False)
        output = XOSProcessor.process(args)
        self.assertIn("name:", output)
        self.assertIn("files:", output)

    def test_generate_inherithed_tosca(self):
        """
        [TOSCA_xtarget] Should generate a TOSCA recipe for a models that inherits from another model
        """
        xproto = \
            """
            option app_label = "core";

            message Service (XosBase) {
                 option verbose_name="Basic Service";
                 required string name = 1 [max_length = 200, content_type = "stripped", blank = False, null = False, db_index = False];
            }
            
            message MyService (Service) {
                 option verbose_name="Extending service";
                 required string prop = 1 [max_length = 200, content_type = "stripped", blank = False, null = False, db_index = False];
            }
            """
        args = XOSProcessorArgs(inputs = xproto,
                                target = os.path.join(current_dir, '../src/tosca/xtarget/tosca.xtarget'),
                                output = OUTPUT_DIR,
                                write_to_file = 'target',
                                quiet = False)
        output = XOSProcessor.process(args)
        self.assertEqual(output.count("name:"), 4)
        self.assertIn("prop:", output)

if __name__ == '__main__':
  unittest.main()
