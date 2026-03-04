#!/usr/bin/env bash
set -euo pipefail

# Agent Pulse — Self-Configuring Setup
# Detects wallet, checks PULSE balance, checks approval, verifies registration.
# Usage: setup.sh [--auto-approve] [--quiet]

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
API_BASE="${API_BASE:-https://x402pulse.xyz}"
BASE_RPC_URL="${BASE_RPC_URL:-https://mainnet.base.org}"
REGISTRY="0xe61C615743A02983A46aFF66Db035297e8a43846"
PULSE_TOKEN="0x21111B39A502335aC7e45c4574Dd083A69258b07"
MIN_PULSE="1000000000000000000"

AUTO_APPROVE=false
QUIET=false

for arg in "$@"; do
  case "$arg" in
    --auto-approve) AUTO_APPROVE=true ;;
    --quiet|-q) QUIET=true ;;
    -h|--help)
      echo "Usage: $0 [--auto-approve] [--quiet]"
      echo "  --auto-approve  Approve PulseRegistry for max allowance automatically"
      echo "  --quiet         Machine-readable JSON output only"
      exit 0
      ;;
  esac
done

# Output helpers
info()  { $QUIET || echo "[✓] $*"; }
warn()  { $QUIET || echo "[!] $*"; }
fail()  { $QUIET || echo "[✗] $*"; }

RESULT_WALLET=""
RESULT_BALANCE="0"
RESULT_APPROVED=false
RESULT_ALIVE=false
RESULT_STREAK=0
RESULT_ERRORS=()

# ── Step 1: Wallet ───────────────────────────────────────────────
$QUIET || echo "=== Agent Pulse Setup ==="
$QUIET || echo ""

if [[ -z "${PRIVATE_KEY:-}" ]]; then
  RESULT_ERRORS+=("PRIVATE_KEY not set")
  fail "PRIVATE_KEY not set. Export it before running setup."
  $QUIET && echo '{"ok":false,"error":"PRIVATE_KEY not set"}'
  exit 1
fi

if ! command -v cast &>/dev/null; then
  RESULT_ERRORS+=("cast not found")
  fail "'cast' (Foundry) not installed. Install: curl -L https://foundry.paradigm.xyz | bash"
  $QUIET && echo '{"ok":false,"error":"cast not found"}'
  exit 1
fi

RESULT_WALLET=$(cast wallet address "$PRIVATE_KEY" 2>/dev/null) || {
  fail "Could not derive wallet address from PRIVATE_KEY."
  $QUIET && echo '{"ok":false,"error":"bad private key"}'
  exit 1
}
info "Wallet: $RESULT_WALLET"

# ── Step 2: PULSE Balance ────────────────────────────────────────
BALANCE_RAW=$(cast call --rpc-url "$BASE_RPC_URL" \
  "$PULSE_TOKEN" "balanceOf(address)(uint256)" "$RESULT_WALLET" 2>/dev/null) || {
  warn "Could not query PULSE balance (RPC error)."
  BALANCE_RAW="0"
}
RESULT_BALANCE=$(echo "$BALANCE_RAW" | head -1 | tr -cd '0-9')
RESULT_BALANCE="${RESULT_BALANCE:-0}"

# Human-readable balance (integer division to avoid bc dependency)
if [[ ${#RESULT_BALANCE} -gt 18 ]]; then
  BALANCE_INT="${RESULT_BALANCE:0:$((${#RESULT_BALANCE}-18))}"
else
  BALANCE_INT="0"
fi

if [[ "$RESULT_BALANCE" == "0" ]]; then
  fail "PULSE balance: 0. You need PULSE tokens to send pulses."
  fail "Get PULSE at: $API_BASE"
else
  info "PULSE balance: ~${BALANCE_INT} PULSE ($RESULT_BALANCE wei)"
fi

# ── Step 3: Registry Approval ────────────────────────────────────
ALLOWANCE_RAW=$(cast call --rpc-url "$BASE_RPC_URL" \
  "$PULSE_TOKEN" "allowance(address,address)(uint256)" \
  "$RESULT_WALLET" "$REGISTRY" 2>/dev/null) || ALLOWANCE_RAW="0"
ALLOWANCE=$(echo "$ALLOWANCE_RAW" | head -1 | tr -cd '0-9')
ALLOWANCE="${ALLOWANCE:-0}"

if [[ "$ALLOWANCE" != "0" ]]; then
  RESULT_APPROVED=true
  info "Registry approved (allowance: $ALLOWANCE wei)"
else
  warn "Registry not yet approved."
  if [[ "$AUTO_APPROVE" == "true" && "$RESULT_BALANCE" != "0" ]]; then
    # Bounded approval: 1000 PULSE (enough for ~1000 pulses before re-approval)
    # Use --max-approve flag for unlimited approval if needed
    APPROVE_AMOUNT="1000000000000000000000"  # 1000 * 1e18
    info "Auto-approving registry for 1,000 PULSE (bounded)..."
    if cast send --rpc-url "$BASE_RPC_URL" --private-key "$PRIVATE_KEY" \
        "$PULSE_TOKEN" "approve(address,uint256)(bool)" \
        "$REGISTRY" "$APPROVE_AMOUNT" >/dev/null 2>&1; then
      RESULT_APPROVED=true
      info "Registry approved."
    else
      warn "Auto-approval failed. Will approve on first pulse."
    fi
  fi
fi

# ── Step 4: Agent Status ─────────────────────────────────────────
STATUS_JSON=$(curl -sS --connect-timeout 10 --max-time 15 \
  "$API_BASE/api/status/$RESULT_WALLET" 2>/dev/null) || STATUS_JSON=""

if [[ -n "$STATUS_JSON" ]] && echo "$STATUS_JSON" | jq -e '.isAlive // .alive' &>/dev/null 2>&1; then
  RESULT_ALIVE=$(echo "$STATUS_JSON" | jq -r '.isAlive // .alive')
  RESULT_STREAK=$(echo "$STATUS_JSON" | jq -r '.streak // 0')
  if [[ "$RESULT_ALIVE" == "true" ]]; then
    info "Agent status: ALIVE (streak: $RESULT_STREAK)"
  else
    warn "Agent status: NOT ALIVE (streak: $RESULT_STREAK). Send a pulse to activate."
  fi
else
  warn "Agent not registered yet. Send your first pulse to register."
fi

# ── Step 5: Protocol Health ──────────────────────────────────────
HEALTH_JSON=$(curl -sS --connect-timeout 10 --max-time 15 \
  "$API_BASE/api/protocol-health" 2>/dev/null) || HEALTH_JSON=""

PROTOCOL_OK=true
if [[ -n "$HEALTH_JSON" ]] && echo "$HEALTH_JSON" | jq -e '.' &>/dev/null 2>&1; then
  PAUSED=$(echo "$HEALTH_JSON" | jq -r '.paused // false')
  if [[ "$PAUSED" == "true" ]]; then
    warn "Protocol is PAUSED. Pulses will fail until unpaused."
    PROTOCOL_OK=false
  else
    info "Protocol: healthy"
  fi
fi

# ── Summary ──────────────────────────────────────────────────────
if $QUIET; then
  jq -n \
    --arg wallet "$RESULT_WALLET" \
    --arg balance "$RESULT_BALANCE" \
    --argjson approved "$RESULT_APPROVED" \
    --argjson alive "$RESULT_ALIVE" \
    --argjson streak "$RESULT_STREAK" \
    --argjson protocolOk "$PROTOCOL_OK" \
    '{ok:true, wallet:$wallet, balance:$balance, approved:$approved, alive:$alive, streak:($streak|tonumber), protocolOk:$protocolOk}'
else
  echo ""
  echo "=== Setup Summary ==="
  echo "  Wallet:    $RESULT_WALLET"
  echo "  Balance:   ~${BALANCE_INT} PULSE ($RESULT_BALANCE wei)"
  echo "  Approved:  $([ "$RESULT_APPROVED" == "true" ] && echo 'Yes' || echo 'No')"
  echo "  Alive:     $RESULT_ALIVE (streak: $RESULT_STREAK)"
  echo "  Protocol:  $([ "$PROTOCOL_OK" == "true" ] && echo 'Healthy' || echo 'PAUSED')"
  echo "  Network:   Base (8453)"
  echo ""
  if [[ "$RESULT_BALANCE" == "0" ]]; then
    echo "Next step: Get PULSE tokens at $API_BASE"
  elif [[ "$RESULT_ALIVE" != "true" ]]; then
    echo "Next step: $SCRIPT_DIR/pulse.sh --direct $MIN_PULSE"
  else
    echo "Ready! Use auto-pulse.sh for automatic heartbeat."
  fi
fi
