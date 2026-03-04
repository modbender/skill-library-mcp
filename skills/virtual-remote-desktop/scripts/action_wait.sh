#!/usr/bin/env bash
set -euo pipefail

SECS="${1:-2}"
if [[ ! "${SECS}" =~ ^[0-9]+$ ]]; then
  echo "Usage: $0 <seconds>" >&2
  exit 1
fi
sleep "${SECS}"
exec "$(dirname "$0")/action_screenshot.sh"
