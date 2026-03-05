---
name: WhatsApp Business API
slug: whatsapp-business-api
version: 1.0.0
homepage: https://clawic.com/skills/whatsapp-business-api
description: Complete WhatsApp Business Cloud API for messages, templates, media, webhooks, flows, and business profiles.
changelog: Initial release with full Cloud API coverage.
metadata: {"clawdbot":{"emoji":"💬","requires":{"env":["WHATSAPP_ACCESS_TOKEN","WHATSAPP_PHONE_NUMBER_ID"]},"primaryEnv":"WHATSAPP_ACCESS_TOKEN","os":["linux","darwin","win32"]}}
---

# WhatsApp Business API

Official Meta Cloud API integration. See auxiliary files for detailed operations.

## Quick Start

```bash
curl -X POST "https://graph.facebook.com/v21.0/$WHATSAPP_PHONE_NUMBER_ID/messages" \
  -H "Authorization: Bearer $WHATSAPP_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"messaging_product":"whatsapp","to":"1234567890","type":"text","text":{"body":"Hello!"}}'
```

## Setup

On first use, read `setup.md`. Preferences stored in `~/whatsapp-business-api/memory.md`.

## When to Use

Any WhatsApp Business operation: send messages, templates, media, interactive elements, manage webhooks, handle conversations, update business profiles.

## Architecture

```
~/whatsapp-business-api/
├── memory.md      # Account context + phone numbers
├── templates.md   # Approved templates reference
└── webhooks.md    # Webhook configurations
```

## Quick Reference

| Topic | File |
|-------|------|
| Setup & memory | `setup.md`, `memory-template.md` |
| Messages (text, media, interactive) | `messages.md` |
| Templates (create, manage, send) | `templates.md` |
| Media (upload, download, manage) | `media.md` |
| Webhooks & Events | `webhooks.md` |
| Business Profile & Phone Numbers | `business.md` |
| Flows (interactive forms) | `flows.md` |
| Best practices & limits | `best-practices.md` |

## Core Rules

1. **International format** — Phone numbers without `+` or leading zeros: `1234567890`
2. **24-hour window** — Free replies within 24h of customer message; templates required to initiate
3. **Template approval** — Templates need Meta approval (24-48h); test in sandbox first
4. **Idempotency** — Use `biz_opaque_callback_data` to track message state
5. **Webhook verification** — Always verify webhook signature with app secret
6. **Rate limits** — 80 messages/second per phone number; 1000 template messages/day (tier 1)
7. **Media limits** — Images <5MB, videos <16MB, documents <100MB

## Authentication

**Required environment variables:**
- `WHATSAPP_ACCESS_TOKEN` — System User access token (permanent) or User access token (60-day)
- `WHATSAPP_PHONE_NUMBER_ID` — Your registered phone number ID
- `WHATSAPP_BUSINESS_ACCOUNT_ID` — Your WABA ID (for templates)
- `WHATSAPP_APP_SECRET` — App secret for webhook verification

```bash
curl "https://graph.facebook.com/v21.0/$WHATSAPP_PHONE_NUMBER_ID" \
  -H "Authorization: Bearer $WHATSAPP_ACCESS_TOKEN"
```

### Token Types

| Type | Duration | Use Case |
|------|----------|----------|
| System User Token | Permanent | Production apps |
| User Token | 60 days | Development, testing |
| Temporary Token | 24 hours | Quick tests |

## Common Traps

- Phone format with `+` or `00` → API rejects
- Missing `messaging_product: "whatsapp"` → 400 error
- Template not approved → message fails silently
- Webhook signature not verified → security vulnerability
- Sending outside 24h window without template → blocked

## External Endpoints

| Endpoint | Purpose |
|----------|---------|
| `https://graph.facebook.com/v21.0/*` | Cloud API |

## Security & Privacy

**Environment variables used:**
- `WHATSAPP_ACCESS_TOKEN` — for API authentication
- `WHATSAPP_APP_SECRET` — for webhook signature verification

**Sent to Meta:** Messages, media, customer phone numbers via graph.facebook.com
**Stays local:** Tokens (never logged), ~/whatsapp-business-api/ preferences
**Never:** Log message content, skip webhook verification, store tokens in code

## Trust

This skill sends data to Meta (facebook.com/whatsapp).

## Related Skills
Install with `clawhub install <slug>` if user confirms:
- `api` — REST API patterns
- `webhook` — Webhook handling
- `chat` — Conversational patterns

## Feedback

- If useful: `clawhub star whatsapp-business-api`
- Stay updated: `clawhub sync`
