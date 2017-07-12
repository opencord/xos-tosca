help:
	@echo "tests: Run unit tests (if you're running local, you'll need to have virtual-env activated)"
	@echo "tosca: Generate tosca definition from core.xproto"
	@echo "test-call: Send a sample tosca recipe"

tests: tosca
	nosetests -s -v --with-id --with-coverage --cover-html --cover-erase --cover-xml --cover-package="grpc_client, tosca"

build:
	@echo 'TBD'

clean:
	@echo 'TBD'

test-call:
	curl -H "xos-username: xosadmin@opencord.org" -H "xos-password: rk1UYDHZXbu6KVCMkhmV" -X POST --data-binary @test/tosca/test.yaml 127.0.0.1:9200/run

tosca:
	xosgenx --target=src/tosca/xtarget/tosca.xtarget --output=src/tosca/custom_types --write-to-file=model --dest-extension=yaml ../xos/xos/core/models/core.xproto