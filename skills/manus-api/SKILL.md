---
name: manus
description: |
  Manus AI Agent API integration with managed API key authentication. Create and manage AI agent tasks, projects, files, and webhooks.
  Use this skill when users want to run AI agent tasks, manage projects, upload files, or set up webhooks with Manus.
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

# Manus

Access the Manus AI Agent API with managed API key authentication. Create and manage AI agent tasks, projects, files, and webhooks.

## Quick Start

```bash
# Create a task
python <<'EOF'
import urllib.request, os, json
data = json.dumps({'prompt': 'What is the capital of France?'}).encode()
req = urllib.request.Request('https://gateway.maton.ai/manus/v1/tasks', data=data, method='POST')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
req.add_header('Content-Type', 'application/json')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

## Base URL

```
https://gateway.maton.ai/manus/{native-api-path}
```

Replace `{native-api-path}` with the actual Manus API endpoint path. The gateway proxies requests to `api.manus.ai` and automatically injects your API key.

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

Manage your Manus API key connections at `https://ctrl.maton.ai`.

### List Connections

```bash
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://ctrl.maton.ai/connections?app=manus&status=ACTIVE')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

### Create Connection

```bash
python <<'EOF'
import urllib.request, os, json
data = json.dumps({'app': 'manus'}).encode()
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
    "connection_id": "f85eb0d5-87d6-41a7-8271-0449d3e407bd",
    "status": "ACTIVE",
    "creation_time": "2026-02-28T00:12:24.030143Z",
    "last_updated_time": "2026-02-28T00:16:08.920760Z",
    "url": "https://connect.maton.ai/?session_token=...",
    "app": "manus",
    "metadata": {},
    "method": "API_KEY"
  }
}
```

Open the returned `url` in a browser to enter your Manus API key.

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

If you have multiple Manus connections, specify which one to use with the `Maton-Connection` header:

```bash
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://gateway.maton.ai/manus/v1/tasks')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
req.add_header('Maton-Connection', 'f85eb0d5-87d6-41a7-8271-0449d3e407bd')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

If omitted, the gateway uses the default (oldest) active connection.

## API Reference

### Projects

#### List Projects

```bash
GET /manus/v1/projects
```

**Response:**
```json
{
  "object": "list",
  "data": [
    {
      "id": "SJhyBaLtYgQwurQoaT5APi",
      "name": "My Project"
    }
  ]
}
```

#### Create Project

```bash
POST /manus/v1/projects
Content-Type: application/json

{
  "name": "My Project",
  "default_instructions": "You are a helpful assistant."
}
```

**Response:**
```json
{
  "id": "SJhyBaLtYgQwurQoaT5APi",
  "object": "project",
  "name": "My Project",
  "created_at": "1772238309"
}
```

---

### Tasks

#### List Tasks

```bash
GET /manus/v1/tasks
```

**Response:**
```json
{
  "object": "list",
  "data": [
    {
      "id": "X7PPAMPNRovuyTXejNeEpv",
      "object": "task",
      "created_at": "1772191227",
      "updated_at": "1772191230",
      "status": "completed",
      "model": "manus-1.6-lite-adaptive",
      "metadata": {
        "task_title": "What is 2+2?",
        "task_url": "https://manus.im/app/X7PPAMPNRovuyTXejNeEpv"
      },
      "output": [...],
      "credit_usage": 0
    }
  ]
}
```

#### Get Task

```bash
GET /manus/v1/tasks/{task_id}
```

**Response:**
```json
{
  "id": "X7PPAMPNRovuyTXejNeEpv",
  "object": "task",
  "created_at": "1772191227",
  "updated_at": "1772191230",
  "status": "completed",
  "model": "manus-1.6-lite-adaptive",
  "metadata": {
    "task_title": "What is 2+2?",
    "task_url": "https://manus.im/app/X7PPAMPNRovuyTXejNeEpv"
  },
  "output": [
    {
      "id": "J9LlYFIfTlMWvR5hrC9FUL",
      "status": "completed",
      "role": "user",
      "type": "message",
      "content": [
        {
          "type": "output_text",
          "text": "What is 2+2? Reply in one word."
        }
      ]
    },
    {
      "id": "kR8Tj0ys7uwzorcSgzqMvZ",
      "status": "completed",
      "role": "assistant",
      "type": "message",
      "content": [
        {
          "type": "output_text",
          "text": "Four"
        }
      ]
    }
  ],
  "credit_usage": 0
}
```

Task status values: `pending`, `running`, `completed`, `failed`

#### Create Task

```bash
POST /manus/v1/tasks
Content-Type: application/json

{
  "prompt": "What is the capital of France?"
}
```

Optional fields:
- `project_id` (string): Associate task with a project
- `file_ids` (array): Attach files to the task

**Response:**
```json
{
  "task_id": "3cbKzkyC9WwRoMwAH8dKuY",
  "task_title": "Capital of France?",
  "task_url": "https://manus.im/app/3cbKzkyC9WwRoMwAH8dKuY"
}
```

#### Delete Task

```bash
DELETE /manus/v1/tasks/{task_id}
```

**Response:**
```json
{
  "id": "3cbKzkyC9WwRoMwAH8dKuY",
  "object": "file",
  "deleted": true
}
```

---

### Files

#### List Files

```bash
GET /manus/v1/files
```

Returns the 10 most recently uploaded files.

**Response:**
```json
{
  "object": "list",
  "data": [
    {
      "id": "file-2Gpoz5yhB8seSu9dxZdquR",
      "object": "file",
      "filename": "test.txt",
      "status": "pending",
      "created_at": "1772238309",
      "expires_at": "1772411109"
    }
  ]
}
```

File status values: `pending`, `ready`, `expired`

#### Get File

```bash
GET /manus/v1/files/{file_id}
```

**Response:**
```json
{
  "id": "file-2Gpoz5yhB8seSu9dxZdquR",
  "object": "file",
  "filename": "test.txt",
  "status": "pending",
  "created_at": "1772238309",
  "expires_at": "1772411109"
}
```

#### Create File

Creates a file record and returns a presigned S3 upload URL.

```bash
POST /manus/v1/files
Content-Type: application/json

{
  "filename": "document.pdf"
}
```

**Response:**
```json
{
  "id": "file-2Gpoz5yhB8seSu9dxZdquR",
  "object": "file",
  "filename": "document.pdf",
  "status": "pending",
  "upload_url": "https://vida-private.s3.us-east-1.amazonaws.com/...",
  "upload_expires_at": "1772238489",
  "created_at": "1772238309"
}
```

Upload your file to the `upload_url` using a PUT request within the expiration time.

#### Delete File

```bash
DELETE /manus/v1/files/{file_id}
```

**Response:**
```json
{
  "id": "file-2Gpoz5yhB8seSu9dxZdquR",
  "object": "file",
  "deleted": true
}
```

---

### Webhooks

#### Create Webhook

Register a webhook URL to receive task lifecycle notifications.

```bash
POST /manus/v1/webhooks
Content-Type: application/json

{
  "webhook": {
    "url": "https://example.com/webhook"
  }
}
```

**Response:**
```json
{
  "webhook_id": "J4dD3mwzZiWuJFiEWAvGnK"
}
```

#### Delete Webhook

```bash
DELETE /manus/v1/webhooks/{webhook_id}
```

**Response:**
```json
{}
```

---

## Code Examples

### JavaScript

```javascript
// Create a task
const response = await fetch(
  'https://gateway.maton.ai/manus/v1/tasks',
  {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${process.env.MATON_API_KEY}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ prompt: 'Summarize the latest news' })
  }
);
const data = await response.json();
console.log(data.task_url);
```

### Python

```python
import os
import requests

# Create a task
response = requests.post(
    'https://gateway.maton.ai/manus/v1/tasks',
    headers={
        'Authorization': f'Bearer {os.environ["MATON_API_KEY"]}',
        'Content-Type': 'application/json'
    },
    json={'prompt': 'Summarize the latest news'}
)
task = response.json()
print(task['task_url'])
```

## Notes

- Tasks are executed asynchronously. Use `GET /manus/v1/tasks/{task_id}` to poll for completion or set up a webhook
- File uploads use presigned S3 URLs that expire within 3 minutes
- Files expire after ~48 hours if not used
- Webhook payloads are signed with RSA-SHA256 for verification
- Available models: `manus-1.6`, `manus-1.6-lite`, `manus-1.6-max`, `manus-1.5`, `manus-1.5-lite`, `speed`
- Connection uses API_KEY authentication method (not OAuth)

## Error Handling

| Status | Meaning |
|--------|---------|
| 400 | Invalid request (missing required fields, invalid format) |
| 401 | Invalid or missing Maton API key |
| 404 | Resource not found |
| 4xx/5xx | Passthrough error from Manus API |

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

Ensure your URL path starts with `manus`. For example:

- Correct: `https://gateway.maton.ai/manus/v1/tasks`
- Incorrect: `https://gateway.maton.ai/v1/tasks`

## Resources

- [Manus API Overview](https://open.manus.im/docs)
- [Manus API Reference](https://open.manus.im/docs/api-reference)
- [Manus Website](https://manus.im)
- [Maton Community](https://discord.com/invite/dBfFAcefs2)
- [Maton Support](mailto:support@maton.ai)
