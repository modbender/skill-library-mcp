#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 1 ]]; then
  echo "Usage: $0 <username> [bootstrap_token]" >&2
  exit 1
fi

USERNAME="$1"
BOOTSTRAP_TOKEN="${2:-${LMFILES_BOOTSTRAP_TOKEN:-}}"

if [[ -z "$BOOTSTRAP_TOKEN" ]]; then
  echo "Error: provide bootstrap token as arg2 or set LMFILES_BOOTSTRAP_TOKEN" >&2
  exit 1
fi

curl -sS -X POST https://lmfiles.com/api/v1/accounts/register \
  -H "Content-Type: application/json" \
  -d "{\"username\":\"${USERNAME}\",\"bootstrap_token\":\"${BOOTSTRAP_TOKEN}\"}"
