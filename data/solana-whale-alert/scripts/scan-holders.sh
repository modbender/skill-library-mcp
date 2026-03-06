#!/bin/bash
# Scan top holders of a token and check for recent activity
# Usage: scan-holders.sh <token_mint>

MINT="${1:?Usage: scan-holders.sh <token_mint>}"
RPC="${SOLANA_RPC_URL:-https://api.mainnet-beta.solana.com}"

echo "Scanning top holders of: $MINT"

# Get largest token accounts
RESULT=$(curl -sf "$RPC" -X POST -H "Content-Type: application/json" -d "{
  \"jsonrpc\": \"2.0\", \"id\": 1,
  \"method\": \"getTokenLargestAccounts\",
  \"params\": [\"$MINT\"]
}")

# Get supply for percentage calc
SUPPLY=$(curl -sf "$RPC" -X POST -H "Content-Type: application/json" -d "{
  \"jsonrpc\": \"2.0\", \"id\": 1,
  \"method\": \"getTokenSupply\",
  \"params\": [\"$MINT\"]
}")

echo "$RESULT" | python3 -c "
import sys, json

data = json.load(sys.stdin)
accounts = data.get('result', {}).get('value', [])

if not accounts:
    print('No holder data available')
    sys.exit(0)

# Try to get total supply from second JSON on stdin... skip for now
# Just show raw amounts
print(f'Top {len(accounts)} holders:')
print(f'{\"Rank\":>4} {\"Amount\":>20} {\"Account\":>50}')
print('-' * 76)
for i, acc in enumerate(accounts):
    amount = acc.get('uiAmount', 0) or float(acc.get('amount', 0)) / (10 ** (acc.get('decimals', 0) or 9))
    address = acc.get('address', '?')
    print(f'{i+1:4d} {amount:>20,.2f} {address}')
" 2>/dev/null
