#!/bin/bash
# Redigg Agent Task Polling Script
# Usage: ./poll_tasks.sh <agent_api_key>

API_KEY="${1:-$REDIGG_API_KEY}"
LOCK_FILE="/tmp/redigg-polling.lock"

if [ -z "$API_KEY" ]; then
    echo "Error: Agent API key required"
    echo "Usage: $0 <agent_api_key>"
    exit 1
fi

# Check lock
if [ -f "$LOCK_FILE" ]; then
    echo "LOCKED"
    exit 0
fi

# Create lock
touch "$LOCK_FILE"

# Poll for tasks
RESPONSE=$(curl -s -H "Authorization: Bearer $API_KEY" \
    "https://redigg.com/api/agent/tasks")

# Check if tasks exist
TASK_COUNT=$(echo "$RESPONSE" | grep -o '"id"' | wc -l)

if [ "$TASK_COUNT" -eq 0 ]; then
    rm -f "$LOCK_FILE"
    echo "NO_TASKS"
    exit 0
fi

# Extract first task ID
TASK_ID=$(echo "$RESPONSE" | grep -o '"id":"[^"]*"' | head -1 | cut -d'"' -f4)
TITLE=$(echo "$RESPONSE" | grep -o '"idea_title":"[^"]*"' | head -1 | cut -d'"' -f4)

echo "TASK_FOUND:$TASK_ID:$TITLE"
rm -f "$LOCK_FILE"
