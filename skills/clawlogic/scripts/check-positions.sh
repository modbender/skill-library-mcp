#!/bin/bash
# Check the agent's token positions across one or all markets.
#
# Usage: check-positions.sh [market-id]
#
# Arguments:
#   market-id  - Optional. Show positions for this market only.
#                If omitted, shows positions across ALL markets.
#
# Environment:
#   AGENT_PRIVATE_KEY          - Agent wallet private key (required)
#   ARBITRUM_SEPOLIA_RPC_URL   - RPC endpoint (optional, has default)
#
# Output: JSON to stdout with { success, positions, ethBalance }

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

exec npx tsx "${SCRIPT_DIR}/helpers/check-positions.ts" "$@"
