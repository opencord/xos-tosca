import os
from xosapi import xos_grpc_client
from xosapi.xos_grpc_client import Empty
from xosgenx.generator import XOSGenerator

class Main:

    def start(self):
        print "[XOS-TOSCA] Starting"
        self.conenct_to_core()
        self.get_xproto()


    def grpc_cb(self):
        self.client = xos_grpc_client.coreclient.xos_orm
        self.utility = xos_grpc_client.coreclient.utility

    def conenct_to_core(self):
        xos_grpc_client.start_api_parseargs(self.grpc_cb)

    def get_xproto(self):
        xproto = self.utility.GetXproto(Empty())
        self.generate_tosca(xproto)

    def generate_tosca(self, xproto):
        class Args:
            output = os.path.dirname(os.path.realpath(__file__)) + "/tosca/custom_types"
            inputs = str(xproto.xproto)
            target = 'tosca.xtarget'
            write_to_file = 'model'
            dest_extension = 'yaml'

        output = XOSGenerator.generate(Args())
        print output

if __name__ == '__main__':
    Main().start()