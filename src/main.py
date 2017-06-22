from grpc_client.main import GRPC_Client
from tosca.generator import TOSCA_Generator
from web_server.main import TOSCA_WebServer
from twisted.internet import reactor, defer
import functools

class Main:

    def __init__(self):
        self.grpc_client = None

    def generate_tosca(self, client):

        deferred = defer.Deferred()

        TOSCA_Generator().generate(client)

        reactor.callLater(0, TOSCA_WebServer)

        return deferred

    def start(self):
        print "[XOS-TOSCA] Starting"

        grpc_setup = GRPC_Client().start('xosadmin@opencord.org', 'rk1UYDHZXbu6KVCMkhmV')
        # grpc_setup = GRPC_Client().start()
        grpc_setup.addCallback(self.generate_tosca)

        reactor.run()


if __name__ == '__main__':
    Main().start()