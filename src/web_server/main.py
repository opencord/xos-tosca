from grpc_client.main import GRPC_Client
from klein import Klein
import os
from tosca.parser import TOSCA_Parser
from tosca.default import TOSCA_DEFS_DIR
import json

BANNER = """
   _  ______  _____    __________  _____ _________ 
  | |/ / __ \/ ___/   /_  __/ __ \/ ___// ____/   |
  |   / / / /\__ \     / / / / / /\__ \/ /   / /| |
 /   / /_/ /___/ /    / / / /_/ /___/ / /___/ ___ |
/_/|_\____//____/    /_/  \____//____/\____/_/  |_|
"""

class TOSCA_WebServer:

    current_dir = os.path.dirname(os.path.realpath(__file__))
    template_dir = os.path.join(current_dir, 'templates/')

    app = Klein()

    def execute_tosca(self, recipe):
        try:
            self.parser.execute()
            response_text = "Created models: %s" % str(self.parser.ordered_models_name)
            return response_text
        except Exception, e:
            return e.message

    @app.route('/', methods=['GET'])
    def index(self, request):
        request.responseHeaders.addRawHeader(b"content-type", b"application/json")
        tosca_defs = [f for f in os.listdir(TOSCA_DEFS_DIR) if not f.startswith('.')]

        response = {}
        for d in tosca_defs:
            name = d.replace('.yaml', '')
            response[name] = "/custom_type/%s" % name
        return json.dumps(response)

    @app.route("/custom_type/<name>")
    def custom_type(self, request, name):
        request.responseHeaders.addRawHeader(b"content-type", b"text/plain")
        custom_type = open(TOSCA_DEFS_DIR + '/' + name + '.yaml').read()
        return custom_type

    @app.route('/run', methods=['POST'])
    def run(self, request):
        recipe = request.content.read()
        headers = request.getAllHeaders()
        username = headers['xos-username']
        password = headers['xos-password']

        d = GRPC_Client().create_secure_client(username, password, recipe)
        self.parser = TOSCA_Parser(recipe, username, password)
        d.addCallback(self.execute_tosca)
        return d

    @app.route('/delete', methods=['POST'])
    def delete(self, request):
        recipe = request.content.read()
        headers = request.getAllHeaders()
        username = headers['xos-username']
        password = headers['xos-password']

        d = GRPC_Client().create_secure_client(username, password, recipe)
        self.parser = TOSCA_Parser(recipe, username, password, delete=True)
        d.addCallback(self.execute_tosca)
        return d

    def __init__(self):
        self.app.run('0.0.0.0', '9102')