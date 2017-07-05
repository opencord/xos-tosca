from tosca.parser import TOSCA_Parser
from grpc_client.main import GRPC_Client
from klein import Klein
import functools

BANNER = """
   _  ______  _____    __________  _____ _________ 
  | |/ / __ \/ ___/   /_  __/ __ \/ ___// ____/   |
  |   / / / /\__ \     / / / / / /\__ \/ /   / /| |
 /   / /_/ /___/ /    / / / /_/ /___/ / /___/ ___ |
/_/|_\____//____/    /_/  \____//____/\____/_/  |_|
"""

class TOSCA_WebServer:

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
        return BANNER

    @app.route('/run', methods=['POST'])
    def execute(self, request):
        recipe = request.content.read()
        headers = request.getAllHeaders()
        username = headers['xos-username']
        password = headers['xos-password']

        d = GRPC_Client().create_secure_client(username, password, recipe)
        self.parser = TOSCA_Parser(recipe, username, password)
        d.addCallback(self.execute_tosca)
        return d

    def __init__(self):
        self.app.run('0.0.0.0', '9102')