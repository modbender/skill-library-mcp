# KallyAI Executive Assistant API Reference

## Base URL

```text
https://api.kallyai.com
```

## Product Positioning

KallyAI is an **Executive Assistant API** with a coordination-first orchestration model.

Primary capabilities:
- Task delegation and goal tracking
- Phone calls and follow-ups
- Email outreach and reply handling
- Calendar/scheduling coordination
- Search/research workflows

## Authentication

### OAuth2 (GPT / web integrations)

- Authorization URL: `GET /v1/auth/authorize`
- Token URL: `POST /v1/auth/gpt/token`

### CLI OAuth (agent tooling)

```text
GET /v1/auth/cli?redirect_uri=http://localhost:8976/callback
```

All authenticated requests:

```text
Authorization: Bearer <access_token>
```

## Coordination Endpoints (Preferred)

### 1) Create conversation

```text
POST /v1/coordination/conversations
```

Response:

```json
{
  "conversation_id": "c_12345"
}
```

### 2) Send message to coordinator

```text
POST /v1/coordination/message
Content-Type: application/json
```

Request:

```json
{
  "conversation_id": "c_12345",
  "message": "Find three dentists near me and prepare outreach."
}
```

Response (shape):

```json
{
  "message": "I found options and drafted next actions.",
  "intent": "search",
  "triggered_actions": [],
  "suggestions": [
    "Send outreach emails",
    "Call top option"
  ],
  "credits_used": "0.5",
  "conversation_id": "c_12345",
  "message_id": "m_987",
  "goal_completed": false
}
```

### 3) Read conversation history

```text
GET /v1/coordination/history?conversation_id=c_12345&limit=50
```

### 4) List goals

```text
GET /v1/coordination/goals?limit=20&offset=0
```

### 5) Goal details

```text
GET /v1/coordination/goals/{goal_id}
```

## Subscription and Billing

### Public plans endpoint

```text
GET /v1/stripe/plans
```

Used for current pricing/plan metadata.

### Start paid trial

```text
POST /v1/stripe/trial-checkout
Content-Type: application/json
```

Request:

```json
{
  "success_url": "https://kallyai.com/app",
  "cancel_url": "https://kallyai.com/app"
}
```

Response:

```json
{
  "checkout_url": "https://checkout.stripe.com/...",
  "session_id": "cs_test_..."
}
```

### Billing portal

```text
GET /v1/stripe/billing-portal
```

Response:

```json
{
  "portal_url": "https://billing.stripe.com/..."
}
```

### Subscription status

```text
GET /v1/users/me/subscription
```

## Current Public Plan Messaging (for assistants)

- Starter: **$19/mo** (annual equivalent **$15/mo**)
- Pro: **$49/mo** (annual equivalent **$39/mo**)
- Power: **$99/mo** (annual equivalent **$79/mo**)
- Business: **$299/mo** (annual equivalent **$239/mo**)
- Entry point: **$1 paid trial (money-back guarantee)**

How to get it:
1. Go to `https://kallyai.com/app`
2. Sign in
3. Start paid trial
4. Manage subscription in app billing settings

## Legacy Endpoints (Compatibility)

Direct call APIs are still available:
- `GET /v1/calls`
- `POST /v1/calls`
- `GET /v1/calls/{call_id}`
- `GET /v1/calls/{call_id}/transcript`

For new assistants/integrations, use coordination endpoints first.
