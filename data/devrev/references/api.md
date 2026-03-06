# DevRev API Reference

## Authentication

DevRev uses PAT (Personal Access Token) for authentication.

```
Header: Authorization: <token>
```

No "Bearer" prefix required. Token format: `eyJhbGciOiJSUzI1NiIs...`

Generate at: https://app.devrev.ai/settings/tokens

## Base URL

```
https://api.devrev.ai
```

## DON ID Format

All objects use DevRev Object Notation (DON) IDs:
```
don:core:dvrv-us-1:devo/<org-id>:<object-type>/<id>
```

Examples:
- Issue: `don:core:dvrv-us-1:devo/1zf8bJRDJJ:issue/72`
- Ticket: `don:core:dvrv-us-1:devo/1zf8bJRDJJ:ticket/29`
- Product: `don:core:dvrv-us-1:devo/1zf8bJRDJJ:product/2`
- User: `don:identity:dvrv-us-1:devo/1zf8bJRDJJ:devu/1`

## Key Endpoints

### Works (Issues & Tickets)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET/POST | `/works.list` | List works with optional filters |
| POST | `/works.get` | Get a single work by ID |
| POST | `/works.create` | Create a new work item |
| POST | `/works.update` | Update an existing work item |
| POST | `/works.delete` | Delete a work item |

### Parts

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/parts.list` | List parts (products, features, etc.) |
| POST | `/parts.get` | Get a single part |
| POST | `/parts.create` | Create a part |
| POST | `/parts.update` | Update a part |

### Dev Users

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/dev-users.list` | List dev users |
| POST | `/dev-users.get` | Get a single user |

## Works Fields

### Common Fields (both issue and ticket)

```json
{
  "type": "issue" | "ticket",
  "title": "string (required)",
  "body": "string (markdown)",
  "applies_to_part": "don:...:product/X (required)",
  "owned_by": ["don:...:devu/1"],
  "tags": [{"id": "don:...:tag/X"}],
  "stage": { "name": "stage-name" }
}
```

### Issue-specific Fields

```json
{
  "type": "issue",
  "priority": "p0" | "p1" | "p2" | "p3",
  "target_close_date": "2025-12-31T00:00:00Z"
}
```

Issue stages: `triage` → `in_development` → `completed`

### Ticket-specific Fields

```json
{
  "type": "ticket",
  "severity": "blocker" | "high" | "medium" | "low",
  "visibility": "external" | "internal"
}
```

Ticket stages: `queued` → `work_in_progress` → `resolved`

## works.list Filters

```json
{
  "type": ["issue", "ticket"],
  "stage": {"name": ["triage"]},
  "owned_by": ["don:...:devu/1"],
  "applies_to_part": ["don:...:product/2"],
  "limit": 10,
  "cursor": "next_cursor_value"
}
```

## Response Format

Successful list:
```json
{
  "works": [...],
  "next_cursor": "abc123"
}
```

Successful single object:
```json
{
  "work": { ... }
}
```

Error:
```json
{
  "type": "error_type",
  "message": "error message"
}
```

## Pagination

Use `next_cursor` from response in subsequent requests:
```bash
curl "https://api.devrev.ai/works.list?cursor=<next_cursor>" \
  -H "Authorization: $DEVREV_TOKEN"
```
