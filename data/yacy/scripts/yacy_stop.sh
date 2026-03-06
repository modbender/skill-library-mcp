#!/bin/bash
# YaCy Stop Script
# Usage: yacy_stop

YACY_DIR="${OPENCLAWSKILL_CONFIG_yacy_dir:-/home/q/.openclaw/workspace/yacy_search_server}"

if [ ! -d "$YACY_DIR" ]; then
  echo "Error: YaCy directory not found: $YACY_DIR"
  exit 1
fi

echo "Stopping YaCy..."
cd "$YACY_DIR"
./stopYACY.sh
echo "YaCy stopped."
