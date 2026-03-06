# User API

Base URL: `/api/v1/users`

All endpoints require authentication via Bearer token.

---

## GET /api/v1/users/me

Retrieve the current authenticated user's profile.

**Auth:** Required (any role)

### Request Body

None.

### Request Example

```
GET /api/v1/users/me
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
```

### Response Example

**Status: 200 OK**

```json
{
  "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "email": "personal@example.com",
  "display_name": "张明",
  "avatar_url": "https://cdn.tmrland.com/avatars/a1b2c3d4.jpg",
  "role": "personal",
  "is_active": true,
  "is_email_verified": true,
  "kyc_status": "verified",
  "locale_preference": "zh",
  "theme_preference": "dark",
  "created_at": "2026-02-27T10:30:00Z"
}
```

### Errors

| Status | Detail | Condition |
|---|---|---|
| 401 | `"Not authenticated"` | Missing or invalid Bearer token |

---

## PATCH /api/v1/users/me

Update the current user's profile fields. Only provided fields are updated.

**Auth:** Required (any role)

### Request Body

| Field | Type | Required | Description |
|---|---|---|---|
| `display_name` | str \| None | No | Display name, max 100 characters |
| `avatar_url` | str \| None | No | Avatar image URL, max 500 characters |
| `locale_preference` | str \| None | No | Preferred locale (`"zh"`, `"en"`), max 10 characters |
| `theme_preference` | str \| None | No | Theme preference (`"light"`, `"dark"`, `"system"`), max 10 characters |

### Request Example

```json
{
  "display_name": "Ming Zhang",
  "locale_preference": "en",
  "theme_preference": "dark"
}
```

### Response Example

**Status: 200 OK**

```json
{
  "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "email": "personal@example.com",
  "display_name": "Ming Zhang",
  "avatar_url": "https://cdn.tmrland.com/avatars/a1b2c3d4.jpg",
  "role": "personal",
  "is_active": true,
  "is_email_verified": true,
  "kyc_status": "verified",
  "locale_preference": "en",
  "theme_preference": "dark",
  "created_at": "2026-02-27T10:30:00Z"
}
```

### Errors

| Status | Detail | Condition |
|---|---|---|
| 401 | `"Not authenticated"` | Missing or invalid Bearer token |
| 422 | Pydantic validation array | Field exceeds max length or invalid type |

---

## PATCH /api/v1/users/me/password

Change the current user's password. Requires the old password for verification.

**Auth:** Required (any role)

### Request Body

| Field | Type | Required | Description |
|---|---|---|---|
| `old_password` | str | Yes | Current password |
| `new_password` | str | Yes | New password, minimum 8 characters |

### Request Example

```json
{
  "old_password": "securePass123",
  "new_password": "evenMoreSecure456"
}
```

### Response Example

**Status: 200 OK**

```json
{
  "message": "Password updated successfully"
}
```

### Errors

| Status | Detail | Condition |
|---|---|---|
| 400 | `"Incorrect old password"` | Old password does not match |
| 401 | `"Not authenticated"` | Missing or invalid Bearer token |
| 422 | Pydantic validation array | New password too short |
