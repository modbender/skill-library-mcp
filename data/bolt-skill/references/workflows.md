# Bolt Workflow Patterns

Common recipes for working with Bolt as an AI agent. All examples assume `BOLT_BASE_URL` and optionally `BOLT_API_TOKEN` are set.

---

## 1. Session Startup — Orient Yourself

At the start of a session, get a full picture of what's happening before doing anything.

```bash
# 1. Verify connection
curl -s "$BOLT_BASE_URL/health"

# 2. List projects
curl -s \
  ${BOLT_API_TOKEN:+-H "x-bolt-token: $BOLT_API_TOKEN"} \
  "$BOLT_BASE_URL/api/v1/projects"

# 3. Get active sprint and its digest
SPRINT_ID="sprint_abc123"
curl -s \
  ${BOLT_API_TOKEN:+-H "x-bolt-token: $BOLT_API_TOKEN"} \
  "$BOLT_BASE_URL/api/v1/digests/sprint/$SPRINT_ID"

# 4. List all in-progress stories
curl -s \
  ${BOLT_API_TOKEN:+-H "x-bolt-token: $BOLT_API_TOKEN"} \
  "$BOLT_BASE_URL/api/v1/stories?sprintId=$SPRINT_ID&status=in_progress&fields=id,title,blocked,assignee,priority"
```

---

## 2. Sprint Planning — Create and Populate a Sprint

```bash
PROJECT_ID="proj_abc123"

# 1. Create the sprint
SPRINT=$(curl -s -X POST \
  -H "Content-Type: application/json" \
  ${BOLT_API_TOKEN:+-H "x-bolt-token: $BOLT_API_TOKEN"} \
  -H "Idempotency-Key: $(uuidgen)" \
  -d '{
    "name": "Sprint 3",
    "goal": "Ship user authentication and onboarding",
    "startAt": "2024-02-01T00:00:00Z",
    "endAt": "2024-02-14T00:00:00Z"
  }' \
  "$BOLT_BASE_URL/api/v1/projects/$PROJECT_ID/sprints")
SPRINT_ID=$(echo $SPRINT | jq -r '.id')

# 2. Create stories for the sprint
curl -s -X POST \
  -H "Content-Type: application/json" \
  ${BOLT_API_TOKEN:+-H "x-bolt-token: $BOLT_API_TOKEN"} \
  -H "Idempotency-Key: $(uuidgen)" \
  -d '{
    "title": "Implement JWT authentication",
    "projectId": "'"$PROJECT_ID"'",
    "sprintId": "'"$SPRINT_ID"'",
    "description": "Add JWT-based auth to the API",
    "acceptanceCriteria": "Given a valid user, when they POST /auth/login, then they receive a signed JWT",
    "priority": "high",
    "points": 5,
    "assignee": "Alice"
  }' \
  "$BOLT_BASE_URL/api/v1/stories"

# 3. Start the sprint when ready
curl -s -X POST \
  ${BOLT_API_TOKEN:+-H "x-bolt-token: $BOLT_API_TOKEN"} \
  "$BOLT_BASE_URL/api/v1/sprints/$SPRINT_ID/start"
```

---

## 3. Picking Up a Story — Start Work

When you pick up a story to implement:

```bash
STORY_ID="story_abc123"

# 1. Move story to in_progress
curl -s -X POST \
  -H "Content-Type: application/json" \
  ${BOLT_API_TOKEN:+-H "x-bolt-token: $BOLT_API_TOKEN"} \
  -H "Idempotency-Key: $(uuidgen)" \
  -d '{"status": "in_progress"}' \
  "$BOLT_BASE_URL/api/v1/stories/$STORY_ID/move"

# 2. Log that the AI session has started
SESSION_ID="session_abc123"
curl -s -X POST \
  -H "Content-Type: application/json" \
  ${BOLT_API_TOKEN:+-H "x-bolt-token: $BOLT_API_TOKEN"} \
  -H "Idempotency-Key: $(uuidgen)" \
  -d '{
    "message": "Starting implementation of '"$STORY_ID"': analyzing codebase",
    "type": "action"
  }' \
  "$BOLT_BASE_URL/api/v1/agent/sessions/$SESSION_ID/events"
```

---

## 4. Completing a Story

When you finish implementing a story:

```bash
STORY_ID="story_abc123"

# 1. Add a completion note
curl -s -X POST \
  -H "Content-Type: application/json" \
  ${BOLT_API_TOKEN:+-H "x-bolt-token: $BOLT_API_TOKEN"} \
  -H "Idempotency-Key: $(uuidgen)" \
  -d '{
    "body": "Implemented JWT auth. Added /auth/login and /auth/refresh endpoints. PR #42 opened.",
    "author": "AI",
    "kind": "update"
  }' \
  "$BOLT_BASE_URL/api/v1/stories/$STORY_ID/notes"

# 2. Move to completed
curl -s -X POST \
  -H "Content-Type: application/json" \
  ${BOLT_API_TOKEN:+-H "x-bolt-token: $BOLT_API_TOKEN"} \
  -H "Idempotency-Key: $(uuidgen)" \
  -d '{"status": "completed"}' \
  "$BOLT_BASE_URL/api/v1/stories/$STORY_ID/move"
```

---

## 5. Marking a Blocker

When a story is blocked and you need to escalate:

```bash
STORY_ID="story_abc123"

# 1. Mark the story as blocked and note why
curl -s -X PATCH \
  -H "Content-Type: application/json" \
  ${BOLT_API_TOKEN:+-H "x-bolt-token: $BOLT_API_TOKEN"} \
  -H "Idempotency-Key: $(uuidgen)" \
  -d '{"blocked": true}' \
  "$BOLT_BASE_URL/api/v1/stories/$STORY_ID"

# 2. Add a blocker note
curl -s -X POST \
  -H "Content-Type: application/json" \
  ${BOLT_API_TOKEN:+-H "x-bolt-token: $BOLT_API_TOKEN"} \
  -H "Idempotency-Key: $(uuidgen)" \
  -d '{
    "body": "Blocked: waiting for the database migration to be approved before proceeding",
    "author": "AI",
    "kind": "note"
  }' \
  "$BOLT_BASE_URL/api/v1/stories/$STORY_ID/notes"

# 3. Add a dependency if this story is blocked by another
curl -s -X POST \
  -H "Content-Type: application/json" \
  ${BOLT_API_TOKEN:+-H "x-bolt-token: $BOLT_API_TOKEN"} \
  -H "Idempotency-Key: $(uuidgen)" \
  -d '{
    "dependsOnStoryId": "story_blocking_id",
    "type": "blocks"
  }' \
  "$BOLT_BASE_URL/api/v1/stories/$STORY_ID/dependencies"
```

---

## 6. Daily Standup Digest

Get a quick summary at the start of each day:

```bash
PROJECT_ID="proj_abc123"
SPRINT_ID="sprint_abc123"

# Full sprint digest: counts, blockers, by-assignee
curl -s \
  ${BOLT_API_TOKEN:+-H "x-bolt-token: $BOLT_API_TOKEN"} \
  "$BOLT_BASE_URL/api/v1/digests/sprint/$SPRINT_ID"

# Daily project snapshot (last 24 hours)
curl -s \
  ${BOLT_API_TOKEN:+-H "x-bolt-token: $BOLT_API_TOKEN"} \
  "$BOLT_BASE_URL/api/v1/digests/project/$PROJECT_ID/daily"

# All blocked stories
curl -s \
  ${BOLT_API_TOKEN:+-H "x-bolt-token: $BOLT_API_TOKEN"} \
  "$BOLT_BASE_URL/api/v1/stories?sprintId=$SPRINT_ID&blocked=true&fields=id,title,assignee,priority"
```

---

## 7. Bulk Story Updates (Batch Operations)

Efficiently update multiple stories at once:

```bash
# Close out all completed stories in one call
curl -s -X POST \
  -H "Content-Type: application/json" \
  ${BOLT_API_TOKEN:+-H "x-bolt-token: $BOLT_API_TOKEN"} \
  -H "Idempotency-Key: $(uuidgen)" \
  -d '{
    "items": [
      {"id": "story_1", "status": "completed"},
      {"id": "story_2", "status": "completed"},
      {"id": "story_3", "status": "completed"}
    ],
    "all_or_nothing": false
  }' \
  "$BOLT_BASE_URL/api/v1/stories/batch/move"

# Reassign a set of stories to a new sprint
curl -s -X POST \
  -H "Content-Type: application/json" \
  ${BOLT_API_TOKEN:+-H "x-bolt-token: $BOLT_API_TOKEN"} \
  -H "Idempotency-Key: $(uuidgen)" \
  -d '{
    "items": [
      {"id": "story_4", "patch": {"sprintId": "sprint_next"}},
      {"id": "story_5", "patch": {"sprintId": "sprint_next"}}
    ]
  }' \
  "$BOLT_BASE_URL/api/v1/stories/batch/patch"
```

---

## 8. Polling for Changes (Delta Sync)

Efficiently sync only what changed since your last check:

```bash
LAST_SYNC="2024-01-10T09:00:00Z"

# Get only stories updated since last sync
curl -s \
  ${BOLT_API_TOKEN:+-H "x-bolt-token: $BOLT_API_TOKEN"} \
  "$BOLT_BASE_URL/api/v1/stories?updated_since=$LAST_SYNC&fields=id,title,status,blocked,updatedAt"

# Get audit log since last sync
curl -s \
  ${BOLT_API_TOKEN:+-H "x-bolt-token: $BOLT_API_TOKEN"} \
  "$BOLT_BASE_URL/api/v1/audit?since=$LAST_SYNC&projectId=$PROJECT_ID"
```

---

## 9. Handling Pagination

When a response has `page.hasMore: true`, fetch the next page:

```bash
# First page
RESPONSE=$(curl -s \
  ${BOLT_API_TOKEN:+-H "x-bolt-token: $BOLT_API_TOKEN"} \
  "$BOLT_BASE_URL/api/v1/stories?sprintId=$SPRINT_ID&limit=100")

# Extract cursor
CURSOR=$(echo $RESPONSE | jq -r '.page.nextCursor')
HAS_MORE=$(echo $RESPONSE | jq -r '.page.hasMore')

# Next page (if hasMore is true)
if [ "$HAS_MORE" = "true" ]; then
  curl -s \
    ${BOLT_API_TOKEN:+-H "x-bolt-token: $BOLT_API_TOKEN"} \
    "$BOLT_BASE_URL/api/v1/stories?sprintId=$SPRINT_ID&limit=100&cursor=$CURSOR"
fi
```

---

## 10. Closing a Sprint

When a sprint is done:

```bash
SPRINT_ID="sprint_abc123"

# 1. Check what's not done yet
curl -s \
  ${BOLT_API_TOKEN:+-H "x-bolt-token: $BOLT_API_TOKEN"} \
  "$BOLT_BASE_URL/api/v1/stories?sprintId=$SPRINT_ID&status=waiting&fields=id,title,priority"

curl -s \
  ${BOLT_API_TOKEN:+-H "x-bolt-token: $BOLT_API_TOKEN"} \
  "$BOLT_BASE_URL/api/v1/stories?sprintId=$SPRINT_ID&status=in_progress&fields=id,title,priority"

# 2. Get final digest
curl -s \
  ${BOLT_API_TOKEN:+-H "x-bolt-token: $BOLT_API_TOKEN"} \
  "$BOLT_BASE_URL/api/v1/digests/sprint/$SPRINT_ID"

# 3. Close the sprint (irreversible)
curl -s -X POST \
  ${BOLT_API_TOKEN:+-H "x-bolt-token: $BOLT_API_TOKEN"} \
  "$BOLT_BASE_URL/api/v1/sprints/$SPRINT_ID/close"
```

---

## Tips

- **Use `fields` projection** on list endpoints to fetch only what you need — this reduces payload size and LLM token consumption.
- **Use `Idempotency-Key`** on all write operations so you can safely retry on network errors without creating duplicates.
- **Use `dry_run: true`** on batch operations to preview the outcome before committing.
- **Use delta sync** (`updated_since`) instead of full fetches when polling for changes.
- **Log agent events** liberally — it makes your activity visible to human collaborators in the Bolt UI.
