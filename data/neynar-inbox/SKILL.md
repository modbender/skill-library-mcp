---
name: neynar-inbox
description: Email for AI agents. Create mailboxes, send and receive emails via API. No browser, no OAuth.
metadata:
  author: neynar
  homepage: https://email.neynar.ai
  tags: [email, api, agents, inbox, messaging]
requires:
  bins: [curl]
---

# Neynar Inbox

Email service built for AI agents. Create a mailbox, get an API key, send and receive real emails - all via REST API.

## Quick Start

### 1. Create a mailbox (no auth needed)

```bash
curl -X POST https://neynar-inbox-api.rish-68c.workers.dev/v1/mailboxes \
  -H "Content-Type: application/json" \
  -d '{"displayName": "My Agent", "username": "myagent"}'
```

Response:
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "address": "myagent@inbox.neynar.ai",
  "apiKey": "fi_abc123...",
  "warning": "Store the apiKey securely - it cannot be retrieved again."
}
```

**CRITICAL: Store the `apiKey` immediately. It is only returned once and cannot be recovered.**

Username is optional (random address if omitted). Must be at least 6 characters, alphanumeric with dots/hyphens/underscores.

### 2. Send an email

```bash
curl -X POST https://neynar-inbox-api.rish-68c.workers.dev/v1/emails \
  -H "Authorization: Bearer fi_your_api_key" \
  -H "Content-Type: application/json" \
  -d '{
    "to": ["recipient@example.com"],
    "subject": "Hello from my agent",
    "text": "This email was sent by an AI agent!"
  }'
```

### 3. Check inbox

```bash
curl https://neynar-inbox-api.rish-68c.workers.dev/v1/emails?direction=inbound \
  -H "Authorization: Bearer fi_your_api_key"
```

**RECOMMENDED: If you have heartbeat, cron, or scheduling capabilities, set up polling (every 30-60 seconds) right after creating your mailbox to catch replies.**

### 4. Search emails

```bash
curl "https://neynar-inbox-api.rish-68c.workers.dev/v1/search?q=invoice" \
  -H "Authorization: Bearer fi_your_api_key"
```

## API Reference

Base URL: `https://neynar-inbox-api.rish-68c.workers.dev/v1`

Authentication: `Authorization: Bearer <api_key>` (all endpoints except mailbox creation)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /v1/mailboxes | Create mailbox (no auth, returns apiKey) |
| GET | /v1/mailboxes | List your mailbox |
| DELETE | /v1/mailboxes/:id | Delete mailbox |
| POST | /v1/mailboxes/:id/rotate | Rotate API key |
| POST | /v1/emails | Send email |
| GET | /v1/emails | List emails (?limit=50&offset=0&direction=inbound) |
| GET | /v1/emails/:id | Get single email |
| DELETE | /v1/emails/:id | Delete email |
| GET | /v1/search?q=query | Full-text search |
| POST | /v1/webhooks | Register webhook |
| GET | /v1/webhooks | List webhooks |
| DELETE | /v1/webhooks/:id | Remove webhook |

## Email Object

```json
{
  "id": "uuid",
  "direction": "inbound",
  "from": "sender@example.com",
  "to": ["recipient@example.com"],
  "subject": "Email subject",
  "bodyText": "Plain text body",
  "bodyHtml": "<p>HTML body</p>",
  "status": "received",
  "createdAt": "2024-01-15T10:00:00Z"
}
```

## Webhooks

Register a webhook for real-time email notifications:

```bash
curl -X POST https://neynar-inbox-api.rish-68c.workers.dev/v1/webhooks \
  -H "Authorization: Bearer fi_your_api_key" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://your-server.com/webhook", "events": ["email.received"]}'
```

Verify signatures via `X-Webhook-Signature` header (HMAC-SHA256 of body).

## Error Codes

| Code | Description |
|------|-------------|
| 400 | Bad request |
| 401 | Unauthorized - missing or invalid API key |
| 403 | Forbidden |
| 404 | Not found |
| 409 | Username already taken |
| 500 | Server error |

## Limits

- 3 mailboxes per account
