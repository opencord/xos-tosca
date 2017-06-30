import functools
from xosapi.xos_grpc_client import SecureClient, InsecureClient
from twisted.internet import reactor, defer
from resources import RESOURCES
from xosconfig import Config

LOCAL_CERT = '/Users/teone/Sites/opencord/orchestration/xos-tosca/local_certs.crt'

class GRPC_Client:
    def __init__(self):
        self.client = None

        self.grpc_secure_endpoint = Config.get('grpc.secure_endpoint')
        self.grpc_insecure_endpoint = Config.get('grpc.insecure_endpoint')
        self.username = Config.get('grpc.admin_username')
        self.password = Config.get('grpc.admin_password')

    def setup_resources(self, client):
        print "[XOS-TOSCA] Loading resources"
        for k in client.xos_orm.all_model_names:
            RESOURCES[k] = getattr(client.xos_orm, k)

    def start(self):
        print "[XOS-TOSCA] Connecting to xos-core"

        deferred = defer.Deferred()

        if self.client:
            self.client.stop()
            self.client.session_change = True

        if self.username and self.password:
            # NOTE if we authenticate users given the parameters in the rest request, do we need this?
            self.client = SecureClient(endpoint=self.grpc_secure_endpoint, username=self.username, password=self.password, cacert=LOCAL_CERT)
        else:
            self.client = InsecureClient(endpoint=self.grpc_insecure_endpoint)

        self.client.set_reconnect_callback(functools.partial(self.setup_resources, self.client))
        self.client.start()

        # TODO can we call this once the client is setted up?
        reactor.callLater(12, deferred.callback, self.client)
        return deferred