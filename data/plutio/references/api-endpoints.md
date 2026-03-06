# Plutio API Endpoints Reference

**Base URL**: `https://api.plutio.com/v1.8/`

**Authentication**: OAuth 2.0 (app key + secret → access token)

**Rate Limit**: 1000 calls/hour

## Authentication

### Generate Access Token

```
POST /tokens
Content-Type: application/json

{
  "appKey": "YOUR_APP_KEY",
  "secret": "YOUR_SECRET",
  "subdomain": "your-subdomain"
}
```

**Response** (200 OK):
```json
{
  "accessToken": "token_string",
  "expiresIn": 3600,
  "tokenType": "Bearer"
}
```

**Headers for subsequent requests**:
```
Authorization: Bearer {accessToken}
YOUR_PLUTIO_SUBDOMAIN: your-subdomain
```

---

## Projects

### List Projects

```
GET /projects?skip=0&limit=50
```

**Query Parameters**:
- `skip` - Number of items to skip (default: 0)
- `limit` - Max items to return (default: 50, max: 100)

**Response** (200 OK):
```json
{
  "data": [
    {
      "_id": "project_id",
      "name": "Project Name",
      "description": "Project description",
      "status": "active",
      "owner": {
        "_id": "person_id",
        "name": "Owner Name"
      },
      "createdAt": "2026-01-01T10:00:00Z",
      "updatedAt": "2026-03-01T15:30:00Z"
    }
  ],
  "total": 5
}
```

### Get Single Project

```
GET /projects/{projectId}
```

**Response** (200 OK): Same structure as list, single object

---

## Tasks

### List Tasks (in a Project)

```
GET /tasks?projectId={projectId}&skip=0&limit=50
```

**Query Parameters**:
- `projectId` - Required, filter by project
- `skip` - Number of items to skip
- `limit` - Max items to return
- `status` - Optional filter (e.g., `status=open`)

**Response** (200 OK):
```json
{
  "data": [
    {
      "_id": "task_id",
      "title": "Task Title",
      "description": "Task description",
      "projectId": "project_id",
      "status": "open",
      "priority": "high",
      "assigneeId": "person_id",
      "assignee": {
        "_id": "person_id",
        "name": "Assignee Name"
      },
      "dueDate": "2026-03-15T00:00:00Z",
      "labels": ["label_id_1"],
      "customFields": {},
      "createdAt": "2026-01-01T10:00:00Z",
      "updatedAt": "2026-03-01T15:30:00Z"
    }
  ],
  "total": 12
}
```

### Get Single Task

```
GET /tasks/{taskId}
```

**Response** (200 OK): Same structure as list, single object

### Create Task

```
POST /tasks
Content-Type: application/json

{
  "projectId": "project_id",
  "title": "New Task",
  "description": "Task details",
  "status": "open",
  "priority": "medium",
  "assigneeId": "person_id",
  "dueDate": "2026-03-15T00:00:00Z",
  "labelIds": ["label_id_1", "label_id_2"],
  "customFields": {
    "custom_field_id": "field_value"
  }
}
```

**Required Fields**:
- `projectId`
- `title`

**Optional Fields**:
- `description` - Task details
- `status` - `open`, `in_progress`, `closed`, or custom status name
- `priority` - `low`, `medium`, `high`, `urgent`
- `assigneeId` - Person ID
- `dueDate` - ISO 8601 format (YYYY-MM-DD or YYYY-MM-DDTHH:MM:SSZ)
- `labelIds` - Array of label IDs
- `customFields` - Object with custom field ID → value mapping

**Response** (201 Created):
```json
{
  "_id": "new_task_id",
  "title": "New Task",
  ...
}
```

### Update Task

```
PUT /tasks/{taskId}
Content-Type: application/json

{
  "title": "Updated Title",
  "status": "closed",
  "priority": "high",
  "assigneeId": "person_id",
  "dueDate": "2026-03-20T00:00:00Z",
  "customFields": {
    "custom_field_id": "new_value"
  }
}
```

**Response** (200 OK):
```json
{
  "_id": "task_id",
  "title": "Updated Title",
  ...
}
```

### Delete Task

```
DELETE /tasks/{taskId}
```

**Response** (204 No Content)

---

## People (Users)

### List People (in workspace)

```
GET /people?skip=0&limit=50
```

**Response** (200 OK):
```json
{
  "data": [
    {
      "_id": "person_id",
      "name": {
        "first": "John",
        "last": "Doe"
      },
      "email": "john@example.com",
      "role": "admin",
      "status": "active"
    }
  ],
  "total": 5
}
```

### Get Single Person

```
GET /people/{personId}
```

---

## Status Codes

| Code | Meaning |
|------|---------|
| 200 | OK - Request succeeded |
| 201 | Created - Resource created successfully |
| 204 | No Content - Request succeeded, no response body |
| 400 | Bad Request - Invalid parameters or request format |
| 401 | Unauthorized - Missing or invalid access token |
| 403 | Forbidden - User lacks permission for this action |
| 404 | Not Found - Resource doesn't exist |
| 405 | Method Not Allowed - Wrong HTTP method for endpoint |
| 429 | Too Many Requests - Rate limit exceeded (1000/hour) |
| 500 | Internal Server Error - Plutio server error |

---

## Pagination Example

To fetch all tasks across multiple pages:

```bash
# First page
GET /tasks?projectId=xyz&skip=0&limit=50

# Next page (if total > 50)
GET /tasks?projectId=xyz&skip=50&limit=50

# Continue until: skip + limit >= total
```

---

## Field Descriptions

### Task Status
- `open` - Task not started
- `in_progress` - Work in progress
- `closed` - Task completed
- Custom status names are supported if configured in Plutio

### Task Priority
- `low` - Low priority
- `medium` - Medium priority (default)
- `high` - High priority
- `urgent` - Urgent priority

### Date Format
- ISO 8601: `YYYY-MM-DD` or `YYYY-MM-DDTHH:MM:SSZ`
- Example: `2026-03-15` or `2026-03-15T14:30:00Z`

### Custom Fields
Custom fields are workspace-specific. To use them:
1. Get field ID from your Plutio workspace settings
2. Pass as `customFields: { "field_id": "value" }`
3. Value type depends on field configuration (text, date, dropdown, etc.)

---

## Error Response Format

```json
{
  "error": "Error message describing what went wrong",
  "code": "ERROR_CODE",
  "details": {}
}
```

---

*Reference last updated: 2026-03-01*
