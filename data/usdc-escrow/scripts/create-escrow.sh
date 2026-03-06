#!/bin/bash
# Create a new USDC escrow
set -e

API_URL="${ESCROW_API_URL:-https://api.payclawback.xyz}"

if [ $# -lt 4 ]; then
  echo "Usage: $0 <beneficiary_address> <amount_usdc> <description> <deadline_hours>"
  echo "Example: $0 0x742d35Cc6634C0532925a3b844Bc9e7595f2bD28 10 'Payment for service' 48"
  exit 1
fi

BENEFICIARY="$1"
AMOUNT="$2"
DESCRIPTION="$3"
DEADLINE_HOURS="$4"

curl -s -X POST "${API_URL}/api/escrows" \
  -H "Content-Type: application/json" \
  -d "{
    \"beneficiary\": \"${BENEFICIARY}\",
    \"amount\": ${AMOUNT},
    \"description\": \"${DESCRIPTION}\",
    \"deadline_hours\": ${DEADLINE_HOURS}
  }" | jq .
