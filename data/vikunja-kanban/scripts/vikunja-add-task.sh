#!/bin/bash
# Add a task to Vikunja kanban board
# Usage: vikunja-add-task.sh "title" "description" bucket_id [priority]
# Bucket IDs: 1=Urgent, 2=WaitingOn, 3=Done, 7=SystemIssues, 8=Active, 9=Upcoming, 10=Inbox
# Priority: 0=unset, 1=low, 2=medium, 3=high, 4=urgent

VIKUNJA_URL="https://kanban.pigpen.haus"
TOKEN="${VIKUNJA_TOKEN:?Set VIKUNJA_TOKEN env var}"
PROJECT_ID=1
VIEW_ID=4

TITLE="$1"
DESC="$2"
BUCKET_ID="${3:-10}"
PRIORITY="${4:-0}"

if [ -z "$TITLE" ]; then
  echo "Usage: $0 \"title\" \"description\" bucket_id [priority]"
  echo "Buckets: 1=Urgent 2=WaitingOn 3=Done 7=SystemIssues 8=Active 9=Upcoming 10=Inbox"
  exit 1
fi

# Create task
RESULT=$(curl -sk -X PUT "$VIKUNJA_URL/api/v1/projects/$PROJECT_ID/tasks" \
  -H "Authorization: Bearer $TOKEN" -H 'Content-Type: application/json' \
  -d "{\"title\":\"$TITLE\",\"description\":\"$DESC\",\"priority\":$PRIORITY}")

TASK_ID=$(echo "$RESULT" | grep -o '"id":[0-9]*' | head -1 | cut -d: -f2)

if [ -z "$TASK_ID" ]; then
  echo "ERROR: Failed to create task"
  echo "$RESULT"
  exit 1
fi

# Move to correct bucket (default bucket is 1/Urgent, so move if different)
if [ "$BUCKET_ID" != "1" ]; then
  curl -sk -X POST "$VIKUNJA_URL/api/v1/projects/$PROJECT_ID/views/$VIEW_ID/buckets/$BUCKET_ID/tasks" \
    -H "Authorization: Bearer $TOKEN" -H 'Content-Type: application/json' \
    -d "{\"task_id\":$TASK_ID}" > /dev/null 2>&1
fi

echo "Created task #$TASK_ID: $TITLE (bucket:$BUCKET_ID, priority:$PRIORITY)"
