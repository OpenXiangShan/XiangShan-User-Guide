#!/bin/bash

# Requires @lint-md/cli and markdownlint-cli2 on PATH.

AUTOFIX=${AUTOFIX:-true}
TARGET=${TARGET:-"./**/*.md"}
GENERAL_FLAGS=""

if [[ "${AUTOFIX}" == "true" ]]; then
    GENERAL_FLAGS+=" --fix"
fi

markdownlint-cli2 ${GENERAL_FLAGS} "${TARGET}"
lint-md ${GENERAL_FLAGS} "${TARGET}"
