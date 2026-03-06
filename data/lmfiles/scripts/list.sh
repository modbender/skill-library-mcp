#!/usr/bin/env bash
set -euo pipefail

: "${LMFILES_API_KEY:?Set LMFILES_API_KEY first}"

curl -sS https://lmfiles.com/api/v1/accounts/me/files \
  -H "X-API-Key: $LMFILES_API_KEY"
