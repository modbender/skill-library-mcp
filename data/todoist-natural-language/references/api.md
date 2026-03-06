# Todoist API v1 Reference

Full REST API documentation for Todoist.

Base URL: `https://api.todoist.com/api/v1`

Authentication: Bearer token in `Authorization` header

## Tasks

### List Tasks
```
GET /tasks
```

Query parameters:
- `project_id` — Filter by project
- `section_id` — Filter by section
- `label` — Filter by label name
- `filter` — Todoist filter string
- `ids` — Comma-separated task IDs
- `limit` — Max results (default: 30)

### Get Task
```
GET /tasks/{task_id}
```

### Create Task
```
POST /tasks
```

Body fields:
- `content` (required) — Task text
- `description` — Task description
- `project_id` — Project to add to (defaults to Inbox)
- `section_id` — Section ID
- `parent_id` — Parent task ID (for subtasks)
- `order` — Position in list
- `labels` — Array of label names
- `priority` — 1 (urgent) to 4 (low)
- `due_string` — Natural language due date
- `due_date` — YYYY-MM-DD format
- `due_datetime` — ISO 8601 datetime
- `due_lang` — Language for parsing due_string
- `assignee_id` — User ID to assign
- `duration` — Object with `amount` and `unit` (minute/day)

### Update Task
```
POST /tasks/{task_id}
```

Same fields as Create Task. Only provided fields are updated.

### Complete Task
```
POST /tasks/{task_id}/close
```

### Reopen Task
```
POST /tasks/{task_id}/reopen
```

### Delete Task
```
DELETE /tasks/{task_id}
```

## Projects

### List Projects
```
GET /projects
```

### Get Project
```
GET /projects/{project_id}
```

### Create Project
```
POST /projects
```

Body:
- `name` (required)
- `parent_id` — Parent project ID
- `color` — Color ID or name
- `is_favorite` — boolean
- `view_style` — "list" or "board"

### Update Project
```
POST /projects/{project_id}
```

### Delete Project
```
DELETE /projects/{project_id}
```

## Sections

Sections are groupings within projects.

### List Sections
```
GET /sections?project_id={project_id}
```

### Create Section
```
POST /sections
```

Body:
- `name` (required)
- `project_id` (required)
- `order` — Position

## Labels

### List Labels
```
GET /labels
```

### Create Label
```
POST /labels
```

Body:
- `name` (required)
- `color` — Color ID
- `is_favorite` — boolean

## Comments

Comments can be on tasks or projects.

### List Comments
```
GET /comments?task_id={task_id}
GET /comments?project_id={project_id}
```

### Create Comment
```
POST /comments
```

Body:
- `task_id` OR `project_id` (required)
- `content` (required) — Text or markdown
- `attachment` — Object with file info

## Shared Labels

### Rename Shared Label
```
POST /labels/shared/rename
```

Body:
- `name` (old name)
- `new_name` (new name)

### Remove Shared Label
```
POST /labels/shared/remove
```

Body:
- `name` — Label name to remove from all tasks

## Quick Add (Natural Language)

```
POST /quick/add
```

Parses natural language task strings:
- `text` (required) — Full task string
- `note` — Additional description
- `reminder` — Reminder string

Example: "Buy milk tomorrow at 5pm p1 #shopping"

## Sync API (Advanced)

For real-time sync, use the Sync API:
- Endpoint: `https://api.todoist.com/sync/v9/sync`
- Supports commands, sync tokens, incremental sync
- See: https://developer.todoist.com/sync/v9/

## Error Responses

HTTP status codes:
- `200` — Success
- `400` — Bad request (invalid params)
- `401` — Unauthorized (bad token)
- `403` — Forbidden (no access)
- `404` — Not found
- `422` — Unprocessable entity
- `429` — Rate limited
- `500` — Server error

Error body:
```json
{
  "error": "Error message",
  "error_code": 20,
  "error_extra": { ... },
  "http_code": 400
}
```

## Rate Limits

- 450 requests per 15 minutes per token
- Rate limit headers included in responses
- Backoff on 429 responses

## Colors

Color IDs for projects/labels:
- 30: Light red
- 31: Light orange
- 32: Light yellow
- 33: Light green
- 34: Light teal
- 35: Light blue
- 36: Light purple
- 37: Light gray
- 38: Dark red
- 39: Dark orange
- 40: Dark yellow
- 41: Dark green
- 42: Dark teal
- 43: Dark blue
- 44: Dark purple
- 45: Dark gray
- 46: Red
- 47: Orange
- 48: Yellow
- 49: Green
- 50: Teal
- 51: Blue
- 52: Purple
- 53: Gray
