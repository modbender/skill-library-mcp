# Noya Agent API Reference

Base URL: `https://safenet.one`

All endpoints require authentication via the `x-api-key` header (except where noted).

---

## Authentication

| Header    | Value        | Description                    |
| --------- | ------------ | ------------------------------ |
| x-api-key | `noya_<key>` | API key generated from the app |

API keys are created with a duration: `thirty_days`, `ninety_days`, or `one_year`. Expired or revoked keys return `401`.

---

## POST /api/messages/stream

Send a message to the Noya agent and receive a streamed response.

### Request

**Content-Type:** `application/json`

```json
{
  "message": "What is the price of ETH?",
  "threadId": "unique-thread-id"
}
```

| Field    | Type   | Required | Description                                       |
| -------- | ------ | -------- | ------------------------------------------------- |
| message  | string | Yes      | User message text                                 |
| threadId | string | Yes      | UUID v4 thread identifier. Creates thread if new. |

### Response

**Content-Type:** `text/plain; charset=utf-8`
**Transfer-Encoding:** `chunked`

The response is a text stream. Each chunk is a JSON object followed by `--breakpoint--\n`. Keep-alive pings (`keep-alive\n\n`) are sent every second.

### Chunk Types

#### message

```json
{
  "type": "message",
  "threadId": "t1",
  "messageId": "msg-uuid",
  "message": "The current price of ETH is..."
}
```

#### tool

```json
{
  "type": "tool",
  "threadId": "t1",
  "messageId": "msg-uuid",
  "content": {
    "type": "token_price",
    "data": { ... }
  }
}
```

Non-visible tool results have `content.type` set to `"non_visible"`.

#### progress

```json
{
  "type": "progress",
  "threadId": "t1",
  "current": 1,
  "total": 3,
  "message": "Analyzing token metrics..."
}
```

#### interrupt

Sent when the agent needs user confirmation before proceeding.

```json
{
  "type": "interrupt",
  "threadId": "t1",
  "content": {
    "type": "interrupt",
    "question": "Do you want to proceed with this swap?",
    "options": ["Yes", "No"]
  }
}
```

To respond to an interrupt, send another message to the same thread with the user's answer.

#### reasonForExecution

```json
{
  "type": "reasonForExecution",
  "threadId": "t1",
  "message": "Looking up current market data for ETH"
}
```

#### executionSteps

```json
{
  "type": "executionSteps",
  "threadId": "t1",
  "steps": ["Fetching price data", "Analyzing trends", "Generating summary"]
}
```

#### error

```json
{
  "type": "error",
  "message": "I couldn't find your wallet address. Please try reloading the page."
}
```

### Error Responses

| Status | Condition                   |
| ------ | --------------------------- |
| 400    | Missing message or threadId |
| 401    | Unauthorized                |

---

## GET /api/threads

List all conversation threads for the authenticated user.

### Response `200 OK`

```json
{
  "success": true,
  "data": {
    "threads": [
      {
        "id": "abc123",
        "name": "ETH Analysis",
        "userId": "user-id",
        "created_at": "2026-02-16T00:00:00.000Z",
        "updated_at": "2026-02-16T12:00:00.000Z"
      }
    ]
  }
}
```

### Error Responses

| Status | Condition    |
| ------ | ------------ |
| 401    | Unauthorized |
| 500    | Server error |

---

## GET /api/threads/:threadId/messages

Get all messages from a specific thread. The threadId in the URL is the user-facing ID (the server internally prefixes it with the user ID).

### Response `200 OK`

```json
{
  "success": true,
  "data": {
    "messages": [
      {
        "id": ["HumanMessage"],
        "kwargs": {
          "id": "msg-uuid",
          "content": "What is ETH price?"
        }
      },
      {
        "id": ["AIMessage"],
        "kwargs": {
          "id": "msg-uuid",
          "content": "ETH is currently trading at..."
        }
      }
    ]
  }
}
```

Messages follow LangChain message format. Types include `HumanMessage`, `AIMessage`, `ToolMessage`, and `InterruptMessage`.

### Error Responses

| Status | Condition    |
| ------ | ------------ |
| 401    | Unauthorized |
| 500    | Server error |

---

## DELETE /api/threads/:threadId

Delete a conversation thread.

### Response `200 OK`

```json
{
  "success": true,
  "message": "Thread deleted successfully"
}
```

### Error Responses

| Status | Condition        |
| ------ | ---------------- |
| 401    | Unauthorized     |
| 404    | Thread not found |
| 500    | Server error     |

---

## POST /api/chat/completions

OpenAI-compatible chat completion endpoint. Maintains message history per session in Redis.

### Request

```json
{
  "sessionId": "session-1",
  "message": "Hello, what can you do?",
  "config": {},
  "tools": [],
  "toolResults": []
}
```

| Field       | Type   | Required | Description                             |
| ----------- | ------ | -------- | --------------------------------------- |
| sessionId   | string | Yes      | Session identifier for history tracking |
| message     | string | Yes      | User message                            |
| config      | object | No       | Model configuration overrides           |
| tools       | array  | No       | OpenAI-format tool definitions          |
| toolResults | array  | No       | Tool call results from previous turn    |

Each entry in `toolResults`:

| Field        | Type   | Description         |
| ------------ | ------ | ------------------- |
| tool_call_id | string | ID of the tool call |
| content      | string | Result content      |

### Response `200 OK`

```json
{
  "success": true,
  "response": {
    "id": "chatcmpl-xxx",
    "object": "chat.completion",
    "created": 1708000000,
    "model": "gpt-4o",
    "choices": [
      {
        "message": {
          "role": "assistant",
          "content": "I can help with...",
          "tool_calls": null
        },
        "finish_reason": "stop"
      }
    ]
  },
  "usage": {
    "prompt_tokens": 50,
    "completion_tokens": 100,
    "total_tokens": 150
  }
}
```

### Error Responses

| Status | Condition            |
| ------ | -------------------- |
| 400    | Invalid request data |
| 401    | Unauthorized         |
| 429    | Rate limit exceeded  |
| 500    | Server error         |

---

## GET /api/chat/session/:sessionId

Get the message history for a chat session.

### Response `200 OK`

```json
{
  "success": true,
  "sessionId": "session-1",
  "messages": [
    { "role": "user", "content": "Hello" },
    { "role": "assistant", "content": "Hi! How can I help?" }
  ],
  "count": 2
}
```

---

## DELETE /api/chat/session/:sessionId

Clear all message history for a session.

### Response `200 OK`

```json
{
  "success": true,
  "message": "Chat history cleared successfully"
}
```

---

## GET /api/agents/summarize

Returns all available agent types, their specialties, and the tools they have access to.

### Response `200 OK`

```json
{
  "success": true,
  "data": "The available agent types are:\n  - tokenAnalysis: Name: Token Analysis, Speciality: ...\n    tools:\n      - name: getTokenPrice\n        description: ...\n  ..."
}
```

The `data` field is a YAML-formatted string describing all agents and their tools.

---

## API Key Management

These endpoints require Privy token authentication (not API key auth). They are included for reference but are not accessible via API keys.

### POST /api/keys

Create a new API key.

**Request:**

```json
{
  "name": "My integration key",
  "duration": "ninety_days"
}
```

| Field    | Type   | Required | Description                                      |
| -------- | ------ | -------- | ------------------------------------------------ |
| name     | string | No       | Label for the key (max 255 chars)                |
| duration | string | Yes      | One of: `thirty_days`, `ninety_days`, `one_year` |

**Response `201 Created`:**

```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "key": "noya_abc123...",
    "prefix": "noya_abc",
    "name": "My integration key",
    "duration": "ninety_days",
    "expires_at": "2026-05-17T00:00:00.000Z",
    "created_at": "2026-02-16T00:00:00.000Z"
  }
}
```

The `key` field is only returned once at creation.

### GET /api/keys

List all API keys for the authenticated user. Returns prefixes only, never full keys.

### DELETE /api/keys/:id

Revoke an API key (soft delete).

---

## Common Error Format

All error responses follow this structure:

```json
{
  "success": false,
  "message": "Human-readable error description"
}
```

## Rate Limiting

The `/api/messages/stream` endpoint is rate-limited to 15 requests per 5-minute window per user.
