#!/usr/bin/env bash
# deai-status.sh — Check your agent's status and reputation
# Usage: deai-status.sh [address]
# If no address given, derives wallet from DEAI_ACCOUNT keystore
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/_common.sh"

ADDRESS="${1:-$(get_wallet)}"

if [[ -n "${1:-}" ]]; then
  assert_address "address" "$ADDRESS"
fi

echo "=== DeAI Agent Status ($(chain_name)) ==="
echo "Address: $ADDRESS"
echo "Profile: https://deai.au/agents/$ADDRESS"
echo ""

# Try indexer first
AGENT_DATA=$(curl -sf "${DEAI_INDEXER_URL}/api/agents/${ADDRESS}" 2>/dev/null || echo "")

if [[ -n "$AGENT_DATA" && "$AGENT_DATA" != "null" ]]; then
  NAME=$(echo "$AGENT_DATA" | jq -r '.name // "Unknown"')
  AGENT_ID=$(echo "$AGENT_DATA" | jq -r '.agentId // "?"')
  ACTIVE=$(echo "$AGENT_DATA" | jq -r '.isActive')
  REP=$(echo "$AGENT_DATA" | jq -r '.metrics.reputationScore // 50')
  JOBS=$(echo "$AGENT_DATA" | jq -r '.metrics.jobsCompleted // 0')
  ENDORSEMENTS=$(echo "$AGENT_DATA" | jq -r '.metrics.endorsementCount // 0')
  EARNINGS=$(echo "$AGENT_DATA" | jq -r '.metrics.totalEarnings // 0')
  CAPS=$(echo "$AGENT_DATA" | jq -r '.capabilities // [] | join(", ")')

  echo "Name:          $NAME"
  echo "Agent ID:      $AGENT_ID"
  echo "Active:        $ACTIVE"
  echo "Reputation:    $REP / 100"
  echo "Trades Done:   $JOBS"
  echo "Endorsements:  $ENDORSEMENTS"
  echo "Total Volume:  $EARNINGS"
  echo "Capabilities:  ${CAPS:-none}"
else
  echo "Agent not found in indexer. Checking on-chain..."

  AGENT_ID=$(cast call "$IDENTITY_ADDR" "getAgentByWallet(address)(uint256)" "$ADDRESS" --rpc-url "$DEAI_RPC_URL" 2>/dev/null || echo "NOT_FOUND")

  if [[ "$AGENT_ID" == "NOT_FOUND" || "$AGENT_ID" == "0" ]]; then
    echo "No agent registered for this wallet."
    echo ""
    echo "Register with: deai-register.sh <name> <metadataJSON>"
    exit 0
  fi

  echo "Agent ID: $AGENT_ID"

  AGENT_INFO=$(cast call "$IDENTITY_ADDR" "getAgent(uint256)" "$AGENT_ID" --rpc-url "$DEAI_RPC_URL" 2>/dev/null || echo "")
  METADATA=$(cast call "$IDENTITY_ADDR" "getMetadataURI(uint256)(string)" "$AGENT_ID" --rpc-url "$DEAI_RPC_URL" 2>/dev/null || echo "")

  echo "On-chain data: $AGENT_INFO"
  [[ -n "$METADATA" ]] && echo "Metadata: $METADATA"
fi
