#!/usr/bin/env bash
#
# Check Gotchi channeling cooldown status
# Returns: ready:0 or waiting:SECONDS
#
# Usage: ./check-cooldown.sh <gotchi-id>

set -euo pipefail

if [ $# -lt 1 ]; then
  echo "❌ Usage: check-cooldown.sh <gotchi-id>"
  exit 1
fi

GOTCHI_ID="$1"
REALM_DIAMOND="0x4B0040c3646D3c44B8a28Ad7055cfCF536c05372"
RPC_URL="${BASE_MAINNET_RPC:-https://mainnet.base.org}"
COOLDOWN_SECONDS=86400  # 24 hours

# Get last channeled timestamp from contract
# This reads the s_gotchiChannelings mapping
LAST_CHANNELED=$(cast call $REALM_DIAMOND \
  "s_gotchiChannelings(uint256)" \
  "$GOTCHI_ID" \
  --rpc-url "$RPC_URL" 2>/dev/null || echo "0")

LAST_CHANNELED_DEC=$(cast --to-dec "$LAST_CHANNELED" 2>/dev/null || echo "0")
CURRENT_TIME=$(date +%s)
TIME_SINCE=$((CURRENT_TIME - LAST_CHANNELED_DEC))
TIME_REMAINING=$((COOLDOWN_SECONDS - TIME_SINCE))

if [ "$TIME_REMAINING" -le 0 ]; then
  # Ready to channel
  echo "ready:0"
  exit 0
else
  # Still on cooldown
  echo "waiting:$TIME_REMAINING"
  exit 0
fi
