---
name: baserow
description: Work with Baserow tables/rows over the REST API for reads, inserts, and updates. Use when user asks to view or modify Baserow CRM/pipeline data.
metadata:
  {
    "openclaw": {
      "requires": { "bins": ["python3"] },
      "env": ["BASEROW_BASE_URL", "BASEROW_TOKEN"]
    }
  }
---

# Baserow Skill

Use Baserow REST API directly via Python stdlib (`urllib`). API docs: https://baserow.ericbone.me/api-docs/database/265

## Local auth convention (this workspace)

Primary env vars in `~/.openclaw/.env`:
- `BASEROW_BASE_URL=https://baserow.ericbone.me`
- `BASEROW_TOKEN=<personal API token>` (static; no expiry)

Auth header for DB calls:
```
Authorization: Token <BASEROW_TOKEN>
```

## Core API patterns

Base endpoint:
```
$BASEROW_BASE_URL/api/database/rows/table/{table_id}/
```

Always include: `?user_field_names=true`

## Renpho CRM table map (DB 265)

- `827` Sales Pipeline (BD Opportunity table)
- `828` Opportunity Line Items
- `829` Contacts
- `830` Interactions
- `831` Account Execution

## Operating conventions (Renpho)

- For inbound/outbound emails that are active deal motion: log in **Interactions (830)** and link Contact + Opportunity.
- Create/update a **Sales Pipeline (827)** opportunity for real BD opportunities.
- **BD Inbox** field can be used for intake linkage when that inbox object is present, but in-progress opportunity work should still live in Pipeline + Interactions.
- Keep Interactions to real sales interactions (no LinkedIn enrichment spam).

## ⚠️ Critical: .env Must Have Real Newlines

The `.env` file **must** use real newlines between vars, NOT `\n` literals:

```
BASEROW_BASE_URL="https://baserow.ericbone.me"
BASEROW_TOKEN="mOsuizlNhyUWclr7xKjIgxJxdMPVmkNy"
```

If written by an agent (e.g. `write` tool), verify with `cat ~/.openclaw/.env` — literal `\n` breaks `export $(grep ...)` silently.

## ⚠️ Use curl for Writes (PATCH/POST), Python for Reads

Python `urllib` returns 403 on PATCH/POST against this Baserow instance. **Use curl for all writes.** Python urllib is fine for GET/reads.

## Minimal examples

### List rows (Python OK for reads)
```bash
export $(grep -v '^#' ~/.openclaw/.env | xargs) && python3 - <<'PY'
import os, json, urllib.request
base=os.environ['BASEROW_BASE_URL'].rstrip('/')
token=os.environ['BASEROW_TOKEN']
table=829
url=f"{base}/api/database/rows/table/{table}/?user_field_names=true&size=50"
req=urllib.request.Request(url, headers={"Authorization": f"Token {token}"})
with urllib.request.urlopen(req, timeout=30) as r:
  print(json.dumps(json.load(r), indent=2)[:8000])
PY
```

### Create row (use curl)
```bash
source ~/.openclaw/.env  # or export from .env
curl -s -X POST \
  -H "Authorization: Token $BASEROW_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"Interaction title":"Example","Type":"Email","Sales Pipeline":[5],"Contact":[3]}' \
  "$BASEROW_BASE_URL/api/database/rows/table/830/?user_field_names=true"
```

### Update row (use curl)
```bash
source ~/.openclaw/.env
curl -s -X PATCH \
  -H "Authorization: Token $BASEROW_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"Blockers":"Updated blocker text","Last Touch":"2026-02-24"}' \
  "$BASEROW_BASE_URL/api/database/rows/table/827/5/?user_field_names=true"
```

## Safety

- Confirm table + row targets before bulk updates/deletes.
- Prefer small scoped updates and echo changed fields.
- Treat Baserow as source-of-truth for Renpho sales workflow (DB 265).
