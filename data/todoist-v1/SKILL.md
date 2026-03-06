---
name: todoist
description: Manage Todoist tasks — list, create, complete, update, and organize tasks and projects.
---

# Todoist

API v1 at `https://api.todoist.com/api/v1/`. Auth via Bearer token.

## Auth

Token stored in env var `TODOIST_TOKEN`. Set it in your shell or OpenClaw config:

```bash
export TODOIST_TOKEN=your-token-here
```

Get your token from: https://app.todoist.com/app/settings/integrations/developer

## Common Operations

### List tasks

```bash
curl -s "https://api.todoist.com/api/v1/tasks" \
  -H "Authorization: Bearer $TODOIST_TOKEN" | python3 -m json.tool
```

Filter by project:
```bash
curl -s "https://api.todoist.com/api/v1/tasks?project_id=PROJECT_ID" \
  -H "Authorization: Bearer $TODOIST_TOKEN"
```

### Get a single task

```bash
curl -s "https://api.todoist.com/api/v1/tasks/TASK_ID" \
  -H "Authorization: Bearer $TODOIST_TOKEN"
```

### Create a task

```bash
curl -s -X POST "https://api.todoist.com/api/v1/tasks" \
  -H "Authorization: Bearer $TODOIST_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"content": "Task name", "project_id": "PROJECT_ID", "due_string": "tomorrow", "priority": 1}'
```

Priority: 1 (normal) to 4 (urgent). due_string supports natural language ("tomorrow", "every monday", "Feb 20").

### Complete a task

```bash
curl -s -X POST "https://api.todoist.com/api/v1/tasks/TASK_ID/close" \
  -H "Authorization: Bearer $TODOIST_TOKEN"
```

### Update a task

```bash
curl -s -X POST "https://api.todoist.com/api/v1/tasks/TASK_ID" \
  -H "Authorization: Bearer $TODOIST_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"content": "Updated name", "due_string": "next friday"}'
```

### Delete a task

```bash
curl -s -X DELETE "https://api.todoist.com/api/v1/tasks/TASK_ID" \
  -H "Authorization: Bearer $TODOIST_TOKEN"
```

### List projects

```bash
curl -s "https://api.todoist.com/api/v1/projects" \
  -H "Authorization: Bearer $TODOIST_TOKEN"
```

### Create a project

```bash
curl -s -X POST "https://api.todoist.com/api/v1/projects" \
  -H "Authorization: Bearer $TODOIST_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name": "Project Name"}'
```

### List sections

```bash
curl -s "https://api.todoist.com/api/v1/sections?project_id=PROJECT_ID" \
  -H "Authorization: Bearer $TODOIST_TOKEN"
```

### Create a section

```bash
curl -s -X POST "https://api.todoist.com/api/v1/sections" \
  -H "Authorization: Bearer $TODOIST_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"project_id": "PROJECT_ID", "name": "Section Name", "order": 0}'
```

### Move task to section

```bash
curl -s -X POST "https://api.todoist.com/api/v1/tasks/TASK_ID" \
  -H "Authorization: Bearer $TODOIST_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"section_id": "SECTION_ID"}'
```

## Notes

- API v2 is deprecated (410 Gone). Use v1.
- Token is a personal API token, not OAuth.
- Use "List projects" and "List sections" to discover your project/section IDs.
- Prefer completing tasks over deleting them.
