#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SHARE_SCRIPT="$SCRIPT_DIR/share-file.js"

FILE_PATH="${1:-}"
PORT="${2:-8888}"
HOURS="${3:-1}"

if [[ -z "$FILE_PATH" ]] || [[ ! -f "$FILE_PATH" ]]; then
    echo "Usage: $0 <file-path> [port=8888] [hours=1] [once]"
    exit 1
fi

# Max 24h
if [[ "$HOURS" -gt 24 ]]; then
    echo "⚠️  Max validity is 24h, capping at 24h"
    HOURS=24
fi

# Find next available port if default is in use
while lsof -i:"$PORT" >/dev/null 2>&1; do
    echo "⚠️  Port $PORT in use, trying $((PORT+1))"
    PORT=$((PORT+1))
done

# Start server in background
ONCE_ARG="${4:-}"
ONCE="0"
if [[ "$ONCE_ARG" == "once" || "$ONCE_ARG" == "1" || "$ONCE_ARG" == "true" ]]; then
    ONCE="1"
fi

node "$SHARE_SCRIPT" "$FILE_PATH" "$PORT" "$HOURS" "$ONCE" > /tmp/share-$PORT.log 2>&1 &
PID=$!

# Wait for server to start
sleep 1

# Extract link from log
if [[ -f /tmp/share-$PORT.log ]]; then
    LINK=$(grep "Link:" /tmp/share-$PORT.log | sed -E 's/^.*Link:[[:space:]]*//')
    FULL_PATH=$(realpath "$FILE_PATH")
    
    # Extract path relative to workspace
    WORKSPACE_PATH="${HOME}/.openclaw/workspace"
    REL_PATH="${FULL_PATH#$WORKSPACE_PATH/}"
    
    echo "📂 $REL_PATH"
    echo "🔗 $LINK"
    echo ""
    echo "Server PID: $PID | Stop: kill $PID"
else
    echo "❌ Failed to start share server (see /tmp/share-$PORT.log)"
    exit 1
fi
