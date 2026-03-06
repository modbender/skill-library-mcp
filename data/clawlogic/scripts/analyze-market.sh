#!/bin/bash
# Analyze a prediction market -- returns full details for agent reasoning.
#
# Usage: analyze-market.sh <market-id>
#
# Arguments:
#   market-id  - The bytes32 market identifier (hex string). Required.
#
# Environment:
#   AGENT_PRIVATE_KEY          - Agent wallet private key (optional for read-only)
#   ARBITRUM_SEPOLIA_RPC_URL   - RPC endpoint (optional, has default)
#
# Output: JSON to stdout with market details, positions, token metrics, and analysis hints.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if [ $# -lt 1 ]; then
  echo '{"success": false, "error": "Usage: analyze-market.sh <market-id>"}' >&2
  exit 1
fi

exec npx tsx "${SCRIPT_DIR}/helpers/analyze-market.ts" "$@"
