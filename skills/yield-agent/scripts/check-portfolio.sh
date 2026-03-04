#!/bin/bash
# Check balances for a yield position — POST /v1/yields/{yieldId}/balances
# Returns YieldBalancesDto with balances, pending actions, and validator info.
# Usage: ./check-portfolio.sh <yield_id> <address>

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
CONFIG_DIR=""
for dir in "${SCRIPT_DIR}/.." "${HOME}/.openclaw/skills/yield-agent" "${HOME}/.clawhub/skills/yield-agent" "${HOME}/.clawdbot/skills/yield-agent"; do
  [ -f "${dir}/skill.json" ] && CONFIG_DIR="$dir" && break
done
[ -z "$CONFIG_DIR" ] && echo "Error: skill.json not found" && exit 1

API_KEY="${YIELDS_API_KEY:-$(jq -r '.api.apiKey' "${CONFIG_DIR}/skill.json")}"
API_URL="${YIELDS_API_URL:-$(jq -r '.api.baseUrl' "${CONFIG_DIR}/skill.json")}"

YIELD_ID=$1; ADDRESS=$2

if [ -z "$YIELD_ID" ] || [ -z "$ADDRESS" ]; then
  echo "Usage: ./check-portfolio.sh <yield_id> <address>"
  echo "Example: ./check-portfolio.sh base-usdc-aave-v3-lending 0x742d..."
  exit 1
fi

sanitize() { [[ "$1" =~ [^a-zA-Z0-9._\-] ]] && { echo "Error: Invalid characters: $1" >&2; exit 1; } || true; }
sanitize "$YIELD_ID"

PAYLOAD=$(jq -n --arg addr "$ADDRESS" '{address: $addr}')

RESPONSE=$(curl -s -X POST "${API_URL}/v1/yields/${YIELD_ID}/balances" \
  -H "x-api-key: ${API_KEY}" -H "Content-Type: application/json" -d "$PAYLOAD")

if echo "$RESPONSE" | jq -e '.error // .message' > /dev/null 2>&1; then
  echo "$RESPONSE" | jq -r '"Error: \(.message // .error)"'
  exit 1
fi

echo "$RESPONSE" | jq '.'
