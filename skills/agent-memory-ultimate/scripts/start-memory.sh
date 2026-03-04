#!/bin/bash
# Start the cognitive memory embedding server if not already running
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SERVER="$SCRIPT_DIR/embed_server.py"

if python3 "$SERVER" --status 2>/dev/null | grep -q RUNNING; then
    echo "Embedding server already running"
else
    echo "Starting embedding server..."
    nohup python3 "$SERVER" > /tmp/embed-server.log 2>&1 &
    sleep 6
    python3 "$SERVER" --status
fi
