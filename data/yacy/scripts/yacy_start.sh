#!/bin/bash
# YaCy Start Script
# Usage: yacy_start

YACY_DIR="${OPENCLAWSKILL_CONFIG_yacy_dir:-/home/q/.openclaw/workspace/yacy_search_server}"

if [ ! -d "$YACY_DIR" ]; then
  echo "Error: YaCy directory not found: $YACY_DIR"
  exit 1
fi

echo "Starting YaCy..."
cd "$YACY_DIR"
./startYACY.sh

# Give it a moment to start
sleep 3

# Check if it's responding
curl -s -o /dev/null -w "%{http_code}" http://localhost:8090 >/dev/null 2>&1
if [ $? -eq 0 ]; then
  echo "YaCy started. Access at: http://localhost:8090"
  echo "Default credentials: admin / yacy (change after login)"
else
  echo "YaCy start command issued, but service may still be initializing."
  echo "Check logs at: $YACY_DIR/DATA/LOG/yacy00.log"
fi
