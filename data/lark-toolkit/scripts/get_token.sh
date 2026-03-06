#!/bin/bash
# Get Lark tenant_access_token
#
# Usage:
#   export LARK_APP_ID=cli_xxx LARK_APP_SECRET=xxx
#   source scripts/get_token.sh
#
# Credential sources (checked in order):
#   1. Command-line arguments: ./get_token.sh <app_id> <app_secret>
#   2. Environment variables: LARK_APP_ID, LARK_APP_SECRET
#   3. OpenClaw config file: ~/.openclaw/openclaw.json
#      (reads channels.lark.accounts.default.appId/appSecret)
#
# Output: prints the token to stdout and exports LARK_TOKEN env var
# No credentials are stored, logged, or transmitted beyond the Lark auth API.

set -euo pipefail

APP_ID="${1:-${LARK_APP_ID:-}}"
APP_SECRET="${2:-${LARK_APP_SECRET:-}}"

if [ -z "$APP_ID" ] || [ -z "$APP_SECRET" ]; then
  # Fallback: read from OpenClaw config (standard location for claw-lark plugin)
  CONFIG="${OPENCLAW_CONFIG:-$HOME/.openclaw/openclaw.json}"
  if [ -f "$CONFIG" ]; then
    echo "Reading credentials from $CONFIG (channels.lark.accounts.default)" >&2
    APP_ID=$(python3 -c "
import json, sys
try:
    c = json.load(open('$CONFIG'))
    print(c['channels']['lark']['accounts']['default']['appId'])
except (KeyError, FileNotFoundError):
    sys.exit(1)
" 2>/dev/null) || true
    APP_SECRET=$(python3 -c "
import json, sys
try:
    c = json.load(open('$CONFIG'))
    print(c['channels']['lark']['accounts']['default']['appSecret'])
except (KeyError, FileNotFoundError):
    sys.exit(1)
" 2>/dev/null) || true
  fi
fi

if [ -z "$APP_ID" ] || [ -z "$APP_SECRET" ]; then
  echo "Error: No credentials found." >&2
  echo "Set LARK_APP_ID + LARK_APP_SECRET env vars, or configure in ~/.openclaw/openclaw.json" >&2
  exit 1
fi

# Request tenant_access_token from Lark Open API
RESPONSE=$(curl -s https://open.larksuite.com/open-apis/auth/v3/tenant_access_token/internal \
  -H "Content-Type: application/json" \
  -d "{\"app_id\":\"$APP_ID\",\"app_secret\":\"$APP_SECRET\"}")

TOKEN=$(echo "$RESPONSE" | python3 -c "import sys,json; print(json.load(sys.stdin).get('tenant_access_token',''))" 2>/dev/null)

if [ -z "$TOKEN" ]; then
  echo "Error: Failed to get token. Response: $RESPONSE" >&2
  exit 1
fi

export LARK_TOKEN="$TOKEN"
echo "$TOKEN"
