#!/usr/bin/env bash
set -euo pipefail

if [[ "$#" -lt 1 ]]; then
  echo "Usage: $0 '<message>'"
  exit 2
fi

REMOTE_TARGET="${REMOTE_TARGET:-neill@<YOUR_REMOTE_HOST>}"
MESSAGE="$1"

# Placeholder: replace with actual REMOTE inbox command
# Keep NO_REPLY discipline for automated messages.
ssh "${REMOTE_TARGET}" "echo 'TODO: send inbox message: ${MESSAGE}'"
