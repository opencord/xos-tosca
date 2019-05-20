# Copyright 2019-present Open Networking Foundation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Configure shell
SHELL = bash -e -o pipefail

# Variables
VERSION                  ?= $(shell cat ./VERSION)
SERVICE_NAME             ?= $(notdir $(abspath .))
LOADER_NAME              ?= tosca-loader

## Docker related
DOCKER_REGISTRY          ?=
DOCKER_REPOSITORY        ?=
DOCKER_BUILD_ARGS        ?=
DOCKER_TAG               ?= ${VERSION}
DOCKER_IMAGENAME         := ${DOCKER_REGISTRY}${DOCKER_REPOSITORY}${SERVICE_NAME}:${DOCKER_TAG}
LOADER_IMAGENAME         := ${DOCKER_REGISTRY}${DOCKER_REPOSITORY}${LOADER_NAME}:${DOCKER_TAG}

## Docker labels. Only set ref and commit date if committed
DOCKER_LABEL_VCS_URL     ?= $(shell git remote get-url $(shell git remote))
DOCKER_LABEL_VCS_REF     ?= $(shell git diff-index --quiet HEAD -- && git rev-parse HEAD || echo "unknown")
DOCKER_LABEL_COMMIT_DATE ?= $(shell git diff-index --quiet HEAD -- && git show -s --format=%cd --date=iso-strict HEAD || echo "unknown" )
DOCKER_LABEL_BUILD_DATE  ?= $(shell date -u "+%Y-%m-%dT%H:%M:%SZ")

all: test

docker-build: generate-xproto
	docker build $(DOCKER_BUILD_ARGS) \
    -t ${DOCKER_IMAGENAME} \
    --build-arg org_label_schema_version="${VERSION}" \
    --build-arg org_label_schema_vcs_url="${DOCKER_LABEL_VCS_URL}" \
    --build-arg org_label_schema_vcs_ref="${DOCKER_LABEL_VCS_REF}" \
    --build-arg org_label_schema_build_date="${DOCKER_LABEL_BUILD_DATE}" \
    --build-arg org_opencord_vcs_commit_date="${DOCKER_LABEL_COMMIT_DATE}" \
    -f Dockerfile .
	docker build $(DOCKER_BUILD_ARGS) \
    -t ${LOADER_IMAGENAME} \
    --build-arg org_label_schema_version="${VERSION}" \
    --build-arg org_label_schema_vcs_url="${DOCKER_LABEL_VCS_URL}" \
    --build-arg org_label_schema_vcs_ref="${DOCKER_LABEL_VCS_REF}" \
    --build-arg org_label_schema_build_date="${DOCKER_LABEL_BUILD_DATE}" \
    --build-arg org_opencord_vcs_commit_date="${DOCKER_LABEL_COMMIT_DATE}" \
    -f loader/Dockerfile.tosca-loader loader

docker-push:
	docker push ${DOCKER_IMAGENAME}
	docker push ${LOADER_IMAGENAME}

# Test starting the image, loading TOSCA, deleting TOSCA, and cleaning up after
# Not sure if this has been functional recently
test-docker: docker-start test-create test-delete docker-clean

docker-start:
	docker run -p 9102:9102 --name xos-tosca -d ${DOCKER_IMAGENAME}

test-create:
	curl -H "xos-username: xosadmin@opencord.org" \
       -H "xos-password: rk1UYDHZXbu6KVCMkhmV" \
       -X POST \
       --data-binary @test/tosca/test.yaml \
       127.0.0.1:9102/run

test-delete:
	curl -H "xos-username: xosadmin@opencord.org" \
       -H "xos-password: rk1UYDHZXbu6KVCMkhmV" \
       -X POST \
       --data-binary @test/tosca/test.yaml \
       127.0.0.1:9102/delete

docker-clean:
	docker rm -f xos-tosca || true
	docker rmi -f ${DOCKER_IMAGENAME} || true

test: test-unit

test-unit: generate-xproto
	tox

venv-tosca:
	virtualenv $@;\
    source ./$@/bin/activate ; set -u ;\
    pip install -r requirements.txt

generate-xproto: venv-tosca
	source ./venv-tosca/bin/activate ; set -u ;\
	xosgenx \
    --target=src/tosca/xtarget/tosca.xtarget \
    --output=src/tosca/custom_types \
    --write-to-file=target \
    test/test.xproto ;\
	xosgenx \
    --target=src/tosca/xtarget/tosca_keys.xtarget \
    --output=src/grpc_client/ \
    --write-to-file=single \
    --dest-file=KEYS.py \
    test/test.xproto

clean:
	find . -name '*.pyc' | xargs rm -f
	rm -rf \
    .tox \
    .coverage \
    venv-tosca \
    coverage \
    coverage.xml \
    nose2-results.xml \
    src/grpc_client/KEYS.py \
    src/grpc_client/__pycache__ \
    src/tosca/__pycache__ \
    src/tosca/custom_types/* \
    test/__pycache__ \
    test/out/*
