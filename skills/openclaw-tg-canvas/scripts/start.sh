#!/usr/bin/env bash
set -euo pipefail

if [[ -z "${BOT_TOKEN:-}" ]]; then
  echo "Missing BOT_TOKEN" >&2
  exit 1
fi
if [[ -z "${ALLOWED_USER_IDS:-}" ]]; then
  echo "Missing ALLOWED_USER_IDS" >&2
  exit 1
fi
if [[ -z "${PUSH_TOKEN:-}" ]]; then
  echo "Missing PUSH_TOKEN — required when using cloudflared (loopback check alone is not sufficient)." >&2
  echo "Generate one with: openssl rand -hex 32" >&2
  exit 1
fi

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

if [[ ! -d node_modules ]]; then
  echo "Installing dependencies..."
  npm install
fi

mkdir -p logs
SERVER_LOG="logs/server.log"

# Start server
node server.js >>"$SERVER_LOG" 2>&1 &
SERVER_PID=$!

echo "Server started (pid $SERVER_PID)."

# Start cloudflared and capture URL
CF_LOG="logs/cloudflared.log"
: > "$CF_LOG"

cloudflared tunnel --url http://localhost:3721 2>&1 | tee -a "$CF_LOG" &
CF_PID=$!

TUNNEL_URL=""
for i in {1..60}; do
  if grep -Eo 'https://[-a-zA-Z0-9]+\.trycloudflare\.com' "$CF_LOG" >/dev/null 2>&1; then
    TUNNEL_URL=$(grep -Eo 'https://[-a-zA-Z0-9]+\.trycloudflare\.com' "$CF_LOG" | tail -n1)
    break
  fi
  sleep 1
  # If cloudflared crashed, bail out
  if ! kill -0 "$CF_PID" >/dev/null 2>&1; then
    echo "cloudflared exited early. Check $CF_LOG" >&2
    exit 1
  fi
done

if [[ -z "$TUNNEL_URL" ]]; then
  echo "Failed to detect Cloudflare tunnel URL. Check $CF_LOG" >&2
  exit 1
fi

echo "Mini App URL: $TUNNEL_URL"
echo "Run: BOT_TOKEN=... MINIAPP_URL=$TUNNEL_URL node scripts/setup-bot.js"

echo "Tailing server logs ($SERVER_LOG). Press Ctrl+C to stop." 
tail -f "$SERVER_LOG"
