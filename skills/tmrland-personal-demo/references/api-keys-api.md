# API Keys API

Base URL: `/api/v1/api-keys`

All endpoints require authentication via Bearer token. API keys provide an alternative authentication mechanism for agent/SDK integrations, passed via the `X-API-Key` header on subsequent requests.

---

## POST /api/v1/api-keys

Create a new API key. The `raw_key` field is returned only once at creation time and cannot be retrieved again.

**Auth:** Required

### Request Body

| Field | Type | Required | Description |
|---|---|---|---|
| `name` | str | Yes | Human-readable key name, max 100 characters |
| `role` | str | No | Role scope for the key, default `"business"`. Accepted: `"business"`, `"business"`, `"both"` |
| `permissions` | list[str] \| None | No | Optional list of fine-grained permission scopes |

### Request Example

```json
{
  "name": "Production Personal Agent",
  "role": "personal",
  "permissions": ["intentions:write", "orders:write", "wallet:read"]
}
```

### Response Example

**Status: 201 Created**

```json
{
  "id": "d4e5f6a7-b8c9-0123-defa-234567890123",
  "name": "Production Personal Agent",
  "key_prefix": "tmr_b_7k3m",
  "role": "personal",
  "permissions": ["intentions:write", "orders:write", "wallet:read"],
  "status": "active",
  "usage_count": 0,
  "created_at": "2026-02-27T10:30:00Z",
  "raw_key": "tmr_b_7k3mX9pLqR2wN8vT4jH6cF1dA5sY0eU3gI7oK"
}
```

### Errors

| Status | Detail | Condition |
|---|---|---|
| 400 | `"Maximum API key limit reached"` | User has too many active keys |
| 401 | `"Not authenticated"` | Missing or invalid Bearer token |
| 422 | Pydantic validation array | Name exceeds max length or invalid role |

---

## GET /api/v1/api-keys

List all API keys belonging to the current user. The `raw_key` field is never included in list responses.

**Auth:** Required

### Request Body

None.

### Request Example

```
GET /api/v1/api-keys
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
```

### Response Example

**Status: 200 OK**

```json
[
  {
    "id": "d4e5f6a7-b8c9-0123-defa-234567890123",
    "name": "Production Personal Agent",
    "key_prefix": "tmr_b_7k3m",
    "role": "personal",
    "permissions": ["intentions:write", "orders:write", "wallet:read"],
    "status": "active",
    "usage_count": 142,
    "created_at": "2026-02-27T10:30:00Z"
  },
  {
    "id": "e5f6a7b8-c9d0-1234-efab-345678901234",
    "name": "Staging Test Key",
    "key_prefix": "tmr_b_2n8q",
    "role": "personal",
    "permissions": null,
    "status": "active",
    "usage_count": 7,
    "created_at": "2026-02-25T08:00:00Z"
  }
]
```

### Errors

| Status | Detail | Condition |
|---|---|---|
| 401 | `"Not authenticated"` | Missing or invalid Bearer token |

---

## DELETE /api/v1/api-keys/{key_id}

Permanently revoke and delete an API key. Only the key owner can delete their own keys.

**Auth:** Required (owner)

### Path Parameters

| Field | Type | Required | Description |
|---|---|---|---|
| `key_id` | UUID | Yes | ID of the API key to delete |

### Request Body

None.

### Request Example

```
DELETE /api/v1/api-keys/d4e5f6a7-b8c9-0123-defa-234567890123
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
```

### Response Example

**Status: 204 No Content**

No response body.

### Errors

| Status | Detail | Condition |
|---|---|---|
| 401 | `"Not authenticated"` | Missing or invalid Bearer token |
| 403 | `"Not authorized to delete this API key"` | User does not own this key |
| 404 | `"API key not found"` | Key ID does not exist |
