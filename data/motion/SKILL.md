---
name: motion
description: |
  Motion API integration with managed OAuth. Manage tasks, projects, workspaces, and more with AI-powered scheduling.
  Use this skill when users want to create, update, or manage tasks and projects in Motion, or query their scheduled work.
  For other third party apps, use the api-gateway skill (https://clawhub.ai/byungkyu/api-gateway).
compatibility: Requires network access and valid Maton API key
metadata:
  author: maton
  version: "1.0"
  clawdbot:
    emoji: 🧠
    homepage: "https://maton.ai"
    requires:
      env:
        - MATON_API_KEY
---

# Motion

Access the Motion API with managed OAuth authentication. Manage tasks, projects, workspaces, comments, and recurring tasks with full CRUD operations.

## Quick Start

```bash
# List tasks
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://gateway.maton.ai/motion/v1/tasks')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

## Base URL

```
https://gateway.maton.ai/motion/{native-api-path}
```

Replace `{native-api-path}` with the actual Motion API endpoint path. The gateway proxies requests to `api.usemotion.com` and automatically injects your OAuth token.

## Authentication

All requests require the Maton API key in the Authorization header:

```
Authorization: Bearer $MATON_API_KEY
```

**Environment Variable:** Set your API key as `MATON_API_KEY`:

```bash
export MATON_API_KEY="YOUR_API_KEY"
```

### Getting Your API Key

1. Sign in or create an account at [maton.ai](https://maton.ai)
2. Go to [maton.ai/settings](https://maton.ai/settings)
3. Copy your API key

## Connection Management

Manage your Motion OAuth connections at `https://ctrl.maton.ai`.

### List Connections

```bash
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://ctrl.maton.ai/connections?app=motion&status=ACTIVE')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

### Create Connection

```bash
python <<'EOF'
import urllib.request, os, json
data = json.dumps({'app': 'motion'}).encode()
req = urllib.request.Request('https://ctrl.maton.ai/connections', data=data, method='POST')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
req.add_header('Content-Type', 'application/json')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

### Get Connection

```bash
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://ctrl.maton.ai/connections/{connection_id}')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

**Response:**
```json
{
  "connection": {
    "connection_id": "21fd90f9-5935-43cd-b6c8-bde9d915ca80",
    "status": "ACTIVE",
    "creation_time": "2025-12-08T07:20:53.488460Z",
    "last_updated_time": "2026-01-31T20:03:32.593153Z",
    "url": "https://connect.maton.ai/?session_token=...",
    "app": "motion",
    "metadata": {}
  }
}
```

Open the returned `url` in a browser to complete OAuth authorization.

### Delete Connection

```bash
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://ctrl.maton.ai/connections/{connection_id}', method='DELETE')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

### Specifying Connection

If you have multiple Motion connections, specify which one to use with the `Maton-Connection` header:

```bash
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://gateway.maton.ai/motion/v1/tasks')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
req.add_header('Maton-Connection', '21fd90f9-5935-43cd-b6c8-bde9d915ca80')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

If omitted, the gateway uses the default (oldest) active connection.

## API Reference

### Task Operations

#### List Tasks

```bash
GET /motion/v1/tasks
```

**Query Parameters:**
- `workspaceId` (string) - Filter by workspace
- `projectId` (string) - Filter by project
- `assigneeId` (string) - Filter by assignee
- `status` (array) - Filter by status (cannot combine with `includeAllStatuses`)
- `includeAllStatuses` (boolean) - Return tasks across all statuses
- `label` (string) - Filter by label
- `name` (string) - Search task names (case-insensitive)
- `cursor` (string) - Pagination cursor

**Example:**
```bash
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://gateway.maton.ai/motion/v1/tasks?workspaceId=WORKSPACE_ID')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

#### Get Task

```bash
GET /motion/v1/tasks/{taskId}
```

#### Create Task

```bash
POST /motion/v1/tasks
Content-Type: application/json

{
  "name": "Task name",
  "workspaceId": "WORKSPACE_ID",
  "dueDate": "2024-03-15T10:00:00Z",
  "duration": 60,
  "priority": "HIGH",
  "description": "Task description in markdown",
  "projectId": "PROJECT_ID",
  "assigneeId": "USER_ID",
  "labels": ["label1", "label2"],
  "autoScheduled": {
    "startDate": "2024-03-14T09:00:00Z",
    "deadlineType": "SOFT",
    "schedule": "Work Hours"
  }
}
```

**Required Fields:**
- `name` (string) - Task title
- `workspaceId` (string) - Workspace ID

**Optional Fields:**
- `dueDate` (datetime, ISO 8601) - Task deadline (required for scheduled tasks)
- `duration` (string | number) - "NONE", "REMINDER", or minutes (integer > 0)
- `status` (string) - Defaults to workspace default status
- `projectId` (string) - Associated project
- `description` (string) - GitHub Flavored Markdown supported
- `priority` (string) - ASAP, HIGH, MEDIUM, or LOW
- `labels` (array) - Label names to add
- `assigneeId` (string) - User ID for task assignment
- `autoScheduled` (object) - Auto-scheduling settings with `startDate`, `deadlineType` (HARD, SOFT, NONE), and `schedule`

**Example:**
```bash
python <<'EOF'
import urllib.request, os, json
data = json.dumps({
    'name': 'New task',
    'workspaceId': 'WORKSPACE_ID',
    'priority': 'HIGH',
    'duration': 30
}).encode()
req = urllib.request.Request('https://gateway.maton.ai/motion/v1/tasks', data=data, method='POST')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
req.add_header('Content-Type', 'application/json')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

#### Update Task

```bash
PATCH /motion/v1/tasks/{taskId}
Content-Type: application/json

{
  "name": "Updated task name",
  "status": "Completed",
  "priority": "LOW"
}
```

#### Delete Task

```bash
DELETE /motion/v1/tasks/{taskId}
```

#### Move Task

```bash
POST /motion/v1/tasks/{taskId}/move
Content-Type: application/json

{
  "workspaceId": "NEW_WORKSPACE_ID"
}
```

#### Unassign Task

```bash
POST /motion/v1/tasks/{taskId}/unassign
```

### Project Operations

#### List Projects

```bash
GET /motion/v1/projects?workspaceId={workspaceId}
```

**Query Parameters:**
- `workspaceId` (string, **required**) - Workspace ID
- `cursor` (string) - Pagination cursor

#### Get Project

```bash
GET /motion/v1/projects/{projectId}
```

#### Create Project

```bash
POST /motion/v1/projects
Content-Type: application/json

{
  "name": "Project name",
  "workspaceId": "WORKSPACE_ID",
  "description": "Project description",
  "dueDate": "2024-06-30T00:00:00Z",
  "priority": "HIGH",
  "labels": ["label1"]
}
```

**Required Fields:**
- `name` (string) - Project name
- `workspaceId` (string) - Workspace ID

**Optional Fields:**
- `dueDate` (datetime, ISO 8601) - Project deadline
- `description` (string) - HTML input accepted
- `labels` (array) - Label names
- `priority` (string) - ASAP, HIGH, MEDIUM (default), or LOW
- `projectDefinitionId` (string) - Template ID (requires `stages` array if provided)
- `stages` (array) - Stage objects for project templates

### Workspace Operations

#### List Workspaces

```bash
GET /motion/v1/workspaces
```

### User Operations

#### List Users

```bash
GET /motion/v1/users?workspaceId={workspaceId}
```

**Query Parameters:**
- `workspaceId` (string) - Workspace ID (required if no teamId)
- `teamId` (string) - Team ID (required if no workspaceId)

Note: You must provide either `workspaceId` or `teamId`.

#### Get Current User

```bash
GET /motion/v1/users/me
```

### Comment Operations

#### List Comments

```bash
GET /motion/v1/comments?taskId={taskId}
```

**Query Parameters:**
- `taskId` (string, **required**) - Filter comments by task
- `cursor` (string) - Pagination cursor

#### Create Comment

```bash
POST /motion/v1/comments
Content-Type: application/json

{
  "taskId": "TASK_ID",
  "content": "Comment in GitHub Flavored Markdown"
}
```

**Required Fields:**
- `taskId` (string) - Task to comment on

**Optional Fields:**
- `content` (string) - Comment content in GitHub Flavored Markdown

### Recurring Task Operations

#### List Recurring Tasks

```bash
GET /motion/v1/recurring-tasks?workspaceId={workspaceId}
```

**Query Parameters:**
- `workspaceId` (string, **required**) - Filter by workspace
- `cursor` (string) - Pagination cursor

#### Create Recurring Task

```bash
POST /motion/v1/recurring-tasks
Content-Type: application/json

{
  "name": "Weekly review",
  "workspaceId": "WORKSPACE_ID",
  "frequency": "weekly"
}
```

#### Delete Recurring Task

```bash
DELETE /motion/v1/recurring-tasks/{recurringTaskId}
```

### Schedule Operations

#### List Schedules

```bash
GET /motion/v1/schedules
```

### Status Operations

#### List Statuses

```bash
GET /motion/v1/statuses?workspaceId={workspaceId}
```

**Query Parameters:**
- `workspaceId` (string, **required**) - Filter by workspace

### Custom Field Operations

#### List Custom Fields

```bash
GET /motion/v1/custom-fields
```

#### Create Custom Field

```bash
POST /motion/v1/custom-fields
Content-Type: application/json

{
  "name": "Field name",
  "type": "text"
}
```

#### Delete Custom Field

```bash
DELETE /motion/v1/custom-fields/{customFieldId}
```

#### Add Custom Field to Project

```bash
POST /motion/v1/custom-fields/{customFieldId}/project
Content-Type: application/json

{
  "projectId": "PROJECT_ID"
}
```

#### Add Custom Field to Task

```bash
POST /motion/v1/custom-fields/{customFieldId}/task
Content-Type: application/json

{
  "taskId": "TASK_ID"
}
```

#### Remove Custom Field from Project

```bash
DELETE /motion/v1/custom-fields/{customFieldId}/project
```

#### Remove Custom Field from Task

```bash
DELETE /motion/v1/custom-fields/{customFieldId}/task
```

## Pagination

Motion uses cursor-based pagination:

```bash
GET /motion/v1/tasks?cursor=CURSOR_VALUE
```

Response includes pagination metadata:

```json
{
  "tasks": [...],
  "meta": {
    "nextCursor": "abc123",
    "pageSize": 20
  }
}
```

Use the `nextCursor` value in subsequent requests to retrieve more results.

## Code Examples

### JavaScript

```javascript
const response = await fetch(
  'https://gateway.maton.ai/motion/v1/tasks',
  {
    headers: {
      'Authorization': `Bearer ${process.env.MATON_API_KEY}`
    }
  }
);
const data = await response.json();
```

### Python

```python
import os
import requests

response = requests.get(
    'https://gateway.maton.ai/motion/v1/tasks',
    headers={'Authorization': f'Bearer {os.environ["MATON_API_KEY"]}'}
)
data = response.json()
```

## Notes

- All timestamps use ISO 8601 format
- Task descriptions support GitHub Flavored Markdown
- Project descriptions accept HTML input
- Priority values: ASAP, HIGH, MEDIUM, LOW
- Deadline types for auto-scheduling: HARD, SOFT, NONE
- Rate limits: 12 req/min (Individual), 120 req/min (Team)
- IMPORTANT: When using curl commands, use `curl -g` when URLs contain brackets to disable glob parsing
- IMPORTANT: When piping curl output to `jq` or other commands, environment variables like `$MATON_API_KEY` may not expand correctly in some shell environments

## Error Handling

| Status | Meaning |
|--------|---------|
| 400 | Missing Motion connection or invalid request |
| 401 | Invalid or missing Maton API key |
| 429 | Rate limited |
| 4xx/5xx | Passthrough error from Motion API |

## Resources

- [Motion API Documentation](https://docs.usemotion.com/)
- [Motion API Reference](https://docs.usemotion.com/api-reference)
- [Motion Cookbooks](https://docs.usemotion.com/cookbooks/getting-started)
- [Maton Community](https://discord.com/invite/dBfFAcefs2)
- [Maton Support](mailto:support@maton.ai)
