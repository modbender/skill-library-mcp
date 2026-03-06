#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck disable=SC1091
source "$SCRIPT_DIR/ha_env.sh"

# Quick health check for Home Assistant skill environment.
#
# Verifies:
# - Required tools (curl, jq)
# - Required env vars (HA_TOKEN + HA_URL_PUBLIC)
# - Home Assistant reachability and auth
# - /api/states JSON response validity
#
# URL strategy:
# - If HA_URL is set: use only HA_URL.
# - Otherwise: try HA_URL_LOCAL first, then HA_URL_PUBLIC as fallback.

ok()   { echo "[OK] $*"; }
warn() { echo "[WARN] $*"; }
err()  { echo "[ERROR] $*"; }

FAIL=0

check_cmd() {
  local cmd="$1"
  if command -v "$cmd" >/dev/null 2>&1; then
    ok "Found '$cmd'"
  else
    err "Missing required command: $cmd"
    FAIL=1
  fi
}

check_env() {
  local var="$1"
  if [[ -n "${!var:-}" ]]; then
    ok "Env var set: $var"
  else
    err "Env var missing: $var"
    FAIL=1
  fi
}

echo "Running Home Assistant skill self-check..."

echo
check_cmd curl
check_cmd jq

echo
check_env HA_TOKEN
check_env HA_URL_PUBLIC

CANDIDATES=()
if [[ -n "${HA_URL:-}" ]]; then
  CANDIDATES+=("${HA_URL%/}")
  ok "URL source: HA_URL (override)"
elif [[ -n "${HA_URL_LOCAL:-}" ]]; then
  CANDIDATES+=("${HA_URL_LOCAL%/}")
  ok "URL source: HA_URL_LOCAL"
  if [[ -n "${HA_URL_PUBLIC:-}" && "${HA_URL_PUBLIC%/}" != "${HA_URL_LOCAL%/}" ]]; then
    CANDIDATES+=("${HA_URL_PUBLIC%/}")
    ok "Fallback URL configured: HA_URL_PUBLIC"
  fi
else
  CANDIDATES+=("${HA_URL_PUBLIC%/}")
  ok "URL source: HA_URL_PUBLIC"
fi

if [[ "$FAIL" -ne 0 ]]; then
  echo
  err "Pre-check failed. Fix missing dependencies/env vars first."
  exit 1
fi

TMP_BODY="$(mktemp)"
trap 'rm -f "$TMP_BODY"' EXIT

HTTP_CODE=""
USED_URL=""
LAST_TRANSPORT_ERR=""

for i in "${!CANDIDATES[@]}"; do
  base="${CANDIDATES[$i]}"
  HTTP_CODE="$(curl -sS -o "$TMP_BODY" -w "%{http_code}" \
    -H "Authorization: Bearer $HA_TOKEN" \
    -H "Content-Type: application/json" \
    "$base/api/states" 2>/tmp/ha_self_check_err.$$ || true)"

  # curl transport failure => try fallback
  if [[ "$HTTP_CODE" == "000" || -z "$HTTP_CODE" ]]; then
    LAST_TRANSPORT_ERR="$(cat /tmp/ha_self_check_err.$$ 2>/dev/null || true)"
    if [[ "$i" -lt $((${#CANDIDATES[@]} - 1)) ]]; then
      warn "Primary URL unreachable, trying fallback..."
      continue
    fi
  fi

  USED_URL="$base"
  break
done

rm -f /tmp/ha_self_check_err.$$ 2>/dev/null || true

if [[ -z "$USED_URL" ]]; then
  err "No HTTP status returned from any configured URL."
  [[ -n "$LAST_TRANSPORT_ERR" ]] && echo "$LAST_TRANSPORT_ERR" >&2
  exit 2
fi

if [[ "$USED_URL" != "${CANDIDATES[0]}" ]]; then
  warn "Switched to fallback URL: $USED_URL"
fi

case "$HTTP_CODE" in
  200)
    ok "Connected to Home Assistant API (/api/states)"
    ;;
  401|403)
    err "Authentication failed (HTTP $HTTP_CODE). Check HA_TOKEN permissions."
    head -c 300 "$TMP_BODY" 2>/dev/null || true
    exit 3
    ;;
  404)
    err "Endpoint not found (HTTP 404). Check configured URL (local often ends with :8123)"
    head -c 300 "$TMP_BODY" 2>/dev/null || true
    exit 4
    ;;
  *)
    err "Unexpected HTTP status: $HTTP_CODE"
    head -c 300 "$TMP_BODY" 2>/dev/null || true
    exit 5
    ;;
esac

if jq empty "$TMP_BODY" >/dev/null 2>&1; then
  ok "Response is valid JSON"
else
  err "Response is not valid JSON (proxy/login page?)."
  head -c 300 "$TMP_BODY" 2>/dev/null || true
  exit 6
fi

if jq -e '.message? != null' "$TMP_BODY" >/dev/null 2>&1; then
  warn "API returned message field:"
  jq -r '.message' "$TMP_BODY" || true
fi

ENTITY_COUNT="$(jq 'length' "$TMP_BODY" 2>/dev/null || echo "0")"
if [[ "$ENTITY_COUNT" =~ ^[0-9]+$ ]]; then
  ok "Entities returned: $ENTITY_COUNT"
else
  warn "Could not determine entity count"
fi

echo
echo "Self-check complete: environment looks good."
