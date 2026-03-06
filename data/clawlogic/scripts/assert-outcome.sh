#!/bin/bash
# Assert the outcome of a market via UMA Optimistic Oracle V3.
#
# Usage: assert-outcome.sh <market-id> <outcome>
#
# Arguments:
#   market-id  - The bytes32 market identifier (hex string). Required.
#   outcome    - The outcome to assert (must match outcome1, outcome2, or "Unresolvable"). Required.
#
# WARNING: Asserting requires posting a bond. If disputed and wrong, you LOSE the bond.
#
# Environment:
#   AGENT_PRIVATE_KEY          - Agent wallet private key (required)
#   ARBITRUM_SEPOLIA_RPC_URL   - RPC endpoint (optional, has default)
#
# Output: JSON to stdout with { success, txHash, assertedOutcome }

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if [ $# -lt 2 ]; then
  echo '{"success": false, "error": "Usage: assert-outcome.sh <market-id> <outcome>"}' >&2
  exit 1
fi

exec npx tsx "${SCRIPT_DIR}/helpers/assert-outcome.ts" "$@"
