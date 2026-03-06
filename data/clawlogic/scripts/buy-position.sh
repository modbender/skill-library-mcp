#!/bin/bash
# Buy a position by minting outcome tokens with ETH collateral.
#
# Usage: buy-position.sh <market-id> <eth-amount>
#
# Arguments:
#   market-id   - The bytes32 market identifier (hex string). Required.
#   eth-amount  - Amount of ETH to deposit (e.g. "0.1"). Required.
#
# Environment:
#   AGENT_PRIVATE_KEY          - Agent wallet private key (required)
#   ARBITRUM_SEPOLIA_RPC_URL   - RPC endpoint (optional, has default)
#
# Output: JSON to stdout with { success, txHash, balances }

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if [ $# -lt 2 ]; then
  echo '{"success": false, "error": "Usage: buy-position.sh <market-id> <eth-amount>"}' >&2
  exit 1
fi

exec npx tsx "${SCRIPT_DIR}/helpers/buy-position.ts" "$@"
