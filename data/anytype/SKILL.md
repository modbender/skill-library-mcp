---
name: anytype
description: Interact with Anytype via anytype-cli and its HTTP API. Use when reading, creating, updating, or searching objects/pages in Anytype spaces; managing spaces; or automating Anytype workflows. Covers first-time setup (account creation, service start, space joining, API key) and ongoing API usage.
---

# Anytype Skill

Binary: `/root/.local/bin/anytype` (v0.1.9, already installed)
API base: `http://127.0.0.1:31012`
Auth: `Authorization: Bearer <ANYTYPE_API_KEY>` (key stored in `.env` as `ANYTYPE_API_KEY`)
API docs: https://developers.anytype.io

## Check Status First

```bash
anytype auth status     # is an account set up?
anytype space list      # is the service running + spaces joined?
```

If either fails → follow **Setup** below. Otherwise skip to **API Usage**.

## Setup (one-time)

```bash
# 1. Create a dedicated bot account (generates a key, NOT mnemonic-based)
anytype auth create tippy-bot

# 2. Install and start as a user service
anytype service install
anytype service start

# 3. Have Tadas send an invite link from Anytype desktop, then join
anytype space join <invite-link>

# 4. Create an API key
anytype auth apikey create tippy

# 5. Store the key
echo "ANYTYPE_API_KEY=<key>" >> /root/.openclaw/workspace/.env
```

Ask Tadas for the space invite link if not already provided.

## API Usage

Load `.env` first:
```python
import json, os, urllib.request
env = dict(l.strip().split('=',1) for l in open('/root/.openclaw/workspace/.env') if '=' in l and not l.startswith('#'))
API_KEY = env.get('ANYTYPE_API_KEY', '')
BASE = 'http://127.0.0.1:31012'
HEADERS = {'Authorization': f'Bearer {API_KEY}', 'Content-Type': 'application/json'}
```

See `references/api.md` for all endpoints and request shapes.

### Common Patterns

**List spaces:**
```
GET /v1/spaces
```

**Search objects globally:**
```
POST /v1/search
{"query": "meeting notes", "limit": 10}
```

**List objects in a space:**
```
GET /v1/spaces/{space_id}/objects?limit=50
```

**Create an object:**
```
POST /v1/spaces/{space_id}/objects
{"type_key": "page", "name": "My Page", "body": "Markdown content here"}
```

**Update an object (patch body/properties):**
```
PATCH /v1/spaces/{space_id}/objects/{object_id}
{"markdown": "Updated content"}
```
⚠️ **Create uses `body`, Update uses `markdown`** — different field names for the same content. Easy to mix up.

Use `scripts/anytype_api.py` as a ready-made helper for making API calls.
