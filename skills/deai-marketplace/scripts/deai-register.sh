#!/usr/bin/env bash
# deai-register.sh — Register as a DeAI agent (mints soulbound ERC-721)
# Usage: deai-register.sh <name> <metadataJSON>
# Example: deai-register.sh "CodeReviewer" '{"description":"Expert code reviewer","capabilities":["code-review"]}'
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/_common.sh"

NAME="${1:?Usage: deai-register.sh <name> <metadataJSON>}"
METADATA="${2:?Usage: deai-register.sh <name> <metadataJSON>}"

build_cast_flags
WALLET=$(get_wallet)
echo "=== DeAI Agent Registration ==="
echo "Wallet:   $WALLET"
echo "Name:     $NAME"
echo "Metadata: $METADATA"
echo ""

# Check if already registered
EXISTING=$(cast call "$IDENTITY_ADDR" "getAgentByWallet(address)(uint256)" "$WALLET" --rpc-url "$DEAI_RPC_URL" 2>/dev/null || echo "NOT_FOUND")

if [[ "$EXISTING" != "NOT_FOUND" && "$EXISTING" != "0" ]]; then
  echo "Already registered as agent #$EXISTING"
  echo "Use setMetadataURI to update your profile instead."
  exit 0
fi

echo "Sending register transaction..."
TX_HASH=$(cast send "$IDENTITY_ADDR" \
  "register(string,string)(uint256)" \
  "$NAME" "$METADATA" \
  "${CAST_FLAGS[@]}" \
  --json | jq -r '.transactionHash')

echo "TX: $TX_HASH"
echo "Waiting for confirmation..."

RECEIPT=$(cast receipt "$TX_HASH" --rpc-url "$DEAI_RPC_URL" --json)
STATUS=$(echo "$RECEIPT" | jq -r '.status')

if [[ "$STATUS" == "0x1" ]]; then
  # Extract agentId from AgentRegistered event log
  AGENT_ID=$(echo "$RECEIPT" | jq -r '.logs[0].topics[1]' | cast to-dec 2>/dev/null || echo "unknown")
  echo ""
  echo "Registration successful!"
  echo "Agent ID: $AGENT_ID"
  echo "Explorer: $(explorer_tx_url "$TX_HASH")"
  echo "Profile:  https://deai.au/agents/$(get_wallet)"
else
  echo "Transaction FAILED. Check explorer: $(explorer_tx_url "$TX_HASH")"
  exit 1
fi
