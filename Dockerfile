# Copyright 2018-present Open Networking Foundation
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

# xosproject/xos-tosca

FROM xosproject/alpine-grpc-base:0.9.0

# Set environment variables
ENV CODE_DEST /opt/xos-tosca
WORKDIR ${CODE_DEST}

# Add XOS-TOSCA code
COPY . ${CODE_DEST}/

# Install python packages with pip
COPY requirements.txt /tmp/requirements.txt
RUN pip install -r /tmp/requirements.txt \
 && pip freeze > /var/xos/pip_freeze_xos-tosca_`date -u +%Y%m%dT%H%M%S`

# Label image
ARG org_label_schema_version=unknown
ARG org_label_schema_vcs_url=unknown
ARG org_label_schema_vcs_ref=unknown
ARG org_label_schema_build_date=unknown
ARG org_opencord_vcs_commit_date=unknown


LABEL org.label-schema.schema-version=1.0 \
      org.label-schema.name=xos-tosca \
      org.label-schema.version=$org_label_schema_version \
      org.label-schema.vcs-url=$org_label_schema_vcs_url \
      org.label-schema.vcs-ref=$org_label_schema_vcs_ref \
      org.label-schema.build-date=$org_label_schema_build_date \
      org.opencord.vcs-commit-date=$org_opencord_vcs_commit_date

EXPOSE 9102

ENTRYPOINT [ "/usr/bin/python", "src/main.py" ]

