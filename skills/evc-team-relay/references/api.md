# EVC Team Relay — API Reference

Base URL: `$RELAY_CP_URL` (e.g. `https://cp.tr.entire.vc`)

All endpoints require `Authorization: Bearer <token>` unless noted otherwise.

---

## Authentication

### POST /v1/auth/login

Login with email and password.

**No auth required.**

Request:
```json
{"email": "user@example.com", "password": "secretpass"}
```

Response `200`:
```json
{
  "access_token": "eyJ...",
  "refresh_token": "abc123...",
  "token_type": "bearer",
  "expires_in": 3600
}
```

Errors: `400` (invalid credentials), `429` (rate limit: 10/min).

### POST /v1/auth/refresh

Refresh an expired access token.

Request:
```json
{"refresh_token": "abc123..."}
```

Response `200`: same as login response with new tokens.

### GET /v1/auth/me

Get current user information.

Response `200`:
```json
{
  "id": "uuid",
  "email": "user@example.com",
  "is_admin": false,
  "is_active": true,
  "created_at": "2026-01-01T00:00:00Z"
}
```

---

## Shares

### GET /v1/shares

List shares accessible to the authenticated user.

Query parameters:
| Param | Type | Default | Description |
|-------|------|---------|-------------|
| `kind` | string | — | Filter: `doc` or `folder` |
| `owned_only` | bool | false | Only shares owned by user |
| `member_only` | bool | false | Only shares where user is member (not owner) |
| `skip` | int | 0 | Pagination offset |
| `limit` | int | 50 | Max results (1-100) |

Response `200` (array):
```json
[
  {
    "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
    "kind": "doc",
    "path": "Projects/meeting-notes.md",
    "visibility": "private",
    "owner_user_id": "user-uuid",
    "created_at": "2026-01-15T10:30:00Z",
    "updated_at": "2026-02-19T08:00:00Z",
    "is_owner": true,
    "user_role": null,
    "web_published": false,
    "web_slug": null
  }
]
```

Fields:
- `id` — share UUID. For `doc` shares, also used as `doc_id` and `share_id`.
- `kind` — `doc` (single document) or `folder` (directory of documents).
- `path` — vault-relative path (e.g. `Notes/daily.md` or `Projects/`).
- `visibility` — `private`, `public`, or `protected`.
- `is_owner` — true if current user owns this share.
- `user_role` — `viewer`, `editor`, or `null` (owner/non-member).

### GET /v1/shares/{id}

Get share details by ID.

Response `200`: single share object (same schema as list item, plus `password_protected` field).

### POST /v1/shares

Create a new share.

Request:
```json
{
  "kind": "doc",
  "path": "Notes/new-note.md",
  "visibility": "private"
}
```

Response `201`: created share object.

Rate limit: 20/min.

---

## Documents

### GET /v1/documents/{doc_id}/content

Read plain text content from a Yjs document.

Path parameters:
- `doc_id` — document identifier (for `doc` shares, equals `share_id`)

Query parameters:
| Param | Type | Default | Description |
|-------|------|---------|-------------|
| `share_id` | UUID | required | Share UUID for ACL check |
| `key` | string | `contents` | Yjs shared type key name |

Response `200`:
```json
{
  "doc_id": "a1b2c3d4-...",
  "content": "# Meeting Notes\n\nContent here...",
  "format": "text"
}
```

Access: viewer, editor, or owner of the share.

Errors:
- `400` — invalid `share_id` format
- `401` — no/expired token
- `403` — no read access
- `404` — share not found
- `422` — missing `share_id`
- `502` — relay server unavailable

### GET /v1/documents/{doc_id}/files

List files stored in a folder share's `filemeta_v0` Y.Map.

Path parameters:
- `doc_id` — document identifier (for folder shares, equals `share_id`)

Query parameters:
| Param | Type | Default | Description |
|-------|------|---------|-------------|
| `share_id` | UUID | required | Share UUID for ACL check |

Response `200`:
```json
{
  "doc_id": "e5f6g7h8-...",
  "files": {
    "meeting-notes.md": {"id": "abc123", "type": "markdown", "hash": "h1a2b3c4"},
    "project-plan.md": {"id": "def456", "type": "markdown", "hash": "h5e6f7g8"}
  }
}
```

Fields:
- `doc_id` — the document ID queried (same as `share_id` for folder shares).
- `files` — map of virtual file paths to metadata dicts. Keys are vault-relative paths within the folder. Values are Y.Map entries (shape depends on plugin version; typically includes `id`, `type`, `hash`).

Use each file's `id` value as the `doc_id` for `GET /v1/documents/{doc_id}/content` to read its text.

Returns an empty `files` dict if the folder share has no files synced yet.

Access: viewer, editor, or owner of the share.

Errors:
- `400` — invalid `share_id` format
- `401` — no/expired token
- `403` — no read access
- `404` — share not found
- `422` — missing `share_id`
- `502` — relay server unavailable

### POST /v1/documents/{doc_id}/files

Create a new file inside a folder share. Generates a document, writes content, and registers the file in the folder's `filemeta_v0` Y.Map.

Path parameters:
- `doc_id` — folder share's document ID (equals `share_id` for folder shares)

Request body:
```json
{
  "share_id": "e5f6g7h8-...",
  "path": "new-note.md",
  "content": "# New Note\n\nContent here.",
  "key": "contents"
}
```

Fields:
- `share_id` (required) — folder share UUID for ACL check.
- `path` (required) — file name/path within the folder (e.g. `notes.md`).
- `content` (optional, default `""`) — initial text content.
- `key` (optional, default `contents`) — Yjs shared type key.

Response `201`:
```json
{
  "doc_id": "generated-uuid",
  "path": "new-note.md",
  "status": "ok",
  "length": 30
}
```

The returned `doc_id` can be used with `GET/PUT /documents/{doc_id}/content` for subsequent reads/writes. The file will appear in the Obsidian plugin on next sync.

Access: editor or owner only. Only works on `folder` shares (not `doc` shares).

Errors:
- `400` — invalid `share_id`, not a folder share, or empty path
- `401` — no/expired token
- `403` — no write access
- `404` — share not found
- `422` — missing required fields
- `502` — relay server unavailable

### DELETE /v1/documents/{doc_id}/files/{file_path}

Delete a file from a folder share. Removes the entry from `filemeta_v0` Y.Map.

Path parameters:
- `doc_id` — folder share's document ID
- `file_path` — file name/path to delete (e.g. `notes.md`)

Query parameters:
| Param | Type | Default | Description |
|-------|------|---------|-------------|
| `share_id` | UUID | required | Share UUID for ACL check |

Response `200`:
```json
{
  "path": "notes.md",
  "status": "ok"
}
```

Access: editor or owner only. Only works on `folder` shares.

Errors:
- `400` — invalid `share_id` or not a folder share
- `401` — no/expired token
- `403` — no write access
- `404` — file not found in folder, or share not found
- `502` — relay server unavailable

### PUT /v1/documents/{doc_id}/content

Write (replace) text content in a Yjs document.

Path parameters:
- `doc_id` — document identifier

Request body:
```json
{
  "share_id": "a1b2c3d4-...",
  "content": "# Updated Content\n\nNew text here.",
  "key": "contents"
}
```

Fields:
- `share_id` (required) — share UUID for ACL check.
- `content` (required) — full document text. Replaces the entire document.
- `key` (optional, default `contents`) — Yjs shared type key.

Response `200`:
```json
{
  "doc_id": "a1b2c3d4-...",
  "status": "ok",
  "length": 42
}
```

Access: editor or owner only. Viewers get `403`.

Errors: same as GET, plus `422` if `content` is missing.

---

## Health

### GET /health

Health check endpoint. **No auth required.**

Response `200`:
```json
{"ok": true}
```

### GET /server/info

Server metadata. **No auth required.**

Response `200`:
```json
{
  "name": "Relay Server",
  "version": "2.9.0",
  "relay_url": "wss://...",
  "features": { ... }
}
```

---

## Rate limits

| Endpoint | Limit |
|----------|-------|
| POST /v1/auth/login | 10/min |
| POST /v1/shares | 20/min |
| POST /v1/tokens/relay | 30/min |

Rate-limited responses return `429 Too Many Requests`.

## Error format

All errors return JSON:
```json
{"detail": "Error description"}
```

For validation errors (422):
```json
{
  "detail": [
    {"loc": ["body", "field"], "msg": "field required", "type": "value_error.missing"}
  ]
}
```
