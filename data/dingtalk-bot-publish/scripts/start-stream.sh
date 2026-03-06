#!/bin/bash
# Start DingTalk stream bridge
cd "$(dirname "$0")/.."
source .env
python scripts/stream-bridge.py &
echo "DingTalk stream bridge started"