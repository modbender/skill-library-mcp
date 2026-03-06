#!/usr/bin/env bash
set -euo pipefail

SERVER="${1:-}"
if [[ -z "$SERVER" ]]; then
  echo "Usage: $0 <server-name>" >&2
  exit 2
fi

docker mcp server disable "$SERVER"
