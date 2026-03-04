---
name: clockify
description: |
  Clockify API integration with managed OAuth. Track time, manage projects, clients, tasks, and workspaces.
  Use this skill when users want to track time, create or manage projects, view time entries, or manage workspace members.
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

# Clockify

Access the Clockify API with managed OAuth authentication. Track time, manage projects, clients, tasks, tags, and workspaces.

## Quick Start

```bash
# Get current user
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://gateway.maton.ai/clockify/api/v1/user')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

## Base URL

```
https://gateway.maton.ai/clockify/{native-api-path}
```

Replace `{native-api-path}` with the actual Clockify API endpoint path. The gateway proxies requests to `api.clockify.me` and automatically injects your credentials.

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

Manage your Clockify OAuth connections at `https://ctrl.maton.ai`.

### List Connections

```bash
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://ctrl.maton.ai/connections?app=clockify&status=ACTIVE')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

### Create Connection

```bash
python <<'EOF'
import urllib.request, os, json
data = json.dumps({'app': 'clockify'}).encode()
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
    "connection_id": "13fe7b78-42ba-4b43-9631-69a4bf7091ec",
    "status": "ACTIVE",
    "creation_time": "2026-02-13T09:18:02.529448Z",
    "last_updated_time": "2026-02-13T09:18:09.334540Z",
    "url": "https://connect.maton.ai/?session_token=...",
    "app": "clockify",
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

If you have multiple Clockify connections, specify which one to use with the `Maton-Connection` header:

```bash
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://gateway.maton.ai/clockify/api/v1/user')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
req.add_header('Maton-Connection', '13fe7b78-42ba-4b43-9631-69a4bf7091ec')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

If omitted, the gateway uses the default (oldest) active connection.

## API Reference

### User Operations

#### Get Current User

```bash
GET /clockify/api/v1/user
```

**Response:**
```json
{
  "id": "698eeb9f5cd3a921db12069f",
  "email": "user@example.com",
  "name": "John Doe",
  "activeWorkspace": "698eeb9e5cd3a921db120693",
  "defaultWorkspace": "698eeb9e5cd3a921db120693",
  "status": "ACTIVE"
}
```

### Workspace Operations

#### List Workspaces

```bash
GET /clockify/api/v1/workspaces
```

#### Get Workspace

```bash
GET /clockify/api/v1/workspaces/{workspaceId}
```

#### Create Workspace

```bash
POST /clockify/api/v1/workspaces
Content-Type: application/json

{
  "name": "My Workspace"
}
```

#### List Workspace Users

```bash
GET /clockify/api/v1/workspaces/{workspaceId}/users
```

### Project Operations

#### List Projects

```bash
GET /clockify/api/v1/workspaces/{workspaceId}/projects
```

#### Get Project

```bash
GET /clockify/api/v1/workspaces/{workspaceId}/projects/{projectId}
```

#### Create Project

```bash
POST /clockify/api/v1/workspaces/{workspaceId}/projects
Content-Type: application/json

{
  "name": "My Project",
  "isPublic": true,
  "clientId": "optional-client-id"
}
```

**Response:**
```json
{
  "id": "698f7cba4f748f6209ea8995",
  "name": "My Project",
  "clientId": "",
  "workspaceId": "698eeb9e5cd3a921db120693",
  "billable": true,
  "color": "#1976D2",
  "archived": false,
  "public": true
}
```

#### Update Project

```bash
PUT /clockify/api/v1/workspaces/{workspaceId}/projects/{projectId}
Content-Type: application/json

{
  "name": "Updated Project Name",
  "archived": true
}
```

#### Delete Project

```bash
DELETE /clockify/api/v1/workspaces/{workspaceId}/projects/{projectId}
```

**Note:** You cannot delete active projects. Set `archived: true` first.

### Client Operations

#### List Clients

```bash
GET /clockify/api/v1/workspaces/{workspaceId}/clients
```

#### Get Client

```bash
GET /clockify/api/v1/workspaces/{workspaceId}/clients/{clientId}
```

#### Create Client

```bash
POST /clockify/api/v1/workspaces/{workspaceId}/clients
Content-Type: application/json

{
  "name": "Acme Corp",
  "address": "123 Main St",
  "note": "Important client"
}
```

**Response:**
```json
{
  "id": "698f7cba0705b7d880830262",
  "name": "Acme Corp",
  "workspaceId": "698eeb9e5cd3a921db120693",
  "archived": false,
  "address": "123 Main St",
  "note": "Important client"
}
```

#### Update Client

```bash
PUT /clockify/api/v1/workspaces/{workspaceId}/clients/{clientId}
Content-Type: application/json

{
  "name": "Acme Corporation"
}
```

#### Delete Client

```bash
DELETE /clockify/api/v1/workspaces/{workspaceId}/clients/{clientId}
```

### Tag Operations

#### List Tags

```bash
GET /clockify/api/v1/workspaces/{workspaceId}/tags
```

#### Get Tag

```bash
GET /clockify/api/v1/workspaces/{workspaceId}/tags/{tagId}
```

#### Create Tag

```bash
POST /clockify/api/v1/workspaces/{workspaceId}/tags
Content-Type: application/json

{
  "name": "urgent"
}
```

**Response:**
```json
{
  "id": "698f7cbbaa9e9f33e5fc0126",
  "name": "urgent",
  "workspaceId": "698eeb9e5cd3a921db120693",
  "archived": false
}
```

#### Update Tag

```bash
PUT /clockify/api/v1/workspaces/{workspaceId}/tags/{tagId}
Content-Type: application/json

{
  "name": "high-priority"
}
```

#### Delete Tag

```bash
DELETE /clockify/api/v1/workspaces/{workspaceId}/tags/{tagId}
```

### Task Operations

#### List Tasks on Project

```bash
GET /clockify/api/v1/workspaces/{workspaceId}/projects/{projectId}/tasks
```

#### Get Task

```bash
GET /clockify/api/v1/workspaces/{workspaceId}/projects/{projectId}/tasks/{taskId}
```

#### Create Task

```bash
POST /clockify/api/v1/workspaces/{workspaceId}/projects/{projectId}/tasks
Content-Type: application/json

{
  "name": "Implement feature",
  "assigneeIds": ["user-id-1"],
  "estimate": "PT2H",
  "billable": true
}
```

**Response:**
```json
{
  "id": "698f7cc4aa9e9f33e5fc017b",
  "name": "Implement feature",
  "projectId": "698f7cba4f748f6209ea8995",
  "assigneeIds": [],
  "estimate": "PT0S",
  "status": "ACTIVE",
  "billable": true
}
```

#### Update Task

```bash
PUT /clockify/api/v1/workspaces/{workspaceId}/projects/{projectId}/tasks/{taskId}
Content-Type: application/json

{
  "name": "Updated task name",
  "status": "DONE"
}
```

#### Delete Task

```bash
DELETE /clockify/api/v1/workspaces/{workspaceId}/projects/{projectId}/tasks/{taskId}
```

**Note:** You cannot delete active tasks. Set `status: "DONE"` first.

### Time Entry Operations

#### Get User's Time Entries

```bash
GET /clockify/api/v1/workspaces/{workspaceId}/user/{userId}/time-entries
```

**Response:**
```json
[
  {
    "id": "698f7cc4aa9e9f33e5fc0180",
    "description": "Working on project",
    "userId": "698eeb9f5cd3a921db12069f",
    "billable": true,
    "projectId": "698f7cba4f748f6209ea8995",
    "taskId": null,
    "workspaceId": "698eeb9e5cd3a921db120693",
    "timeInterval": {
      "start": "2026-02-13T18:34:28Z",
      "end": "2026-02-13T19:34:28Z",
      "duration": "PT1H"
    }
  }
]
```

#### Create Time Entry

```bash
POST /clockify/api/v1/workspaces/{workspaceId}/time-entries
Content-Type: application/json

{
  "start": "2026-02-13T09:00:00Z",
  "end": "2026-02-13T10:00:00Z",
  "description": "Team meeting",
  "projectId": "project-id",
  "taskId": "task-id",
  "tagIds": ["tag-id-1", "tag-id-2"],
  "billable": true
}
```

#### Create Time Entry for Another User

```bash
POST /clockify/api/v1/workspaces/{workspaceId}/user/{userId}/time-entries
Content-Type: application/json

{
  "start": "2026-02-13T09:00:00Z",
  "end": "2026-02-13T10:00:00Z",
  "description": "Team meeting"
}
```

#### Get Time Entry

```bash
GET /clockify/api/v1/workspaces/{workspaceId}/time-entries/{timeEntryId}
```

#### Update Time Entry

```bash
PUT /clockify/api/v1/workspaces/{workspaceId}/time-entries/{timeEntryId}
Content-Type: application/json

{
  "start": "2026-02-13T09:00:00Z",
  "end": "2026-02-13T11:00:00Z",
  "description": "Extended meeting"
}
```

#### Delete Time Entry

```bash
DELETE /clockify/api/v1/workspaces/{workspaceId}/time-entries/{timeEntryId}
```

#### Stop Running Timer

```bash
PATCH /clockify/api/v1/workspaces/{workspaceId}/user/{userId}/time-entries
Content-Type: application/json

{
  "end": "2026-02-13T17:00:00Z"
}
```

#### Get In-Progress Time Entries

```bash
GET /clockify/api/v1/workspaces/{workspaceId}/time-entries
```

## Pagination

Clockify uses page-based pagination:

```bash
GET /clockify/api/v1/workspaces/{workspaceId}/projects?page=1&page-size=50
```

**Query Parameters:**
- `page` - Page number (1-indexed, default: 1)
- `page-size` - Items per page (default varies by endpoint)

Response includes a `Last-Page` header indicating if there are more pages.

## Code Examples

### JavaScript

```javascript
const response = await fetch(
  'https://gateway.maton.ai/clockify/api/v1/workspaces',
  {
    headers: {
      'Authorization': `Bearer ${process.env.MATON_API_KEY}`
    }
  }
);
const workspaces = await response.json();
```

### Python

```python
import os
import requests

response = requests.get(
    'https://gateway.maton.ai/clockify/api/v1/workspaces',
    headers={'Authorization': f'Bearer {os.environ["MATON_API_KEY"]}'}
)
workspaces = response.json()
```

### Create Time Entry (Python)

```python
import os
import requests
from datetime import datetime, timedelta, timezone

workspace_id = "your-workspace-id"
start_time = (datetime.now(timezone.utc) - timedelta(hours=1)).isoformat().replace('+00:00', 'Z')
end_time = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')

response = requests.post(
    f'https://gateway.maton.ai/clockify/api/v1/workspaces/{workspace_id}/time-entries',
    headers={
        'Authorization': f'Bearer {os.environ["MATON_API_KEY"]}',
        'Content-Type': 'application/json'
    },
    json={
        'start': start_time,
        'end': end_time,
        'description': 'Working on feature'
    }
)
```

## Notes

- All IDs are string identifiers
- Timestamps must be in ISO 8601 format with UTC timezone (e.g., `2026-02-13T09:00:00Z`)
- Duration format uses ISO 8601 duration (e.g., `PT1H` for 1 hour, `PT30M` for 30 minutes)
- Cannot delete active projects or tasks - must archive them first
- Rate limit: 50 requests per second per workspace
- IMPORTANT: When using curl commands, use `curl -g` when URLs contain brackets to disable glob parsing
- IMPORTANT: When piping curl output to `jq` or other commands, environment variables like `$MATON_API_KEY` may not expand correctly in some shell environments

## Error Handling

| Status | Meaning |
|--------|---------|
| 400 | Missing Clockify connection or invalid request |
| 401 | Invalid or missing Maton API key |
| 403 | Insufficient permissions |
| 404 | Resource not found |
| 429 | Rate limited (50 req/sec per workspace) |
| 4xx/5xx | Passthrough error from Clockify API |

### Troubleshooting: API Key Issues

1. Check that the `MATON_API_KEY` environment variable is set:

```bash
echo $MATON_API_KEY
```

2. Verify the API key is valid by listing connections:

```bash
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://ctrl.maton.ai/connections')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

### Troubleshooting: Invalid App Name

1. Ensure your URL path starts with `clockify`. For example:

- Correct: `https://gateway.maton.ai/clockify/api/v1/user`
- Incorrect: `https://gateway.maton.ai/api/v1/user`

## Resources

- [Clockify API Documentation](https://docs.clockify.me/)
- [Clockify API Reference](https://docs.clockify.me/#tag/Time-entry)
- [Maton Community](https://discord.com/invite/dBfFAcefs2)
- [Maton Support](mailto:support@maton.ai)
