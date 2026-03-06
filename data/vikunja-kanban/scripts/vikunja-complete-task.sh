#!/bin/bash
# Mark a task as done and move to Done bucket
# Usage: vikunja-complete-task.sh TASK_ID

VIKUNJA_URL="https://kanban.pigpen.haus"
TOKEN="${VIKUNJA_TOKEN:?Set VIKUNJA_TOKEN env var}"
PROJECT_ID=1
VIEW_ID=4
DONE_BUCKET=3

TASK_ID="$1"

if [ -z "$TASK_ID" ]; then
  echo "Usage: $0 TASK_ID"
  exit 1
fi

# Mark as done
curl -sk -X POST "$VIKUNJA_URL/api/v1/tasks/$TASK_ID" \
  -H "Authorization: Bearer $TOKEN" -H 'Content-Type: application/json' \
  -d '{"done":true}' > /dev/null 2>&1

# Move to Done bucket
curl -sk -X POST "$VIKUNJA_URL/api/v1/projects/$PROJECT_ID/views/$VIEW_ID/buckets/$DONE_BUCKET/tasks" \
  -H "Authorization: Bearer $TOKEN" -H 'Content-Type: application/json' \
  -d "{\"task_id\":$TASK_ID}" > /dev/null 2>&1

echo "Completed task #$TASK_ID"
