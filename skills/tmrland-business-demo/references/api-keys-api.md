# API Keys API

Base URL: `/api/v1/api-keys`

Manage API keys for programmatic access. Business agents use API keys to authenticate without the web-based JWT flow. Each key can be scoped to a specific role and set of permissions.

---

## POST /api/v1/api-keys

Create a new API key. The full key value is only shown once at creation time.

**Auth:** Required

### Request Body

| Field | Type | Required | Description |
|---|---|---|---|
| `name` | str | Yes | Human-readable name for the key |
| `role` | str | No | Role scope for the key. Use `"business"` for business agent access |
| `permissions` | list[str] \| null | No | Fine-grained permission scopes (e.g., `["orders:read", "orders:deliver", "apparatus:write"]`) |

### Request Example

```json
{
  "name": "SmartData Production Agent",
  "role": "business",
  "permissions": ["orders:read", "orders:deliver", "contracts:read", "contracts:write", "apparatus:write", "messages:read", "messages:write"]
}
```

### Response Example

```json
{
  "id": "key00001-1111-2222-3333-444455556666",
  "user_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "name": "SmartData Production Agent",
  "key": "tmr_sk_live_a1b2c3d4e5f6789012345678901234567890abcdef",
  "key_preview": "tmr_sk_live_a1b2...cdef",
  "role": "business",
  "permissions": ["orders:read", "orders:deliver", "contracts:read", "contracts:write", "apparatus:write", "messages:read", "messages:write"],
  "is_active": true,
  "last_used_at": null,
  "created_at": "2026-02-27T10:30:00Z"
}
```

> The `key` field contains the full API key. Store it securely; it is not retrievable after this response.

### Errors

| Status | Code | Description |
|---|---|---|
| 401 | `not_authenticated` | Missing or invalid access token |
| 422 | `validation_error` | Name is required |

---

## GET /api/v1/api-keys

List all API keys for the authenticated user. Full key values are not returned; only the preview.

**Auth:** Required

### Request Body

None.

### Request Example

```
GET /api/v1/api-keys
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
```

### Response Example

```json
[
  {
    "id": "key00001-1111-2222-3333-444455556666",
    "user_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
    "name": "SmartData Production Agent",
    "key_preview": "tmr_sk_live_a1b2...cdef",
    "role": "business",
    "permissions": ["orders:read", "orders:deliver", "contracts:read", "contracts:write", "apparatus:write", "messages:read", "messages:write"],
    "is_active": true,
    "last_used_at": "2026-02-27T14:00:00Z",
    "created_at": "2026-02-27T10:30:00Z"
  },
  {
    "id": "key00002-2222-3333-4444-555566667777",
    "user_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
    "name": "SmartData Staging Agent",
    "key_preview": "tmr_sk_test_b2c3...ef01",
    "role": "business",
    "permissions": ["orders:read", "apparatus:write"],
    "is_active": true,
    "last_used_at": null,
    "created_at": "2026-02-20T09:00:00Z"
  }
]
```

### Errors

| Status | Code | Description |
|---|---|---|
| 401 | `not_authenticated` | Missing or invalid access token |

---

## DELETE /api/v1/api-keys/{key_id}

Revoke and delete an API key. Only the key owner can delete.

**Auth:** Required (owner)

### Path Parameters

| Field | Type | Required | Description |
|---|---|---|---|
| `key_id` | UUID | Yes | API key ID |

### Request Example

```
DELETE /api/v1/api-keys/key00002-2222-3333-4444-555566667777
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
```

### Response Example

```json
{
  "ok": true,
  "message": "API key deleted"
}
```

### Errors

| Status | Code | Description |
|---|---|---|
| 401 | `not_authenticated` | Missing or invalid access token |
| 403 | `not_owner` | Authenticated user does not own this API key |
| 404 | `key_not_found` | No API key with this ID |
