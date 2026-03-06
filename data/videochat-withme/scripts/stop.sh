#!/bin/bash
# Stop videochat-withme service
set -e

PLIST_LABEL="com.openclaw.videochat-withme"
PORT=${PORT:-8766}

# If launchd service is installed, use it
if launchctl list "$PLIST_LABEL" >/dev/null 2>&1; then
  launchctl stop "$PLIST_LABEL"
  echo "✅ Stopped via launchd"
  exit 0
fi

# Fallback: kill by port
PID=$(lsof -ti:$PORT 2>/dev/null || true)
if [ -n "$PID" ]; then
  kill "$PID" 2>/dev/null
  echo "✅ Stopped (PID $PID)"
else
  echo "ℹ️  Not running"
fi
