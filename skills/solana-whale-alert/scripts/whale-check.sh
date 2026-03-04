#!/bin/bash
# Check recent large SOL transfers
# Usage: whale-check.sh [min_sol_amount] [num_recent_slots]

MIN_SOL="${1:-500}"
RPC="${SOLANA_RPC_URL:-https://api.mainnet-beta.solana.com}"

echo "Checking recent large SOL transfers (>$MIN_SOL SOL)..."
echo "Using RPC: $RPC"

# Get recent block info
SLOT=$(curl -sf "$RPC" -X POST -H "Content-Type: application/json" -d '{
  "jsonrpc": "2.0", "id": 1, "method": "getSlot"
}' | python3 -c "import sys,json; print(json.load(sys.stdin)['result'])")

echo "Current slot: $SLOT"

# Get recent block with transactions
BLOCK=$(curl -sf "$RPC" -X POST -H "Content-Type: application/json" -d "{
  \"jsonrpc\": \"2.0\", \"id\": 1,
  \"method\": \"getBlock\",
  \"params\": [$SLOT, {
    \"encoding\": \"json\",
    \"transactionDetails\": \"accounts\",
    \"maxSupportedTransactionVersion\": 0
  }]
}")

echo "$BLOCK" | python3 -c "
import sys, json

MIN_LAMPORTS = $MIN_SOL * 1_000_000_000
data = json.load(sys.stdin)
result = data.get('result')
if not result:
    print('No block data available (slot may be skipped)')
    sys.exit(0)

txns = result.get('transactions', [])
print(f'Transactions in block: {len(txns)}')

# Check balance changes
for tx in txns:
    meta = tx.get('meta', {})
    if not meta:
        continue
    pre = meta.get('preBalances', [])
    post = meta.get('postBalances', [])
    accounts = tx.get('transaction', {}).get('accountKeys', [])
    
    if not accounts:
        continue
    
    for i, (pre_bal, post_bal) in enumerate(zip(pre, post)):
        diff = abs(post_bal - pre_bal)
        if diff >= MIN_LAMPORTS and i < len(accounts):
            direction = 'RECEIVED' if post_bal > pre_bal else 'SENT'
            sol_amount = diff / 1_000_000_000
            account = accounts[i] if isinstance(accounts[i], str) else accounts[i].get('pubkey', '?')
            print(f'  {direction} {sol_amount:,.1f} SOL | {account[:12]}...')
" 2>/dev/null
