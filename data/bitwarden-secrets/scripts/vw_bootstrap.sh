#!/usr/bin/env bash
# Source this script to bootstrap Vaultwarden env for OpenClaw safely.
# Usage:
#   source /root/.openclaw/workspace/skills/vaultwarden-secrets/scripts/vw_bootstrap.sh

_vw_fail() {
  echo "[vw_bootstrap] ERROR: $*" >&2
  return 1 2>/dev/null || exit 1
}

# Warn when executed (not sourced)
if [[ "${BASH_SOURCE[0]}" == "$0" ]]; then
  echo "This script must be sourced to persist exports."
  echo "Use: source ${BASH_SOURCE[0]}"
  exit 1
fi

command -v bw >/dev/null 2>&1 || _vw_fail "bw CLI not found"

STATUS_JSON="$(bw status 2>/dev/null || true)"
STATUS="$(printf '%s' "$STATUS_JSON" | python3 -c 'import sys,json; 
try:
 o=json.load(sys.stdin); print(o.get("status",""))
except Exception:
 print("")')"

if [[ "$STATUS" == "unauthenticated" ]]; then
  _vw_fail "bw is unauthenticated. Run: bw login --apikey"
fi

# If session missing, unlock from BW_PASSWORD if present
if [[ -z "${BW_SESSION:-}" ]]; then
  if [[ -z "${BW_PASSWORD:-}" ]]; then
    _vw_fail "BW_SESSION missing and BW_PASSWORD not set. Run: bw unlock (or set BW_PASSWORD)"
  fi
  export BW_SESSION="$(bw unlock --passwordenv BW_PASSWORD --raw)"
fi

# Pull runtime secrets from Vaultwarden items
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
EXPORTED="$("$SCRIPT_DIR"/vw_env_export.sh)" || _vw_fail "vw_env_export.sh failed"
# shellcheck disable=SC1090
source /dev/stdin <<< "$EXPORTED"

# Refresh session now that BW_PASSWORD is guaranteed from vault item
export BW_SESSION="$(bw unlock --passwordenv BW_PASSWORD --raw)"

# Optional quick sync check
python3 "$SCRIPT_DIR"/vw_cli.py sync >/dev/null || _vw_fail "sync failed"

echo "[vw_bootstrap] READY (BW_SESSION + BW_CLIENTID/BW_CLIENTSECRET/BW_PASSWORD loaded)"
