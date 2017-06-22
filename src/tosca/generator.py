import os
from default import TOSCA_DEFS_DIR
from xosgenx.generator import XOSGenerator
from xosapi.xos_grpc_client import Empty

class Args:
    pass

current_dir = os.path.dirname(os.path.realpath(__file__))

class TOSCA_Generator:

    def _clean(self, dir=TOSCA_DEFS_DIR):
        filesToRemove = [f for f in os.listdir(dir)]
        for f in filesToRemove:
            if not f.startswith('.'):
                os.remove(dir + '/' + f)

    def generate(self, client):
        print "[XOS-TOSCA] Generating TOSCA"
        self._clean()
        xproto = client.utility.GetXproto(Empty())

        try:
            args = Args()
            args.output = TOSCA_DEFS_DIR
            args.inputs = str(xproto.xproto)
            args.target = os.path.join(current_dir, 'xtarget/tosca.xtarget')
            args.write_to_file = 'model'
            args.dest_extension = 'yaml'
            XOSGenerator.generate(args)
            print "[XOS-TOSCA] Recipes generated in %s" % args.output
        except Exception as e:
            print "[XOS-TOSCA] Failed to generate TOSCA"
            print e

