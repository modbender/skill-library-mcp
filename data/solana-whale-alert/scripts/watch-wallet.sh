#!/bin/bash
# Watch a wallet for new transactions
# Usage: watch-wallet.sh <wallet_address> [interval_seconds]

WALLET="${1:?Usage: watch-wallet.sh <wallet_address> [interval_seconds]}"
INTERVAL="${2:-60}"
RPC="${SOLANA_RPC_URL:-https://api.mainnet-beta.solana.com}"
LAST_SIG=""

echo "Watching wallet: $WALLET"
echo "Check interval: ${INTERVAL}s"
echo "Press Ctrl+C to stop"
echo "---"

while true; do
    RESULT=$(curl -sf "$RPC" -X POST -H "Content-Type: application/json" -d "{
      \"jsonrpc\": \"2.0\", \"id\": 1,
      \"method\": \"getSignaturesForAddress\",
      \"params\": [\"$WALLET\", {\"limit\": 5}]
    }")
    
    LATEST=$(echo "$RESULT" | python3 -c "
import sys, json
data = json.load(sys.stdin)
sigs = data.get('result', [])
if sigs:
    s = sigs[0]
    print(f\"{s['signature'][:16]}... | slot {s.get('slot','?')} | {'OK' if not s.get('err') else 'FAIL'}\")
" 2>/dev/null)
    
    if [ -n "$LATEST" ] && [ "$LATEST" != "$LAST_SIG" ]; then
        echo "[$(date '+%H:%M:%S')] New tx: $LATEST"
        LAST_SIG="$LATEST"
        
        # Get transaction details for the latest
        SIG=$(echo "$RESULT" | python3 -c "import sys,json; print(json.load(sys.stdin)['result'][0]['signature'])" 2>/dev/null)
        
        if [ -n "$SIG" ]; then
            TX_DETAIL=$(curl -sf "$RPC" -X POST -H "Content-Type: application/json" -d "{
              \"jsonrpc\": \"2.0\", \"id\": 1,
              \"method\": \"getTransaction\",
              \"params\": [\"$SIG\", {\"encoding\": \"json\", \"maxSupportedTransactionVersion\": 0}]
            }")
            
            echo "$TX_DETAIL" | python3 -c "
import sys, json
data = json.load(sys.stdin)
result = data.get('result')
if not result:
    sys.exit(0)
meta = result.get('meta', {})
pre = meta.get('preBalances', [])
post = meta.get('postBalances', [])
keys = result.get('transaction', {}).get('message', {}).get('accountKeys', [])
if not keys:
    keys = result.get('transaction', {}).get('accountKeys', [])

# Show SOL balance changes
for i in range(min(len(pre), len(post), len(keys))):
    diff = post[i] - pre[i]
    if abs(diff) > 1_000_000:  # > 0.001 SOL
        key = keys[i] if isinstance(keys[i], str) else keys[i].get('pubkey', '?')
        sol = diff / 1_000_000_000
        direction = '+' if diff > 0 else ''
        print(f'    {key[:20]}... {direction}{sol:.4f} SOL')

# Show token balance changes
token_pre = meta.get('preTokenBalances', [])
token_post = meta.get('postTokenBalances', [])
for tp in token_post:
    mint = tp.get('mint', '?')
    amount = float(tp.get('uiTokenAmount', {}).get('uiAmountString', '0') or '0')
    # Find matching pre balance
    pre_amount = 0
    for tpr in token_pre:
        if tpr.get('accountIndex') == tp.get('accountIndex'):
            pre_amount = float(tpr.get('uiTokenAmount', {}).get('uiAmountString', '0') or '0')
    diff = amount - pre_amount
    if abs(diff) > 0:
        print(f'    Token {mint[:12]}... {diff:+,.2f}')
" 2>/dev/null
        fi
    fi
    
    sleep "$INTERVAL"
done
