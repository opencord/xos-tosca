help:
	@echo "tests: Run unit tests (if you're running local, you'll need to have virtual-env activated)"

tests:
	nosetests -s -v --with-id

build:
	@echo 'TBD'

clean:
	@echo 'TBD'

test-call:
	curl -H "xos-username: xosadmin@opencord.org" -H "xos-password: rk1UYDHZXbu6KVCMkhmV" -X POST --data-binary @test/tosca/test.yaml 127.0.0.1:9200