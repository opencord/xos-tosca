
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


import functools
from xosapi.xos_grpc_client import SecureClient, InsecureClient
from twisted.internet import defer
from resources import RESOURCES
from xosconfig import Config
from twisted.internet import reactor

from xosconfig import Config
from multistructlog import create_logger
log = create_logger(Config().get('logging'))

class GRPC_Client:
    def __init__(self):
        self.client = None

        insecure = Config.get('gprc_endpoint')
        secure = Config.get('gprc_endpoint')

        self.grpc_secure_endpoint = secure + ":50051"
        self.grpc_insecure_endpoint = insecure + ":50055"

    def setup_resources(self, client, key, deferred, arg):
        log.info("[XOS-TOSCA] Loading resources for authenticated user")
        if key not in RESOURCES:
            RESOURCES[key] = {}
        for k in client.xos_orm.all_model_names:
            RESOURCES[key][k] = getattr(client.xos_orm, k)
        reactor.callLater(0, deferred.callback, arg)

    def start(self):
        log.info("[XOS-TOSCA] Connecting to xos-core")

        deferred = defer.Deferred()

        if self.client:
            self.client.stop()
            self.client.session_change = True

        self.client = InsecureClient(endpoint=self.grpc_insecure_endpoint)
        self.client.restart_on_disconnect = True

        self.client.set_reconnect_callback(functools.partial(deferred.callback, self.client))
        self.client.start()

        return deferred

    def create_secure_client(self, username, password, arg):
        """
        This method will check if this combination of username/password already has stored orm classes in RESOURCES, otherwise create them
        """
        deferred = defer.Deferred()
        key = "%s~%s" % (username, password)
        if key in RESOURCES:
            reactor.callLater(0, deferred.callback, arg)
        else:
            local_cert = Config.get('local_cert')
            client = SecureClient(endpoint=self.grpc_secure_endpoint, username=username, password=password, cacert=local_cert)
            client.restart_on_disconnect = True
            # SecureClient is preceeded by an insecure client, so treat all secure clients as previously connected
            # See CORD-3152
            client.was_connected = True
            client.set_reconnect_callback(functools.partial(self.setup_resources, client, key, deferred, arg))
            client.start()
        return deferred
