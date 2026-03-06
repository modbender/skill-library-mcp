# Cursor Cloud Agents API Reference

## Base URL

```
https://api.cursor.com/v0
```

## Authentication

All API requests require Basic Authentication with your Cursor API key as the username and an empty password:

```
Authorization: Basic {base64(CURSOR_API_KEY:)}
```

The API key can be found in Cursor IDE Settings → General.

## Content Type

All requests and responses use JSON:

```
Content-Type: application/json
```

## Endpoints

### List Agents

Returns all agents associated with your account.

```http
GET /agents
```

**Response:**
```json
[
  {
    "id": "agent_abc123",
    "status": "RUNNING",
    "repo": "owner/repo",
    "createdAt": "2024-01-15T10:30:00Z",
    "updatedAt": "2024-01-15T10:35:00Z",
    "model": "claude-4-sonnet",
    "prompt": "Add tests for auth module"
  }
]
```

### Launch Agent

Creates and launches a new agent on a repository.

```http
POST /agents
```

**Request Body:**
```json
{
  "target": {
    "repo": "owner/repo",
    "autoCreatePr": true,
    "branchName": "optional-branch-name"
  },
  "prompt": "Your task description here",
  "model": "claude-4-sonnet"
}
```

**Parameters:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `target.repo` | string | Yes | Repository in `owner/repo` format |
| `target.autoCreatePr` | boolean | No | Auto-create PR on completion (default: false) |
| `target.branchName` | string | No | Custom branch name (auto-generated if omitted) |
| `prompt` | string | Yes | Initial instructions for the agent |
| `model` | string | No | Model to use (auto-selected if omitted) |

**Response:**
```json
{
  "id": "agent_abc123",
  "status": "CREATING",
  "repo": "owner/repo",
  "createdAt": "2024-01-15T10:30:00Z",
  "model": "claude-4-sonnet",
  "prompt": "Add tests for auth module"
}
```

**Status Values:**
- `CREATING` - Agent is being initialized
- `RUNNING` - Agent is actively working
- `FINISHED` - Agent completed successfully
- `STOPPED` - Agent was stopped manually
- `ERROR` - Agent encountered an error

### Get Agent Status

Returns the current status and metadata of an agent.

```http
GET /agents/:id
```

**Response:**
```json
{
  "id": "agent_abc123",
  "status": "FINISHED",
  "repo": "owner/repo",
  "createdAt": "2024-01-15T10:30:00Z",
  "updatedAt": "2024-01-15T10:45:00Z",
  "model": "claude-4-sonnet",
  "prompt": "Add tests for auth module",
  "summary": "Added 15 unit tests for auth module covering login, logout, and token refresh",
  "prUrl": "https://github.com/owner/repo/pull/42"
}
```

### Get Conversation

Returns the full conversation history of an agent.

```http
GET /agents/:id/conversation
```

**Response:**
```json
{
  "messages": [
    {
      "role": "user",
      "content": "Add tests for auth module",
      "timestamp": "2024-01-15T10:30:00Z"
    },
    {
      "role": "assistant",
      "content": "I'll help you add comprehensive tests...",
      "timestamp": "2024-01-15T10:30:05Z"
    },
    {
      "role": "assistant",
      "content": "I've created tests for the login function...",
      "timestamp": "2024-01-15T10:35:00Z"
    }
  ]
}
```

### Send Follow-up

Sends a new message to an existing agent, resuming its work.

```http
POST /agents/:id/followup
```

**Request Body:**
```json
{
  "prompt": "Also add tests for the password reset flow"
}
```

**Response:**
```json
{
  "id": "agent_abc123",
  "status": "RUNNING",
  "message": "Follow-up received, resuming work"
}
```

### Stop Agent

Stops a running agent gracefully.

```http
POST /agents/:id/stop
```

**Response:**
```json
{
  "id": "agent_abc123",
  "status": "STOPPED",
  "message": "Agent stopped successfully"
}
```

### Delete Agent

Permanently deletes an agent and its conversation history.

```http
DELETE /agents/:id
```

**Response:**
```json
{
  "id": "agent_abc123",
  "deleted": true
}
```

### List Models

Returns available models for agent tasks.

```http
GET /models
```

**Response:**
```json
{
  "models": [
    {
      "id": "claude-4-sonnet",
      "name": "Claude 4 Sonnet",
      "description": "Balanced performance and speed"
    },
    {
      "id": "claude-4-opus",
      "name": "Claude 4 Opus",
      "description": "Best for complex tasks"
    },
    {
      "id": "gpt-5.2",
      "name": "GPT-5.2",
      "description": "Latest GPT model"
    }
  ]
}
```

### Get Account Info

Returns information about the authenticated account.

```http
GET /me
```

**Response:**
```json
{
  "email": "user@example.com",
  "username": "username",
  "tier": "ultra",
  "subscriptionStatus": "active",
  "accessibleRepos": ["owner/repo1", "owner/repo2"],
  "agentsUsed": 3,
  "agentsLimit": 5,
  "computeUsed": 150,
  "computeLimit": 500
}
```

## Error Responses

All errors follow a consistent format:

```json
{
  "error": "Error message",
  "code": "ERROR_CODE",
  "details": {}
}
```

### HTTP Status Codes

| Code | Meaning | Description |
|------|---------|-------------|
| 200 | OK | Request succeeded |
| 201 | Created | Resource created successfully |
| 400 | Bad Request | Invalid request parameters |
| 401 | Unauthorized | Invalid or missing API key |
| 403 | Forbidden | Insufficient permissions or repo access |
| 404 | Not Found | Resource not found |
| 429 | Too Many Requests | Rate limit exceeded |
| 500 | Internal Server Error | Server error |

### Error Codes

| Code | Description |
|------|-------------|
| `INVALID_REQUEST` | Request body is malformed |
| `REPO_NOT_FOUND` | Repository not found or not accessible |
| `AGENT_NOT_FOUND` | Agent ID not found |
| `RATE_LIMITED` | Too many requests |
| `CONCURRENT_LIMIT` | Concurrent agent limit reached |
| `INVALID_MODEL` | Specified model is not available |

## Rate Limiting

The API enforces rate limits:

- **Standard requests:** 60 per minute
- **Agent operations:** 30 per minute
- **Launch operations:** 10 per minute

Rate limit headers are included in responses:

```
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 45
X-RateLimit-Reset: 1705312800
```

## Concurrent Limits

| Tier | Concurrent Agents | Description |
|------|-------------------|-------------|
| Free | 1 | Basic model access |
| Pro | 3 | Most models available |
| Ultra | 5 | Full access with priority |

When the limit is reached, attempts to launch new agents will return a 429 error with code `CONCURRENT_LIMIT`:

```json
{
  "error": "Concurrent agent limit reached",
  "code": "CONCURRENT_LIMIT",
  "details": {
    "current": 3,
    "limit": 3,
    "message": "Stop an existing agent before launching a new one"
  }
}
```

**Error Handling:**

```bash
# Check if limit is reached
response=$(cursor-api.sh launch --repo owner/repo --prompt "..." 2>&1) || {
    if [[ "$response" == *"CONCURRENT_LIMIT"* ]]; then
        echo "Concurrent limit reached. Stopping oldest agent..."
        oldest=$(cursor-api.sh list | jq -r '.[0].id')
        cursor-api.sh stop "$oldest"
        # Retry launch
    fi
}
```

## Webhooks

The API supports webhooks for real-time notifications:

```json
{
  "target": {
    "repo": "owner/repo"
  },
  "prompt": "...",
  "webhook": {
    "url": "https://your-server.com/webhook",
    "secret": "your-webhook-secret"
  }
}
```

Webhook events:
- `agent.created` - Agent was created
- `agent.started` - Agent started working
- `agent.finished` - Agent completed
- `agent.stopped` - Agent was stopped
- `agent.error` - Agent encountered an error

## Pagination

List endpoints support pagination via query parameters:

```http
GET /agents?limit=10&offset=20
```

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `limit` | integer | 20 | Number of items per page |
| `offset` | integer | 0 | Number of items to skip |

**Response includes pagination metadata:**

```json
{
  "data": [...],
  "pagination": {
    "total": 100,
    "limit": 20,
    "offset": 20,
    "hasMore": true
  }
}
```

## SDK Examples

### cURL

```bash
# Launch agent
curl -X POST https://api.cursor.com/v0/agents \
  -H "Authorization: Basic $(echo -n '$CURSOR_API_KEY:' | base64)" \
  -H "Content-Type: application/json" \
  -d '{
    "target": {"repo": "owner/repo", "autoCreatePr": true},
    "prompt": "Add tests"
  }'
```

### JavaScript

```javascript
const launchAgent = async (repo, prompt) => {
  const credentials = Buffer.from(`${process.env.CURSOR_API_KEY}:`).toString('base64');
  
  const response = await fetch('https://api.cursor.com/v0/agents', {
    method: 'POST',
    headers: {
      'Authorization': `Basic ${credentials}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      target: { repo, autoCreatePr: true },
      prompt
    })
  });
  
  return response.json();
};
```

### Python

```python
import base64
import os
import requests

def launch_agent(repo: str, prompt: str):
    credentials = base64.b64encode(f"{os.environ['CURSOR_API_KEY']}:".encode()).decode()
    
    response = requests.post(
        'https://api.cursor.com/v0/agents',
        headers={
            'Authorization': f'Basic {credentials}',
            'Content-Type': 'application/json'
        },
        json={
            'target': {'repo': repo, 'autoCreatePr': True},
            'prompt': prompt
        }
    )
    
    return response.json()
```
