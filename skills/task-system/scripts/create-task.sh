#!/bin/bash
# Create new task entry
# Usage: ./create-task.sh "Your request here"

DB_PATH="${HOME}/.openclaw/workspace/databases/tasks.db"
REQUEST="${1:-Task}"

# Ensure database and table exist
mkdir -p "$(dirname "$DB_PATH")"
sqlite3 "$DB_PATH" "CREATE TABLE IF NOT EXISTS tasks (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  request_text TEXT NOT NULL,
  status TEXT DEFAULT 'pending',
  priority INTEGER DEFAULT 5,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  started_at DATETIME,
  completed_at DATETIME,
  last_updated DATETIME DEFAULT CURRENT_TIMESTAMP,
  notes TEXT
);"

# Create task
TASK_ID=$(sqlite3 "$DB_PATH" "
  INSERT INTO tasks (request_text, status, priority, last_updated, started_at) 
  VALUES ('$(echo "$REQUEST" | sed "s/'/''/g")', 'in_progress', 5, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP);
  SELECT last_insert_rowid();
")

echo "$TASK_ID"
