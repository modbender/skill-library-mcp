---
name: devrev
description: Interact with DevRev to create/update issues and tickets, and search/query works and parts. Use when asked to create a DevRev issue or ticket, update an existing work item, search for issues or tickets, list open/closed works, get details about a specific work item by ID, or perform any DevRev API operations. Requires DEVREV_TOKEN environment variable.
---

# DevRev Skill

Interact with DevRev via its REST API to manage issues, tickets, and parts.

## Setup

Requires a DevRev PAT token. Read from env var `DEVREV_TOKEN` or ask the user to provide it.

```bash
export DEVREV_TOKEN=<your-pat-token>
```

Base URL: `https://api.devrev.ai`
Auth header: `Authorization: <token>` (no "Bearer" prefix needed)

## Common Operations

### List Works (issues + tickets)
```bash
curl -s "https://api.devrev.ai/works.list" \
  -H "Authorization: $DEVREV_TOKEN" | python3 -m json.tool
```

Filter by type:
```bash
# Only issues
curl -s "https://api.devrev.ai/works.list?type[]=issue" \
  -H "Authorization: $DEVREV_TOKEN"

# Only tickets  
curl -s "https://api.devrev.ai/works.list?type[]=ticket" \
  -H "Authorization: $DEVREV_TOKEN"
```

### Get a Specific Work Item
```bash
# Get by DON ID
curl -s -X POST "https://api.devrev.ai/works.get" \
  -H "Authorization: $DEVREV_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"id": "don:core:dvrv-us-1:devo/XXXX:issue/72"}'
```

### Create an Issue
```bash
curl -s -X POST "https://api.devrev.ai/works.create" \
  -H "Authorization: $DEVREV_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "type": "issue",
    "title": "Issue title",
    "body": "Description here",
    "applies_to_part": "don:core:...:product/X",
    "owned_by": ["don:identity:...:devu/1"]
  }'
```

### Create a Ticket
```bash
curl -s -X POST "https://api.devrev.ai/works.create" \
  -H "Authorization: $DEVREV_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "type": "ticket",
    "title": "Ticket title",
    "body": "Description here",
    "applies_to_part": "don:core:...:product/X",
    "severity": "medium"
  }'
```

Severity options: `blocker`, `high`, `medium`, `low`

### Update a Work Item
```bash
curl -s -X POST "https://api.devrev.ai/works.update" \
  -H "Authorization: $DEVREV_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "id": "don:core:...:issue/72",
    "title": "Updated title",
    "body": "Updated description"
  }'
```

### Search Works
```bash
curl -s -X POST "https://api.devrev.ai/works.list" \
  -H "Authorization: $DEVREV_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "type": ["issue"],
    "stage": {"name": ["triage", "in_development"]}
  }'
```

### List Parts (products, features, enhancements)
```bash
curl -s "https://api.devrev.ai/parts.list" \
  -H "Authorization: $DEVREV_TOKEN"
```

## Key Data Structures

See `references/api.md` for full field details and DON ID format.

## Tips

- **DON IDs** are the full `don:core:...` identifiers used for all references
- **display_id** (e.g. `ISS-72`, `TKT-29`) is human-readable but use the DON ID for API calls
- To get parts (products) for creating works, call `parts.list` first
- Priority for issues: `p0` (critical) → `p1` → `p2` → `p3`
- Stage names for issues: `triage`, `in_development`, `completed`
- Stage names for tickets: `queued`, `work_in_progress`, `resolved`
