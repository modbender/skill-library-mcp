#!/bin/bash
# Solana Token Scanner — Analyze any token for safety
# Usage: scan-token.sh <mint_address>

set -euo pipefail

MINT="${1:?Usage: scan-token.sh <mint_address>}"
RPC="${SOLANA_RPC_URL:-https://api.mainnet-beta.solana.com}"

echo "{"
echo "  \"mint\": \"$MINT\","
echo "  \"scan_time\": \"$(date -u +%Y-%m-%dT%H:%M:%SZ)\","

# 1. Token metadata from DexScreener
echo "  \"dexscreener\": $(curl -sf "https://api.dexscreener.com/latest/dex/tokens/$MINT" 2>/dev/null || echo '{"error":"failed"}'),"

# 2. Jupiter price
echo "  \"jupiter_price\": $(curl -sf "https://api.jup.ag/price/v2?ids=$MINT" 2>/dev/null || echo '{"error":"failed"}'),"

# 3. Token supply info from RPC
SUPPLY=$(curl -sf "$RPC" -X POST -H "Content-Type: application/json" -d "{
  \"jsonrpc\": \"2.0\",
  \"id\": 1,
  \"method\": \"getTokenSupply\",
  \"params\": [\"$MINT\"]
}" 2>/dev/null || echo '{"error":"failed"}')
echo "  \"supply\": $SUPPLY,"

# 4. Largest holders
HOLDERS=$(curl -sf "$RPC" -X POST -H "Content-Type: application/json" -d "{
  \"jsonrpc\": \"2.0\",
  \"id\": 1,
  \"method\": \"getTokenLargestAccounts\",
  \"params\": [\"$MINT\"]
}" 2>/dev/null || echo '{"error":"failed"}')
echo "  \"largest_holders\": $HOLDERS"

echo "}"
