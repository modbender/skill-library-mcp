#!/usr/bin/env bash
# deai-approve-token.sh — Approve token spending for the Escrow contract
# Usage: deai-approve-token.sh <usdc|address> <amount>
# Example: deai-approve-token.sh usdc 10000
# Amount is in human-readable units (e.g. 10000 = 10,000 USDC). Converted to raw internally.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/_common.sh"

TOKEN_NAME="${1:?Usage: deai-approve-token.sh <usdt|usdc|address> <amount>}"
AMOUNT="${2:?Usage: deai-approve-token.sh <usdt|usdc|address> <amount>}"

assert_decimal "amount" "$AMOUNT"
build_cast_flags

TOKEN_ADDR=$(resolve_token "$TOKEN_NAME")
# If token wasn't resolved from a known symbol, validate it's a proper address
if [[ "${TOKEN_NAME,,}" != "usdc" ]]; then
  assert_address "tokenAddress" "$TOKEN_ADDR"
fi
AMOUNT_WEI=$(to_wei "$AMOUNT")
WALLET=$(get_wallet)

echo "=== DeAI Token Approval ==="
echo "Token:   $TOKEN_NAME ($TOKEN_ADDR)"
echo "Amount:  $AMOUNT ($AMOUNT_WEI wei)"
echo "Spender: $ESCROW_ADDR (Escrow)"
echo "Wallet:  $WALLET"
echo ""

# Check current allowance
CURRENT=$(cast call "$TOKEN_ADDR" "allowance(address,address)(uint256)" "$WALLET" "$ESCROW_ADDR" --rpc-url "$DEAI_RPC_URL" 2>/dev/null || echo "0")
CURRENT_HUMAN=$(to_token_units "$CURRENT")
echo "Current allowance: $CURRENT_HUMAN"

echo "Approving $AMOUNT tokens..."
TX_HASH=$(cast send "$TOKEN_ADDR" \
  "approve(address,uint256)" \
  "$ESCROW_ADDR" "$AMOUNT_WEI" \
  "${CAST_FLAGS[@]}" \
  --json | jq -r '.transactionHash')

echo "TX: $TX_HASH"
echo "Waiting for confirmation..."

RECEIPT=$(cast receipt "$TX_HASH" --rpc-url "$DEAI_RPC_URL" --json)
STATUS=$(echo "$RECEIPT" | jq -r '.status')

if [[ "$STATUS" == "0x1" ]]; then
  echo ""
  echo "Approval successful!"
  echo "Escrow can now spend up to $AMOUNT ${TOKEN_NAME^^} from your wallet."
  echo "Explorer: $(explorer_tx_url "$TX_HASH")"
else
  echo "Transaction FAILED. Check explorer: $(explorer_tx_url "$TX_HASH")"
  exit 1
fi
