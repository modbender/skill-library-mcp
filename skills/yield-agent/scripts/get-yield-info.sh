#!/bin/bash
# Fetch yield metadata and argument schema — GET /v1/yields/{yieldId}
# Shows name, provider, type, rate, token, entry/exit arguments, and limits.
# Usage: ./get-yield-info.sh <yield_id>

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
CONFIG_DIR=""
for dir in "${SCRIPT_DIR}/.." "${HOME}/.openclaw/skills/yield-agent" "${HOME}/.clawhub/skills/yield-agent" "${HOME}/.clawdbot/skills/yield-agent"; do
  [ -f "${dir}/skill.json" ] && CONFIG_DIR="$dir" && break
done
[ -z "$CONFIG_DIR" ] && echo "Error: skill.json not found" && exit 1

API_KEY="${YIELDS_API_KEY:-$(jq -r '.api.apiKey' "${CONFIG_DIR}/skill.json")}"
API_URL="${YIELDS_API_URL:-$(jq -r '.api.baseUrl' "${CONFIG_DIR}/skill.json")}"

YIELD_ID=$1

if [ -z "$YIELD_ID" ]; then
  echo "Usage: ./get-yield-info.sh <yield_id>"
  echo "Example: ./get-yield-info.sh base-usdc-aave-v3-lending"
  exit 1
fi

sanitize() { [[ "$1" =~ [^a-zA-Z0-9._\-] ]] && { echo "Error: Invalid characters: $1" >&2; exit 1; } || true; }
sanitize "$YIELD_ID"

RESPONSE=$(curl -s -w "\n%{http_code}" -X GET \
  "${API_URL}/v1/yields/${YIELD_ID}" \
  -H "x-api-key: ${API_KEY}" -H "Content-Type: application/json")

HTTP_CODE=$(echo "$RESPONSE" | tail -1)
BODY=$(echo "$RESPONSE" | sed '$d')

if [ "$HTTP_CODE" != "200" ]; then
  echo "$BODY" | jq -r '"Error (\(.statusCode // "'"$HTTP_CODE"'")): \(.message // .error // "Unknown")"' 2>/dev/null
  exit 1
fi

echo "=== $YIELD_ID ==="
echo ""
echo "$BODY" | jq -r '"Name:     \(.metadata.name // "Unknown")
Provider: \(.providerId // "Unknown")
Type:     \(.mechanics.type // "Unknown")
Network:  \(.network // "Unknown")
Status:   enter=\(.status.enter // false), exit=\(.status.exit // false)
Rate (\(.rewardRate.rateType // "APR")): \(.rewardRate.total // "N/A")"'

echo ""
echo "--- Token ---"
echo "$BODY" | jq -r '"Symbol:   \(.token.symbol // "Unknown")  Decimals: \(.token.decimals // "N/A")  Address: \(.token.address // "N/A")"'

REQUIRES_VALIDATOR=$(echo "$BODY" | jq -r '.mechanics.requiresValidatorSelection // false')
if [ "$REQUIRES_VALIDATOR" = "true" ]; then
  echo ""
  echo "Validators required: ./list-validators.sh $YIELD_ID"
fi

ENTER_ARGS=$(echo "$BODY" | jq '.mechanics.arguments.enter // empty' 2>/dev/null)
if [ ! -z "$ENTER_ARGS" ] && [ "$ENTER_ARGS" != "null" ]; then
  echo ""
  echo "--- Enter Arguments ---"
  echo "$ENTER_ARGS" | jq '.'
fi

EXIT_ARGS=$(echo "$BODY" | jq '.mechanics.arguments.exit // empty' 2>/dev/null)
if [ ! -z "$EXIT_ARGS" ] && [ "$EXIT_ARGS" != "null" ]; then
  echo ""
  echo "--- Exit Arguments ---"
  echo "$EXIT_ARGS" | jq '.'
fi

LIMITS=$(echo "$BODY" | jq '.mechanics.entryLimits // empty' 2>/dev/null)
if [ ! -z "$LIMITS" ] && [ "$LIMITS" != "null" ]; then
  echo ""
  echo "--- Entry Limits ---"
  echo "$LIMITS" | jq '.'
fi
