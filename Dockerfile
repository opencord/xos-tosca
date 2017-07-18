# xosproject/xos-tosca
FROM xosproject/xos-client:candidate

# Set environment variables
ENV CODE_SOURCE .
ENV CODE_DEST /opt/xos-tosca
WORKDIR ${CODE_DEST}

# Add XOS-TOSCA code
COPY ${CODE_SOURCE}/ ${CODE_DEST}/

# Install dependencies
RUN pip install -r ${CODE_DEST}/pip_requirements.txt

EXPOSE 9102

# Label image
ARG org_label_schema_schema_version=1.0
ARG org_label_schema_name=gui-extension-sample
ARG org_label_schema_version=unknown
ARG org_label_schema_vcs_url=unknown
ARG org_label_schema_vcs_ref=unknown
ARG org_label_schema_build_date=unknown
ARG org_opencord_vcs_commit_date=unknown
ARG org_opencord_component_chameleon_version=unknown
ARG org_opencord_component_chameleon_vcs_url=unknown
ARG org_opencord_component_chameleon_vcs_ref=unknown
ARG org_opencord_component_xos_version=unknown
ARG org_opencord_component_xos_vcs_url=unknown
ARG org_opencord_component_xos_vcs_ref=unknown

LABEL org.label-schema.schema-version=$org_label_schema_schema_version \
      org.label-schema.name=$org_label_schema_name \
      org.label-schema.version=$org_label_schema_version \
      org.label-schema.vcs-url=$org_label_schema_vcs_url \
      org.label-schema.vcs-ref=$org_label_schema_vcs_ref \
      org.label-schema.build-date=$org_label_schema_build_date \
      org.opencord.vcs-commit-date=$org_opencord_vcs_commit_date \
      org.opencord.component.chameleon.version=$org_opencord_component_chameleon_version \
      org.opencord.component.chameleon.vcs-url=$org_opencord_component_chameleon_vcs_url \
      org.opencord.component.chameleon.vcs-ref=$org_opencord_component_chameleon_vcs_ref \
      org.opencord.component.xos.version=$org_opencord_component_xos_version \
      org.opencord.component.xos.vcs-url=$org_opencord_component_xos_vcs_url \
      org.opencord.component.xos.vcs-ref=$org_opencord_component_xos_vcs_ref

ENTRYPOINT [ "/usr/bin/python", "src/main.py" ]

