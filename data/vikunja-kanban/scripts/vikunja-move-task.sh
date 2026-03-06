#!/bin/bash
# Move a task to a different bucket
# Usage: vikunja-move-task.sh TASK_ID BUCKET_ID

VIKUNJA_URL="https://kanban.pigpen.haus"
TOKEN="${VIKUNJA_TOKEN:?Set VIKUNJA_TOKEN env var}"
PROJECT_ID=1
VIEW_ID=4

TASK_ID="$1"
BUCKET_ID="$2"

if [ -z "$TASK_ID" ] || [ -z "$BUCKET_ID" ]; then
  echo "Usage: $0 TASK_ID BUCKET_ID"
  echo "Buckets: 1=Urgent 2=WaitingOn 3=Done 7=SystemIssues 8=Active 9=Upcoming 10=Inbox"
  exit 1
fi

curl -sk -X POST "$VIKUNJA_URL/api/v1/projects/$PROJECT_ID/views/$VIEW_ID/buckets/$BUCKET_ID/tasks" \
  -H "Authorization: Bearer $TOKEN" -H 'Content-Type: application/json' \
  -d "{\"task_id\":$TASK_ID}" > /dev/null 2>&1

echo "Moved task #$TASK_ID to bucket $BUCKET_ID"
