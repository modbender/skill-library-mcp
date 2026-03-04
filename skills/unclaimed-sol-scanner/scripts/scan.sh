#!/bin/bash
# Unclaimed SOL Scanner — scan a Solana wallet for reclaimable SOL
# Usage: bash scan.sh <wallet_address>

set -euo pipefail

WALLET="${1:-}"
API_URL="https://unclaimedsol.com/api/check-claimable-sol"

if [ -z "$WALLET" ]; then
  echo '{"error": "No wallet address provided. Please provide a Solana public key."}'
  exit 1
fi

# Basic format check (base58, 32-44 chars)
if ! echo "$WALLET" | grep -qE '^[1-9A-HJ-NP-Za-km-z]{32,44}$'; then
  echo '{"error": "Invalid wallet address format. Expected a base58 Solana public key (32-44 characters)."}'
  exit 1
fi

RESPONSE=$(curl -s -f -X POST "$API_URL" \
  -H "Content-Type: application/json" \
  -d "{\"publicKey\": \"$WALLET\"}" \
  --max-time 15 2>/dev/null) || {
  echo '{"error": "Failed to reach Unclaimed SOL API. Try again or visit https://unclaimedsol.com directly."}'
  exit 1
}

# Check if response looks like valid JSON with expected fields
if echo "$RESPONSE" | grep -q '"totalClaimableSol"'; then
  echo "$RESPONSE"
else
  echo '{"error": "Unexpected response from API. Try again or visit https://unclaimedsol.com directly."}'
  exit 1
fi
