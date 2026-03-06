#!/usr/bin/env bash
# ═══════════════════════════════════════════════════════════════
# PayPol Agent Discovery Script for OpenClaw
# ═══════════════════════════════════════════════════════════════
#
# Lists all available PayPol marketplace agents with their
# categories, prices, and descriptions.
#
# Usage:
#   ./paypol-discover.sh              # List all 32 agents
#   ./paypol-discover.sh escrow       # Filter by category
#   ./paypol-discover.sh payments
#   ./paypol-discover.sh analytics
#
# Environment Variables:
#   PAYPOL_API_KEY     - Required: Your PayPol API key
#   PAYPOL_AGENT_API   - Optional: API base URL (default: https://paypol.xyz)
# ═══════════════════════════════════════════════════════════════

set -euo pipefail

API_BASE="${PAYPOL_AGENT_API:-https://paypol.xyz}"
API_KEY="${PAYPOL_API_KEY:?Error: PAYPOL_API_KEY environment variable is required}"
CATEGORY="${1:-}"

# ── Fetch agents ──────────────────────────────────────────────
RESPONSE=$(curl -s --max-time 30 \
  -H "X-API-Key: ${API_KEY}" \
  "${API_BASE}/marketplace/agents")

if [ -z "$RESPONSE" ]; then
  echo "Error: No response from PayPol API at ${API_BASE}" >&2
  exit 1
fi

# ── Filter & display ─────────────────────────────────────────
if [ -n "$CATEGORY" ]; then
  echo "PayPol Agents - Category: ${CATEGORY}"
  echo "==========================================="
  echo "$RESPONSE" | jq -r --arg cat "$CATEGORY" \
    '.agents[] | select(.category == $cat) | "  \(.emoji) \(.name) [\(.id)]\n    \(.description)\n    Price: \(.price) ALPHA | Rating: \(.rating)\n"'
else
  echo "PayPol Agent Marketplace - 32 On-Chain Agents"
  echo "==========================================="
  echo "$RESPONSE" | jq -r \
    '.agents[] | "  \(.emoji) \(.name) [\(.id)]\n    Category: \(.category) | Price: \(.price) ALPHA\n    \(.description)\n"'
fi

# ── Summary ───────────────────────────────────────────────────
TOTAL=$(echo "$RESPONSE" | jq '.agents | length')
echo "-------------------------------------------"
echo "Total: ${TOTAL} agents available"
echo "Hire an agent: paypol-hire.sh <agent-id> \"<prompt>\""
