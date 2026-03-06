---
name: lemlist
primaryEnv: LEMLIST_API_KEY
description: |
  Official Lemlist API integration for sales automation and multichannel outreach.
  Use this skill when users want to:
  - Manage campaigns (create, list, pause, start, get stats)
  - Add, update, or remove leads from campaigns
  - Send messages via email, LinkedIn, WhatsApp, or SMS through inbox
  - Set up and manage webhooks for campaign events
  - Configure schedules for campaign sending
  - Manage unsubscribes (emails and domains)
  - Export campaign data (leads, activities, contacts)
  - Enrich leads with additional data
  - Control Lemwarm email warming
  - Work with sequences and steps
  - Manage inbox labels and conversations
  Examples: "list my lemlist campaigns", "add a lead to my campaign", "pause my campaign",
  "show campaign stats", "set up a webhook for email opens", "export my leads"
---

# Lemlist

Interact with the Lemlist API to manage campaigns, leads, sequences, schedules, activities, inbox, webhooks, unsubscribes, exports, and enrichment.

Full endpoint reference: `references/api-endpoints.md`
Official API docs: https://developer.lemlist.com/api-reference

## Setup

### 1. Get API key

1. Log in to [Lemlist](https://app.lemlist.com)
2. Go to **Settings > Integrations > API Keys**
3. Create a new key — copy immediately, shown **only once**

### 2. Configure in OpenClaw

Add to `~/.openclaw/openclaw.json`:

```json
{
  "skills": {
    "entries": {
      "lemlist": {
        "apiKey": "your-lemlist-api-key"
      }
    }
  }
}
```

Alternative explicit format:

```json
{
  "skills": {
    "entries": {
      "lemlist": {
        "env": {
          "LEMLIST_API_KEY": "your-lemlist-api-key"
        }
      }
    }
  }
}
```

### 3. Verify

Run: `Get my Lemlist team info`

### Docker sandbox

Forward the key explicitly:

```json
{
  "agents": {
    "defaults": {
      "sandbox": {
        "docker": {
          "env": ["LEMLIST_API_KEY"]
        }
      }
    }
  }
}
```

## Authentication

Base URL: `https://api.lemlist.com/api`

Basic Auth with **empty username** (colon before key is mandatory):

```
Authorization: Basic base64(:LEMLIST_API_KEY)
```

## Python Helper

Use this pattern for all API calls:

```python
import urllib.request, os, json, base64

API_KEY = os.environ["LEMLIST_API_KEY"]
AUTH = base64.b64encode(f":{API_KEY}".encode()).decode()
BASE = "https://api.lemlist.com/api"

def api(path, method="GET", data=None):
    body = json.dumps(data).encode() if data else None
    req = urllib.request.Request(f"{BASE}{path}", data=body, method=method)
    req.add_header("Authorization", f"Basic {AUTH}")
    req.add_header("User-Agent", "OpenClaw/1.0")
    if data:
        req.add_header("Content-Type", "application/json")
    return json.load(urllib.request.urlopen(req))
```

## Endpoint Summary

| Domain | Key endpoints |
|--------|--------------|
| **Team** | GET `/team`, `/team/members`, `/team/credits`, `/team/senders` |
| **Campaigns** | GET/POST `/campaigns`, PATCH `/campaigns/:id`, POST `pause`/`start` |
| **Sequences** | GET `/campaigns/:id/sequences`, POST/PATCH/DELETE steps |
| **Leads (campaign)** | GET/POST/PATCH/DELETE `/campaigns/:id/leads/:idOrEmail` |
| **Leads (global)** | GET `/leads`, POST `pause`/`start`/`interested`/`notinterested` |
| **Lead variables** | POST/PATCH/DELETE `/leads/:id/variables` |
| **Activities** | GET `/activities` (filter: `campaignId`, `type`) |
| **Schedules** | CRUD `/schedules`, POST `/campaigns/:id/schedules` |
| **Unsubscribes** | GET `/unsubscribes`, POST/DELETE `/unsubscribes/:value` |
| **Webhooks** | GET/POST/DELETE `/hooks` (max 200/team) |
| **Inbox** | GET `/inbox`, POST `email`/`linkedin`/`whatsapp`/`sms` |
| **Inbox labels** | CRUD `/inbox/labels`, assign via `/conversations/labels/:contactId` |
| **Companies** | GET `/companies`, `/companies/:id/notes` |
| **Contacts** | GET `/contacts`, `/contacts/:idOrEmail` |
| **Exports** | GET `/campaigns/:id/export` (sync), `/export/start` (async) |
| **Enrichment** | POST `/leads/:id/enrich`, GET `/enrich/:id`, POST `/enrich` (batch) |
| **Tasks** | GET/POST/PATCH `/tasks`, POST `/tasks/ignore` |
| **Lemwarm** | POST `start`/`pause`, GET/PATCH `settings` via `/lemwarm/:mailboxId` |

For request/response details, read `references/api-endpoints.md`.

## Pagination

Params: `offset` (default 0), `limit` (max 100), `page` (1-based, overrides offset).

Paginated responses include `pagination: { totalRecords, currentPage, nextPage, totalPage }`. Some older endpoints return a plain array.

## ID Prefixes

`cam_` campaign, `lea_` lead, `skd_` schedule, `seq_` sequence, `tea_` team, `usr_` user.

## Gotchas

- **User-Agent required** — set `User-Agent: OpenClaw/1.0`, Python's default UA is blocked by Cloudflare (403)
- **Basic Auth format** — empty username mandatory: `base64(":key")`, not `base64("key")`
- **No campaign deletion** — only pause via API
- **Email encoding** — `@` → `%40` in URL path params
- **Webhook auto-deletion** — 404/410 response silently removes the webhook
- **No rate limiting** — the public API does not throttle
- **Variable deletion** — `DELETE /leads/:id/variables` deletes vars, not the lead
- **Sync vs async export** — `/export` returns CSV directly, `/export/start` + poll for large volumes
- **Limits** — 100 items/page, 200 webhooks/team, 100 API keys/team
