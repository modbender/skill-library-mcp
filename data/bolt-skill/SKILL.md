---
name: bolt-sprint
description: Manage software development sprints and stories in Bolt. Use for creating/updating stories, moving tasks through the Kanban workflow (waiting → in_progress → completed), tracking blockers and dependencies, getting sprint digests, logging AI activity, and attaching files. Requires BOLT_BASE_URL environment variable pointing to a running Bolt instance.
license: MIT
metadata:
  author: ndhill84
  version: "1.0.0"
  source: https://github.com/ndhill84/Bolt
allowed-tools: Bash
---

# Bolt Sprint Management Skill

Bolt is a collaborative software development platform built for human-AI teamwork. This skill lets you manage projects, sprints, and stories through Bolt's REST API.

## Configuration

Set these environment variables before using this skill:

```bash
export BOLT_BASE_URL="http://localhost:4000"   # Your Bolt API base URL
export BOLT_API_TOKEN="your-token-here"         # Optional: only needed if server was started with BOLT_API_TOKEN
```

The base curl pattern for authenticated requests:

```bash
curl -s \
  -H "Content-Type: application/json" \
  ${BOLT_API_TOKEN:+-H "x-bolt-token: $BOLT_API_TOKEN"} \
  "$BOLT_BASE_URL/api/v1/..."
```

Check connectivity before starting:

```bash
curl -s "$BOLT_BASE_URL/health"
# → {"ok":true}
```

---

## Common Operations

### List Projects

```bash
curl -s \
  ${BOLT_API_TOKEN:+-H "x-bolt-token: $BOLT_API_TOKEN"} \
  "$BOLT_BASE_URL/api/v1/projects"
```

### List Sprints for a Project

```bash
curl -s \
  ${BOLT_API_TOKEN:+-H "x-bolt-token: $BOLT_API_TOKEN"} \
  "$BOLT_BASE_URL/api/v1/projects/$PROJECT_ID/sprints"
```

### Get Sprint Digest (blockers, story counts, assignee breakdown)

```bash
curl -s \
  ${BOLT_API_TOKEN:+-H "x-bolt-token: $BOLT_API_TOKEN"} \
  "$BOLT_BASE_URL/api/v1/digests/sprint/$SPRINT_ID"
```

### List Stories

```bash
# All stories in a sprint
curl -s \
  ${BOLT_API_TOKEN:+-H "x-bolt-token: $BOLT_API_TOKEN"} \
  "$BOLT_BASE_URL/api/v1/stories?sprintId=$SPRINT_ID&limit=100"

# Only blocked stories
curl -s \
  ${BOLT_API_TOKEN:+-H "x-bolt-token: $BOLT_API_TOKEN"} \
  "$BOLT_BASE_URL/api/v1/stories?sprintId=$SPRINT_ID&blocked=true"

# Delta sync — only stories changed since a timestamp
curl -s \
  ${BOLT_API_TOKEN:+-H "x-bolt-token: $BOLT_API_TOKEN"} \
  "$BOLT_BASE_URL/api/v1/stories?updated_since=2024-01-01T00:00:00Z"

# Request only specific fields to reduce token usage
curl -s \
  ${BOLT_API_TOKEN:+-H "x-bolt-token: $BOLT_API_TOKEN"} \
  "$BOLT_BASE_URL/api/v1/stories?sprintId=$SPRINT_ID&fields=id,title,status,blocked,priority"
```

### Create a Story

```bash
curl -s -X POST \
  -H "Content-Type: application/json" \
  ${BOLT_API_TOKEN:+-H "x-bolt-token: $BOLT_API_TOKEN"} \
  -d '{
    "title": "Story title",
    "projectId": "'"$PROJECT_ID"'",
    "sprintId": "'"$SPRINT_ID"'",
    "description": "What needs to be done",
    "acceptanceCriteria": "Definition of done",
    "priority": "high",
    "status": "waiting",
    "points": 3
  }' \
  "$BOLT_BASE_URL/api/v1/stories"
```

### Update a Story

```bash
curl -s -X PATCH \
  -H "Content-Type: application/json" \
  ${BOLT_API_TOKEN:+-H "x-bolt-token: $BOLT_API_TOKEN"} \
  -d '{"blocked": true, "priority": "urgent"}' \
  "$BOLT_BASE_URL/api/v1/stories/$STORY_ID"
```

### Move a Story (Kanban transition)

```bash
# Single story
curl -s -X POST \
  -H "Content-Type: application/json" \
  ${BOLT_API_TOKEN:+-H "x-bolt-token: $BOLT_API_TOKEN"} \
  -d '{"status": "in_progress"}' \
  "$BOLT_BASE_URL/api/v1/stories/$STORY_ID/move"

# Batch move multiple stories at once
curl -s -X POST \
  -H "Content-Type: application/json" \
  ${BOLT_API_TOKEN:+-H "x-bolt-token: $BOLT_API_TOKEN"} \
  -d '{
    "items": [
      {"id": "story-1", "status": "completed"},
      {"id": "story-2", "status": "completed"}
    ],
    "all_or_nothing": true
  }' \
  "$BOLT_BASE_URL/api/v1/stories/batch/move"
```

### Add a Note to a Story

```bash
curl -s -X POST \
  -H "Content-Type: application/json" \
  ${BOLT_API_TOKEN:+-H "x-bolt-token: $BOLT_API_TOKEN"} \
  -d '{"body": "Note content here", "author": "AI", "kind": "note"}' \
  "$BOLT_BASE_URL/api/v1/stories/$STORY_ID/notes"
```

### Log AI Activity

```bash
# Post an event to the agent session (creates session if it doesn't exist)
curl -s -X POST \
  -H "Content-Type: application/json" \
  ${BOLT_API_TOKEN:+-H "x-bolt-token: $BOLT_API_TOKEN"} \
  -d '{"message": "Analyzing codebase to implement story", "type": "action"}' \
  "$BOLT_BASE_URL/api/v1/agent/sessions/$SESSION_ID/events"
```

---

## Story Status Values

| Status | Meaning |
|--------|---------|
| `waiting` | Not started — in the backlog/queue |
| `in_progress` | Actively being worked on |
| `completed` | Done |

## Priority Values

`low` · `med` · `high` · `urgent`

---

## Key API Behaviors

- **Idempotency:** Include `Idempotency-Key: <uuid>` header on POST/PATCH to safely retry without duplicates (48-hour TTL).
- **Pagination:** Responses include `page.nextCursor` and `page.hasMore`. Pass `cursor=<value>` to fetch the next page. Default limit 50, max 200.
- **Field projection:** Use `?fields=id,title,status` to request only the fields you need — reduces payload size and token cost.
- **Delta sync:** Use `?updated_since=<ISO8601>` to fetch only items changed since a timestamp — efficient for polling.
- **Error format:** All errors return `{ "error": { "code": "...", "message": "..." } }`.
- **Rate limits:** Write methods capped at 120 requests/minute per IP.

---

## References

- Full API endpoint reference: `references/api-reference.md`
- Workflow patterns and recipes: `references/workflows.md`
