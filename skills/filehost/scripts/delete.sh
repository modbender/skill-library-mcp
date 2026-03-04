#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 1 ]]; then
  echo "Usage: $0 <file_id>" >&2
  exit 1
fi

FILE_ID="$1"
: "${LMFILES_API_KEY:?Set LMFILES_API_KEY first}"

curl -sS -X DELETE "https://lmfiles.com/api/v1/files/${FILE_ID}" \
  -H "X-API-Key: $LMFILES_API_KEY"
