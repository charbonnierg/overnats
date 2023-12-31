#!/usr/bin/env bash

set -euo pipefail

datamodel-codegen \
    --input schemas \
    --output src/easynats/models \
    --output-model-type=dataclasses.dataclass \
    --disable-timestamp \
    --use-schema-description \
    --use-field-description \
    --use-double-quote \
    --custom-file-header "# @generated"
