#!/bin/bash
# HeySummon Consumer Watcher — Teardown
# Stops the Mercure response watcher.

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
NAME="heysummon-watcher"

if command -v pm2 &>/dev/null; then
  pm2 delete "$NAME" 2>/dev/null
  pm2 save
  echo "✅ Consumer watcher stopped and removed from pm2"
else
  PIDFILE="$SCRIPT_DIR/watcher.pid"
  if [ -f "$PIDFILE" ]; then
    PID=$(cat "$PIDFILE")
    if kill -0 "$PID" 2>/dev/null; then
      kill "$PID"
      echo "✅ Consumer watcher stopped (PID: $PID)"
    else
      echo "⚠️ Process $PID was not running"
    fi
    rm -f "$PIDFILE"
  else
    echo "⚠️ No pidfile found — watcher may not be running"
  fi
fi
