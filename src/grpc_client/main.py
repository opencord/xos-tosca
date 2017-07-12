import functools
from xosapi.xos_grpc_client import SecureClient, InsecureClient
from twisted.internet import defer
from resources import RESOURCES
from xosconfig import Config
from twisted.internet import reactor

LOCAL_CERT = '/Users/teone/Sites/opencord/orchestration/xos-tosca/local_certs.crt'

class GRPC_Client:
    def __init__(self):
        self.client = None

        self.grpc_secure_endpoint = Config.get('grpc.secure_endpoint')
        self.grpc_insecure_endpoint = Config.get('grpc.insecure_endpoint')

    def setup_resources(self, client, key, deferred, recipe):
        print "[XOS-TOSCA] Loading resources"
        if key not in RESOURCES:
            RESOURCES[key] = {}
        for k in client.xos_orm.all_model_names:
            RESOURCES[key][k] = getattr(client.xos_orm, k)
        reactor.callLater(0, deferred.callback, recipe)

    def start(self):
        print "[XOS-TOSCA] Connecting to xos-core"

        deferred = defer.Deferred()

        if self.client:
            self.client.stop()
            self.client.session_change = True

        self.client = InsecureClient(endpoint=self.grpc_insecure_endpoint)

        self.client.set_reconnect_callback(functools.partial(deferred.callback, self.client))
        self.client.start()

        return deferred

    def create_secure_client(self, username, password, recipe):
        """
        This method will check if this combination of username/password already has stored orm classes in RESOURCES, otherwise create them
        """
        deferred = defer.Deferred()
        key = "%s~%s" % (username, password)
        if key in RESOURCES:
            reactor.callLater(0, deferred.callback, recipe)
        else:
            client = SecureClient(endpoint=self.grpc_secure_endpoint, username=username, password=password, cacert=LOCAL_CERT)
            client.set_reconnect_callback(functools.partial(self.setup_resources, client, key, deferred, recipe))
            client.start()
        return deferred
