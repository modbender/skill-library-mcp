---
name: ai-email-service
description: Receive-only email addresses for AI agents via aiemailservice.com. Use when an agent needs to sign up for a service, receive verification codes/OTPs, get password reset links, or read incoming emails. Provides free mailbox creation, message reading, long-polling for new mail, and automatic OTP extraction. No sending capability — receive-only by design.
---

# AI Email Service

Free receive-only email addresses for AI agents at `aiemailservice.com`.

## Base URL

```
https://aiemailservice.com
```

## Quick Start

### 1. Get an API Key

```
POST /v1/api-key/create
Content-Type: application/json

{}
```

Returns `{ "api_key": "ak_..." }` — save this, it's your only authentication.

### 2. Create a Mailbox

```
POST /v1/mailbox/create
x-api-key: ak_your_key
Content-Type: application/json

{}
```

Returns `{ "mailbox_id": "mbx_...", "email": "agent-xyz@aiemailservice.com", "status": "active" }`.

Pass `{ "username": "preferred-name" }` to request a specific name (random assigned if omitted).

### 3. Use the Email

Sign up for any service using the email address. Then read incoming mail via API.

### 4. Read Messages

```
GET /v1/mailbox/{mailbox_id}/messages
x-api-key: ak_your_key
```

### 5. Wait for a Specific Email (Long-Poll)

```
GET /v1/mailbox/{mailbox_id}/wait?timeout=30&from=noreply@github.com
x-api-key: ak_your_key
```

Hangs until a matching message arrives or timeout. Use this instead of polling.

### 6. Extract Verification Codes

```
GET /v1/mailbox/{mailbox_id}/codes
x-api-key: ak_your_key
```

Auto-extracts OTP codes, verification codes, and confirmation links.

## Authentication

All requests require `x-api-key: ak_your_key` header (except `POST /v1/api-key/create`).

Alternative: `Authorization: Bearer ak_your_key`

## All Endpoints

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `/v1/api-key/create` | No | Create API key |
| POST | `/v1/mailbox/create` | Yes | Create mailbox (up to 5 per key) |
| GET | `/v1/mailboxes` | Yes | List your mailboxes |
| GET | `/v1/mailbox/{id}/status` | Yes | Mailbox status |
| GET | `/v1/mailbox/{id}/messages` | Yes | List messages (`?limit=50&since=ISO`) |
| GET | `/v1/mailbox/{id}/messages/{msgId}` | Yes | Full message (text + HTML) |
| GET | `/v1/mailbox/{id}/latest` | Yes | Most recent message |
| GET | `/v1/mailbox/{id}/wait` | Yes | Long-poll for new mail (`?timeout=30&from=&subject_contains=`) |
| GET | `/v1/mailbox/{id}/codes` | Yes | Auto-extracted OTP/verification codes |
| DELETE | `/v1/mailbox/{id}` | Yes | Delete mailbox + messages |
| GET | `/v1/username/check/{username}` | No | Check custom username availability |
| GET | `/v1/ai-prompt` | No | Structured JSON prompt for AI agents |

## Example: Complete Signup Flow

```javascript
// 1. Get API key
const { api_key } = await fetch('https://aiemailservice.com/v1/api-key/create', {
  method: 'POST', headers: { 'Content-Type': 'application/json' }, body: '{}'
}).then(r => r.json());

// 2. Create mailbox
const { mailbox_id, email } = await fetch('https://aiemailservice.com/v1/mailbox/create', {
  method: 'POST',
  headers: { 'x-api-key': api_key, 'Content-Type': 'application/json' },
  body: '{}'
}).then(r => r.json());

// 3. Sign up for a service using `email`
// ... (browser automation, API call, etc.)

// 4. Wait for verification email
const { message } = await fetch(
  `https://aiemailservice.com/v1/mailbox/${mailbox_id}/wait?timeout=30&from=noreply@github.com`,
  { headers: { 'x-api-key': api_key } }
).then(r => r.json());

// 5. Get extracted code
const codes = await fetch(
  `https://aiemailservice.com/v1/mailbox/${mailbox_id}/codes`,
  { headers: { 'x-api-key': api_key } }
).then(r => r.json());

console.log('Verification code:', codes[0]?.codes[0]);
```

## Example: cURL

```bash
# Create API key
KEY=$(curl -s -X POST https://aiemailservice.com/v1/api-key/create -H 'Content-Type: application/json' -d '{}' | jq -r '.api_key')

# Create mailbox
curl -s -X POST https://aiemailservice.com/v1/mailbox/create \
  -H "x-api-key: $KEY" -H 'Content-Type: application/json' -d '{}'

# Read messages
curl -s https://aiemailservice.com/v1/mailbox/mbx_xxx/messages -H "x-api-key: $KEY"

# Wait for email from specific sender
curl -s "https://aiemailservice.com/v1/mailbox/mbx_xxx/wait?timeout=30&from=noreply@github.com" \
  -H "x-api-key: $KEY"

# Get verification codes
curl -s https://aiemailservice.com/v1/mailbox/mbx_xxx/codes -H "x-api-key: $KEY"
```

## Pricing

- **Free**: Up to 5 mailboxes per API key. All features included (messages, wait, codes).
- **Custom Username**: £99/year to reserve a specific username (e.g., `yourname@aiemailservice.com`). Random usernames are free.

## Important Rules

1. **Receive-only** — no sending capability exists. Do not attempt to send.
2. Up to 5 free mailboxes per API key. Create additional API keys if needed.
3. Rate limit: 60 requests/minute.
4. Message retention: 30 days.
5. Max 100 inbound emails per mailbox per day.
6. Use `/wait` for long-polling instead of repeatedly hitting `/messages`.
7. The `/codes` endpoint handles OTP extraction — prefer it over parsing emails manually.
