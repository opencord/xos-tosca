#!/bin/sh

# Copyright 2017-present Open Networking Foundation
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

# tosca-loader.sh
# loads TOSCA files found in /opt/tosca into XOS

echo "Starting TOSCA loader using httpie version: $(http --version)"

for recipe in /opt/tosca/*
do
  echo "Loading: $recipe"
  http --check-status --ignore-stdin \
       POST "http://xos-tosca:$XOS_TOSCA_SERVICE_PORT/run" \
       "xos-username:$XOS_USER" \
       "xos-password:$XOS_PASSWD" \
       "@$recipe" || exit 1
  echo ''
done
