#!/bin/bash
# Usage: check-status.sh <request-id>
# Polls a HeySummon help request and prints its current status.

set -e

REQUEST_ID="${1:-}"

if [ -z "$REQUEST_ID" ]; then
  echo "Usage: check-status.sh <request-id>"
  echo ""
  echo "  request-id   The ID returned from request-help.sh"
  exit 1
fi

BASE_URL="${HEYSUMMON_BASE_URL:-https://cloud.heysummon.ai}"

RESPONSE=$(curl -s "${BASE_URL}/api/v1/help/${REQUEST_ID}")

echo "$RESPONSE" | jq .
