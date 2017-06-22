from grpc_client.main import GRPC_Client
from tosca.generator import TOSCA_Generator
from web_server.main import TOSCA_WebServer
class Main:

    def __init__(self):
        self.grpc_client = None

    def start(self):
        print "[XOS-TOSCA] Starting"

        # self.grpc_client = GRPC_Client()
        # self.grpc_client.start()
        # TOSCA_Generator(self.grpc_client).generate()

        TOSCA_WebServer()


if __name__ == '__main__':
    Main().start()