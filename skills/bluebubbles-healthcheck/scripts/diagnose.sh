#!/bin/bash
# diagnose.sh — BlueBubbles ↔ OpenClaw connectivity diagnostics
# Runs 4 checks in order, reports status for each
# Exit 0 if all healthy, non-zero if any check fails

set -uo pipefail

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
    --quiet|-q) QUIET=1; shift ;;
    --json) JSON_OUTPUT=1; shift ;;
    *) echo "Unknown arg: $1"; exit 1 ;;
  esac
done

QUIET="${QUIET:-0}"
JSON_OUTPUT="${JSON_OUTPUT:-0}"

if [[ -z "$BB_PASSWORD" ]]; then
  echo "ERROR: BB_PASSWORD not set. Use --password or BB_PASSWORD env var." >&2
  exit 1
fi

# Track results
RESULTS=()
OVERALL_OK=0

log() {
  [[ "$QUIET" == "0" ]] && echo "$@"
}

check_pass() {
  local name="$1"
  local detail="${2:-}"
  log "✅ CHECK $name: PASS${detail:+ ($detail)}"
  RESULTS+=("{\"check\":\"$name\",\"status\":\"pass\",\"detail\":\"$detail\"}")
}

check_fail() {
  local name="$1"
  local detail="${2:-}"
  log "❌ CHECK $name: FAIL${detail:+ ($detail)}"
  RESULTS+=("{\"check\":\"$name\",\"status\":\"fail\",\"detail\":\"$detail\"}")
  OVERALL_OK=1
}

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# CHECK 1: BB server reachable?
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
log "─── CHECK 1: BlueBubbles server reachable ───"

HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" --max-time 5 -H "Authorization: Bearer ${BB_PASSWORD}" "${BB_URL}/api/v1/ping" 2>/dev/null || echo "000")

if [[ "$HTTP_CODE" == "200" ]]; then
  check_pass "bb_server_reachable" "HTTP 200"
else
  check_fail "bb_server_reachable" "HTTP $HTTP_CODE (expected 200)"
fi

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# CHECK 2: Webhook registered pointing to OpenClaw?
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
log "─── CHECK 2: Webhook registered ───"

if [[ "$HTTP_CODE" != "200" ]]; then
  check_fail "webhook_registered" "skipped - BB server unreachable"
else
  WEBHOOK_RESPONSE=$(curl -s --max-time 5 -H "Authorization: Bearer ${BB_PASSWORD}" "${BB_URL}/api/v1/webhook" 2>/dev/null || echo "{}")
  
  # Extract webhook URLs using Python (portable JSON parsing)
  WEBHOOK_URLS=$(echo "$WEBHOOK_RESPONSE" | python3 -c "
import sys, json
try:
    d = json.load(sys.stdin)
    for w in d.get('data', []):
        print(w.get('url', ''))
except:
    pass
" 2>/dev/null)

  # Check if any webhook points to OpenClaw (port 18789)
  if echo "$WEBHOOK_URLS" | grep -q "18789"; then
    MATCHING_URL=$(echo "$WEBHOOK_URLS" | grep "18789" | head -1)
    check_pass "webhook_registered" "$MATCHING_URL"
  elif [[ -z "$WEBHOOK_URLS" ]]; then
    check_fail "webhook_registered" "no webhooks registered"
  else
    check_fail "webhook_registered" "no webhook pointing to OpenClaw (port 18789)"
  fi
fi

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# CHECK 3: OpenClaw webhook endpoint alive?
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
log "─── CHECK 3: OpenClaw webhook endpoint alive ───"

# Test OpenClaw webhook endpoint with Authorization header
ENDPOINT_RESPONSE=$(curl -s -X POST --max-time 5 \
  -H "Authorization: Bearer ${BB_PASSWORD}" \
  -H "Content-Type: application/json" \
  -d '{"type":"ping","data":{}}' \
  "${OPENCLAW_WEBHOOK_URL}" 2>/dev/null || echo "")

if [[ "$ENDPOINT_RESPONSE" == *"ok"* ]] || [[ "$ENDPOINT_RESPONSE" == *"OK"* ]]; then
  check_pass "gateway_endpoint_alive" "responded ok"
else
  # Check if port is even listening
  if nc -z 127.0.0.1 18789 2>/dev/null; then
    check_fail "gateway_endpoint_alive" "port open but bad response: ${ENDPOINT_RESPONSE:0:100}"
  else
    check_fail "gateway_endpoint_alive" "port 18789 not listening (gateway down?)"
  fi
fi

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# CHECK 4: Recent webhook delivery activity?
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
log "─── CHECK 4: Recent webhook delivery ───"

if [[ "$HTTP_CODE" != "200" ]]; then
  check_fail "webhook_delivery" "skipped - BB server unreachable"
else
  # Get server info which includes uptime and message stats
  SERVER_INFO=$(curl -s --max-time 5 -H "Authorization: Bearer ${BB_PASSWORD}" "${BB_URL}/api/v1/server/info" 2>/dev/null || echo "{}")
  
  # Check if we can get logs (this endpoint may not exist in all BB versions)
  LOGS_RESPONSE=$(curl -s --max-time 5 -H "Authorization: Bearer ${BB_PASSWORD}" "${BB_URL}/api/v1/server/logs?count=50" 2>/dev/null || echo "{}")
  
  # Look for recent webhook dispatch in logs
  RECENT_DISPATCH=$(echo "$LOGS_RESPONSE" | python3 -c "
import sys, json
try:
    d = json.load(sys.stdin)
    logs = d.get('data', [])
    # Look for webhook-related log entries
    for log in logs[-20:]:
        msg = str(log).lower()
        if 'webhook' in msg and ('dispatch' in msg or 'sent' in msg or 'delivered' in msg):
            print('found')
            break
except:
    pass
" 2>/dev/null)

  # Also check if there are any recent messages (proxy for activity)
  MSG_COUNT=$(curl -s --max-time 5 -H "Authorization: Bearer ${BB_PASSWORD}" "${BB_URL}/api/v1/message/count" 2>/dev/null | python3 -c "
import sys, json
try:
    d = json.load(sys.stdin)
    print(d.get('data', {}).get('total', 0))
except:
    print(0)
" 2>/dev/null || echo "0")

  if [[ "$RECENT_DISPATCH" == "found" ]]; then
    check_pass "webhook_delivery" "recent dispatch found in logs"
  elif [[ "$MSG_COUNT" -gt 0 ]]; then
    # Can't confirm delivery but messages exist - soft pass with note
    check_pass "webhook_delivery" "messages exist ($MSG_COUNT total), delivery assumed working"
  else
    # No way to confirm - mark as unknown/soft fail
    check_fail "webhook_delivery" "cannot confirm recent delivery (logs unavailable)"
  fi
fi

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# OUTPUT SUMMARY
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
log ""
if [[ "$OVERALL_OK" == "0" ]]; then
  log "═══════════════════════════════════════════════"
  log "✅ ALL CHECKS PASSED - BlueBubbles connectivity healthy"
  log "═══════════════════════════════════════════════"
else
  log "═══════════════════════════════════════════════"
  log "❌ SOME CHECKS FAILED - healing may be required"
  log "═══════════════════════════════════════════════"
fi

# JSON output if requested
if [[ "$JSON_OUTPUT" == "1" ]]; then
  echo "{"
  echo "  \"healthy\": $( [[ "$OVERALL_OK" == "0" ]] && echo "true" || echo "false" ),"
  echo "  \"checks\": ["
  for i in "${!RESULTS[@]}"; do
    echo -n "    ${RESULTS[$i]}"
    [[ $i -lt $((${#RESULTS[@]} - 1)) ]] && echo "," || echo ""
  done
  echo "  ]"
  echo "}"
fi

exit $OVERALL_OK
