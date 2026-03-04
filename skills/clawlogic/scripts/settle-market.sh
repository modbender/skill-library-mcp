#!/bin/bash
# Settle a resolved market and redeem winning tokens for ETH.
#
# Usage: settle-market.sh <market-id>
#
# Arguments:
#   market-id  - The bytes32 market identifier (hex string). Required.
#
# The market must be resolved before calling this.
#
# Environment:
#   AGENT_PRIVATE_KEY          - Agent wallet private key (required)
#   ARBITRUM_SEPOLIA_RPC_URL   - RPC endpoint (optional, has default)
#
# Output: JSON to stdout with { success, txHash, estimatedEthPayout }

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if [ $# -lt 1 ]; then
  echo '{"success": false, "error": "Usage: settle-market.sh <market-id>"}' >&2
  exit 1
fi

exec npx tsx "${SCRIPT_DIR}/helpers/settle-market.ts" "$@"
