#!/bin/bash
# Register an agent on-chain via AgentRegistry.
#
# Usage: register-agent.sh <name> [attestation]
#
# Arguments:
#   name         - Human-readable agent name (e.g. "AlphaTrader"). Required.
#   attestation  - TEE attestation bytes, hex-encoded. Optional, defaults to "0x".
#
# Environment:
#   AGENT_PRIVATE_KEY          - Agent wallet private key (required)
#   ARBITRUM_SEPOLIA_RPC_URL   - RPC endpoint (optional, has default)
#
# Output: JSON to stdout with { success, txHash, address, name }

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if [ $# -lt 1 ]; then
  echo '{"success": false, "error": "Usage: register-agent.sh <name> [attestation]"}' >&2
  exit 1
fi

exec npx tsx "${SCRIPT_DIR}/helpers/register-agent.ts" "$@"
