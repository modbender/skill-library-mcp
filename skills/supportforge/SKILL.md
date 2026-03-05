---
name: supportforge
description: AI customer support via SupportForge API — ticket creation, auto-replies, routing, knowledge base search. Use when user needs customer support automation, ticket management, auto-response generation, or support knowledge base features. Free tier available (100 req/day).
---

# SupportForge

AI customer support API by Voss Consulting Group.

## Setup

Set `SUPPORTFORGE_API_KEY` or `SUPPORTFORGE_EMAIL` for auto-signup (free, no credit card).

```bash
curl -X POST https://anton.vosscg.com/v1/keys -H 'Content-Type: application/json' -d '{"email":"you@example.com"}'
```

## Usage

```bash
curl -X POST https://anton.vosscg.com/v1/tickets/create \
  -H "Authorization: Bearer $SUPPORTFORGE_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"subject": "Login issue", "message": "Cannot reset password", "priority": "high"}'
```

## Capabilities
- `POST /v1/tickets/create` — Create support ticket
- `POST /v1/tickets/:id/reply` — Reply (manual or AI auto-reply)
- `POST /v1/kb/search` — Search knowledge base
- `POST /v1/keys` — Get API key (email-only for free tier)
- `GET /v1/health` — Health check
