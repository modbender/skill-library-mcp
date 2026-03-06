---
name: init-manager
description: Manage tasks in Init Manager — pick up ready tasks, update status, comment, and close out. Use when assigned tasks via webhook or cron, or when interacting with Init Manager projects.
metadata:
  openclaw:
    requires: {}
---

# Init Manager Skill

This skill enables AI agents to work with [Init Manager](https://manager.init.hr) as a project management backend — picking up tasks, doing work, and closing them out.

## Setup

Your workspace needs these in `TOOLS.md` or environment:
- **Init Manager URL** (e.g. `https://manager.init.hr`)
- **API Key** (Bearer token, starts with `initm_`)
- **Your User ID** (UUID)

## AI Guides (Instruction Hierarchy)

There are three levels of AI instructions. **Always follow them.** More specific wins on conflict:

1. **Global AI Guide** — `GET /api/settings?key=ai_global_guide`
2. **Per-User AI Guide** — `GET /api/users/<your-user-id>` → `aiGuide` field
3. **Project AI Guide** — `GET /api/projects/<project-id>` → `aiGuide` field

**On first boot and periodically:** fetch all three and follow the combined instructions.

## Task Workflow

1. **Pick up** tasks in `ready` status assigned to you
2. **Move to `in_progress`** before starting work
3. **Read** full description + all comments + project AI guide before writing code
4. **If unsure** — comment asking for clarification, keep in `ready`, assign to a human
5. **When done** — move to `done`, add comment with commit/PR link + summary
6. **If blocked** — comment with details, assign to a human

## API Reference

### Authentication

All requests need:
```
Authorization: Bearer initm_<your-key>
```

### Key Endpoints

| Action | Method | Endpoint |
|--------|--------|----------|
| List projects | GET | `/api/projects` |
| Project board | GET | `/api/projects/<id>/board` |
| Project details | GET | `/api/projects/<id>` |
| List tasks | GET | `/api/tasks?assignee=me&status=ready` |
| Get task | GET | `/api/tasks/<id>` |
| Update task | PATCH | `/api/tasks/<id>` |
| Move task | POST | `/api/tasks/<id>/move` |
| Create task | POST | `/api/tasks` |
| Add comment | POST | `/api/tasks/<id>/comments` |
| Assign user | POST | `/api/tasks/<id>/assign` |
| Complete assignment | POST | `/api/tasks/<id>/complete` |
| Activity log | GET | `/api/activity` |
| Global AI guide | GET | `/api/settings?key=ai_global_guide` |

### Create a Task

```
POST /api/tasks
{
  "projectId": "<uuid>",
  "title": "Task title",
  "type": "task",           // epic | task | bug
  "status": "backlog",      // backlog | ready | in_progress | done | verified
  "priority": "medium",     // low | medium | high | urgent
  "description": "...",     // plain text or Tiptap JSON
  "parentId": "<uuid>",     // optional, makes subtask
  "dueDate": "2026-03-01T00:00:00.000Z"
}
```

### Update a Task

```
PATCH /api/tasks/<id>
{
  "status": "in_progress",
  "title": "New title",
  "priority": "high"
}
```
All fields optional — only include what changes.

### Add a Comment

```
POST /api/tasks/<id>/comments
{
  "body": "Your comment text"
}
```
⚠️ Use `body` field, not `content`.

### Assign a User

```
POST /api/tasks/<id>/assign
{ "userId": "<uuid>" }
```

### Labels

```
GET    /api/labels?projectId=<uuid>
POST   /api/labels                        { "name": "Bug", "color": "#ef4444", "projectId": "<uuid>" }
POST   /api/tasks/<id>/labels             { "labelId": "<uuid>" }
DELETE /api/tasks/<id>/labels             { "labelId": "<uuid>" }
```

## Behavior Notes

- Assignments auto-complete when task moves to `done` or `verified`
- Moving task back to `ready`/`backlog` clears notification flags and assignment completion
- Comments created via API are flagged `viaApi: true`
- Task keys (e.g. `IMG-32`) are auto-generated from project prefix

## Error Responses

```json
{ "error": "Description" }
```

| Status | Meaning |
|--------|---------|
| 400 | Bad request / validation |
| 401 | Invalid or missing API key |
| 403 | Not allowed for your role |
| 404 | Resource not found |
| 409 | Conflict |
| 500 | Server error |

## Common Workflow: Check for Tasks

```bash
# Get all projects
curl -H "Authorization: Bearer $KEY" $URL/api/projects

# Check each project board for ready tasks assigned to you
curl -H "Authorization: Bearer $KEY" $URL/api/projects/$PID/board

# Pick up a task
curl -X PATCH -H "Authorization: Bearer $KEY" -H "Content-Type: application/json" \
  -d '{"status":"in_progress"}' $URL/api/tasks/$TID

# ... do the work ...

# Close it out
curl -X PATCH -H "Authorization: Bearer $KEY" -H "Content-Type: application/json" \
  -d '{"status":"done"}' $URL/api/tasks/$TID

curl -X POST -H "Authorization: Bearer $KEY" -H "Content-Type: application/json" \
  -d '{"body":"Done. Commit: https://..."}' $URL/api/tasks/$TID/comments
```
