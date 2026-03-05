#!/bin/bash
# Task system CLI

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DB_PATH="${HOME}/.openclaw/workspace/databases/tasks.db"

case "$1" in
  create)
    REQUEST="${2:-Task}"
    TASK_ID=$(sqlite3 "$DB_PATH" "INSERT INTO tasks (request_text, status, priority, last_updated, started_at) VALUES ('$(echo \"$REQUEST\" | sed "s/'/''/g")', 'in_progress', 5, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP); SELECT last_insert_rowid();")
    echo "Task #$TASK_ID created: $REQUEST"
    ;;
  heartbeat|update)
    TASK_ID="${2:-1}"
    sqlite3 "$DB_PATH" "UPDATE tasks SET last_updated=CURRENT_TIMESTAMP WHERE id=$TASK_ID;"
    echo "Task #$TASK_ID heartbeat updated"
    ;;
  complete|done)
    TASK_ID="${2:-1}"
    NOTES="${3:-}"
    sqlite3 "$DB_PATH" "UPDATE tasks SET status='completed', completed_at=CURRENT_TIMESTAMP, last_updated=CURRENT_TIMESTAMP, notes='$(echo \"$NOTES\" | sed "s/'/''/g")' WHERE id=$TASK_ID;"
    echo "Task #$TASK_ID completed"
    ;;
  stuck)
    sqlite3 "$DB_PATH" "SELECT id, request_text, CAST((julianday('now') - julianday(last_updated)) * 24 * 60 AS INTEGER) as minutes FROM tasks WHERE status IN ('pending', 'in_progress') AND last_updated < datetime('now', '-30 minutes') ORDER BY priority ASC, created_at;"
    ;;
  status|list)
    echo "=== Active Tasks ==="
    sqlite3 "$DB_PATH" "SELECT id, status, substr(request_text, 1, 50), last_updated FROM tasks WHERE status != 'completed' ORDER BY priority ASC, created_at;"
    echo ""
    echo "=== Today's Summary ==="
    sqlite3 "$DB_PATH" "SELECT status, COUNT(*) FROM tasks WHERE date(created_at) = date('now') GROUP BY status;"
    ;;
  *)
    echo "Usage: task-system {create|heartbeat|complete|stuck|status} [args]"
    echo "  create 'request text'     - Create new task"
    echo "  heartbeat [id]           - Update heartbeat"
    echo "  complete [id] [notes]    - Mark complete"
    echo "  stuck                    - Check stuck tasks"
    echo "  status                   - List active + summary"
    ;;
esac
