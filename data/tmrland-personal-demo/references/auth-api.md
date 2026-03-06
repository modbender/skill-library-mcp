# Authentication API

Base URL: `/api/v1/auth`

All endpoints in this section are **public** (no authentication required).

---

## POST /api/v1/auth/register

Register a new user account.

**Auth:** None

### Request Body

| Field | Type | Required | Description |
|---|---|---|---|
| `email` | EmailStr | Yes | User email address |
| `password` | str | Yes | Password, minimum 8 characters |
| `display_name` | str \| None | No | Display name, max 100 characters |
| `locale_preference` | str | No | Preferred locale, default `"zh"` |

### Request Example

```json
{
  "email": "personal@example.com",
  "password": "securePass123",
  "display_name": "张明",
  "locale_preference": "zh"
}
```

### Response Example

**Status: 201 Created**

```json
{
  "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "email": "personal@example.com",
  "display_name": "张明",
  "avatar_url": null,
  "role": "personal",
  "is_active": true,
  "is_email_verified": false,
  "kyc_status": "unverified",
  "locale_preference": "zh",
  "theme_preference": "system",
  "created_at": "2026-02-27T10:30:00Z"
}
```

### Errors

| Status | Detail | Condition |
|---|---|---|
| 400 | `"Email already registered"` | Email already exists in the system |
| 422 | Pydantic validation array | Invalid email format or password too short |

---

## POST /api/v1/auth/login

Authenticate with email and password.

**Auth:** None

### Request Body

| Field | Type | Required | Description |
|---|---|---|---|
| `email` | EmailStr | Yes | Registered email address |
| `password` | str | Yes | Account password |

### Request Example

```json
{
  "email": "personal@example.com",
  "password": "securePass123"
}
```

### Response Example

**Status: 200 OK**

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhMWIyYzNkNC1lNWY2LTc4OTAtYWJjZC1lZjEyMzQ1Njc4OTAiLCJleHAiOjE3NDA3MjAwMDB9.abc123",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhMWIyYzNkNC1lNWY2LTc4OTAtYWJjZC1lZjEyMzQ1Njc4OTAiLCJ0eXBlIjoicmVmcmVzaCJ9.def456",
  "token_type": "bearer"
}
```

### Errors

| Status | Detail | Condition |
|---|---|---|
| 401 | `"Incorrect email or password"` | Invalid credentials |
| 401 | `"Account is deactivated"` | User account is inactive |
| 422 | Pydantic validation array | Invalid email format |

---

## POST /api/v1/auth/login/code

Authenticate with email and a 6-digit verification code.

**Auth:** None

### Request Body

| Field | Type | Required | Description |
|---|---|---|---|
| `email` | EmailStr | Yes | Registered email address |
| `code` | str | Yes | 6-character verification code |

### Request Example

```json
{
  "email": "personal@example.com",
  "code": "482917"
}
```

### Response Example

**Status: 200 OK**

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhMWIyYzNkNC1lNWY2LTc4OTAtYWJjZC1lZjEyMzQ1Njc4OTAiLCJleHAiOjE3NDA3MjAwMDB9.abc123",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhMWIyYzNkNC1lNWY2LTc4OTAtYWJjZC1lZjEyMzQ1Njc4OTAiLCJ0eXBlIjoicmVmcmVzaCJ9.def456",
  "token_type": "bearer"
}
```

### Errors

| Status | Detail | Condition |
|---|---|---|
| 401 | `"Invalid or expired verification code"` | Code is wrong or expired |
| 404 | `"User not found"` | No account with that email |
| 422 | Pydantic validation array | Invalid email or code format |

---

## POST /api/v1/auth/send-code

Send a verification code to the user's email for passwordless login.

**Auth:** None

### Request Body

| Field | Type | Required | Description |
|---|---|---|---|
| `email` | EmailStr | Yes | Registered email address |

### Request Example

```json
{
  "email": "personal@example.com"
}
```

### Response Example

**Status: 200 OK**

```json
{
  "message": "Verification code sent",
  "code_preview": "482917"
}
```

### Errors

| Status | Detail | Condition |
|---|---|---|
| 404 | `"User not found"` | No account with that email |
| 422 | Pydantic validation array | Invalid email format |

---

## POST /api/v1/auth/refresh

Exchange a refresh token for a new access/refresh token pair.

**Auth:** None

### Request Body

| Field | Type | Required | Description |
|---|---|---|---|
| `refresh_token` | str | Yes | Valid refresh token from a previous login |

### Request Example

```json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhMWIyYzNkNC1lNWY2LTc4OTAtYWJjZC1lZjEyMzQ1Njc4OTAiLCJ0eXBlIjoicmVmcmVzaCJ9.def456"
}
```

### Response Example

**Status: 200 OK**

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhMWIyYzNkNC1lNWY2LTc4OTAtYWJjZC1lZjEyMzQ1Njc4OTAiLCJleHAiOjE3NDA3MjUwMDB9.ghi789",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhMWIyYzNkNC1lNWY2LTc4OTAtYWJjZC1lZjEyMzQ1Njc4OTAiLCJ0eXBlIjoicmVmcmVzaDIifQ.jkl012",
  "token_type": "bearer"
}
```

### Errors

| Status | Detail | Condition |
|---|---|---|
| 401 | `"Invalid or expired refresh token"` | Token is malformed, expired, or revoked |

---

## POST /api/v1/auth/forgot-password

Request a password reset code sent to the user's email.

**Auth:** None

### Request Body

| Field | Type | Required | Description |
|---|---|---|---|
| `email` | EmailStr | Yes | Registered email address |

### Request Example

```json
{
  "email": "personal@example.com"
}
```

### Response Example

**Status: 200 OK**

```json
{
  "message": "Password reset code sent",
  "code_preview": "739281"
}
```

### Errors

| Status | Detail | Condition |
|---|---|---|
| 404 | `"User not found"` | No account with that email |
| 422 | Pydantic validation array | Invalid email format |

---

## POST /api/v1/auth/verify-reset-code

Verify a password reset code and receive a reset token. Call this between `forgot-password` and `reset-password`.

**Auth:** None

### Request Body

| Field | Type | Required | Description |
|---|---|---|---|
| `email` | EmailStr | Yes | Registered email address |
| `code` | str | Yes | 6-character reset code from email |

### Request Example

```json
{
  "email": "user@example.com",
  "code": "739281"
}
```

### Response Example

**Status: 200 OK**

```json
{
  "reset_token": "eyJhbGciOiJIUzI1NiIs..."
}
```

### Errors

| Status | Detail | Condition |
|---|---|---|
| 400 | `"Invalid or expired reset code"` | Code is wrong or expired |
| 404 | `"User not found"` | No account with that email |

---

## POST /api/v1/auth/reset-password

Reset the user's password using a reset token/code.

**Auth:** None

### Request Body

| Field | Type | Required | Description |
|---|---|---|---|
| `token` | str | Yes | Password reset token received via email |
| `new_password` | str | Yes | New password, minimum 8 characters |

### Request Example

```json
{
  "token": "739281",
  "new_password": "newSecurePass456"
}
```

### Response Example

**Status: 200 OK**

```json
{
  "message": "Password has been reset successfully"
}
```

### Errors

| Status | Detail | Condition |
|---|---|---|
| 400 | `"Invalid or expired reset token"` | Token is wrong or expired |
| 422 | Pydantic validation array | Password too short |
