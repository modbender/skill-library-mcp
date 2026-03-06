#!/bin/bash
# test-smoke.sh — Validate Codeflow prerequisites and configuration
#
# Usage: ./test-smoke.sh [-P discord|telegram] [--tg-chat <id>]

set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
PY_DIR="$(cd "$SCRIPT_DIR/../py" && pwd)"
PASS=0
FAIL=0
PLATFORM="discord"
TG_CHAT_ID=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    -P) PLATFORM="$2"; shift 2 ;;
    --tg-chat) TG_CHAT_ID="$2"; shift 2 ;;
    *) echo "Unknown option: $1" >&2; exit 1 ;;
  esac
done

pass() { echo "  ✅ $1"; PASS=$((PASS + 1)); }
fail() { echo "  ❌ $1"; FAIL=$((FAIL + 1)); }

echo "🔍 Codeflow Smoke Test"
echo "======================"
echo "Platform: $PLATFORM"

# --- Required binaries ---
echo ""
echo "Dependencies:"
for bin in python3; do
  if command -v "$bin" &>/dev/null; then
    pass "$bin found ($(command -v "$bin"))"
  else
    fail "$bin not found"
  fi
done

echo ""
echo "Python version:"
if PYTHONPATH="$PY_DIR${PYTHONPATH:+:$PYTHONPATH}" python3 -c 'from py_compat import require_python310; require_python310(prog="codeflow")'; then
  pass "python3 is >= 3.10"
else
  fail "python3 is < 3.10 (requires >= 3.10)"
fi

# unbuffer only required for Claude streaming runs; still useful to have
if command -v unbuffer &>/dev/null; then
  pass "unbuffer found ($(command -v unbuffer))"
else
  echo "  ⚠️  unbuffer not found (required for Claude stream-json sessions)"
fi

# --- Script permissions ---
echo ""
echo "Permissions:"
for script in "$SCRIPT_DIR/dev-relay.sh" "$PY_DIR/parse-stream.py"; do
  if [ -x "$script" ]; then
    pass "$(basename "$script") is executable"
  else
    fail "$(basename "$script") is not executable — run: chmod +x $script"
  fi
done

if [ "$PLATFORM" = "discord" ]; then
  echo ""
  echo "Webhook:"
  WEBHOOK_FILE="$ROOT_DIR/.webhook-url"
  if [ -f "$WEBHOOK_FILE" ]; then
    WEBHOOK_URL=$(cat "$WEBHOOK_FILE" | tr -d '\n')
    if [ -n "$WEBHOOK_URL" ]; then
      pass ".webhook-url file exists"
      if WEBHOOK_URL="$WEBHOOK_URL" python3 -c '
import os, sys, urllib.request
url = (os.environ.get("WEBHOOK_URL") or "").strip()
if not url:
    raise SystemExit(1)
try:
    with urllib.request.urlopen(url, timeout=10) as resp:
        code = getattr(resp, "status", None) or resp.getcode()
    raise SystemExit(0 if int(code) == 200 else 1)
except Exception:
    raise SystemExit(1)
' 2>/dev/null; then
        pass "Webhook URL is reachable (HTTP 200)"
      else
        fail "Webhook URL is unreachable/invalid (expected HTTP 200)"
      fi
    else
      fail ".webhook-url file is empty"
    fi
  else
    fail ".webhook-url file not found at $WEBHOOK_FILE"
  fi

  echo ""
  echo "Bot token (optional):"
  BOT_TOKEN="${CODEFLOW_BOT_TOKEN:-$(cat "$ROOT_DIR/.bot-token" 2>/dev/null | tr -d '\n')}"
  if [ -n "$BOT_TOKEN" ]; then
    pass "Bot token found (needed for --thread mode)"
  else
    echo "  ⚠️  No bot token — --thread mode will be unavailable"
    echo "     Set CODEFLOW_BOT_TOKEN env var or create $ROOT_DIR/.bot-token"
  fi
else
  echo ""
  echo "Telegram:"
  TELEGRAM_BOT_TOKEN="${TELEGRAM_BOT_TOKEN:-}"
  if [ -z "$TELEGRAM_BOT_TOKEN" ]; then
    TELEGRAM_BOT_TOKEN=$(python3 - <<'PY'
import json, os
from pathlib import Path
p = Path(os.environ.get('OPENCLAW_CONFIG_PATH','~/.openclaw/openclaw.json')).expanduser()
try:
    d = json.loads(p.read_text(encoding='utf-8'))
    print((((d.get('channels') or {}).get('telegram') or {}).get('botToken') or '').strip())
except Exception:
    print('')
PY
)
  fi

  if [ -n "$TELEGRAM_BOT_TOKEN" ]; then
    pass "Telegram bot token found"
    if TELEGRAM_BOT_TOKEN="$TELEGRAM_BOT_TOKEN" python3 -c '
import json, os, sys, urllib.request
tok = (os.environ.get("TELEGRAM_BOT_TOKEN") or "").strip()
if not tok:
    raise SystemExit(1)
url = f"https://api.telegram.org/bot{tok}/getMe"
try:
    with urllib.request.urlopen(url, timeout=10) as resp:
        raw = resp.read().decode("utf-8", errors="replace")
    data = json.loads(raw)
    ok = isinstance(data, dict) and data.get("ok") is True
    raise SystemExit(0 if ok else 1)
except Exception:
    raise SystemExit(1)
' 2>/dev/null; then
      pass "Telegram bot token validated via getMe"
    else
      fail "Telegram getMe failed (token/network issue)"
    fi
  else
    fail "Telegram bot token missing"
  fi

  CHAT_ID="${TG_CHAT_ID:-${CODEFLOW_TELEGRAM_CHAT_ID:-${TELEGRAM_CHAT_ID:-}}}"
  if [ -n "$CHAT_ID" ]; then
    pass "Telegram chat id available ($CHAT_ID)"
  else
    fail "Telegram chat id missing — use --tg-chat <id> or CODEFLOW_TELEGRAM_CHAT_ID"
  fi
fi

# --- Python platform adapter ---
echo ""
echo "Platform adapter:"
if python3 -c "import sys,os; sys.path.insert(0,'$PY_DIR'); from platforms import get_platform; get_platform('$PLATFORM')" 2>/dev/null; then
  pass "$PLATFORM platform adapter loads"
else
  fail "$PLATFORM platform adapter failed to load"
fi

# --- Summary ---
echo ""
echo "======================"
TOTAL=$((PASS + FAIL))
echo "Results: $PASS/$TOTAL passed"
if [ "$FAIL" -gt 0 ]; then
  echo "⚠️  $FAIL check(s) failed — fix before running Codeflow"
  exit 1
else
  echo "✅ All checks passed — ready to stream!"
  exit 0
fi
