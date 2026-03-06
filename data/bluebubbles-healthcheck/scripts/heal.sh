#!/bin/bash
# heal.sh — BlueBubbles ↔ OpenClaw auto-healing
# Diagnoses issues, attempts fixes, verifies resolution

set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Config: from args or env vars
BB_URL="${BB_URL:-http://127.0.0.1:1234}"
BB_PASSWORD="${BB_PASSWORD:-}"
OPENCLAW_WEBHOOK_URL="${OPENCLAW_WEBHOOK_URL:-http://127.0.0.1:18789/bluebubbles-webhook}"

# Parse args
while [[ $# -gt 0 ]]; do
  case $1 in
    --bb-url) BB_URL="$2"; shift 2 ;;
    --password) BB_PASSWORD="$2"; shift 2 ;;
    --webhook-url) OPENCLAW_WEBHOOK_URL="$2"; shift 2 ;;
    --dry-run) DRY_RUN=1; shift ;;
    *) echo "Unknown arg: $1"; exit 1 ;;
  esac
done

DRY_RUN="${DRY_RUN:-0}"

if [[ -z "$BB_PASSWORD" ]]; then
  echo "ERROR: BB_PASSWORD not set. Use --password or BB_PASSWORD env var." >&2
  exit 1
fi

export BB_URL BB_PASSWORD OPENCLAW_WEBHOOK_URL

log() {
  echo "[heal] $@"
}

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# PHASE 1: Initial Diagnosis
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
log "═══════════════════════════════════════════════"
log "PHASE 1: Initial Diagnosis"
log "═══════════════════════════════════════════════"

# Capture diagnose output for analysis
DIAGNOSE_OUTPUT=$("${SCRIPT_DIR}/diagnose.sh" 2>&1) || true
DIAGNOSE_EXIT=$?

echo "$DIAGNOSE_OUTPUT"

if [[ "$DIAGNOSE_EXIT" == "0" ]]; then
  log ""
  log "✅ All checks passed — no healing needed"
  exit 0
fi

log ""
log "Issues detected. Analyzing failures..."

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# PHASE 2: Determine what needs healing
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
HEAL_BB_SERVER=0
HEAL_GATEWAY=0
HEAL_WEBHOOK=0

# Check which components failed
if echo "$DIAGNOSE_OUTPUT" | grep -q "❌.*bb_server_reachable"; then
  HEAL_BB_SERVER=1
  log "  → BlueBubbles server unreachable"
fi

if echo "$DIAGNOSE_OUTPUT" | grep -q "❌.*gateway_endpoint_alive"; then
  HEAL_GATEWAY=1
  log "  → OpenClaw gateway endpoint down"
fi

if echo "$DIAGNOSE_OUTPUT" | grep -q "❌.*webhook_registered"; then
  HEAL_WEBHOOK=1
  log "  → Webhook not registered or misconfigured"
fi

if echo "$DIAGNOSE_OUTPUT" | grep -q "❌.*webhook_delivery"; then
  # Delivery issues often fixed by webhook reset
  HEAL_WEBHOOK=1
  log "  → Webhook delivery issues detected"
fi

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# PHASE 3: Healing Actions
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
log ""
log "═══════════════════════════════════════════════"
log "PHASE 2: Healing"
log "═══════════════════════════════════════════════"

HEALED_SOMETHING=0

# ─────────────────────────────────────────────────────────────────────────────
# HEAL: BlueBubbles server unreachable
# ─────────────────────────────────────────────────────────────────────────────
if [[ "$HEAL_BB_SERVER" == "1" ]]; then
  log ""
  log "🔧 BlueBubbles server unreachable"
  log "   Cannot auto-heal: BlueBubbles must be started manually on the Mac"
  log "   Suggestions:"
  log "   - Check if BlueBubbles.app is running"
  log "   - Check if port 1234 is correct"
  log "   - Check network connectivity"
  log ""
  log "❌ Cannot proceed without BlueBubbles server"
  exit 1
fi

# ─────────────────────────────────────────────────────────────────────────────
# HEAL: OpenClaw gateway down
# ─────────────────────────────────────────────────────────────────────────────
if [[ "$HEAL_GATEWAY" == "1" ]]; then
  log ""
  log "🔧 Attempting to restart OpenClaw gateway..."
  
  if [[ "$DRY_RUN" == "1" ]]; then
    log "   [DRY RUN] Would run: openclaw gateway restart"
  else
    # Try to restart the gateway
    if command -v openclaw &> /dev/null; then
      openclaw gateway restart 2>&1 || true
      log "   Waiting 10s for gateway to initialize..."
      sleep 10
      HEALED_SOMETHING=1
      
      # Re-check if gateway came up
      if nc -z 127.0.0.1 18789 2>/dev/null; then
        log "   ✅ Gateway port 18789 now responding"
      else
        log "   ⚠️ Gateway still not responding on port 18789"
      fi
    else
      log "   ❌ 'openclaw' command not found — cannot restart gateway"
      log "   Try manually: openclaw gateway restart"
    fi
  fi
fi

# ─────────────────────────────────────────────────────────────────────────────
# HEAL: Webhook needs reset
# ─────────────────────────────────────────────────────────────────────────────
if [[ "$HEAL_WEBHOOK" == "1" ]] || [[ "$HEAL_GATEWAY" == "1" ]]; then
  log ""
  log "🔧 Resetting webhook registration..."
  
  if [[ "$DRY_RUN" == "1" ]]; then
    log "   [DRY RUN] Would run: reset-webhook.sh"
  else
    "${SCRIPT_DIR}/reset-webhook.sh" 2>&1 || true
    HEALED_SOMETHING=1
  fi
fi

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# PHASE 4: Verification
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
if [[ "$HEALED_SOMETHING" == "1" ]]; then
  log ""
  log "═══════════════════════════════════════════════"
  log "PHASE 3: Verification"
  log "═══════════════════════════════════════════════"
  
  sleep 2
  
  VERIFY_OUTPUT=$("${SCRIPT_DIR}/diagnose.sh" 2>&1) || true
  VERIFY_EXIT=$?
  
  echo "$VERIFY_OUTPUT"
  
  log ""
  if [[ "$VERIFY_EXIT" == "0" ]]; then
    log "═══════════════════════════════════════════════"
    log "✅ HEALING SUCCESSFUL — all checks now passing"
    log "═══════════════════════════════════════════════"
    exit 0
  else
    log "═══════════════════════════════════════════════"
    log "⚠️ HEALING INCOMPLETE — some issues remain"
    log "═══════════════════════════════════════════════"
    log "Manual intervention may be required."
    exit 1
  fi
else
  log ""
  log "No healing actions were taken."
  exit 1
fi
