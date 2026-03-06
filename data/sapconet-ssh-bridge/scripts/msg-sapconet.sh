#!/usr/bin/env bash
set -euo pipefail

if [[ "$#" -lt 1 ]]; then
  echo "Usage: $0 '<message>'"
  exit 2
fi

SAPCONET_TARGET="${SAPCONET_TARGET:-neill@100.110.24.44}"
MESSAGE="$1"

# Placeholder: replace with actual SAPCONET inbox command
# Keep NO_REPLY discipline for automated messages.
ssh "${SAPCONET_TARGET}" "echo 'TODO: send inbox message: ${MESSAGE}'"
