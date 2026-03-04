#!/bin/bash
# HeySummon Provider — Start the event watcher
# Uses pm2 if available, otherwise nohup.

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SKILL_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
[ -f "$SKILL_DIR/.env" ] && set -a && source "$SKILL_DIR/.env" && set +a

WATCHER="$SCRIPT_DIR/mercure-watcher.sh"
NAME="heysummon-provider-watcher"

if ! [ -f "$WATCHER" ]; then
  echo "❌ Watcher script not found" >&2
  exit 1
fi

# Validate required env vars
if [ -z "$HEYSUMMON_BASE_URL" ]; then
  echo "❌ HEYSUMMON_BASE_URL is required in .env" >&2
  exit 1
fi
if [ -z "$HEYSUMMON_API_KEY" ]; then
  echo "❌ HEYSUMMON_API_KEY is required in .env" >&2
  exit 1
fi
if [ -z "$HEYSUMMON_NOTIFY_TARGET" ]; then
  echo "❌ HEYSUMMON_NOTIFY_TARGET is required in .env (e.g. your Telegram chat ID)" >&2
  exit 1
fi

chmod +x "$WATCHER"

if command -v pm2 &>/dev/null; then
  pm2 delete "$NAME" 2>/dev/null
  pm2 start "$WATCHER" --name "$NAME" --interpreter bash
  pm2 save
  echo "✅ Watcher started via pm2 (name: $NAME)"
else
  LOGFILE="$SKILL_DIR/watcher.log"
  PIDFILE="$SKILL_DIR/watcher.pid"

  if [ -f "$PIDFILE" ] && kill -0 "$(cat "$PIDFILE")" 2>/dev/null; then
    kill "$(cat "$PIDFILE")" 2>/dev/null
  fi

  nohup bash "$WATCHER" >> "$LOGFILE" 2>&1 &
  echo $! > "$PIDFILE"
  echo "✅ Watcher started via nohup (PID: $(cat "$PIDFILE"), log: $LOGFILE)"
fi
