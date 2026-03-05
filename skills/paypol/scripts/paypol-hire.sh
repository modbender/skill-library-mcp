#!/usr/bin/env bash
# ═══════════════════════════════════════════════════════════════
# PayPol Agent Hiring Script for OpenClaw
# ═══════════════════════════════════════════════════════════════
#
# Usage:
#   ./paypol-hire.sh <agent-id> "<prompt>"
#
# Examples:
#   ./paypol-hire.sh escrow-manager "Create escrow for 500 AlphaUSD to 0xABC"
#   ./paypol-hire.sh token-transfer "Send 100 AlphaUSD to 0xDEF"
#   ./paypol-hire.sh treasury-manager "Full treasury overview for my wallet"
#
# Environment Variables:
#   PAYPOL_API_KEY     - Required: Your PayPol API key
#   PAYPOL_AGENT_API   - Optional: API base URL (default: https://paypol.xyz)
#   PAYPOL_WALLET      - Optional: Caller wallet ID (default: openclaw-agent)
#   PAYPOL_TIMEOUT     - Optional: Request timeout in seconds (default: 120)
# ═══════════════════════════════════════════════════════════════

set -euo pipefail

# ── Config ────────────────────────────────────────────────────
API_BASE="${PAYPOL_AGENT_API:-https://paypol.xyz}"
API_KEY="${PAYPOL_API_KEY:?Error: PAYPOL_API_KEY environment variable is required}"
WALLET="${PAYPOL_WALLET:-openclaw-agent}"
TIMEOUT="${PAYPOL_TIMEOUT:-120}"

# ── Validation ────────────────────────────────────────────────
if [ $# -lt 2 ]; then
  echo "Usage: paypol-hire.sh <agent-id> \"<prompt>\""
  echo ""
  echo "Available agents (32 on-chain agents on Tempo L1):"
  echo "  Escrow:       escrow-manager, escrow-lifecycle, escrow-dispute,"
  echo "                escrow-batch-settler, bulk-escrow"
  echo "  Payments:     token-transfer, multisend-batch, multi-token-sender,"
  echo "                multi-token-batch, recurring-payment"
  echo "  Streams:      stream-creator, stream-manager, stream-inspector"
  echo "  Privacy:      shield-executor, vault-depositor, vault-inspector"
  echo "  Deployment:   token-deployer, contract-deploy-pro, token-minter"
  echo "  Security:     allowance-manager, wallet-sweeper"
  echo "  Analytics:    tempo-benchmark, balance-scanner, treasury-manager,"
  echo "                gas-profiler, contract-reader, chain-monitor"
  echo "  Verification: proof-verifier, proof-auditor"
  echo "  Orchestrate:  coordinator"
  echo "  Payroll:      payroll-planner"
  echo "  Admin:        fee-collector"
  exit 1
fi

AGENT_ID="$1"
PROMPT="$2"

# ── Valid agent IDs ───────────────────────────────────────────
VALID_AGENTS=(
  "escrow-manager" "escrow-lifecycle" "escrow-dispute"
  "escrow-batch-settler" "bulk-escrow"
  "token-transfer" "multisend-batch" "multi-token-sender"
  "multi-token-batch" "recurring-payment"
  "stream-creator" "stream-manager" "stream-inspector"
  "shield-executor" "vault-depositor" "vault-inspector"
  "token-deployer" "contract-deploy-pro" "token-minter"
  "allowance-manager" "wallet-sweeper"
  "tempo-benchmark" "balance-scanner" "treasury-manager"
  "gas-profiler" "contract-reader" "chain-monitor"
  "proof-verifier" "proof-auditor"
  "coordinator"
  "payroll-planner"
  "fee-collector"
)

VALID=false
for agent in "${VALID_AGENTS[@]}"; do
  if [ "$agent" = "$AGENT_ID" ]; then
    VALID=true
    break
  fi
done

if [ "$VALID" = false ]; then
  echo "Error: Unknown agent '$AGENT_ID'"
  echo "Run without arguments to see available agents."
  exit 1
fi

# ── Execute ───────────────────────────────────────────────────
RESPONSE=$(curl -s --max-time "$TIMEOUT" \
  -X POST "${API_BASE}/agents/${AGENT_ID}/execute" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: ${API_KEY}" \
  -d "$(jq -n --arg prompt "$PROMPT" --arg wallet "$WALLET" \
    '{prompt: $prompt, callerWallet: $wallet}')")

# ── Output ────────────────────────────────────────────────────
STATUS=$(echo "$RESPONSE" | jq -r '.status // "unknown"')

if [ "$STATUS" = "success" ]; then
  echo "$RESPONSE" | jq '.result'
elif [ "$STATUS" = "error" ]; then
  echo "Agent Error: $(echo "$RESPONSE" | jq -r '.error')" >&2
  exit 1
else
  echo "$RESPONSE" | jq '.'
fi
