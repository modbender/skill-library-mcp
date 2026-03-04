#!/bin/bash
# Update task heartbeat
# Usage: ./heartbeat.sh [task_id]

DB_PATH="${HOME}/.openclaw/workspace/databases/tasks.db"
TASK_ID="${1:-1}"

[ -f "$DB_PATH" ] || exit 1

sqlite3 "$DB_PATH" "UPDATE tasks SET last_updated=CURRENT_TIMESTAMP WHERE id=$TASK_ID;"
echo "Task $TASK_ID updated"
