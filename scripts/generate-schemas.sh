#!/usr/bin/env bash

set -euo pipefail

ALL_SCHEMAS=$(nats schema ls --json | jq -r '.[]')

for schema in $ALL_SCHEMAS; do
  if [ $schema == "io.nats.unknown_message" ]; then
    continue
  fi
  echo $schema
  arrIN=(${schema//./ })
  if [ "${#arrIN[@]}" -eq "6" ]; then
    package=${arrIN[2]}
    subpackage=${arrIN[3]}
    module=${arrIN[5]}
    mkdir -p schemas/$package/$subpackage
    nats schema info $schema > schemas/$package/$subpackage/$module.json
  else
    package=${arrIN[2]}
    subpackage=${arrIN[3]}
    module=${arrIN[4]}
    mkdir -p schemas/$package
    nats schema info $schema > schemas/$package/$module.json
  fi
done
