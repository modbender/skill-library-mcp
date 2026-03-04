#!/bin/bash
# ============================================
# Confucius Debug — Quick Search
# ============================================
#
# Security Manifest:
#   ENV accessed: CONFUCIUS_LOBSTER_ID (optional, for attribution)
#   External endpoints: https://api.washinmura.jp/api/v2/debug-ai/search
#   Files: none (read-only API call)
#   Side effects: none
#
# Usage:
#   bash search.sh "your error message here"
#   bash search.sh "ETELEGRAM 409 Conflict"

set -euo pipefail

QUERY="${1:?Usage: search.sh \"your error description\"}"
API_URL="https://api.washinmura.jp/api/v2/debug-ai/search"

echo "🔍 Searching YanHui KB for: ${QUERY:0:80}..."
echo ""

RESPONSE=$(curl -s --max-time 15 -w "%{http_code}" -o >(cat) -X POST "$API_URL" \
  -H "Content-Type: application/json" \
  -d "{\"query\": $(echo "$QUERY" | jq -Rs .), \"limit\": 5, \"channel\": \"clawhub\"}" 2>/dev/null) || {
  echo "❌ Cannot reach Confucius API (api.washinmura.jp). Check your internet or try again later."
  exit 1
}

STATUS="${RESPONSE: -3}"
BODY="${RESPONSE:0:${#RESPONSE}-3}"

if [ "$STATUS" != "200" ]; then
  echo "❌ API returned HTTP $STATUS. Try again later."
  echo "   Endpoint: $API_URL"
  exit 1
fi

# 檢查是否有結果
HITS=$(echo "$BODY" | jq -r '.results // [] | length' 2>/dev/null || echo "0")

if [ "$HITS" = "0" ]; then
  echo "❌ No matches found in YanHui KB."
  echo ""
  echo "💡 Try: confucius_analyze to get free AI-powered analysis"
else
  echo "✅ Found $HITS matches:"
  echo ""
  echo "$BODY" | jq -r '.results[] | "───────────────────\n📌 \(.error_description // "N/A")\n🔧 Fix: \(.fix_description // "N/A")\n📂 Category: \(.error_category // "N/A")\n"' 2>/dev/null || echo "$BODY"
fi
