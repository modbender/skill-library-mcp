#!/bin/bash
# Discover yield opportunities — GET /v1/yields
# Returns paginated list of YieldDto with rates, tokens, mechanics, and status.
# Usage: ./find-yields.sh <network> [token] [limit] [offset] [--summary]

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
CONFIG_DIR=""
for dir in "${SCRIPT_DIR}/.." "${HOME}/.openclaw/skills/yield-agent" "${HOME}/.clawhub/skills/yield-agent" "${HOME}/.clawdbot/skills/yield-agent"; do
  [ -f "${dir}/skill.json" ] && CONFIG_DIR="$dir" && break
done
[ -z "$CONFIG_DIR" ] && echo "Error: skill.json not found" && exit 1

API_KEY="${YIELDS_API_KEY:-$(jq -r '.api.apiKey' "${CONFIG_DIR}/skill.json")}"
API_URL="${YIELDS_API_URL:-$(jq -r '.api.baseUrl' "${CONFIG_DIR}/skill.json")}"

SUMMARY=false; ARGS=()
for arg in "$@"; do
  [ "$arg" = "--summary" ] && SUMMARY=true || ARGS+=("$arg")
done

NETWORK="${ARGS[0]:-${YIELD_NETWORK:-$(jq -r '.defaults.network // "base"' "${CONFIG_DIR}/skill.json")}}"
TOKEN=${ARGS[1]:-}; LIMIT=${ARGS[2]:-20}; OFFSET=${ARGS[3]:-0}

if [ -z "$NETWORK" ]; then
  echo "Usage: ./find-yields.sh <network> [token] [limit] [offset] [--summary]"
  echo "Example: ./find-yields.sh base USDC"
  exit 1
fi

sanitize() { [[ "$1" =~ [^a-zA-Z0-9._\-] ]] && { echo "Error: Invalid characters: $1" >&2; exit 1; } || true; }
sanitize "$NETWORK"
[ ! -z "$TOKEN" ] && sanitize "$TOKEN"
[[ "$LIMIT" =~ ^[0-9]+$ ]] || { echo "Error: limit must be a number" >&2; exit 1; }
[[ "$OFFSET" =~ ^[0-9]+$ ]] || { echo "Error: offset must be a number" >&2; exit 1; }

QUERY="network=${NETWORK}&limit=${LIMIT}&offset=${OFFSET}"
[ ! -z "$TOKEN" ] && QUERY="${QUERY}&token=${TOKEN}"

RESPONSE=$(curl -s -X GET "${API_URL}/v1/yields?${QUERY}" \
  -H "x-api-key: ${API_KEY}" -H "Content-Type: application/json")

if echo "$RESPONSE" | jq -e '.error // .message' > /dev/null 2>&1; then
  echo "$RESPONSE" | jq -r '"Error: \(.message // .error)"'
  exit 1
fi

if [ "$SUMMARY" = true ]; then
  TOTAL=$(echo "$RESPONSE" | jq -r '.total // 0')
  COUNT=$(echo "$RESPONSE" | jq '.items | length')
  echo "Yields on $NETWORK${TOKEN:+ for $TOKEN} (showing $COUNT of $TOTAL)"
  echo ""
  printf "%-55s | %-8s | %-8s | %-4s | %s\n" "ID" "Type" "Rate" "Dec" "Min Deposit"
  printf "%-55s-+-%-8s-+-%-8s-+-%-4s-+-%s\n" "-------------------------------------------------------" "--------" "--------" "----" "------------"
  echo "$RESPONSE" | jq -r '.items[] |
    [
      .id,
      (.mechanics.type // "?"),
      (if .rewardRate.total then (.rewardRate.total * 100 | tostring | split(".") | .[0] + "." + (.[1] // "00" | .[:2]) + "%") else "N/A" end),
      (.token.decimals // "?" | tostring),
      (.mechanics.entryLimits.minimum // "none")
    ] | @tsv' | while IFS=$'\t' read -r ID TYPE RATE DECIMALS MIN; do
    printf "%-55s | %-8s | %8s | %4s | %s\n" "$ID" "$TYPE" "$RATE" "$DECIMALS" "$MIN"
  done
else
  echo "$RESPONSE" | jq '.'
fi
