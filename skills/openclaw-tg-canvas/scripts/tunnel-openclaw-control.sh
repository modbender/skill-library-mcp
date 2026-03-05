#!/usr/bin/env bash
set -euo pipefail

# Expose local OpenClaw Control UI (127.0.0.1:18789) via Cloudflare quick tunnel.
# WARNING: This creates a public URL. Treat it as sensitive.

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"
mkdir -p logs

if ! command -v cloudflared >/dev/null 2>&1; then
  echo "cloudflared not found. Install it first." >&2
  exit 1
fi

LOG="logs/cloudflared-control.log"
PIDFILE="logs/cloudflared-control.pid"
: > "$LOG"

nohup cloudflared tunnel --url http://127.0.0.1:18789 >>"$LOG" 2>&1 &
PID=$!
echo "$PID" > "$PIDFILE"

for i in {1..60}; do
  URL=$(grep -Eo 'https://[-a-zA-Z0-9]+\.trycloudflare\.com' "$LOG" | tail -n1 || true)
  if [[ -n "$URL" ]]; then
    echo "OpenClaw Control tunnel started"
    echo "PID: $PID"
    echo "URL: $URL"
    exit 0
  fi
  sleep 1
  if ! kill -0 "$PID" >/dev/null 2>&1; then
    echo "cloudflared exited early. Check $LOG" >&2
    tail -n 40 "$LOG" >&2
    exit 1
  fi
done

echo "Timed out waiting for tunnel URL. Check $LOG" >&2
exit 1
