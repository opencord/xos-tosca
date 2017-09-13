
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
from grpc_client.main import GRPC_Client
from tosca.generator import TOSCA_Generator
from web_server.main import TOSCA_WebServer
from twisted.internet import defer
from xosconfig import Config

current_dir = os.path.dirname(os.path.realpath(__file__))
config_file = os.path.join(current_dir, './xos-tosca-config.yaml')
config_schema = os.path.join(current_dir, './xos-tosca-config-schema.yaml')
Config.init(config_file, config_schema)

class Main:

    def __init__(self):
        self.grpc_client = None

    def generate_tosca(self, client):

        deferred = defer.Deferred()

        TOSCA_Generator().generate(client)

        return deferred

    def start(self):
        print "[XOS-TOSCA] Starting"

        grpc_setup = GRPC_Client().start()
        grpc_setup.addCallback(self.generate_tosca)

        # NOTE that TOSCA_WebServer create a Klein app that call reactor.run()
        TOSCA_WebServer()


if __name__ == '__main__':
    Main().start()