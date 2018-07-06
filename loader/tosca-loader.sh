#!/bin/sh

echo "Starting TOSCA loader with httpie:"
http --version

for recipe in /opt/tosca/*
do
  echo "Loading: $recipe"
  http --check-status --ignore-stdin \
       POST "http://xos-tosca:$XOS_TOSCA_SERVICE_PORT/run" \
       "xos-username:$XOS_USERNAME" \
       "xos-password:$XOS_PASSWORD" \
       "@$recipe" || exit 1
  echo ''
done
