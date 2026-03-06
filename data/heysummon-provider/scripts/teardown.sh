#!/bin/bash
# HeySummon Provider — Stop the event watcher

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SKILL_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
NAME="heysummon-provider-watcher"

if command -v pm2 &>/dev/null; then
  pm2 delete "$NAME" 2>/dev/null
  pm2 save
  echo "✅ Watcher stopped and removed from pm2"
else
  PIDFILE="$SKILL_DIR/watcher.pid"
  if [ -f "$PIDFILE" ]; then
    PID=$(cat "$PIDFILE")
    if kill -0 "$PID" 2>/dev/null; then
      kill "$PID"
      echo "✅ Watcher stopped (PID: $PID)"
    else
      echo "⚠️ Process $PID was not running"
    fi
    rm -f "$PIDFILE"
  else
    echo "⚠️ No pidfile found — watcher may not be running"
  fi
fi
