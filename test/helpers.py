import os
from xosconfig import Config
current_dir = os.path.dirname(os.path.realpath(__file__))
config_file = os.path.join(current_dir, 'test_config.yaml')
config_schema = os.path.join(current_dir, '../src/xos-tosca-config-schema.yaml')
Config.clear()
Config.init(config_file, config_schema)