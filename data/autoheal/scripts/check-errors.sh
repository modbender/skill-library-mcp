#!/usr/bin/env bash
# Check AutoHeal error status with polling
# Usage: ./check-errors.sh <error_id> [--poll]

set -euo pipefail

if [ -z "${AUTOHEAL_API_KEY:-}" ]; then
  echo "Error: AUTOHEAL_API_KEY environment variable is required"
  exit 1
fi

if [ -z "${1:-}" ]; then
  echo "Usage: $0 <error_id> [--poll]"
  exit 1
fi

ERROR_ID="$1"
POLL="${2:-}"
API_URL="https://autohealai.com/api/errors/${ERROR_ID}/status"

check_status() {
  curl -sf "$API_URL" -H "Authorization: Bearer $AUTOHEAL_API_KEY"
}

if [ "$POLL" = "--poll" ]; then
  echo "Polling error $ERROR_ID..."
  for i in $(seq 1 60); do
    RESPONSE=$(check_status) || { echo "Request failed"; exit 1; }
    STATUS=$(echo "$RESPONSE" | grep -o '"status":"[^"]*"' | cut -d'"' -f4)
    echo "  [$i] Status: $STATUS"
    if [ "$STATUS" = "analyzed" ] || [ "$STATUS" = "fix_applied" ] || [ "$STATUS" = "ignored" ]; then
      echo ""
      echo "$RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$RESPONSE"
      exit 0
    fi
    sleep 2
  done
  echo "Timeout: error not yet analyzed after 120s"
  exit 1
else
  RESPONSE=$(check_status) || { echo "Request failed"; exit 1; }
  echo "$RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$RESPONSE"
fi
