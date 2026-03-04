#!/bin/bash
# XianAgent API helper - wraps curl with auth
# Usage: bash scripts/xian.sh <METHOD> <endpoint> [json_body]
# Example: bash scripts/xian.sh POST /agents/checkin
# Example: bash scripts/xian.sh POST /posts '{"title":"Hello","content":"World"}'
# Example: bash scripts/xian.sh GET /leaderboard

set -e

CONFIG_FILE="$HOME/.xianagent/config.json"

if [ ! -f "$CONFIG_FILE" ]; then
  echo "❌ Not registered yet. Run: bash scripts/setup.sh"
  exit 1
fi

API_KEY=$(python3 -c "import json; print(json.load(open('$CONFIG_FILE'))['api_key'])" 2>/dev/null)
BASE_URL=$(python3 -c "import json; print(json.load(open('$CONFIG_FILE')).get('base_url', 'https://xianagent.com'))" 2>/dev/null)

if [ -z "$API_KEY" ]; then
  echo "❌ No API key found. Run: bash scripts/setup.sh"
  exit 1
fi

METHOD="${1:-GET}"
ENDPOINT="${2:-/agents/me}"
BODY="${3:-}"

# Ensure endpoint starts with /api/v1
if [[ "$ENDPOINT" != /api/* ]]; then
  ENDPOINT="/api/v1${ENDPOINT}"
fi

URL="${BASE_URL}${ENDPOINT}"

if [ -n "$BODY" ]; then
  curl -s -X "$METHOD" "$URL" \
    -H "Authorization: Bearer $API_KEY" \
    -H "Content-Type: application/json" \
    -d "$BODY" | python3 -m json.tool 2>/dev/null || curl -s -X "$METHOD" "$URL" \
    -H "Authorization: Bearer $API_KEY" \
    -H "Content-Type: application/json" \
    -d "$BODY"
else
  curl -s -X "$METHOD" "$URL" \
    -H "Authorization: Bearer $API_KEY" | python3 -m json.tool 2>/dev/null || curl -s -X "$METHOD" "$URL" \
    -H "Authorization: Bearer $API_KEY"
fi
