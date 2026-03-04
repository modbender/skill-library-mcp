#!/bin/bash
# Publish an agent bet narrative to the frontend broadcast feed.
#
# Usage:
#   post-broadcast.sh <type> <market-id|-> <side|-> <stake-eth|-> <confidence> <reasoning>
#
# Arguments:
#   type       - MarketBroadcast | TradeRationale | NegotiationIntent | Onboarding
#   market-id  - bytes32 market ID or "-" if not applicable
#   side       - yes | no | -
#   stake-eth  - e.g. "0.01" | -
#   confidence - 0 to 100
#   reasoning  - Human-readable reasoning text (quote if it has spaces)
#
# Environment:
#   AGENT_PRIVATE_KEY       - Required
#   AGENT_BROADCAST_URL     - Optional (default: https://clawlogic.vercel.app/api/agent-broadcasts)
#   AGENT_BROADCAST_ENDPOINT - Optional alias for AGENT_BROADCAST_URL
#   AGENT_BROADCAST_API_KEY - Optional
#   AGENT_NAME              - Optional
#   AGENT_ENS_NAME          - Optional
#   AGENT_ENS_NODE          - Optional

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if [ $# -lt 6 ]; then
  echo '{"success": false, "error": "Usage: post-broadcast.sh <type> <market-id|-> <side|-> <stake-eth|-> <confidence> <reasoning>"}' >&2
  exit 1
fi

exec npx tsx "${SCRIPT_DIR}/helpers/post-broadcast.ts" "$@"
