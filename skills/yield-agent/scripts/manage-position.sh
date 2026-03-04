#!/bin/bash
# Manage a yield position (claim, restake, redelegate) — POST /v1/actions/manage
# Returns ActionDto with unsigned transactions to sign and broadcast.
# Action and passthrough come from pendingActions[] in the balances response.
# Usage: ./manage-position.sh <yield_id> <address> <action> <passthrough> [arguments_json]

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
CONFIG_DIR=""
for dir in "${SCRIPT_DIR}/.." "${HOME}/.openclaw/skills/yield-agent" "${HOME}/.clawhub/skills/yield-agent" "${HOME}/.clawdbot/skills/yield-agent"; do
  [ -f "${dir}/skill.json" ] && CONFIG_DIR="$dir" && break
done
[ -z "$CONFIG_DIR" ] && echo "Error: skill.json not found" && exit 1

API_KEY="${YIELDS_API_KEY:-$(jq -r '.api.apiKey' "${CONFIG_DIR}/skill.json")}"
API_URL="${YIELDS_API_URL:-$(jq -r '.api.baseUrl' "${CONFIG_DIR}/skill.json")}"

YIELD_ID=$1; ADDRESS=$2; ACTION=$3; PASSTHROUGH=$4; ARGS_JSON=${5:-"{}"}

if [ -z "$YIELD_ID" ] || [ -z "$ADDRESS" ] || [ -z "$ACTION" ] || [ -z "$PASSTHROUGH" ]; then
  echo "Usage: ./manage-position.sh <yield_id> <address> <action> <passthrough> [arguments_json]"
  echo "Example: ./manage-position.sh ethereum-eth-lido-staking 0x742d... CLAIM_REWARDS \"eyJhbGci...\""
  echo ""
  echo "Get action + passthrough from: ./check-portfolio.sh <yield_id> <address> → pendingActions[]"
  exit 1
fi

sanitize() { [[ "$1" =~ [^a-zA-Z0-9._\-] ]] && { echo "Error: Invalid characters: $1" >&2; exit 1; } || true; }
sanitize "$YIELD_ID"
sanitize "$ACTION"

PAYLOAD=$(jq -n --arg yieldId "$YIELD_ID" --arg address "$ADDRESS" --arg action "$ACTION" \
  --arg passthrough "$PASSTHROUGH" --argjson arguments "$ARGS_JSON" \
  '{yieldId: $yieldId, address: $address, action: $action, passthrough: $passthrough, arguments: $arguments}')

RESPONSE=$(curl -s -X POST "${API_URL}/v1/actions/manage" \
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
