#!/bin/bash
# HeySummon Provider — Respond to a help request by request ID
# Usage: respond.sh <request-id> "<response text>"
#
# Similar to reply-handler.sh but uses request ID instead of refCode.

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SKILL_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
[ -f "$SKILL_DIR/.env" ] && set -a && source "$SKILL_DIR/.env" && set +a

REQUEST_ID="${1:-}"
RESPONSE_TEXT="${2:-}"

if [ -z "$REQUEST_ID" ] || [ -z "$RESPONSE_TEXT" ]; then
  echo "Usage: respond.sh <request-id> \"<response text>\"" >&2
  exit 1
fi

BASE_URL="${HEYSUMMON_BASE_URL:?ERROR: Set HEYSUMMON_BASE_URL in .env}"
API_KEY="${HEYSUMMON_API_KEY:?ERROR: Set HEYSUMMON_API_KEY in .env}"

# Validate provider key prefix
if [[ ! "$API_KEY" =~ ^hs_prov_ ]]; then
  echo "❌ HEYSUMMON_API_KEY must be a provider key (hs_prov_...)" >&2
  exit 1
fi

RESULT=$(curl -s -X POST "${BASE_URL}/api/v1/message/${REQUEST_ID}" \
  -H "Content-Type: application/json" \
  -H "x-api-key: ${API_KEY}" \
  -d "$(node -e "console.log(JSON.stringify({plaintext:process.argv[1],from:'provider'}))" "$RESPONSE_TEXT" 2>/dev/null)")

ERROR=$(echo "$RESULT" | node -e "let d='';process.stdin.on('data',c=>d+=c);process.stdin.on('end',()=>{try{const j=JSON.parse(d);if(j.error)console.log(j.error)}catch(e){}})" 2>/dev/null)

if [ -n "$ERROR" ]; then
  echo "❌ Failed: $ERROR" >&2
  exit 1
fi

echo "✅ Response sent for request ${REQUEST_ID}"
