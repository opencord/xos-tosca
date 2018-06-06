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

import os
from xosconfig import Config
current_dir = os.path.dirname(os.path.realpath(__file__))
config_file = os.path.join(current_dir, 'test_config.yaml')
config_schema = os.path.join(current_dir, '../src/xos-tosca-config-schema.yaml')
Config.clear()
Config.init(config_file, config_schema)