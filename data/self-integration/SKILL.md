---
name: self-integration
description: Connect to any external app and perform actions on it. Use when the user wants to interact with external services like Slack, Linear, HubSpot, Salesforce, Jira, GitHub, Google Sheets, or any other app — send messages, create tasks, sync data, manage contacts, or perform any API operation.
license: MIT
metadata:
  author: Membrane Inc
  version: "1.0.0"
  homepage: https://getmembrane.com
  openclaw:
    requires:
      env:
        - MEMBRANE_TOKEN
        - MEMBRANE_API_URL
    primaryEnv: MEMBRANE_TOKEN
    homepage: https://getmembrane.com
---

# Self-Integration

Connect to any external app and perform actions on it. Uses the [Membrane](https://getmembrane.com) API.

## Making API Requests

All requests go to `${MEMBRANE_API_URL:-https://api.getmembrane.com}` with a Bearer token:

```
Authorization: Bearer $MEMBRANE_TOKEN
Content-Type: application/json
```

Get the API token from the [Membrane dashboard](https://console.getmembrane.com).

## Workflow

### Step 1: Get a Connection

A connection is an authenticated link to an external app (e.g. a user's Slack workspace, a HubSpot account). You need one before you can run actions.

#### 1a. Check for existing connections

`GET /connections`

Look for a connection matching the target app. Key fields: `id`, `name`, `connectorId`, `disconnected`.

If a matching connection exists and `disconnected` is `false`, skip to **Step 2**.

#### 1b. Find a connector

A connector is a pre-built adapter for an external app. Search by app name:

`GET /search?q=slack`

Look for results with `elementType: "connector"`. Use `element.id` as `connectorId` in step 1d.

If nothing is found, go to step 1c to build a connector.

#### 1c. Build a connector (if none exists)

Create a Membrane Agent session to build a connector:

`POST /agent/sessions` with body `{"prompt": "Build a connector for Slack (https://slack.com)"}`

Adjust the prompt to describe the actual app you need. Poll `GET /agent/sessions/{sessionId}?wait=true&timeout=30` until `state` is `"idle"` or `status` is `"completed"`.

You can send follow-up instructions via `POST /agent/sessions/{sessionId}/message` or abort via `POST /agent/sessions/{sessionId}/interrupt`.

After the connector is built, search for it again (step 1b).

#### 1d. Request a connection

Create a connection request so the user can authenticate with the external app:

`POST /connection-requests` with body `{"connectorId": "cnt_abc123"}`

The response includes a `url`. **Tell the user to open the `url`** to complete authentication (OAuth, API key, etc.).

#### 1e. Check connection result

Poll until the user completes authentication:

`GET /connection-requests/{requestId}`

- `status: "pending"` — user hasn't completed yet, poll again.
- `status: "success"` — done. Use `resultConnectionId` as the connection ID going forward.
- `status: "error"` — failed. Check `resultError` for details.

### Step 2: Get an Action

An action is an operation you can perform on a connected app (e.g. "Create task", "Send message", "List contacts").

#### 2a. Search for actions

Search using a natural language description of what you want to do:

`GET /actions?connectionId=con_abc123&intent=send+a+message&limit=10`

Each result includes `id`, `name`, `description`, `inputSchema` (what parameters the action accepts), and `outputSchema` (what it returns).

If no suitable action exists, go to step 2b.

#### 2b. Build an action (if none exists)

Use Membrane Agent. ALWAYS include the connection ID in the prompt:

`POST /agent/sessions` with body `{"prompt": "Create a tool to send a message in a channel for connection con_abc123"}`

Adjust the prompt to describe the actual action you need. Poll for completion the same way as step 1c. After the action is built, search for it again (step 2a).

### Step 3: Run an Action

Execute the action using the action ID from step 2 and the connection ID from step 1:

`POST /actions/{actionId}/run?connectionId=con_abc123` with body `{"input": {"channel": "#general", "text": "Hello!"}}`

Provide `input` matching the action's `inputSchema`.

The result is in the `output` field of the response.

## API Reference

Base URL: `${MEMBRANE_API_URL:-https://api.getmembrane.com}`
Auth header: `Authorization: Bearer $MEMBRANE_TOKEN`

### GET /connections

List all connections.

Response:

```json
{
  "items": [
    {
      "id": "string",
      "name": "string",
      "connectorId": "string",
      "integrationId": "string (optional)",
      "disconnected": "boolean",
      "state": "NOT_CONFIGURED | SETUP_IN_PROGRESS | SETUP_FAILED | READY",
      "error": "object (optional)",
      "createdAt": "datetime",
      "updatedAt": "datetime"
    }
  ]
}
```

### GET /search

Search workspace elements by keyword.

Query parameters:

| Param | Type | Description |
|---|---|---|
| `q` | string (required) | Search query (1-200 chars) |
| `elementType` | string (optional) | Filter by type: `Connector`, `Integration`, `Action`, etc. |
| `limit` | number (optional) | Max results (1-100) |

Response:

```json
{
  "items": [
    {
      "elementType": "Connector",
      "element": {
        "id": "string",
        "name": "string",
        "logoUri": "string (optional)"
      }
    }
  ]
}
```

### POST /connection-requests

Create a connection request for user authentication.

Request body (at least one identifier required):

| Field | Type | Description |
|---|---|---|
| `connectorId` | string | Connector ID |
| `integrationId` | string | Integration ID (alternative) |
| `integrationKey` | string | Integration key (alternative) |
| `connectionId` | string | Existing connection ID (for reconnecting) |
| `name` | string | Custom connection name |
| `connectorVersion` | string | Connector version |
| `connectorParameters` | object | Connector-specific parameters |

Response:

```json
{
  "requestId": "string",
  "url": "string",
  "status": "pending | success | cancelled | error",
  "connectorId": "string (optional)",
  "integrationId": "string (optional)",
  "resultConnectionId": "string (optional, set on success)",
  "resultError": "object (optional, set on error)",
  "createdAt": "datetime"
}
```

### GET /connection-requests/:requestId

Check connection request status. Same response schema as POST.

### GET /actions

List or search actions.

Query parameters:

| Param | Type | Description |
|---|---|---|
| `connectionId` | string | Filter by connection |
| `integrationId` | string | Filter by integration |
| `intent` | string | Natural language search (max 200 chars) |
| `limit` | number | Max results (default 10) |

Response:

```json
{
  "items": [
    {
      "id": "string",
      "name": "string",
      "key": "string",
      "description": "string (optional)",
      "type": "string",
      "inputSchema": "JSON Schema (optional)",
      "outputSchema": "JSON Schema (optional)",
      "integrationId": "string (optional)",
      "connectionId": "string (optional)"
    }
  ]
}
```

### POST /actions/:actionId/run

Run an action.

Query parameters:

| Param | Type | Description |
|---|---|---|
| `connectionId` | string | Connection to run the action on |

Request body:

| Field | Type | Description |
|---|---|---|
| `input` | any | Parameters matching the action's `inputSchema` |

Response:

```json
{
  "output": "any"
}
```

### POST /agent/sessions

Create an agent session to build connectors or actions.

Request body:

| Field | Type | Description |
|---|---|---|
| `prompt` | string (required) | Task description |

Response:

```json
{
  "id": "string",
  "status": "queued | starting | running | completed | failed | cancelled",
  "state": "busy | idle",
  "prompt": "string",
  "createdAt": "datetime",
  "updatedAt": "datetime"
}
```

### GET /agent/sessions/:id

Get agent session status.

Query parameters:

| Param | Type | Description |
|---|---|---|
| `wait` | boolean | If true, long-poll until session is idle or timeout |
| `timeout` | number | Max wait in seconds (1-60, default 30) |

Response: same schema as POST /agent/sessions.

### POST /agent/sessions/:id/message

Send a follow-up message to an active agent session.

Request body:

| Field | Type | Description |
|---|---|---|
| `input` | string (required) | Message to send |

Response: same schema as POST /agent/sessions.

### POST /agent/sessions/:id/interrupt

Abort an agent session.

Response:

```json
{
  "interrupted": "boolean"
}
```

## External Endpoints

All requests go to the Membrane API. No other external services are contacted directly by this skill.

| Endpoint | Data Sent |
|---|---|
| `${MEMBRANE_API_URL:-https://api.getmembrane.com}/*` | API token, connection parameters, action inputs, agent prompts |

## Security & Privacy

- All data is sent to the Membrane API over HTTPS.
- `MEMBRANE_TOKEN` is a high-privilege credential that can create connections and run actions across external apps. Treat it as a secret.
- Connection authentication (OAuth, API keys) is handled by Membrane — credentials for external apps are stored by the Membrane service, not locally.
- Action inputs and outputs pass through the Membrane API to the connected external app.

By using this skill, data is sent to [Membrane](https://getmembrane.com). Only install if you trust Membrane with access to your connected apps.
