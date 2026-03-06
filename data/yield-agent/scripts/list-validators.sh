#!/bin/bash
# List validators for staking yields — GET /v1/yields/{yieldId}/validators
# Returns ValidatorDto with name, address, rate, commission, and status.
# Usage: ./list-validators.sh <yield_id> [limit]

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
CONFIG_DIR=""
for dir in "${SCRIPT_DIR}/.." "${HOME}/.openclaw/skills/yield-agent" "${HOME}/.clawhub/skills/yield-agent" "${HOME}/.clawdbot/skills/yield-agent"; do
  [ -f "${dir}/skill.json" ] && CONFIG_DIR="$dir" && break
done
[ -z "$CONFIG_DIR" ] && echo "Error: skill.json not found" && exit 1

API_KEY="${YIELDS_API_KEY:-$(jq -r '.api.apiKey' "${CONFIG_DIR}/skill.json")}"
API_URL="${YIELDS_API_URL:-$(jq -r '.api.baseUrl' "${CONFIG_DIR}/skill.json")}"

YIELD_ID=$1; LIMIT=${2:-20}

if [ -z "$YIELD_ID" ]; then
  echo "Usage: ./list-validators.sh <yield_id> [limit]"
  echo "Example: ./list-validators.sh cosmos-atom-cosmoshub-staking"
  exit 1
fi

sanitize() { [[ "$1" =~ [^a-zA-Z0-9._\-] ]] && { echo "Error: Invalid characters: $1" >&2; exit 1; } || true; }
sanitize "$YIELD_ID"
[[ "$LIMIT" =~ ^[0-9]+$ ]] || { echo "Error: limit must be a number" >&2; exit 1; }

RESPONSE=$(curl -s -w "\n%{http_code}" -X GET \
  "${API_URL}/v1/yields/${YIELD_ID}/validators?limit=${LIMIT}" \
  -H "x-api-key: ${API_KEY}" -H "Content-Type: application/json")

HTTP_CODE=$(echo "$RESPONSE" | tail -1)
BODY=$(echo "$RESPONSE" | sed '$d')

if [ "$HTTP_CODE" != "200" ]; then
  echo "$BODY" | jq -r '"Error: \(.message // .error // "Unknown")"' 2>/dev/null
  exit 1
fi

COUNT=$(echo "$BODY" | jq '.items | length')
if [ "$COUNT" = "0" ] || [ -z "$COUNT" ]; then
  echo "No validators found for $YIELD_ID"
  exit 0
fi

echo "Validators for $YIELD_ID ($COUNT found)"
echo ""
echo "$BODY" | jq -r '.items[] | "Name:       \(.name // "Unnamed")\nAddress:    \(.address)\nRate:       \(.rewardRate.total // "N/A")\nCommission: \(.commission // "N/A")\nStatus:     \(.status // "active")\n---"'
