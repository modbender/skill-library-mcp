#!/usr/bin/env bash
set -euo pipefail

# Agent Pulse — Cron-Compatible Auto-Pulse
# Checks if agent is alive. Sends pulse only when TTL is low or agent is dead.
# Exit codes: 0 = success (pulsed or skipped), 1 = error
#
# Usage: auto-pulse.sh [--force] [--dry-run]
# Env:   PRIVATE_KEY (required), BASE_RPC_URL, API_BASE, PULSE_AMOUNT,
#        TTL_THRESHOLD (seconds, default 21600 = 6h)

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
API_BASE="${API_BASE:-https://x402pulse.xyz}"
BASE_RPC_URL="${BASE_RPC_URL:-https://mainnet.base.org}"
PULSE_AMOUNT="${PULSE_AMOUNT:-1000000000000000000}"
TTL_THRESHOLD="${TTL_THRESHOLD:-21600}"  # pulse when TTL < this many seconds

FORCE=false
DRY_RUN=false

for arg in "$@"; do
  case "$arg" in
    --force)   FORCE=true ;;
    --dry-run) DRY_RUN=true ;;
    -h|--help)
      cat <<EOF
Usage: $0 [--force] [--dry-run]
  --force    Send pulse even if TTL is healthy
  --dry-run  Check status but don't actually pulse
Env:
  PRIVATE_KEY      Agent private key (required)
  BASE_RPC_URL     RPC endpoint (default: https://mainnet.base.org)
  PULSE_AMOUNT     Amount in wei (default: 1000000000000000000 = 1 PULSE)
  TTL_THRESHOLD    Pulse when remaining TTL < this (default: 21600 = 6h)
EOF
      exit 0
      ;;
  esac
done

LOG_PREFIX="[agent-pulse:auto]"
log() { echo "$LOG_PREFIX $(date -u +%Y-%m-%dT%H:%M:%SZ) $*"; }

# ── Validate ──────────────────────────────────────────────────────
if [[ -z "${PRIVATE_KEY:-}" ]]; then
  log "ERROR: PRIVATE_KEY not set"
  exit 1
fi

if ! command -v cast &>/dev/null; then
  log "ERROR: 'cast' (Foundry) not found"
  exit 1
fi

WALLET=$(cast wallet address "$PRIVATE_KEY" 2>/dev/null) || {
  log "ERROR: Could not derive wallet from PRIVATE_KEY"
  exit 1
}

# ── Check alive status ───────────────────────────────────────────
NEED_PULSE=true
REASON="unknown"

ALIVE_JSON=$(curl -sS --connect-timeout 10 --max-time 15 \
  "$API_BASE/api/v2/agent/$WALLET/alive" 2>/dev/null) || ALIVE_JSON=""

if [[ -n "$ALIVE_JSON" ]] && echo "$ALIVE_JSON" | jq -e '.' &>/dev/null 2>&1; then
  IS_ALIVE=$(echo "$ALIVE_JSON" | jq -r '.isAlive // .alive // false' 2>/dev/null || echo "false")
  TTL_RAW=$(echo "$ALIVE_JSON" | jq -r '((.ttl // 86400) - (.staleness // 0))' 2>/dev/null || echo "0")
  TTL_REMAINING=$(echo "$TTL_RAW" | tr -cd '0-9')
  TTL_REMAINING="${TTL_REMAINING:-0}"

  if [[ "$FORCE" == "true" ]]; then
    NEED_PULSE=true
    REASON="forced"
  elif [[ "$IS_ALIVE" == "true" && "$TTL_REMAINING" -gt "$TTL_THRESHOLD" ]]; then
    NEED_PULSE=false
    REASON="alive with TTL=${TTL_REMAINING}s (threshold=${TTL_THRESHOLD}s)"
  elif [[ "$IS_ALIVE" == "true" ]]; then
    NEED_PULSE=true
    REASON="alive but TTL low (${TTL_REMAINING}s < ${TTL_THRESHOLD}s)"
  else
    NEED_PULSE=true
    REASON="not alive"
  fi
else
  NEED_PULSE=true
  REASON="could not check status (API unreachable or agent unregistered)"
fi

# ── Act ───────────────────────────────────────────────────────────
if [[ "$NEED_PULSE" == "false" ]]; then
  log "SKIP: $REASON"
  exit 0
fi

log "PULSE: $REASON — sending $PULSE_AMOUNT wei from $WALLET"

if [[ "$DRY_RUN" == "true" ]]; then
  log "DRY-RUN: Would send pulse. Exiting."
  exit 0
fi

# Send pulse via existing pulse.sh
OUTPUT=$("$SCRIPT_DIR/pulse.sh" --direct "$PULSE_AMOUNT" 2>&1) || {
  log "ERROR: Pulse failed"
  log "$OUTPUT"
  exit 1
}

log "OK: Pulse sent successfully"
