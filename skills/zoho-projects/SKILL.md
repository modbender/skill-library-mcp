---
name: zohoprojects
description: |
  Zoho Projects API integration with managed OAuth. Manage projects, tasks, milestones, tasklists, and team collaboration.
  Use this skill when users want to manage project tasks, track time, organize milestones, or collaborate on projects.
  For other third party apps, use the api-gateway skill (https://clawhub.ai/byungkyu/api-gateway).
compatibility: Requires network access and valid Maton API key
metadata:
  author: maton
  version: "1.0"
  clawdbot:
    emoji:
    homepage: "https://maton.ai"
    requires:
      env:
        - MATON_API_KEY
---

# Zoho Projects

Access the Zoho Projects API with managed OAuth authentication. Manage projects, tasks, milestones, tasklists, and team collaboration.

## Quick Start

```bash
# List all portals
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://gateway.maton.ai/zoho-projects/restapi/portals/')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

## Base URL

```
https://gateway.maton.ai/zoho-projects/{native-api-path}
```

Replace `{native-api-path}` with the actual Zoho Projects API endpoint path. The gateway proxies requests to `projectsapi.zoho.com` and automatically injects your OAuth token.

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

Manage your Zoho Projects OAuth connections at `https://ctrl.maton.ai`.

### List Connections

```bash
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://ctrl.maton.ai/connections?app=zoho-projects&status=ACTIVE')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

### Create Connection

```bash
python <<'EOF'
import urllib.request, os, json
data = json.dumps({'app': 'zoho-projects'}).encode()
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
    "connection_id": "522c11a9-b879-4504-b267-355e3dbac99f",
    "status": "ACTIVE",
    "creation_time": "2026-02-28T00:12:25.223434Z",
    "last_updated_time": "2026-02-28T00:16:32.882675Z",
    "url": "https://connect.maton.ai/?session_token=...",
    "app": "zoho-projects",
    "metadata": {},
    "method": "OAUTH2"
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

If you have multiple Zoho Projects connections, specify which one to use with the `Maton-Connection` header:

```bash
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://gateway.maton.ai/zoho-projects/restapi/portals/')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
req.add_header('Maton-Connection', '522c11a9-b879-4504-b267-355e3dbac99f')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

If omitted, the gateway uses the default (oldest) active connection.

## API Reference

### Portals

#### List Portals

```bash
GET /zoho-projects/restapi/portals/
```

**Response:**
```json
{
  "portals": [
    {
      "id": 916020774,
      "id_string": "916020774",
      "name": "nunchidotapp",
      "plan": "Ultimate",
      "role": "admin",
      "project_count": {"active": 1}
    }
  ]
}
```

#### Get Portal Details

```bash
GET /zoho-projects/restapi/portal/{portal_id}/
```

---

### Projects

#### List Projects

```bash
GET /zoho-projects/restapi/portal/{portal_id}/projects/
```

Query parameters: `index`, `range`, `status`, `sort_column`, `sort_order`

**Response:**
```json
{
  "projects": [
    {
      "id": 2644874000000089119,
      "name": "My Project",
      "status": "active",
      "owner_name": "Byungkyu Park",
      "task_count": {"open": 3, "closed": 0},
      "project_percent": "0"
    }
  ]
}
```

#### Get Project Details

```bash
GET /zoho-projects/restapi/portal/{portal_id}/projects/{project_id}/
```

#### Create Project

```bash
POST /zoho-projects/restapi/portal/{portal_id}/projects/
Content-Type: application/x-www-form-urlencoded

name=New+Project&owner={user_id}&description=Project+description
```

Required: `name`
Optional: `owner`, `description`, `start_date`, `end_date`, `template_id`, `group_id`

**Response:**
```json
{
  "projects": [
    {
      "id": 2644874000000096003,
      "name": "New Project",
      "status": "active"
    }
  ]
}
```

#### Update Project

```bash
POST /zoho-projects/restapi/portal/{portal_id}/projects/{project_id}/
Content-Type: application/x-www-form-urlencoded

name=Updated+Name&status=active
```

#### Delete Project

```bash
DELETE /zoho-projects/restapi/portal/{portal_id}/projects/{project_id}/
```

**Response:**
```json
{"response": "Project Trashed successfully"}
```

---

### Tasks

#### List Tasks

```bash
GET /zoho-projects/restapi/portal/{portal_id}/projects/{project_id}/tasks/
```

Query parameters: `index`, `range`, `owner`, `status`, `priority`, `tasklist_id`, `sort_column`

**Response:**
```json
{
  "tasks": [
    {
      "id": 2644874000000089255,
      "name": "Task 3",
      "status": {"name": "Open", "type": "open"},
      "priority": "None",
      "completed": false,
      "tasklist": {"name": "General", "id": "2644874000000089245"}
    }
  ]
}
```

#### Get Task Details

```bash
GET /zoho-projects/restapi/portal/{portal_id}/projects/{project_id}/tasks/{task_id}/
```

#### Get My Tasks

```bash
GET /zoho-projects/restapi/portal/{portal_id}/mytasks/
```

Query parameters: `index`, `range`, `owner`, `status`, `priority`, `projects_ids`

#### Create Task

```bash
POST /zoho-projects/restapi/portal/{portal_id}/projects/{project_id}/tasks/
Content-Type: application/x-www-form-urlencoded

name=New+Task&tasklist_id={tasklist_id}&priority=High
```

Required: `name`
Optional: `person_responsible`, `tasklist_id`, `start_date`, `end_date`, `priority`, `description`

**Response:**
```json
{
  "tasks": [
    {
      "id": 2644874000000094001,
      "key": "EZ1-T4",
      "name": "New Task",
      "status": {"name": "Open", "type": "open"}
    }
  ]
}
```

#### Update Task

```bash
POST /zoho-projects/restapi/portal/{portal_id}/projects/{project_id}/tasks/{task_id}/
Content-Type: application/x-www-form-urlencoded

name=Updated+Name&priority=High&percent_complete=50
```

#### Delete Task

```bash
DELETE /zoho-projects/restapi/portal/{portal_id}/projects/{project_id}/tasks/{task_id}/
```

**Response:**
```json
{"response": "Task Trashed successfully"}
```

---

### Task Comments

#### List Comments

```bash
GET /zoho-projects/restapi/portal/{portal_id}/projects/{project_id}/tasks/{task_id}/comments/
```

#### Add Comment

```bash
POST /zoho-projects/restapi/portal/{portal_id}/projects/{project_id}/tasks/{task_id}/comments/
Content-Type: application/x-www-form-urlencoded

content=This+is+a+comment
```

**Response:**
```json
{
  "comments": [
    {
      "id": 2644874000000094015,
      "content": "This is a comment",
      "added_person": "Byungkyu Park"
    }
  ]
}
```

#### Update Comment

```bash
POST /zoho-projects/restapi/portal/{portal_id}/projects/{project_id}/tasks/{task_id}/comments/{comment_id}/
Content-Type: application/x-www-form-urlencoded

content=Updated+comment
```

#### Delete Comment

```bash
DELETE /zoho-projects/restapi/portal/{portal_id}/projects/{project_id}/tasks/{task_id}/comments/{comment_id}/
```

---

### Tasklists

#### List Tasklists

```bash
GET /zoho-projects/restapi/portal/{portal_id}/projects/{project_id}/tasklists/
```

Query parameters: `index`, `range`, `flag`, `milestone_id`, `sort_column`

**Response:**
```json
{
  "tasklists": [
    {
      "id": 2644874000000089245,
      "name": "General",
      "flag": "internal",
      "is_default": true,
      "task_count": {"open": 3}
    }
  ]
}
```

#### Create Tasklist

```bash
POST /zoho-projects/restapi/portal/{portal_id}/projects/{project_id}/tasklists/
Content-Type: application/x-www-form-urlencoded

name=New+Tasklist&flag=internal
```

Required: `name`
Optional: `milestone_id`, `flag`

#### Update Tasklist

```bash
POST /zoho-projects/restapi/portal/{portal_id}/projects/{project_id}/tasklists/{tasklist_id}/
Content-Type: application/x-www-form-urlencoded

name=Updated+Name&milestone_id={milestone_id}
```

#### Delete Tasklist

```bash
DELETE /zoho-projects/restapi/portal/{portal_id}/projects/{project_id}/tasklists/{tasklist_id}/
```

**Response:**
```json
{"response": "Tasklist Trashed successfully"}
```

---

### Milestones

#### List Milestones

```bash
GET /zoho-projects/restapi/portal/{portal_id}/projects/{project_id}/milestones/
```

Query parameters: `index`, `range`, `status`, `flag`, `sort_column`

**Note:** Returns 204 No Content if no milestones exist.

#### Create Milestone

```bash
POST /zoho-projects/restapi/portal/{portal_id}/projects/{project_id}/milestones/
Content-Type: application/x-www-form-urlencoded

name=Phase+1&start_date=03-01-2026&end_date=03-15-2026&owner={user_id}&flag=internal
```

Required: `name`, `start_date`, `end_date`, `owner`, `flag`

**Response:**
```json
{
  "milestones": [
    {
      "id": 2644874000000096133,
      "name": "Phase 1",
      "start_date": "03-01-2026",
      "end_date": "03-15-2026",
      "status": "notcompleted"
    }
  ]
}
```

#### Update Milestone

```bash
POST /zoho-projects/restapi/portal/{portal_id}/projects/{project_id}/milestones/{milestone_id}/
Content-Type: application/x-www-form-urlencoded

name=Updated+Phase&start_date=03-01-2026&end_date=03-20-2026&owner={user_id}&flag=internal
```

#### Update Milestone Status

```bash
POST /zoho-projects/restapi/portal/{portal_id}/projects/{project_id}/milestones/{milestone_id}/status/
Content-Type: application/x-www-form-urlencoded

status=2
```

Status values: `1` = not completed, `2` = completed

#### Delete Milestone

```bash
DELETE /zoho-projects/restapi/portal/{portal_id}/projects/{project_id}/milestones/{milestone_id}/
```

**Response:**
```json
{"response": "Milestone Trashed successfully"}
```

---

### Users

#### List Users

```bash
GET /zoho-projects/restapi/portal/{portal_id}/users/
```

**Response:**
```json
{
  "users": [
    {
      "id": "801698114",
      "zpuid": "2644874000000085003",
      "name": "Byungkyu Park",
      "email": "byungkyu@example.com",
      "role_name": "Administrator",
      "active": true
    }
  ]
}
```

---

### Project Groups

#### List Groups

```bash
GET /zoho-projects/restapi/portal/{portal_id}/projects/groups
```

**Response:**
```json
{
  "groups": [
    {
      "id": "2644874000000018001",
      "name": "Ungrouped Projects",
      "is_default": "true"
    }
  ]
}
```

#### Create Group

```bash
POST /zoho-projects/restapi/portal/{portal_id}/projectgroups
Content-Type: application/x-www-form-urlencoded

name=New+Group
```

---

## Pagination

Use `index` and `range` parameters for pagination:

```bash
GET /zoho-projects/restapi/portal/{portal_id}/projects/{project_id}/tasks/?index=1&range=50
```

- `index`: Starting record number (1-based)
- `range`: Number of records to return

## Code Examples

### JavaScript

```javascript
// List tasks in a project
const response = await fetch(
  'https://gateway.maton.ai/zoho-projects/restapi/portal/916020774/projects/2644874000000089119/tasks/',
  {
    headers: {
      'Authorization': `Bearer ${process.env.MATON_API_KEY}`
    }
  }
);
const data = await response.json();
console.log(data.tasks);
```

### Python

```python
import os
import requests

# Create a task
response = requests.post(
    'https://gateway.maton.ai/zoho-projects/restapi/portal/916020774/projects/2644874000000089119/tasks/',
    headers={
        'Authorization': f'Bearer {os.environ["MATON_API_KEY"]}',
        'Content-Type': 'application/x-www-form-urlencoded'
    },
    data={'name': 'New Task', 'priority': 'High'}
)
task = response.json()
print(task['tasks'][0]['id'])
```

## Notes

- All POST requests for create/update use `application/x-www-form-urlencoded` content type, not JSON
- Portal ID is required for most endpoints and can be obtained from `GET /restapi/portals/`
- Date format is `MM-dd-yyyy` (e.g., `03-01-2026`)
- Milestone creation requires all fields: `name`, `start_date`, `end_date`, `owner`, `flag`
- Empty list responses return HTTP 204 No Content
- Deleted items are moved to trash, not permanently deleted

## Error Handling

| Status | Meaning |
|--------|---------|
| 204 | No content (empty list) |
| 400 | Missing/invalid input parameter |
| 401 | Invalid or missing Maton API key |
| 404 | Resource not found |
| 429 | Rate limited (100 requests per 2 minutes) |
| 4xx/5xx | Passthrough error from Zoho Projects API |

Common error codes:
- `6831`: Input Parameter Missing
- `6832`: Input Parameter Does not Match the Pattern Specified

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

Ensure your URL path starts with `zoho-projects`. For example:

- Correct: `https://gateway.maton.ai/zoho-projects/restapi/portals/`
- Incorrect: `https://gateway.maton.ai/restapi/portals/`

## Resources

- [Zoho Projects API Documentation](https://www.zoho.com/projects/help/rest-api/zohoprojectsapi.html)
- [Projects API](https://www.zoho.com/projects/help/rest-api/projects-api.html)
- [Tasks API](https://www.zoho.com/projects/help/rest-api/tasks-api.html)
- [Milestones API](https://www.zoho.com/projects/help/rest-api/milestones-api.html)
- [Maton Community](https://discord.com/invite/dBfFAcefs2)
- [Maton Support](mailto:support@maton.ai)
