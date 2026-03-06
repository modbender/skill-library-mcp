---
name: OpenClaw Integrations API
description: OpenClaw is a skill-based integration system that allows apps built
  on MakeX to discover and execute actions from third-party services (Gmail,
  Slack, GitHub, etc.) via Composio.
---

# OpenClaw Integrations API

OpenClaw is a skill-based integration system that allows apps built on MakeX to discover and execute actions from third-party services (Gmail, Slack, GitHub, etc.) via Composio.

## Authentication

All endpoints require the `X-Org-Token` header containing an organization service token. This token is validated against the organization database. User session cookies are not used — these endpoints are designed for server-to-server communication.

```
X-Org-Token: <org-service-token>
```

**Don't have an org token?**

1. Go to [https://www.makex.app/](https://www.makex.app/) and sign up for an account.
2. Navigate to **Settings** in your dashboard.
3. Copy your API key from the settings page — this is your `X-Org-Token`.

## Base URL

```
POST /api/openclaw/integrations/<endpoint>
```

All endpoints support CORS via a preflight `OPTIONS` handler.

## Endpoints

### 1. Search Actions

**POST** `/api/openclaw/integrations/search-actions`

Discover available actions/tools across one or more integrations.

**Request Body:**
```json
{
  "integrations": ["gmail", "slack", "github"],
  "toolkit": "gmail",
  "search": "send"
}
```

- `integrations` (required): Array of integration slugs to search across.
- `toolkit` (optional): If provided, overrides `integrations` and searches only this toolkit.
- `search` (optional): Filter actions by keyword.

**Response (200):**
```json
{
  "total": 12,
  "actions": {
    "gmail": [
      { "slug": "GMAIL_SEND_EMAIL", "name": "Send Email" },
      { "slug": "GMAIL_CREATE_DRAFT", "name": "Create Draft" }
    ],
    "slack": [
      { "slug": "SLACK_SEND_MESSAGE", "name": "Send Message" }
    ]
  }
}
```

---

### 2. Connected Account

**POST** `/api/openclaw/integrations/connected-account`

Check if a specific integration is connected for the organization and retrieve account details.

**Request Body:**
```json
{
  "integration": "gmail"
}
```

- `integration` (required): The integration slug to check.

**Response (200):**
```json
{
  "accountId": "conn_abc123",
  "userId": "org_xyz",
  "integration": "gmail",
  "status": "ACTIVE"
}
```

**Response (404) — not connected:**
```json
{
  "error": "No active connected account found for integration gmail",
  "availableIntegrations": ["slack", "github"]
}
```

---

### 3. Action Details

**POST** `/api/openclaw/integrations/action-details`

Get the full specification of a specific action, including its input and output parameters.

**Request Body:**
```json
{
  "action_slug": "GMAIL_SEND_EMAIL"
}
```

- `action_slug` (required): The slug of the action to retrieve.

**Response (200):**
```json
{
  "name": "Send Email",
  "slug": "GMAIL_SEND_EMAIL",
  "description": "Send an email via Gmail",
  "inputParameters": {
    "to": { "type": "string", "description": "Recipient email", "required": true },
    "subject": { "type": "string", "description": "Email subject" },
    "body": { "type": "string", "description": "Email body" }
  },
  "outputParameters": {
    "messageId": { "type": "string" },
    "threadId": { "type": "string" }
  }
}
```

---

### 4. Run Action

**POST** `/api/openclaw/integrations/run-action`

Execute a specific action on a connected account.

**Request Body:**
```json
{
  "toolName": "GMAIL_SEND_EMAIL",
  "accountId": "conn_abc123",
  "arguments": {
    "to": "user@example.com",
    "subject": "Hello",
    "body": "Hi there"
  }
}
```

- `toolName` (required): The action slug to execute.
- `accountId` (required): The connected account ID (from the connected-account endpoint).
- `arguments` (optional): Structured key-value arguments for the action.
- `text` (optional): Natural language text input (used if `arguments` is not provided).
- `version` (optional): API version override.
- `custom_auth_params` (optional): Custom authentication parameters.
- `custom_connection_data` (optional): Custom connection data.
- `allow_tracing` (optional): Enable tracing for the execution.

**Response (200):** The raw Composio execution response (varies by action).

---

### 5. Output Structure

**POST** `/api/openclaw/integrations/output-structure`

Execute an action and return its output structure. Useful for determining the shape of an action's response.

**Request Body:**
```json
{
  "action_slug": "GMAIL_SEND_EMAIL",
  "accountId": "conn_abc123",
  "arguments": {
    "to": "test@example.com",
    "subject": "Test",
    "body": "Test body"
  }
}
```

- `action_slug` (required): The action slug to execute.
- `accountId` (required): The connected account ID.
- `arguments` (optional): Arguments to pass to the action.

**Response (200):**
```json
{
  "successful": true,
  "data": { ... }
}
```

## Error Responses

All endpoints return errors in a consistent format:

```json
{ "error": "Description of what went wrong" }
```

| Status | Meaning |
|--------|---------|
| 400 | Missing required parameters |
| 401 | Missing or invalid `X-Org-Token` |
| 404 | Resource not found (e.g., no connected account) |
| 500 | Server error or missing `COMPOSIO_API_KEY` |

## Typical Workflow

1. **Search actions** to discover what's available for connected integrations.
2. **Get connected account** to retrieve the `accountId` for a specific integration.
3. **Get action details** to understand input/output parameters for a chosen action.
4. **Run action** to execute the action with the required arguments.
