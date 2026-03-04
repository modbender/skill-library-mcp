#!/bin/bash
CLAWNET_DIR="$(cd "$(dirname "$0")" && pwd)"
CONFIG="$CLAWNET_DIR/config.json"
POLL="$CLAWNET_DIR/poll.py"
PID_FILE="$CLAWNET_DIR/.poll.pid"

# 1. Poller check (uses PID file, not pgrep — avoids false matches)
if [ ! -f "$POLL" ]; then exit 1; fi
ALIVE=false
if [ -f "$PID_FILE" ]; then
  PID=$(cat "$PID_FILE")
  if kill -0 "$PID" 2>/dev/null; then ALIVE=true; fi
fi
if [ "$ALIVE" = false ]; then
  python3 "$POLL" &
  echo "POLLER_RESTARTED"
else
  echo "POLLER_OK"
fi

# 2. Social dedup check
SOCIAL=$(python3 -c "import json; print(json.load(open('$CONFIG')).get('social', True))" 2>/dev/null)
if [ "$SOCIAL" = "False" ]; then echo "SOCIAL_OFF"; exit 2; fi

INTERVAL=$(python3 -c "import json; print(json.load(open('$CONFIG')).get('social_interval_minutes', 360))" 2>/dev/null)
LAST_RUN="$CLAWNET_DIR/.last_social_run"
if [ -f "$LAST_RUN" ]; then
  LAST=$(cat "$LAST_RUN")
  NOW=$(date +%s)
  ELAPSED=$(( (NOW - LAST) / 60 ))
  if [ "$ELAPSED" -lt "$INTERVAL" ]; then echo "SOCIAL_RECENT"; exit 2; fi
fi

echo "SOCIAL_DUE"
exit 0
