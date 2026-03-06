#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 1 ]]; then
  echo "Usage: $0 /path/to/file" >&2
  exit 1
fi

FILE="$1"
: "${LMFILES_API_KEY:?Set LMFILES_API_KEY first}"

curl -sS -X POST https://lmfiles.com/api/v1/files/upload \
  -H "X-API-Key: $LMFILES_API_KEY" \
  -F "file=@${FILE}"
