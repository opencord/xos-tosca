help:
	@echo "tests: Run unit tests (need the xos dev virtual-env activated)"
	@echo "tosca: Generate tosca definition from core.xproto"
	@echo "build: Build the docker image for xos-tosca"
	@echo "start: Run an xos-tosca container"
	@echo "clean: Remove the xos-tosca container (if any), and the image (if any)"
	@echo "test-create: Send a sample tosca recipe"
	@echo "test-delete: Delete a sample tosca recipe"

tests: tosca
	nose2 --verbose --coverage-report xml --coverage-report term --junit-xml

build:
	docker build -t xosproject/xos-tosca .
	docker tag xosproject/xos-tosca:latest xosproject/xos-tosca:candidate

start: build
	docker run -p 9200:9200 --name xos-tosca -d xosproject/xos-tosca

clean:
	docker rm -f xos-tosca || true
	docker rmi -f xosproject/xos-tosca || true

test-create:
	curl -H "xos-username: xosadmin@opencord.org" -H "xos-password: rk1UYDHZXbu6KVCMkhmV" -X POST --data-binary @test/tosca/test.yaml 127.0.0.1:9102/run

test-delete:
	curl -H "xos-username: xosadmin@opencord.org" -H "xos-password: rk1UYDHZXbu6KVCMkhmV" -X POST --data-binary @test/tosca/test.yaml 127.0.0.1:9102/delete

tosca:
	xosgenx --target=src/tosca/xtarget/tosca.xtarget --output=src/tosca/custom_types --write-to-file=target ../xos/xos/core/models/core.xproto
	xosgenx --target=src/tosca/xtarget/tosca_keys.xtarget --output=src/grpc_client/ --write-to-file=single --dest-file=KEYS.py ../xos/xos/core/models/core.xproto
