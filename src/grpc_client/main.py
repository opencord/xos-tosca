from xosapi import xos_grpc_client

class GRPC_Client:
    def __init__(self):
        self.xos_orm = None
        self.utilities = None

    def _handle_connection(self):
        self.xos_orm = xos_grpc_client.coreclient.xos_orm
        self.utilities = xos_grpc_client.coreclient.utility

    def start(self):
        print "[XOS-TOSCA] Connecting to xos-core"
        xos_grpc_client.start_api_parseargs(self._handle_connection)