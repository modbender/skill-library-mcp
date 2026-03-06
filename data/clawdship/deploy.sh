#!/bin/bash
set -euo pipefail

# Clawdship Deploy Script
# Usage: ./deploy.sh <slug> <path> [api-key]
# Env:   CLAWDSHIP_API_KEY — API key (alternative to arg $3)
#        CLAWDSHIP_API     — API base URL (default: https://api.clawdship.dev)

SLUG="${1:?Usage: ./deploy.sh <slug> <path> [api-key]}"
PATH_TO_FILES="${2:?Usage: ./deploy.sh <slug> <path> [api-key]}"
API_KEY="${3:-${CLAWDSHIP_API_KEY:-}}"
API_BASE="${CLAWDSHIP_API:-https://api.clawdship.dev}"

if [ ! -d "$PATH_TO_FILES" ]; then
  echo "❌ Directory not found: $PATH_TO_FILES" >&2
  exit 1
fi

# Create tar.gz
ARCHIVE=$(mktemp /tmp/clawdship-XXXXXX.tar.gz)
trap 'rm -f "$ARCHIVE"' EXIT

echo "📦 Packaging $PATH_TO_FILES..."
tar czf "$ARCHIVE" -C "$PATH_TO_FILES" .

# Build curl command
CURL_ARGS=(-s -w "\n%{http_code}" -X POST "${API_BASE}/v1/sites")
CURL_ARGS+=(-F "name=${SLUG}" -F "type=static" -F "slug=${SLUG}" -F "archive=@${ARCHIVE}")

if [ -n "$API_KEY" ]; then
  CURL_ARGS+=(-H "Authorization: Bearer $API_KEY")
fi

echo "🚢 Deploying $SLUG..."
RESPONSE=$(curl "${CURL_ARGS[@]}")
HTTP_CODE=$(echo "$RESPONSE" | tail -1)
BODY=$(echo "$RESPONSE" | sed '$d')

if [ "$HTTP_CODE" -ge 400 ]; then
  echo "$BODY"
  echo "❌ Deploy failed (HTTP $HTTP_CODE)" >&2
  exit 1
fi

# Parse JSON fields with grep (no python3 dependency)
json_val() { echo "$BODY" | grep -o "\"$1\"[[:space:]]*:[[:space:]]*\"[^\"]*\"" | head -1 | sed 's/.*:.*"\(.*\)"/\1/'; }

URL=$(json_val url)
API_KEY_OUT=$(json_val apiKey)
BILLING=$(json_val billingUrl)

echo "$BODY"
echo ""
[ -n "$URL" ] && echo "✅ Live at: $URL"
if [ -n "$API_KEY_OUT" ]; then
  echo ""
  echo "🔑 API Key (SAVE THIS — cannot be recovered):"
  echo "   $API_KEY_OUT"
fi
[ -n "$BILLING" ] && echo "💳 Billing: $BILLING"
