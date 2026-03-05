# Jentic API Reference

**Base URL:** `https://api-gw.main.us-east-1.jenticprod.net/api/v1`
**Auth header:** `X-JENTIC-API-KEY: <key>` (from `skills.entries.jentic.apiKey` in openclaw config)

---

## Endpoints

### `GET /agents/apis`
List all APIs scoped to this agent.

```
Response: [{api_vendor, api_name, api_version}, ...]
```

---

### `POST /agents/search`
Semantic search scoped to agent's APIs. Returns results filtered by what the agent has access to.

**Request:**
```json
{
  "query": "send an email",
  "limit": 5
}
```

**Response:**
```json
{
  "results": [{
    "id": "op_...",
    "api_name": "googleapis.com/gmail",
    "entity_type": "operation",
    "summary": "Send email",
    "path": "/gmail/v1/users/{userId}/messages/send",
    "method": "POST",
    "distance": 0.607
  }],
  "total_count": 5,
  "query": "send an email"
}
```

- `entity_type`: `"operation"` or `"workflow"`
- `distance`: lower = more relevant (semantic similarity score)
- `id`: always starts with `op_` (operation) or `wf_` (workflow)

---

### `GET /files`
Load full schema for operations or workflows by UUID.

**Query params:**
- `operation_uuids`: comma-separated `op_...` IDs
- `workflow_uuids`: comma-separated `wf_...` IDs

**Response:**
```json
{
  "operations": {
    "op_...": {
      "method": "POST",
      "path": "/gmail/v1/users/{userId}/messages/send",
      "api_name": "googleapis.com/gmail",
      "summary": "Send email",
      "inputs": { ... },
      "security_requirements": null
    }
  },
  "workflows": { ... },
  "files": { ... }
}
```

- `inputs`: JSON schema for required/optional inputs. `null` means no inputs or they're inferred.
- `security_requirements`: `null` means no credentials needed; non-null means the API secret must be configured in Jentic.

---

### `POST /agents/execute`
Execute an operation or workflow.

**Request:**
```json
{
  "execution_type": "operation",
  "uuid": "op_7ae5ecc5d29bed24",
  "inputs": {
    "category": "general"
  }
}
```

- `execution_type`: `"operation"` or `"workflow"` (derived from UUID prefix)
- `uuid`: the `op_...` or `wf_...` UUID
- `inputs`: key/value pairs matching the schema from `/files`

**Response:**
```json
{
  "success": true,
  "status_code": 200,
  "output": { ... },
  "error": null,
  "step_results": null
}
```

- `success: false` + `error` usually means missing credentials in Jentic or bad inputs
- `output` is whatever the upstream API returned (can be a list, dict, or string)

---

### `POST /search/all` (Public — no auth)
Search the full public catalog. Useful for discovery.

**Request:**
```json
{
  "query": "send a WhatsApp message",
  "limit": 10
}
```

**Response:**
```json
{
  "operations": [ { "id", "api_name", "path", "method", "summary", "distance", ... } ],
  "workflows": [ { "id", "name", "api_name", "workflow_id", ... } ],
  "apis": [ { "id", "api_name", "api_version", ... } ],
  "total_count": 10,
  "query": "send a WhatsApp message"
}
```

---

## Common Error Patterns

| Error | Cause | Fix |
|---|---|---|
| `RemoteDisconnected` | Missing credentials for the API | Add secret at jentic.com |
| `Unauthorized` | Missing or bad `X-JENTIC-API-KEY` | Check key in openclaw config |
| `success: false, error: "..."` | Bad inputs or upstream API error | Check inputs schema via `/files` |
| Empty results from `search` | API not in agent scope | Try `pub-search` to confirm it exists |
