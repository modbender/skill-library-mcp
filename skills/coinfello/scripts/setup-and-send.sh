#!/usr/bin/env bash
# setup-and-send.sh — End-to-end CoinFello workflow
#
# Usage:
#   ./setup-and-send.sh <chain> <prompt>
#
# Example:
#   ./setup-and-send.sh sepolia "send 3 USDC to 0xRecipient"

set -euo pipefail

CHAIN="${1:?Usage: $0 <chain> <prompt>}"
PROMPT="${2:?Missing prompt}"

echo "==> Creating smart account on ${CHAIN}..."
npx @coinfello/agent-cli create_account "$CHAIN"

echo ""
echo "==> Signing in..."
npx @coinfello/agent-cli sign_in

echo ""
echo "==> Sending prompt..."
OUTPUT=$(npx @coinfello/agent-cli send_prompt "$PROMPT")

echo "$OUTPUT"

# Extract txn_id from output
TXN_ID=$(echo "$OUTPUT" | grep -oP 'Transaction ID: \K.*')

if [ -n "$TXN_ID" ]; then
  echo ""
  echo "==> Checking transaction status..."
  npx @coinfello/agent-cli get_transaction_status "$TXN_ID"
fi
