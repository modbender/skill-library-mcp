#!/bin/bash
# Get details of a specific escrow
set -e

API_URL="${ESCROW_API_URL:-https://api.payclawback.xyz}"

if [ $# -lt 1 ]; then
  echo "Usage: $0 <escrow_id>"
  exit 1
fi

ESCROW_ID="$1"

curl -s "${API_URL}/api/escrows/${ESCROW_ID}" | jq .
