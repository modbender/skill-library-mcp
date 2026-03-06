# Bolt API Reference

Base URL: `$BOLT_BASE_URL` (e.g. `http://localhost:3000`)

Authentication: optional `x-bolt-token: $BOLT_API_TOKEN` header (required when server is started with `BOLT_API_TOKEN` env var).

---

## Health

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Liveness probe — returns `{"ok":true}` |
| GET | `/ready` | Readiness probe — checks DB connectivity |

---

## Projects

### GET `/api/v1/projects`
List all projects.

**Response:**
```json
{
  "data": [
    {
      "id": "proj_abc123",
      "name": "My Project",
      "description": "Optional description",
      "createdAt": "2024-01-01T00:00:00Z",
      "updatedAt": "2024-01-01T00:00:00Z"
    }
  ],
  "page": { "nextCursor": null, "hasMore": false }
}
```

### POST `/api/v1/projects`
Create a project.

**Body:**
```json
{
  "name": "Project Name",         // required
  "description": "Optional"       // optional
}
```

**Headers:** `Idempotency-Key: <uuid>` (optional, for safe retries)

### PATCH `/api/v1/projects/{id}`
Update a project's name or description.

**Body:** `name`, `description` (both optional)

### DELETE `/api/v1/projects/{id}`
Delete a project.

**Query:** `force=true` to delete even if sprints/stories exist.

---

## Sprints

### GET `/api/v1/projects/{id}/sprints`
List all sprints for a project.

**Response:**
```json
{
  "data": [
    {
      "id": "sprint_abc123",
      "projectId": "proj_abc123",
      "name": "Sprint 1",
      "goal": "Ship the MVP",
      "status": "active",
      "startAt": "2024-01-01T00:00:00Z",
      "endAt": "2024-01-14T00:00:00Z"
    }
  ]
}
```

**Sprint statuses:** `planning` · `active` · `closed`

### POST `/api/v1/projects/{id}/sprints`
Create a sprint.

**Body:**
```json
{
  "name": "Sprint 2",             // required
  "goal": "Sprint objective",     // optional
  "status": "planning",           // optional, default: "planning"
  "startAt": "2024-01-15T00:00:00Z",  // optional ISO8601
  "endAt": "2024-01-28T00:00:00Z"     // optional ISO8601
}
```

### PATCH `/api/v1/sprints/{id}`
Update sprint fields (`name`, `goal`, `status`, `startAt`, `endAt`).

### POST `/api/v1/sprints/{id}/start`
Transition sprint to `active` status.

### POST `/api/v1/sprints/{id}/close`
Transition sprint to `closed` status.

### POST `/api/v1/sprints/{id}/stories:assign`
Assign stories to a sprint.

**Body:**
```json
{
  "storyIds": ["story_1", "story_2"],  // required, max 100
  "dry_run": false                      // optional, preview without committing
}
```

---

## Stories

### GET `/api/v1/stories`
List stories with filtering, pagination, and field projection.

**Query parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `limit` | int 1–200 | Results per page (default 50) |
| `cursor` | string | Pagination cursor from previous response |
| `updated_since` | ISO8601 | Delta sync — only stories updated after this time |
| `projectId` | string | Filter by project |
| `sprintId` | string | Filter by sprint |
| `status` | string | Filter by status: `waiting`, `in_progress`, `completed` |
| `priority` | string | Filter by priority: `low`, `medium`, `high`, `critical` |
| `assignee` | string | Filter by assignee name |
| `blocked` | boolean | Filter to only blocked (`true`) or unblocked (`false`) stories |
| `due_before` | ISO8601 | Stories due before this date |
| `due_after` | ISO8601 | Stories due after this date |
| `has_dependencies` | boolean | Filter stories with/without dependencies |
| `fields` | string | Comma-separated list of fields to return (reduces payload) |

**Example — efficient sprint board fetch:**
```
GET /api/v1/stories?sprintId=sprint_abc&fields=id,title,status,priority,blocked,assignee&limit=100
```

**Response:**
```json
{
  "data": [
    {
      "id": "story_abc123",
      "title": "Implement login flow",
      "projectId": "proj_abc123",
      "sprintId": "sprint_abc123",
      "description": "Full description...",
      "acceptanceCriteria": "Given/When/Then...",
      "status": "in_progress",
      "priority": "high",
      "blocked": false,
      "points": 5,
      "assignee": "Alice",
      "dueAt": "2024-01-10T00:00:00Z",
      "createdAt": "2024-01-01T00:00:00Z",
      "updatedAt": "2024-01-05T00:00:00Z"
    }
  ],
  "page": {
    "nextCursor": "cursor_xyz",
    "hasMore": true
  }
}
```

### POST `/api/v1/stories`
Create a story.

**Body:**
```json
{
  "title": "Story title",              // required
  "projectId": "proj_abc123",          // optional
  "sprintId": "sprint_abc123",         // optional
  "description": "What needs to be done",
  "acceptanceCriteria": "Definition of done",
  "status": "waiting",                 // default: "waiting"
  "priority": "medium",                // default: "medium"
  "blocked": false,
  "points": 3,
  "assignee": "Alice",
  "dueAt": "2024-01-15T00:00:00Z"
}
```

### PATCH `/api/v1/stories/{id}`
Update any story fields (`title`, `sprintId`, `description`, `acceptanceCriteria`, `status`, `priority`, `blocked`, `points`, `assignee`, `dueAt`).

### DELETE `/api/v1/stories/{id}`
Delete a story.

### POST `/api/v1/stories/{id}/move`
Move a story to a new Kanban status.

**Body:** `{ "status": "in_progress" }` — values: `waiting` · `in_progress` · `completed`

### POST `/api/v1/stories/batch/move`
Move multiple stories at once.

**Body:**
```json
{
  "items": [
    { "id": "story_1", "status": "completed" },
    { "id": "story_2", "status": "in_progress" }
  ],
  "dry_run": false,          // preview without committing
  "all_or_nothing": false    // roll back all if any fail
}
```

### POST `/api/v1/stories/batch/patch`
Update fields on multiple stories at once.

**Body:**
```json
{
  "items": [
    { "id": "story_1", "patch": { "assignee": "Bob", "priority": "high" } },
    { "id": "story_2", "patch": { "blocked": true } }
  ],
  "dry_run": false,
  "all_or_nothing": false
}
```

---

## Notes

### GET `/api/v1/stories/{id}/notes`
List all notes on a story.

**Response:**
```json
{
  "data": [
    {
      "id": "note_abc123",
      "storyId": "story_abc123",
      "body": "Note content",
      "author": "Alice",
      "kind": "note",
      "createdAt": "2024-01-01T00:00:00Z"
    }
  ]
}
```

**Note kinds:** `note` · `comment` · `blocker` · `decision`

### POST `/api/v1/stories/{id}/notes`
Add a note to a story.

**Body:**
```json
{
  "body": "Note content",     // required
  "author": "AI",             // optional, default: "you"
  "kind": "note"              // optional, default: "note"
}
```

---

## Labels

### GET `/api/v1/stories/{id}/labels`
List labels on a story.

### POST `/api/v1/stories/{id}/labels`
Add a label.

**Body:** `{ "label": "bug" }`

### DELETE `/api/v1/stories/{id}/labels/{label}`
Remove a label.

---

## Dependencies

### GET `/api/v1/stories/{id}/dependencies`
List outgoing dependencies (stories that this story blocks).

**Response:**
```json
{
  "data": [
    {
      "id": "dep_abc123",
      "storyId": "story_abc123",
      "dependsOnStoryId": "story_def456",
      "type": "blocks",
      "createdAt": "2024-01-01T00:00:00Z"
    }
  ]
}
```

### POST `/api/v1/stories/{id}/dependencies`
Add a dependency.

**Body:**
```json
{
  "dependsOnStoryId": "story_def456",  // required — story that must complete first
  "type": "blocks"                      // optional, default: "blocks"
}
```

### DELETE `/api/v1/dependencies/{id}`
Remove a dependency by its ID.

---

## Files

### GET `/api/v1/files`
List attached files.

**Query:** `limit`, `cursor`, `updated_since`, `projectId`, `storyId`, `fields`, `include`

### POST `/api/v1/files`
Register a file record (for text/metadata, no binary upload).

**Body:**
```json
{
  "filename": "design.pdf",      // required
  "projectId": "proj_abc123",
  "storyId": "story_abc123",
  "contentType": "application/pdf",
  "byteSize": 102400,
  "filePath": "/uploads/design.pdf",
  "textContent": "Extracted text...",
  "summary": "Design document for login flow",
  "uploadedBy": "Alice"
}
```

### POST `/api/v1/files/upload`
Upload a binary file (multipart form, max 5 MB).

**Form fields:** `file` (binary, required), `projectId` (required), `storyId` (optional), `uploadedBy` (required)

### DELETE `/api/v1/files/{id}`
Delete a file.

### GET `/api/v1/files/{id}/content`
Get the extracted text content of a file.

---

## Agent Sessions

Use these endpoints to make AI activity visible in the Bolt UI.

### GET `/api/v1/agent/sessions`
List agent sessions.

**Query:** `projectId` (optional filter)

### GET `/api/v1/agent/sessions/{id}/events`
List events for a session.

**Query:** `limit`, `cursor`, `updated_since`

### POST `/api/v1/agent/sessions/{id}/events`
Log an agent event.

**Body:**
```json
{
  "message": "Analyzing codebase to implement story",  // required
  "type": "action"                                      // optional, default: "action"
}
```

**Event types:** `action` · `observation` · `thought` · `error`

---

## Audit Log

### GET `/api/v1/audit`
Monotonic changefeed of all write operations (newest first).

**Query:** `since` (ISO8601), `projectId`, `limit`, `cursor`

---

## Digests

### GET `/api/v1/digests/sprint/{id}`
Sprint summary: story counts by status, blocked stories list, assignee breakdown.

**Response:**
```json
{
  "sprintId": "sprint_abc123",
  "counts": {
    "waiting": 5,
    "in_progress": 3,
    "completed": 12,
    "total": 20,
    "blocked": 2
  },
  "blockedStories": [
    { "id": "story_abc", "title": "...", "assignee": "Alice" }
  ],
  "byAssignee": {
    "Alice": { "waiting": 2, "in_progress": 1, "completed": 5 },
    "Bob": { "waiting": 3, "in_progress": 2, "completed": 7 }
  }
}
```

### GET `/api/v1/digests/project/{projectId}/daily`
24-hour aggregated snapshot for a project (use `all` for all projects).

---

## Error Responses

All errors use a consistent envelope:

```json
{
  "error": {
    "code": "NOT_FOUND",
    "message": "Story not found"
  }
}
```

**Common error codes:**

| Code | HTTP | Meaning |
|------|------|---------|
| `NOT_FOUND` | 404 | Resource does not exist |
| `VALIDATION_ERROR` | 400 | Invalid request body or parameters |
| `CONFLICT` | 409 | Idempotency key collision or invalid state transition |
| `RATE_LIMITED` | 429 | Too many write requests (> 120/min) |
| `UNAUTHORIZED` | 401 | Missing or invalid `x-bolt-token` |
