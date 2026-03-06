#!/bin/bash
# Resolve a disputed escrow
set -e

API_URL="${ESCROW_API_URL:-https://api.payclawback.xyz}"

if [ $# -lt 2 ]; then
  echo "Usage: $0 <escrow_id> <true|false>"
  echo "  true  = release funds to beneficiary"
  echo "  false = refund to depositor"
  exit 1
fi

ESCROW_ID="$1"
RELEASE_TO_BENEFICIARY="$2"

curl -s -X POST "${API_URL}/api/escrows/${ESCROW_ID}/resolve" \
  -H "Content-Type: application/json" \
  -d "{\"release_to_beneficiary\": ${RELEASE_TO_BENEFICIARY}}" | jq .
