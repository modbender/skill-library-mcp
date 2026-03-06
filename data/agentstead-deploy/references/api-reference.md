# AgentStead API Reference

**Base URL:** `https://agentstead.com/api/v1`

## Authentication

All authenticated endpoints require: `Authorization: Bearer <token>`

### POST /auth/register

Create a new account.

**Request:**
```json
{
  "email": "user@example.com",
  "password": "securepass123"
}
```

**Response (201):**
```json
{
  "token": "eyJhbGciOi...",
  "user": {
    "id": "usr_abc123",
    "email": "user@example.com",
    "createdAt": "2025-01-01T00:00:00Z"
  }
}
```

### POST /auth/login

Login to existing account.

**Request:**
```json
{
  "email": "user@example.com",
  "password": "securepass123"
}
```

**Response (200):**
```json
{
  "token": "eyJhbGciOi...",
  "user": {
    "id": "usr_abc123",
    "email": "user@example.com"
  }
}
```

---

## Agents

### POST /agents

Create a new agent.

**Request:**
```json
{
  "name": "MyAgent",
  "personality": "You are a helpful assistant.",
  "plan": "starter",
  "aiPlan": "byok",
  "byokProvider": "anthropic",
  "byokApiKey": "sk-ant-..."
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| name | string | yes | Agent display name |
| personality | string | yes | System prompt / personality |
| plan | string | yes | `starter`, `pro`, `business`, `enterprise` |
| aiPlan | string | yes | `byok`, `pro_ai`, `max_ai` |
| byokProvider | string | if BYOK | `anthropic`, `openai`, `google`, `openrouter`, `xai`, `groq`, `mistral`, `bedrock`, `venice` |
| byokApiKey | string | if BYOK | API key for the chosen provider |

**Response (201):**
```json
{
  "id": "agt_xyz789",
  "name": "MyAgent",
  "personality": "You are a helpful assistant.",
  "plan": "starter",
  "aiPlan": "byok",
  "status": "STOPPED",
  "channels": [],
  "createdAt": "2025-01-01T00:00:00Z"
}
```

### GET /agents

List all agents for the authenticated user.

**Response (200):**
```json
{
  "agents": [
    {
      "id": "agt_xyz789",
      "name": "MyAgent",
      "status": "RUNNING",
      "plan": "starter",
      "createdAt": "2025-01-01T00:00:00Z"
    }
  ]
}
```

### GET /agents/:id

Get agent details.

**Response (200):**
```json
{
  "id": "agt_xyz789",
  "name": "MyAgent",
  "personality": "You are a helpful assistant.",
  "plan": "starter",
  "aiPlan": "byok",
  "status": "RUNNING",
  "channels": [
    {
      "id": "ch_abc",
      "type": "telegram",
      "connected": true
    }
  ],
  "createdAt": "2025-01-01T00:00:00Z",
  "startedAt": "2025-01-01T00:01:00Z"
}
```

### PATCH /agents/:id

Update agent settings.

**Request:**
```json
{
  "name": "NewName",
  "personality": "Updated personality..."
}
```

**Response (200):** Updated agent object.

### DELETE /agents/:id

Delete an agent. Agent must be stopped first.

**Response (204):** No content.

### POST /agents/:id/start

Start the agent.

**Response (200):**
```json
{
  "id": "agt_xyz789",
  "status": "STARTING"
}
```

Status transitions: `STOPPED` → `STARTING` → `RUNNING`

### POST /agents/:id/stop

Stop the agent.

**Response (200):**
```json
{
  "id": "agt_xyz789",
  "status": "STOPPING"
}
```

Status transitions: `RUNNING` → `STOPPING` → `STOPPED`

---

## Channels

### POST /agents/:id/channels

Add a channel to an agent.

**Request (Telegram):**
```json
{
  "type": "telegram",
  "botToken": "123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11"
}
```

**Request (Discord):**
```json
{
  "type": "discord",
  "botToken": "MTIzNDU2Nzg5MDEyMzQ1Njc4OQ.AbCdEf.GhIjKlMnOpQrStUvWxYz"
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| type | string | yes | `telegram` or `discord` |
| botToken | string | yes | Bot token from BotFather or Discord Developer Portal |

**Response (201):**
```json
{
  "id": "ch_abc123",
  "type": "telegram",
  "connected": false,
  "createdAt": "2025-01-01T00:00:00Z"
}
```

### GET /agents/:id/channels

List channels for an agent.

**Response (200):**
```json
{
  "channels": [
    {
      "id": "ch_abc123",
      "type": "telegram",
      "connected": true
    }
  ]
}
```

### DELETE /agents/:id/channels/:channelId

Remove a channel. Agent must be stopped first.

**Response (204):** No content.

---

## Billing

### POST /billing/checkout

Create a Stripe checkout session.

**Request:**
```json
{
  "agentId": "agt_xyz789",
  "plan": "starter",
  "aiPlan": "byok"
}
```

**Response (200):**
```json
{
  "checkoutUrl": "https://checkout.stripe.com/c/pay/cs_live_...",
  "sessionId": "cs_live_abc123"
}
```

### POST /billing/crypto/create-invoice

Create a crypto payment invoice (USDC).

**Request:**
```json
{
  "agentId": "agt_xyz789",
  "plan": "starter",
  "aiPlan": "byok"
}
```

**Response (200):**
```json
{
  "invoiceId": "inv_abc123",
  "amount": "9.00",
  "currency": "USDC",
  "paymentAddress": "0x1234...abcd",
  "network": "base",
  "expiresAt": "2025-01-01T01:00:00Z"
}
```

### GET /billing/status

Get billing status for the authenticated user.

**Response (200):**
```json
{
  "subscription": {
    "plan": "starter",
    "aiPlan": "byok",
    "status": "active",
    "currentPeriodEnd": "2025-02-01T00:00:00Z",
    "paymentMethod": "stripe"
  }
}
```

---

## Chat

### POST /agents/:id/chat

Send a message to an agent (for testing or API-based interaction).

**Request:**
```json
{
  "message": "Hello, how are you?",
  "conversationId": "conv_optional"
}
```

**Response (200):**
```json
{
  "reply": "I'm doing well! How can I help you today?",
  "conversationId": "conv_abc123"
}
```

---

## Rate Limits

| Endpoint | Limit |
|----------|-------|
| POST /auth/* | 10 req/min |
| POST /agents | 20 req/min |
| POST /agents/:id/chat | 60 req/min |
| All other endpoints | 120 req/min |

Rate limit headers:
- `X-RateLimit-Limit` — max requests per window
- `X-RateLimit-Remaining` — remaining requests
- `X-RateLimit-Reset` — Unix timestamp when window resets

---

## Error Format

All errors return:

```json
{
  "error": {
    "code": "INVALID_REQUEST",
    "message": "Human-readable description of what went wrong."
  }
}
```

### Error Codes

| Code | HTTP Status | Description |
|------|-------------|-------------|
| INVALID_REQUEST | 400 | Malformed or missing parameters |
| UNAUTHORIZED | 401 | Missing or invalid auth token |
| FORBIDDEN | 403 | Insufficient permissions |
| NOT_FOUND | 404 | Resource not found |
| CONFLICT | 409 | Resource already exists (e.g. duplicate email) |
| AGENT_NOT_STOPPED | 409 | Agent must be stopped before this action |
| PAYMENT_REQUIRED | 402 | Billing not set up or payment failed |
| RATE_LIMITED | 429 | Too many requests |
| INTERNAL_ERROR | 500 | Server error |
