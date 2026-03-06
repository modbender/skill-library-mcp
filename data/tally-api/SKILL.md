---
name: tally
description: |
  Tally API integration with managed OAuth. Manage forms, submissions, workspaces, and webhooks.
  Use this skill when users want to create or manage Tally forms, retrieve form submissions, or work with workspaces.
  For other third party apps, use the api-gateway skill (https://clawhub.ai/byungkyu/api-gateway).
  Requires network access and valid Maton API key.
metadata:
  author: maton
  version: "1.0"
  clawdbot:
    emoji: 🧠
    requires:
      env:
        - MATON_API_KEY
---

# Tally

Access the Tally API with managed OAuth authentication. Manage forms, submissions, workspaces, and webhooks for your Tally account.

## Quick Start

```bash
# List your forms
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://gateway.maton.ai/tally/forms')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
req.add_header('User-Agent', 'Maton/1.0')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

## Base URL

```
https://gateway.maton.ai/tally/{native-api-path}
```

Replace `{native-api-path}` with the actual Tally API endpoint path. The gateway proxies requests to `api.tally.so` and automatically injects your OAuth token.

## Authentication

All requests require the Maton API key in the Authorization header and the User Agent header:

```
Authorization: Bearer $MATON_API_KEY
User-Agent: Maton/1.0
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

Manage your Tally OAuth connections at `https://ctrl.maton.ai`.

### List Connections

```bash
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://ctrl.maton.ai/connections?app=tally&status=ACTIVE')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

### Create Connection

```bash
python <<'EOF'
import urllib.request, os, json
data = json.dumps({'app': 'tally'}).encode()
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
    "connection_id": "cd54e2b0-f1d0-435e-a97d-f2d6a5c474bf",
    "status": "ACTIVE",
    "creation_time": "2026-02-07T21:00:31.222600Z",
    "last_updated_time": "2026-02-07T21:00:37.821240Z",
    "url": "https://connect.maton.ai/?session_token=...",
    "app": "tally",
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

If you have multiple Tally connections, specify which one to use with the `Maton-Connection` header:

```bash
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://gateway.maton.ai/tally/forms')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
req.add_header('Maton-Connection', 'cd54e2b0-f1d0-435e-a97d-f2d6a5c474bf')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

If omitted, the gateway uses the default (oldest) active connection.

## API Reference

### User

#### Get Current User

```bash
GET /tally/users/me
```

**Response:**
```json
{
  "id": "w2lBkb",
  "firstName": "John",
  "lastName": "Doe",
  "email": "john@example.com",
  "organizationId": "n0Ze8Q",
  "subscriptionPlan": "FREE",
  "createdAt": "2026-02-07T20:58:54.000Z",
  "updatedAt": "2026-02-07T22:50:35.000Z"
}
```

### Forms

#### List Forms

```bash
GET /tally/forms
```

**Query Parameters:**
- `page` - Page number (default: 1)
- `limit` - Items per page (default: 50)

**Response:**
```json
{
  "items": [
    {
      "id": "GxdRaQ",
      "name": "Contact Form",
      "workspaceId": "3jW9Q1",
      "organizationId": "n0Ze8Q",
      "status": "PUBLISHED",
      "hasDraftBlocks": false,
      "numberOfSubmissions": 42,
      "createdAt": "2026-02-09T08:36:00.000Z",
      "updatedAt": "2026-02-09T08:36:17.000Z",
      "isClosed": false
    }
  ],
  "page": 1,
  "limit": 50,
  "total": 1,
  "hasMore": false
}
```

#### Get Form

```bash
GET /tally/forms/{formId}
```

**Response:**
```json
{
  "id": "GxdRaQ",
  "name": "Contact Form",
  "workspaceId": "3jW9Q1",
  "status": "PUBLISHED",
  "blocks": [
    {
      "uuid": "11111111-1111-1111-1111-111111111111",
      "type": "FORM_TITLE",
      "groupUuid": "22222222-2222-2222-2222-222222222222",
      "groupType": "FORM_TITLE",
      "payload": {}
    },
    {
      "uuid": "33333333-3333-3333-3333-333333333333",
      "type": "INPUT_TEXT",
      "groupUuid": "44444444-4444-4444-4444-444444444444",
      "groupType": "INPUT_TEXT",
      "payload": {}
    }
  ],
  "settings": null
}
```

#### Create Form

```bash
POST /tally/forms
Content-Type: application/json

{
  "status": "DRAFT",
  "workspaceId": "3jW9Q1",
  "blocks": [
    {
      "type": "FORM_TITLE",
      "uuid": "11111111-1111-1111-1111-111111111111",
      "groupUuid": "22222222-2222-2222-2222-222222222222",
      "groupType": "FORM_TITLE",
      "title": "My Form",
      "payload": {}
    },
    {
      "type": "INPUT_TEXT",
      "uuid": "33333333-3333-3333-3333-333333333333",
      "groupUuid": "44444444-4444-4444-4444-444444444444",
      "groupType": "INPUT_TEXT",
      "title": "Your name",
      "payload": {}
    }
  ]
}
```

**Block Types:**
- `FORM_TITLE` - Form title block
- `INPUT_TEXT` - Single-line text input
- `INPUT_EMAIL` - Email input
- `INPUT_NUMBER` - Number input
- `INPUT_PHONE_NUMBER` - Phone number input
- `INPUT_DATE` - Date picker
- `INPUT_TIME` - Time picker
- `INPUT_LINK` - URL input
- `TEXTAREA` - Multi-line text input
- `MULTIPLE_CHOICE` - Radio buttons
- `CHECKBOXES` - Checkbox group
- `DROPDOWN` - Dropdown select
- `LINEAR_SCALE` - Scale rating
- `RATING` - Star rating
- `FILE_UPLOAD` - File upload
- `SIGNATURE` - Signature field
- `PAYMENT` - Payment field
- `HIDDEN_FIELDS` - Hidden fields

**Note:** Block `uuid` and `groupUuid` must be valid UUIDs (GUIDs).

#### Update Form

```bash
PATCH /tally/forms/{formId}
Content-Type: application/json

{
  "name": "Updated Form Name",
  "status": "PUBLISHED"
}
```

**Status Values:**
- `DRAFT` - Form is a draft
- `PUBLISHED` - Form is live

#### Delete Form

```bash
DELETE /tally/forms/{formId}
```

Moves the form to trash.

### Form Questions

#### List Questions

```bash
GET /tally/forms/{formId}/questions
```

**Response:**
```json
{
  "questions": [
    {
      "uuid": "33333333-3333-3333-3333-333333333333",
      "type": "INPUT_TEXT",
      "title": "Your name"
    }
  ],
  "hasResponses": true
}
```

### Form Submissions

#### List Submissions

```bash
GET /tally/forms/{formId}/submissions
```

**Query Parameters:**
- `page` - Page number (default: 1)
- `limit` - Items per page (default: 50)
- `startDate` - Filter by start date (ISO 8601)
- `endDate` - Filter by end date (ISO 8601)
- `afterId` - Get submissions after this ID (cursor pagination)

**Response:**
```json
{
  "page": 1,
  "limit": 50,
  "hasMore": false,
  "totalNumberOfSubmissionsPerFilter": {
    "all": 42,
    "completed": 40,
    "partial": 2
  },
  "questions": [
    {
      "uuid": "33333333-3333-3333-3333-333333333333",
      "type": "INPUT_TEXT",
      "title": "Your name"
    }
  ],
  "submissions": [
    {
      "id": "sub123",
      "respondentId": "resp456",
      "formId": "GxdRaQ",
      "createdAt": "2026-02-09T10:00:00.000Z",
      "isCompleted": true,
      "responses": [
        {
          "questionId": "33333333-3333-3333-3333-333333333333",
          "value": "John Doe"
        }
      ]
    }
  ]
}
```

#### Get Submission

```bash
GET /tally/forms/{formId}/submissions/{submissionId}
```

#### Delete Submission

```bash
DELETE /tally/forms/{formId}/submissions/{submissionId}
```

### Workspaces

#### List Workspaces

```bash
GET /tally/workspaces
```

**Response:**
```json
{
  "items": [
    {
      "id": "3jW9Q1",
      "name": "My Workspace",
      "createdByUserId": "w2lBkb",
      "createdAt": "2026-02-09T08:35:53.000Z",
      "updatedAt": "2026-02-09T08:35:53.000Z"
    }
  ],
  "page": 1,
  "limit": 50,
  "total": 1,
  "hasMore": false
}
```

#### Get Workspace

```bash
GET /tally/workspaces/{workspaceId}
```

**Response:**
```json
{
  "id": "3jW9Q1",
  "name": "My Workspace",
  "createdByUserId": "w2lBkb",
  "createdAt": "2026-02-09T08:35:53.000Z",
  "members": [
    {
      "id": "w2lBkb",
      "firstName": "John",
      "lastName": "Doe",
      "email": "john@example.com"
    }
  ]
}
```

#### Create Workspace

```bash
POST /tally/workspaces
Content-Type: application/json

{
  "name": "New Workspace"
}
```

**Note:** Creating workspaces requires a Pro subscription.

#### Update Workspace

```bash
PATCH /tally/workspaces/{workspaceId}
Content-Type: application/json

{
  "name": "Updated Workspace Name"
}
```

#### Delete Workspace

```bash
DELETE /tally/workspaces/{workspaceId}
```

Moves the workspace and all its forms to trash.

### Organization Users

#### List Users

```bash
GET /tally/organizations/{organizationId}/users
```

**Response:**
```json
[
  {
    "id": "w2lBkb",
    "firstName": "John",
    "lastName": "Doe",
    "email": "john@example.com",
    "createdAt": "2026-02-07T20:58:54.000Z"
  }
]
```

#### Remove User

```bash
DELETE /tally/organizations/{organizationId}/users/{userId}
```

### Organization Invites

#### List Invites

```bash
GET /tally/organizations/{organizationId}/invites
```

#### Create Invite

```bash
POST /tally/organizations/{organizationId}/invites
Content-Type: application/json

{
  "email": "newuser@example.com",
  "workspaceIds": ["3jW9Q1"]
}
```

#### Cancel Invite

```bash
DELETE /tally/organizations/{organizationId}/invites/{inviteId}
```

### Webhooks

#### List Webhooks

```bash
GET /tally/webhooks
```

**Note:** Listing webhooks may require specific permissions.

#### Create Webhook

```bash
POST /tally/webhooks
Content-Type: application/json

{
  "formId": "GxdRaQ",
  "url": "https://your-endpoint.com/webhook",
  "eventTypes": ["FORM_RESPONSE"]
}
```

**Webhook Event Types:**
- `FORM_RESPONSE` - Triggered when a new form response is submitted

#### Update Webhook

```bash
PATCH /tally/webhooks/{webhookId}
Content-Type: application/json

{
  "url": "https://new-endpoint.com/webhook"
}
```

#### Delete Webhook

```bash
DELETE /tally/webhooks/{webhookId}
```

#### List Webhook Events

```bash
GET /tally/webhooks/{webhookId}/events
```

#### Retry Webhook Event

```bash
POST /tally/webhooks/{webhookId}/events/{eventId}
```

## Pagination

Tally uses page-based pagination:

```bash
GET /tally/forms?page=1&limit=50
```

Response includes pagination info:

```json
{
  "items": [...],
  "page": 1,
  "limit": 50,
  "total": 100,
  "hasMore": true
}
```

For submissions, cursor-based pagination is also available using `afterId`.

## Code Examples

### JavaScript

```javascript
const response = await fetch(
  'https://gateway.maton.ai/tally/forms',
  {
    headers: {
      'Authorization': `Bearer ${process.env.MATON_API_KEY}`,
      'User-Agent': 'Maton/1.0'
    }
  }
);
const data = await response.json();
console.log(data.items);
```

### Python

```python
import os
import requests

response = requests.get(
    'https://gateway.maton.ai/tally/forms',
    headers={
        'Authorization': f'Bearer {os.environ["MATON_API_KEY"]}',
        'User-Agent': 'Maton/1.0'
    }
)
data = response.json()
print(data['items'])
```

### Create Form and Get Submissions

```python
import os
import requests
import uuid

headers = {
    'Authorization': f'Bearer {os.environ["MATON_API_KEY"]}',
    'User-Agent': 'Maton/1.0'
}

# Create a simple form
form_data = {
    'status': 'DRAFT',
    'blocks': [
        {
            'type': 'FORM_TITLE',
            'uuid': str(uuid.uuid4()),
            'groupUuid': str(uuid.uuid4()),
            'groupType': 'FORM_TITLE',
            'title': 'Contact Form',
            'payload': {}
        },
        {
            'type': 'INPUT_EMAIL',
            'uuid': str(uuid.uuid4()),
            'groupUuid': str(uuid.uuid4()),
            'groupType': 'INPUT_EMAIL',
            'title': 'Your email',
            'payload': {}
        }
    ]
}

response = requests.post(
    'https://gateway.maton.ai/tally/forms',
    headers=headers,
    json=form_data
)
form = response.json()
print(f"Created form: {form['id']}")

# Get submissions for a form
response = requests.get(
    f'https://gateway.maton.ai/tally/forms/{form["id"]}/submissions',
    headers=headers
)
submissions = response.json()
print(f"Total submissions: {submissions['totalNumberOfSubmissionsPerFilter']['all']}")
```

## Notes

- Form and workspace IDs are short alphanumeric strings (e.g., `GxdRaQ`)
- Block `uuid` and `groupUuid` fields must be valid UUIDs (GUIDs)
- Creating workspaces requires a Pro subscription
- The API is in public beta and subject to changes
- Rate limit: 100 requests per minute
- Use webhooks instead of polling for real-time submission notifications
- IMPORTANT: When piping curl output to `jq` or other commands, environment variables like `$MATON_API_KEY` may not expand correctly in some shell environments

## Error Handling

| Status | Meaning |
|--------|---------|
| 400 | Missing Tally connection or validation error |
| 401 | Invalid or missing Maton API key |
| 403 | Insufficient permissions |
| 404 | Resource not found |
| 429 | Rate limited (100 req/min) |
| 4xx/5xx | Passthrough error from Tally API |

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

1. Ensure your URL path starts with `tally`. For example:

- Correct: `https://gateway.maton.ai/tally/forms`
- Incorrect: `https://gateway.maton.ai/forms`

## Resources

- [Tally API Introduction](https://developers.tally.so/api-reference/introduction)
- [Tally API Reference](https://developers.tally.so/llms.txt)
- [Tally Help Center](https://help.tally.so/)
- [Maton Community](https://discord.com/invite/dBfFAcefs2)
- [Maton Support](mailto:support@maton.ai)
