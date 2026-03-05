#!/bin/bash
# Check for stuck tasks (idle >30 min)
# Usage: ./stuck-check.sh

DB_PATH="${HOME}/.openclaw/workspace/databases/tasks.db"
[ -f "$DB_PATH" ] || exit 0

sqlite3 "$DB_PATH" "
SELECT id, request_text, status,
  CAST((julianday('now') - julianday(last_updated)) * 24 * 60 AS INTEGER) as minutes
FROM tasks 
WHERE status IN ('pending', 'in_progress') 
  AND last_updated < datetime('now', '-30 minutes')
ORDER BY priority ASC, created_at ASC
LIMIT 5;"
