import functools
from xosapi.xos_grpc_client import SecureClient, InsecureClient
from twisted.internet import reactor, defer
from tosca.resources import RESOURCES

LOCAL_CERT = '/Users/teone/Sites/opencord/orchestration/xos-tosca/local_certs.crt'

class GRPC_Client:
    def __init__(self):
        self.client = None

        self.grpc_secure_endpoint = 'xos-core.opencord.org:50051'
        self.grpc_insecure_endpoint = 'xos-core.opencord.org:50055'

    def setup_resources(self, client):
        print "[XOS-TOSCA] Loading resources"
        for k in client.xos_orm.all_model_names:
            RESOURCES[k] = getattr(client.xos_orm, k)

    def start(self, username=None, password=None):
        print "[XOS-TOSCA] Connecting to xos-core"

        deferred = defer.Deferred()

        if self.client:
            self.client.stop()
            self.client.session_change = True

        if username and password:
            self.client = SecureClient(endpoint=self.grpc_secure_endpoint, username=username, password=password, cacert=LOCAL_CERT)
        else:
            self.client = InsecureClient(endpoint=self.grpc_insecure_endpoint)

        self.client.set_reconnect_callback(functools.partial(self.setup_resources, self.client))
        self.client.start()

        # TODO can we call this once the client is setted up?
        reactor.callLater(12, deferred.callback, self.client)
        return deferred