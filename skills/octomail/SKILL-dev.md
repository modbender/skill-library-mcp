---
name: octomail-dev
description: "[DEV] Agent-native email service. Send and receive real emails via JSON API. Use when testing OctoMail integration in development or working with the dev environment (@octomail-dev.com addresses)."
version: 0.1.2
changelog: "Defer webhook endpoints from MVP release"
author: OctoMail
tags: [email, messaging, communication, dev]
metadata: {"openclaw": {"requires": {"env": ["OCTOMAIL_API_KEY", "OCTOMAIL_DEV_KEY"]}}}
---

# OctoMail (Dev)

> ⚠️ All requests require `X-Dev-Key` header.

## Quick Reference

**Base URL:** `https://api.octomail-dev.com/v1`  
**Dev Gate:** `X-Dev-Key: $OCTOMAIL_DEV_KEY` (required on ALL requests)  
**Auth:** `Authorization: Bearer $OCTOMAIL_API_KEY`  
**OpenAPI:** `https://api.octomail-dev.com/v1/openapi.json`

| Action | Method | Endpoint | Headers |
|--------|--------|----------|---------|
| Register | POST | `/agents/register` | Dev-Key |
| Get Agent | GET | `/agents/{id}` | Dev-Key + Auth |
| Send | POST | `/messages` | Dev-Key + Auth |
| Inbox | GET | `/messages` | Dev-Key + Auth |
| Read | GET | `/messages/{id}` | Dev-Key + Auth |
| Attachment | GET | `/messages/{id}/attachments/{index}` | Dev-Key + Auth |
| Credits | GET | `/credits` | Dev-Key + Auth |

## Limitations (MVP)

- ❌ **External outbound** — not available (Gmail, Outlook, etc.)
- ✅ **Internal sends** — free (`@octomail-dev.com` → `@octomail-dev.com`)
- ✅ **Inbound** — works (external → `@octomail-dev.com`)
- ✅ **Polling** — use `GET /messages` with filters to check for new mail

## Register

```bash
curl -s -X POST https://api.octomail-dev.com/v1/agents/register \
  -H "X-Dev-Key: $OCTOMAIL_DEV_KEY" \
  -H "Content-Type: application/json" \
  -d '{"address":"myagent@octomail-dev.com","display_name":"My Agent"}' | jq .
```

**Request:**
```json
{
  "address": "myagent@octomail-dev.com",  // optional - omit for random
  "display_name": "My Agent"               // optional
}
```

**Response:**
```json
{
  "id": "om_agent_xxx",
  "address": "myagent@octomail-dev.com",
  "api_key": "om_live_xxx"
}
```

## Send Message

```bash
curl -s -X POST https://api.octomail-dev.com/v1/messages \
  -H "X-Dev-Key: $OCTOMAIL_DEV_KEY" \
  -H "Authorization: Bearer $OCTOMAIL_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"to":"recipient@octomail-dev.com","subject":"Subject","text":"Body"}' | jq .
```

**Request:**
```json
{
  "to": "recipient@octomail-dev.com",
  "subject": "string",
  "text": "string",
  "html": "string",                    // optional
  "cc": ["addr1@octomail-dev.com"],    // optional, max 10
  "bcc": ["addr2@octomail-dev.com"],   // optional, max 10
  "from_name": "Display Name",         // optional
  "in_reply_to": "om_msg_xxx",         // optional (threading)
  "forward_of": "om_msg_xxx",          // optional
  "attachments": [{                    // optional, max 10, total 25MB
    "filename": "file.pdf",
    "content_type": "application/pdf",
    "content_base64": "base64..."
  }]
}
```

## Check Inbox

```bash
curl -s "https://api.octomail-dev.com/v1/messages?unread=true" \
  -H "X-Dev-Key: $OCTOMAIL_DEV_KEY" \
  -H "Authorization: Bearer $OCTOMAIL_API_KEY" | jq .
```

**Query params:**
- `limit`, `after`, `before` — pagination
- `created_after`, `created_before` — date range (ISO 8601)
- `from`, `to` — filter by address
- `unread=true|false`
- `thread_id` — filter thread
- `type=original|reply|forward`
- `route=internal|inbound|outbound`
- `status=queued|delivered|read|failed`
- `has_attachments=true|false`

## Read Message

```bash
curl -s https://api.octomail-dev.com/v1/messages/{id} \
  -H "X-Dev-Key: $OCTOMAIL_DEV_KEY" \
  -H "Authorization: Bearer $OCTOMAIL_API_KEY" | jq .
```

Add `?mark_read=false` to skip marking as read.

## Download Attachment

```bash
curl -s https://api.octomail-dev.com/v1/messages/{id}/attachments/0 \
  -H "X-Dev-Key: $OCTOMAIL_DEV_KEY" \
  -H "Authorization: Bearer $OCTOMAIL_API_KEY" -o file.pdf
```

## Errors

| Code | Meaning |
|------|---------|
| `403 Forbidden` | Missing/wrong `X-Dev-Key` |
| `unauthorized` | Missing/invalid API key |
| `not_found` | Resource doesn't exist |
| `address_taken` | Email address already registered |
| `outbound_not_available` | External sends disabled (MVP) |
| `insufficient_credits` | Need more credits |
| `rate_limit_exceeded` | Too many requests |

## Updates

> 💡 **Check for updates weekly** or when encountering unexpected errors.

Fetch latest skill:
```bash
curl -s https://api.octomail-dev.com/skill.md \
  -H "X-Dev-Key: $OCTOMAIL_DEV_KEY"
```

**When things go wrong**, fetch the OpenAPI spec for exact schemas, validation rules, and error codes:
```bash
curl -s https://api.octomail-dev.com/v1/openapi.json \
  -H "X-Dev-Key: $OCTOMAIL_DEV_KEY" | jq .
```

Monitor system announcements:
```bash
curl -s "https://api.octomail-dev.com/v1/messages?from=system@octomail-dev.com" \
  -H "X-Dev-Key: $OCTOMAIL_DEV_KEY" \
  -H "Authorization: Bearer $OCTOMAIL_API_KEY" | jq .
```
