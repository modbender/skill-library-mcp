#!/bin/bash
# reset-webhook.sh — Atomic webhook delete + re-register
# Clears any stale/backoff state in BlueBubbles webhook system

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
    *) echo "Unknown arg: $1"; exit 1 ;;
  esac
done

QUIET="${QUIET:-0}"

if [[ -z "$BB_PASSWORD" ]]; then
  echo "ERROR: BB_PASSWORD not set. Use --password or BB_PASSWORD env var." >&2
  exit 1
fi

log() {
  [[ "$QUIET" == "0" ]] && echo "[reset-webhook] $@"
}

# Build full webhook URL with password (for BB to call OpenClaw)
# Note: The password is included in the registered URL so BB can authenticate with OpenClaw
if [[ "$OPENCLAW_WEBHOOK_URL" == *"password="* ]]; then
  FULL_WEBHOOK_URL="$OPENCLAW_WEBHOOK_URL"
else
  if [[ "$OPENCLAW_WEBHOOK_URL" == *"?"* ]]; then
    FULL_WEBHOOK_URL="${OPENCLAW_WEBHOOK_URL}&password=${BB_PASSWORD}"
  else
    FULL_WEBHOOK_URL="${OPENCLAW_WEBHOOK_URL}?password=${BB_PASSWORD}"
  fi
fi

# Mask password in logged URL
MASKED_WEBHOOK_URL=$(echo "$FULL_WEBHOOK_URL" | sed 's/password=[^&]*/password=***/g')

log "Starting webhook reset at $(date)"
log "BB Server: $BB_URL"
log "Target webhook: $MASKED_WEBHOOK_URL"

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Step 1: Get existing webhooks
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
WEBHOOKS=$(curl -s --max-time 10 -H "Authorization: Bearer ${BB_PASSWORD}" "${BB_URL}/api/v1/webhook" 2>/dev/null)

if [[ -z "$WEBHOOKS" ]] || [[ "$WEBHOOKS" == *"error"* ]]; then
  log "ERROR: Failed to fetch webhooks from BlueBubbles"
  exit 1
fi

# Mask any passwords in webhook URLs before logging
MASKED_WEBHOOKS=$(echo "$WEBHOOKS" | sed 's/password=[^"&]*/password=***/g')
log "Current webhooks: $MASKED_WEBHOOKS"

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Step 2: Delete all existing webhooks
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
IDS=$(echo "$WEBHOOKS" | python3 -c "
import sys, json
try:
    d = json.load(sys.stdin)
    for w in d.get('data', []):
        print(w['id'])
except:
    pass
" 2>/dev/null)

DELETED=0
if [[ -n "$IDS" ]]; then
  while IFS= read -r id; do
    if [[ -n "$id" ]]; then
      log "Deleting webhook id=$id"
      curl -s -X DELETE --max-time 10 -H "Authorization: Bearer ${BB_PASSWORD}" "${BB_URL}/api/v1/webhook/${id}" > /dev/null 2>&1
      ((DELETED++))
    fi
  done <<< "$IDS"
  log "Deleted $DELETED webhook(s)"
else
  log "No existing webhooks to delete"
fi

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Step 3: Brief pause to let state settle
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
sleep 2

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Step 4: Register new webhook
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
log "Registering new webhook..."

# Escape the URL for JSON
ESCAPED_URL=$(echo "$FULL_WEBHOOK_URL" | python3 -c "import sys,json; print(json.dumps(sys.stdin.read().strip()))" | sed 's/^"//;s/"$//')

REGISTER_RESULT=$(curl -s -X POST --max-time 10 \
  -H "Authorization: Bearer ${BB_PASSWORD}" \
  -H "Content-Type: application/json" \
  -d "{\"url\": \"${ESCAPED_URL}\", \"events\": [\"*\"]}" \
  "${BB_URL}/api/v1/webhook" 2>/dev/null)

# Mask any passwords in result before logging
MASKED_RESULT=$(echo "$REGISTER_RESULT" | sed 's/password=[^"&]*/password=***/g')
log "Register result: $MASKED_RESULT"

# Check for errors in response
if echo "$REGISTER_RESULT" | grep -qi "error"; then
  log "ERROR: Webhook registration failed"
  exit 1
fi

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Step 5: Verify registration
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
sleep 1

VERIFY=$(curl -s --max-time 10 -H "Authorization: Bearer ${BB_PASSWORD}" "${BB_URL}/api/v1/webhook" 2>/dev/null)
COUNT=$(echo "$VERIFY" | python3 -c "import sys,json; d=json.load(sys.stdin); print(len(d.get('data',[])))" 2>/dev/null || echo "0")

log "Webhook count after reset: $COUNT"

if [[ "$COUNT" == "1" ]]; then
  log "✅ Webhook reset successful"
  exit 0
else
  log "⚠️ Unexpected webhook count: $COUNT (expected 1)"
  exit 1
fi
