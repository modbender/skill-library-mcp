#!/bin/bash
# test-smoke.sh — Validate codecast prerequisites and configuration
#
# Usage: ./test-smoke.sh
# Checks: webhook URL, required binaries, script permissions

set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PASS=0
FAIL=0

pass() { echo "  ✅ $1"; PASS=$((PASS + 1)); }
fail() { echo "  ❌ $1"; FAIL=$((FAIL + 1)); }

echo "🔍 Codecast Smoke Test"
echo "======================"

# --- Required binaries ---
echo ""
echo "Dependencies:"
for bin in unbuffer python3 curl; do
  if command -v "$bin" &>/dev/null; then
    pass "$bin found ($(command -v "$bin"))"
  else
    fail "$bin not found"
  fi
done

# --- Script permissions ---
echo ""
echo "Permissions:"
for script in "$SCRIPT_DIR/dev-relay.sh" "$SCRIPT_DIR/parse-stream.py"; do
  if [ -x "$script" ]; then
    pass "$(basename "$script") is executable"
  else
    fail "$(basename "$script") is not executable — run: chmod +x $script"
  fi
done

# --- Webhook URL ---
echo ""
echo "Webhook:"
WEBHOOK_FILE="$SCRIPT_DIR/.webhook-url"
if [ -f "$WEBHOOK_FILE" ]; then
  WEBHOOK_URL=$(cat "$WEBHOOK_FILE" | tr -d '\n')
  if [ -n "$WEBHOOK_URL" ]; then
    pass ".webhook-url file exists"
    # Validate webhook URL (GET returns 200 for valid Discord webhooks)
    HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" "$WEBHOOK_URL" 2>/dev/null)
    if [ "$HTTP_CODE" = "200" ]; then
      pass "Webhook URL is reachable (HTTP $HTTP_CODE)"
    else
      fail "Webhook URL returned HTTP $HTTP_CODE (expected 200)"
    fi
  else
    fail ".webhook-url file is empty"
  fi
else
  fail ".webhook-url file not found at $WEBHOOK_FILE"
fi

# --- Bot token (optional) ---
echo ""
echo "Bot token (optional):"
BOT_TOKEN="${CODECAST_BOT_TOKEN:-$(cat "$SCRIPT_DIR/.bot-token" 2>/dev/null | tr -d '\n')}"
if [ -n "$BOT_TOKEN" ]; then
  pass "Bot token found (needed for --thread mode)"
else
  echo "  ⚠️  No bot token — --thread mode will be unavailable"
  echo "     Set CODECAST_BOT_TOKEN env var or create $SCRIPT_DIR/.bot-token"
fi

# --- Python platform adapter ---
echo ""
echo "Platform adapter:"
if python3 -c "import sys; sys.path.insert(0,'$SCRIPT_DIR'); from platforms import get_platform; get_platform()" 2>/dev/null; then
  pass "Discord platform adapter loads"
else
  fail "Discord platform adapter failed to load"
fi

# --- Summary ---
echo ""
echo "======================"
TOTAL=$((PASS + FAIL))
echo "Results: $PASS/$TOTAL passed"
if [ "$FAIL" -gt 0 ]; then
  echo "⚠️  $FAIL check(s) failed — fix before running codecast"
  exit 1
else
  echo "✅ All checks passed — ready to stream!"
  exit 0
fi
