import os
from default import TOSCA_DEFS_DIR
from xosgenx.generator import XOSGenerator
from xosapi.xos_grpc_client import Empty

class Args:
    pass

class TOSCA_Generator:
    def __init__(self, grpc_client=None):
        self.grpc_client = grpc_client

    def _clean(self, dir=TOSCA_DEFS_DIR):
        filesToRemove = [f for f in os.listdir(dir)]
        for f in filesToRemove:
            if not f.startswith('.'):
                os.remove(dir + '/' + f)

    def generate(self):
        self._clean()
        xproto = self.grpc_client.utilities.GetXproto(Empty())

        args = Args()
        args.output = TOSCA_DEFS_DIR
        args.inputs = str(xproto.xproto)
        args.target = 'tosca.xtarget'
        args.write_to_file = 'model'
        args.dest_extension = 'yaml'

        XOSGenerator.generate(args)
        print "[XOS-TOSCA] Recipes generated in %s" % args.output