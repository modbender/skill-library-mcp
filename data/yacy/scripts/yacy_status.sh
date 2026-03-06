#!/bin/bash
# YaCy Status Script
# Usage: yacy_status

YACY_DIR="${OPENCLAWSKILL_CONFIG_yacy_dir:-/home/q/.openclaw/workspace/yacy_search_server}"
PORT="${OPENCLAWSKILL_CONFIG_port:-8090}"

if [ ! -d "$YACY_DIR" ]; then
  echo "Status: YaCy directory not found: $YACY_DIR"
  echo "Configure yacy_dir in skill settings or install YaCy."
  exit 1
fi

# Check if process is running
if pgrep -f "yacy" > /dev/null; then
  echo "Process: running"
else
  echo "Process: not running"
  echo "To start: openclaw skill yacy yacy_start"
  exit 0
fi

# Check if port is responding
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" "http://localhost:$PORT" 2>/dev/null || echo "000")

if [ "$HTTP_CODE" = "200" ]; then
  echo "HTTP: responding on port $PORT (200 OK)"
  echo "URL: http://localhost:$PORT"
else
  echo "HTTP: not responding (code: $HTTP_CODE)"
fi

# Check log file for recent activity
LOG_FILE="$YACY_DIR/DATA/LOG/yacy00.log"
if [ -f "$LOG_FILE" ]; then
  RECENT=$(tail -n 3 "$LOG_FILE" 2>/dev/null || echo "No logs")
  echo "Recent log:"
  echo "$RECENT"
else
  echo "Log file not found: $LOG_FILE"
fi
