#!/bin/bash
# Mark task as complete with verification
# Usage: ./complete-task.sh [task_id] "Notes"

DB_PATH="${HOME}/.openclaw/workspace/databases/tasks.db"
TASK_ID="${1:-1}"
NOTES="${2:-}"

[ -f "$DB_PATH" ] || exit 1

sqlite3 "$DB_PATH" "UPDATE tasks SET 
  status='completed', 
  completed_at=CURRENT_TIMESTAMP,
  last_updated=CURRENT_TIMESTAMP,
  notes='$(echo "$NOTES" | sed "s/'/''/g")'
WHERE id=$TASK_ID;"

echo "Task $TASK_ID completed"
