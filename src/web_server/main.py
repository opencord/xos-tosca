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

from __future__ import absolute_import, print_function

import json
import os

from grpc_client import GRPC_Client
from klein import Klein
from multistructlog import create_logger
from tosca.default import TOSCA_DEFS_DIR
from tosca.parser import TOSCA_Parser
from xosconfig import Config

log = create_logger(Config().get("logging"))


BANNER = r"""
   _  ______  _____    __________  _____ _________
  | |/ / __ \/ ___/   /_  __/ __ \/ ___// ____/   |
  |   / / / /\__ \     / / / / / /\__ \/ /   / /| |
 /   / /_/ /___/ /    / / / /_/ /___/ / /___/ ___ |
/_/|_\____//____/    /_/  \____//____/\____/_/  |_|
"""


class TOSCA_WebServer:

    current_dir = os.path.dirname(os.path.realpath(__file__))
    template_dir = os.path.join(current_dir, "templates/")

    app = Klein()

    def execute_tosca(self, parser):
        parser.execute()
        if parser.delete:
            response_text = "Deleted models: %s" % str(parser.ordered_models_name)
        else:
            response_text = "Created models: %s" % str(parser.ordered_models_name)
        return response_text

    def errorCallback(self, failure, request):
        request.setResponseCode(500)
        try:
            f = failure.getErrorMessage()
            if f.startswith("XOSPermissionDenied"):
                request.setResponseCode(401)
            log.info("[XOS-TOSCA] Error while loading TOSCA: \n\n", failure=f)
            return f
        except Exception:
            log.info("[XOS-TOSCA] Fatal Error: \n\n", failure=failure)
            return "Internal server error, please report this along with the failed recipe."

    @app.route("/", methods=["GET"])
    def index(self, request):
        request.responseHeaders.addRawHeader(b"content-type", b"application/json")
        tosca_defs = [f for f in os.listdir(TOSCA_DEFS_DIR) if not f.startswith(".")]

        response = {}
        for d in tosca_defs:
            name = d.replace(".yaml", "")
            response[name] = "/custom_type/%s" % name
        return json.dumps(response)

    @app.route("/custom_type/<name>")
    def custom_type(self, request, name):
        request.responseHeaders.addRawHeader(b"content-type", b"text/plain")
        custom_type = open(TOSCA_DEFS_DIR + "/" + name + ".yaml").read()
        return custom_type

    @app.route("/run", methods=["POST"])
    def run(self, request):
        return self._handle_post(request, delete=False)

    @app.route("/delete", methods=["POST"])
    def delete(self, request):
        return self._handle_post(request, delete=True)

    def _handle_post(self, request, delete=False):

        headers = request.getAllHeaders()
        username = headers["xos-username"]
        password = headers["xos-password"]
        recipe = request.content.read()

        parser = TOSCA_Parser(recipe, username, password, delete=delete)
        d = GRPC_Client().create_secure_client(username, password, parser)
        tosca_execution = d.addCallback(self.execute_tosca)
        tosca_execution.addErrback(self.errorCallback, request)
        return d

    def __init__(self):
        self.app.run("0.0.0.0", "9102")
