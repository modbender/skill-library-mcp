#!/bin/bash
# Exit a yield position — POST /v1/actions/exit
# Returns ActionDto with unsigned transactions to sign and broadcast.
# Arguments come from the yield's mechanics.arguments.exit schema.
# Usage: ./exit-position.sh <yield_id> <address> <arguments_json>

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
CONFIG_DIR=""
for dir in "${SCRIPT_DIR}/.." "${HOME}/.openclaw/skills/yield-agent" "${HOME}/.clawhub/skills/yield-agent" "${HOME}/.clawdbot/skills/yield-agent"; do
  [ -f "${dir}/skill.json" ] && CONFIG_DIR="$dir" && break
done
[ -z "$CONFIG_DIR" ] && echo "Error: skill.json not found" && exit 1

API_KEY="${YIELDS_API_KEY:-$(jq -r '.api.apiKey' "${CONFIG_DIR}/skill.json")}"
API_URL="${YIELDS_API_URL:-$(jq -r '.api.baseUrl' "${CONFIG_DIR}/skill.json")}"

YIELD_ID=$1; ADDRESS=$2; ARGS_JSON=$3

if [ -z "$YIELD_ID" ] || [ -z "$ADDRESS" ] || [ -z "$ARGS_JSON" ]; then
  echo "Usage: ./exit-position.sh <yield_id> <address> <arguments_json>"
  echo "Example: ./exit-position.sh base-usdc-aave-v3-lending 0x742d... '{\"amount\":\"50\"}'"
  exit 1
fi

sanitize() { [[ "$1" =~ [^a-zA-Z0-9._\-] ]] && { echo "Error: Invalid characters: $1" >&2; exit 1; } || true; }
sanitize "$YIELD_ID"
echo "$ARGS_JSON" | jq '.' > /dev/null 2>&1 || { echo "Error: arguments_json must be valid JSON" >&2; exit 1; }

PAYLOAD=$(jq -n --arg yieldId "$YIELD_ID" --arg address "$ADDRESS" --argjson arguments "$ARGS_JSON" \
  '{yieldId: $yieldId, address: $address, arguments: $arguments}')

RESPONSE=$(curl -s -X POST "${API_URL}/v1/actions/exit" \
  -H "x-api-key: ${API_KEY}" -H "Content-Type: application/json" -d "$PAYLOAD")

if echo "$RESPONSE" | jq -e '.error // .message' > /dev/null 2>&1; then
  echo "$RESPONSE" | jq -r '"Error: \(.message // .error) (code: \(.statusCode // "N/A"))"'
  exit 1
fi

echo "$RESPONSE" | jq '.'
echo ""
echo "NEXT: For each transaction in stepIndex order — sign EXACTLY as returned, broadcast, then submit the hash. Do NOT skip submit-hash — balances will not appear without it."
echo "Do NOT modify the unsigned transaction — WILL RESULT IN PERMANENT LOSS OF FUNDS. Request a new action instead if anything needs changing."
echo ""
echo "$RESPONSE" | jq -r '.transactions[] | "  Step \(.stepIndex // 0): sign → broadcast → PUT /v1/transactions/\(.id)/submit-hash {\"hash\":\"0xBROADCAST_TX_HASH\"} → poll GET /v1/transactions/\(.id) until CONFIRMED"'
