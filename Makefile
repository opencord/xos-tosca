help:
	@echo "tests: Run unit tests (if you're running local, you'll need to have virtual-env activated)"
	@echo "tosca: Generate tosca definition from core.xproto"
	@echo "test-call: Send a sample tosca recipe"
	@echo "build: Build the docker image for xos-tosca"
	@echo "start: Run an xos-tosca container"
	@echo "clean: Remove the xos-tosca container (if any), and the image (if any)"

tests: tosca
	nosetests -s -v --with-id --with-coverage --cover-html --cover-erase --cover-xml --cover-package="grpc_client, tosca"

build:
	docker build -t xosproject/xos-tosca --no-cache=true .

start: build
	docker run -p 9200:9200 --name xos-tosca -d xosproject/xos-tosca

clean:
	docker rm -f xos-tosca || true
	docker rmi -f xosproject/xos-tosca || true

test-call:
	curl -H "xos-username: xosadmin@opencord.org" -H "xos-password: rk1UYDHZXbu6KVCMkhmV" -X POST --data-binary @test/tosca/test.yaml 127.0.0.1:9200/run

tosca:
	xosgenx --target=src/tosca/xtarget/tosca.xtarget --output=src/tosca/custom_types --write-to-file=model --dest-extension=yaml ../xos/xos/core/models/core.xproto