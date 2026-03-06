---
name: toggl-track
description: |
  Toggl Track API integration with managed OAuth. Track time, manage projects, clients, and tags.
  Use this skill when users want to create, read, update, or delete time entries, projects, clients, or tags in Toggl Track.
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

# Toggl Track

Access the Toggl Track API with managed OAuth authentication. Track time, manage projects, clients, tags, and workspaces.

## Quick Start

```bash
# Get current user info
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://gateway.maton.ai/toggl-track/api/v9/me')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

## Base URL

```
https://gateway.maton.ai/toggl-track/{native-api-path}
```

Replace `{native-api-path}` with the actual Toggl Track API endpoint path. The gateway proxies requests to `api.track.toggl.com` and automatically injects your credentials.

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

Manage your Toggl Track OAuth connections at `https://ctrl.maton.ai`.

### List Connections

```bash
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://ctrl.maton.ai/connections?app=toggl-track&status=ACTIVE')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

### Create Connection

```bash
python <<'EOF'
import urllib.request, os, json
data = json.dumps({'app': 'toggl-track'}).encode()
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
    "connection_id": "0acc2145-4d3e-4eaf-bdfd-7b04e0e0d649",
    "status": "ACTIVE",
    "creation_time": "2026-02-13T19:31:31.452264Z",
    "last_updated_time": "2026-02-13T19:36:10.489069Z",
    "url": "https://connect.maton.ai/?session_token=...",
    "app": "toggl-track",
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

If you have multiple Toggl Track connections, specify which one to use with the `Maton-Connection` header:

```bash
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://gateway.maton.ai/toggl-track/api/v9/me')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
req.add_header('Maton-Connection', '0acc2145-4d3e-4eaf-bdfd-7b04e0e0d649')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

If omitted, the gateway uses the default (oldest) active connection.

## API Reference

### User & Workspace

#### Get Current User

```bash
GET /toggl-track/api/v9/me
```

**Response:**
```json
{
  "id": 12932942,
  "email": "user@example.com",
  "fullname": "John Doe",
  "timezone": "America/Los_Angeles",
  "default_workspace_id": 21180405,
  "beginning_of_week": 1,
  "image_url": "https://assets.track.toggl.com/images/profile.png"
}
```

#### List Workspaces

```bash
GET /toggl-track/api/v9/me/workspaces
```

#### Get Workspace

```bash
GET /toggl-track/api/v9/workspaces/{workspace_id}
```

#### List Workspace Users

```bash
GET /toggl-track/api/v9/workspaces/{workspace_id}/users
```

### Time Entries

#### List Time Entries

```bash
GET /toggl-track/api/v9/me/time_entries
```

**Query Parameters:**
- `since` (integer) - UNIX timestamp for entries modified after this time
- `before` (string) - Get entries before this date (RFC3339 or YYYY-MM-DD)
- `start_date` (string) - Filter start date (YYYY-MM-DD)
- `end_date` (string) - Filter end date (YYYY-MM-DD)

#### Get Current (Running) Time Entry

```bash
GET /toggl-track/api/v9/me/time_entries/current
```

Returns `null` if no time entry is currently running.

#### Get Time Entry by ID

```bash
GET /toggl-track/api/v9/me/time_entries/{time_entry_id}
```

#### Create Time Entry

```bash
POST /toggl-track/api/v9/workspaces/{workspace_id}/time_entries
Content-Type: application/json

{
  "description": "Working on project",
  "start": "2026-02-13T10:00:00Z",
  "duration": -1,
  "workspace_id": 21180405,
  "project_id": 216896134,
  "tag_ids": [20053808],
  "created_with": "maton-api"
}
```

**Note:** Set `duration` to `-1` to start a running timer. The `created_with` field is required.

**Response:**
```json
{
  "id": 4290254971,
  "workspace_id": 21180405,
  "project_id": null,
  "task_id": null,
  "billable": false,
  "start": "2026-02-13T19:58:43Z",
  "stop": null,
  "duration": -1,
  "description": "Working on project",
  "tags": null,
  "tag_ids": null,
  "user_id": 12932942
}
```

#### Update Time Entry

```bash
PUT /toggl-track/api/v9/workspaces/{workspace_id}/time_entries/{time_entry_id}
Content-Type: application/json

{
  "description": "Updated description",
  "project_id": 216896134
}
```

#### Stop Running Time Entry

```bash
PATCH /toggl-track/api/v9/workspaces/{workspace_id}/time_entries/{time_entry_id}/stop
```

#### Delete Time Entry

```bash
DELETE /toggl-track/api/v9/workspaces/{workspace_id}/time_entries/{time_entry_id}
```

### Projects

#### List Projects

```bash
GET /toggl-track/api/v9/workspaces/{workspace_id}/projects
```

**Query Parameters:**
- `active` (boolean) - Filter by active status
- `since` (integer) - UNIX timestamp for modification filter
- `name` (string) - Filter by project name
- `page` (integer) - Page number
- `per_page` (integer) - Items per page (max 200)

#### Get Project

```bash
GET /toggl-track/api/v9/workspaces/{workspace_id}/projects/{project_id}
```

#### Create Project

```bash
POST /toggl-track/api/v9/workspaces/{workspace_id}/projects
Content-Type: application/json

{
  "name": "New Project",
  "active": true,
  "is_private": true,
  "client_id": 68493239,
  "color": "#0b83d9",
  "billable": true
}
```

**Response:**
```json
{
  "id": 216896134,
  "workspace_id": 21180405,
  "client_id": null,
  "name": "New Project",
  "is_private": true,
  "active": true,
  "color": "#0b83d9",
  "billable": true,
  "created_at": "2026-02-13T19:58:36+00:00"
}
```

#### Update Project

```bash
PUT /toggl-track/api/v9/workspaces/{workspace_id}/projects/{project_id}
Content-Type: application/json

{
  "name": "Updated Project Name",
  "color": "#ff0000"
}
```

#### Delete Project

```bash
DELETE /toggl-track/api/v9/workspaces/{workspace_id}/projects/{project_id}
```

### Clients

#### List Clients

```bash
GET /toggl-track/api/v9/workspaces/{workspace_id}/clients
```

**Query Parameters:**
- `status` (string) - Filter: `active`, `archived`, or `both`
- `name` (string) - Case-insensitive name filter

#### Get Client

```bash
GET /toggl-track/api/v9/workspaces/{workspace_id}/clients/{client_id}
```

#### Create Client

```bash
POST /toggl-track/api/v9/workspaces/{workspace_id}/clients
Content-Type: application/json

{
  "name": "New Client",
  "notes": "Client notes here"
}
```

**Response:**
```json
{
  "id": 68493239,
  "wid": 21180405,
  "archived": false,
  "name": "New Client",
  "at": "2026-02-13T19:58:36+00:00",
  "creator_id": 12932942
}
```

#### Update Client

```bash
PUT /toggl-track/api/v9/workspaces/{workspace_id}/clients/{client_id}
Content-Type: application/json

{
  "name": "Updated Client Name"
}
```

#### Delete Client

```bash
DELETE /toggl-track/api/v9/workspaces/{workspace_id}/clients/{client_id}
```

#### Archive Client

```bash
POST /toggl-track/api/v9/workspaces/{workspace_id}/clients/{client_id}/archive
```

#### Restore Client

```bash
POST /toggl-track/api/v9/workspaces/{workspace_id}/clients/{client_id}/restore
Content-Type: application/json

{
  "restore_all_projects": true
}
```

### Tags

#### List Tags

```bash
GET /toggl-track/api/v9/workspaces/{workspace_id}/tags
```

**Query Parameters:**
- `page` (integer) - Page number
- `per_page` (integer) - Items per page

#### Create Tag

```bash
POST /toggl-track/api/v9/workspaces/{workspace_id}/tags
Content-Type: application/json

{
  "name": "New Tag"
}
```

**Response:**
```json
{
  "id": 20053808,
  "workspace_id": 21180405,
  "name": "New Tag",
  "at": "2026-02-13T19:58:37.115714Z",
  "creator_id": 12932942
}
```

#### Update Tag

```bash
PUT /toggl-track/api/v9/workspaces/{workspace_id}/tags/{tag_id}
Content-Type: application/json

{
  "name": "Updated Tag Name"
}
```

#### Delete Tag

```bash
DELETE /toggl-track/api/v9/workspaces/{workspace_id}/tags/{tag_id}
```

## Pagination

Toggl Track uses page-based pagination for most list endpoints:

```bash
GET /toggl-track/api/v9/workspaces/{workspace_id}/projects?page=1&per_page=50
```

For time entries, use timestamp-based filtering:

```bash
GET /toggl-track/api/v9/me/time_entries?since=1707840000&start_date=2026-02-01&end_date=2026-02-28
```

## Code Examples

### JavaScript

```javascript
const response = await fetch(
  'https://gateway.maton.ai/toggl-track/api/v9/me/time_entries',
  {
    headers: {
      'Authorization': `Bearer ${process.env.MATON_API_KEY}`
    }
  }
);
const timeEntries = await response.json();
```

### Python

```python
import os
import requests

response = requests.get(
    'https://gateway.maton.ai/toggl-track/api/v9/me/time_entries',
    headers={'Authorization': f'Bearer {os.environ["MATON_API_KEY"]}'}
)
time_entries = response.json()
```

### Start a Timer

```python
import os
import requests
from datetime import datetime, timezone

response = requests.post(
    'https://gateway.maton.ai/toggl-track/api/v9/workspaces/21180405/time_entries',
    headers={
        'Authorization': f'Bearer {os.environ["MATON_API_KEY"]}',
        'Content-Type': 'application/json'
    },
    json={
        'description': 'Working on task',
        'start': datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
        'duration': -1,
        'workspace_id': 21180405,
        'created_with': 'maton-api'
    }
)
```

## Notes

- Workspace IDs are integers (e.g., `21180405`)
- Time entry IDs are large integers (e.g., `4290254971`)
- Duration is in seconds; use `-1` for running timers
- Timestamps use ISO 8601 format (e.g., `2026-02-13T19:58:43Z`)
- The `created_with` field is required when creating time entries
- IMPORTANT: When using curl commands, use `curl -g` when URLs contain brackets to disable glob parsing
- IMPORTANT: When piping curl output to `jq` or other commands, environment variables like `$MATON_API_KEY` may not expand correctly in some shell environments

## Error Handling

| Status | Meaning |
|--------|---------|
| 400 | Missing Toggl Track connection or invalid request |
| 401 | Invalid or missing Maton API key |
| 403 | Access denied |
| 404 | Resource not found |
| 429 | Rate limited |
| 4xx/5xx | Passthrough error from Toggl Track API |

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

1. Ensure your URL path starts with `toggl-track`. For example:

- Correct: `https://gateway.maton.ai/toggl-track/api/v9/me`
- Incorrect: `https://gateway.maton.ai/api/v9/me`

## Resources

- [Toggl Track API Documentation](https://engineering.toggl.com/docs/)
- [Toggl Track API Reference](https://engineering.toggl.com/docs/api/)
- [Time Entries API](https://engineering.toggl.com/docs/api/time_entries)
- [Projects API](https://engineering.toggl.com/docs/api/projects)
- [Clients API](https://engineering.toggl.com/docs/api/clients)
- [Tags API](https://engineering.toggl.com/docs/api/tags)
- [Maton Community](https://discord.com/invite/dBfFAcefs2)
- [Maton Support](mailto:support@maton.ai)
