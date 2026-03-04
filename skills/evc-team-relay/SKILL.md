---
name: evc-team-relay
version: 1.1.2
description: >
  Read and write Obsidian notes stored in EVC Team Relay collaborative vault.
  Use when agent needs to: read note content from a shared Obsidian vault,
  create or update documents, list available shared folders and documents,
  or search across shared vault content. Relay stores documents as Yjs CRDTs;
  this skill provides a REST interface to read/write their text content.
metadata:
  openclaw:
    requires:
      env:
        - RELAY_CP_URL
        - RELAY_EMAIL
        - RELAY_PASSWORD
      bins:
        - curl
        - jq
    primaryEnv: RELAY_CP_URL
    homepage: https://github.com/entire-vc/evc-team-relay
---

# EVC Team Relay

REST API skill for reading and writing collaborative Obsidian vault documents via EVC Team Relay.

## Environment variables

| Variable | Required | Description |
|----------|----------|-------------|
| `RELAY_CP_URL` | yes | Control plane URL, e.g. `https://cp.tr.entire.vc` |
| `RELAY_EMAIL` | yes | User email for authentication |
| `RELAY_PASSWORD` | yes | User password |
| `RELAY_TOKEN` | no | JWT token (set via `export RELAY_TOKEN=$(scripts/auth.sh)`) |

## Quick start

```bash
# 1. Authenticate — get a JWT token (stored in env var, not visible in ps)
export RELAY_TOKEN=$(scripts/auth.sh)

# 2. List shares to find available documents
scripts/list-shares.sh

# 3. Read a file from a folder share BY PATH (most common)
scripts/read-file.sh <folder_share_id> "Marketing/plan.md"

# 4. Create or update a file in a folder share
scripts/upsert-file.sh <folder_share_id> "note.md" "# Content"

# 5. List all files in a folder share
scripts/list-files.sh <folder_share_id>

# 6. Delete a file from a folder share
scripts/delete-file.sh <folder_share_id> "old-note.md"

# 7. Read a doc share (single document, share_id = doc_id)
scripts/read.sh <share_id>

# 8. Write to a doc share
scripts/write.sh <share_id> <share_id> "# Updated content"
```

All scripts accept the token via `RELAY_TOKEN` env var (preferred) or as the first CLI argument (backward-compatible).

## Two kinds of shares

| | Doc share | Folder share |
|--|-----------|--------------|
| **Contains** | Single document | Multiple files |
| **doc_id** | Same as share_id | Each file has its own doc_id (in folder metadata) |
| **Read** | `read.sh <share_id>` | **`read-file.sh <share_id> "path/to/file.md"`** |
| **Write** | `write.sh <share_id> <share_id> <content>` | **`upsert-file.sh <share_id> "path" <content>`** |
| **Delete** | N/A | `delete-file.sh <share_id> "path"` |

**Most shares are folder shares.** Use `read-file.sh` and `upsert-file.sh` — they handle path resolution automatically.

> **Warning**: `write.sh` does NOT work for folder shares — it writes content but does not register the file in folder metadata, so Obsidian will never see it. The script detects folder shares and refuses with an error.

## Scripts reference

| Script | Purpose | Args |
|--------|---------|------|
| `auth.sh` | Get JWT token | — |
| `list-shares.sh` | List all shares | `[kind] [owned_only]` |
| `list-files.sh` | List files in folder share | `<share_id>` |
| **`read-file.sh`** | **Read file by path (folder share)** | `<share_id> <file_path>` |
| `read.sh` | Read by doc_id (low-level) | `<share_id> [doc_id]` |
| **`upsert-file.sh`** | **Create/update file (folder share)** | `<share_id> <file_path> <content>` |
| `write.sh` | Write by doc_id (doc shares only) | `<share_id> <doc_id> <content>` |
| `delete-file.sh` | Delete file from folder share | `<share_id> <file_path>` |
| `create-file.sh` | Create new file (low-level) | `<share_id> <file_path> <content>` |

**Bold = recommended for most use cases.** All scripts use `RELAY_TOKEN` env var (or accept token as first arg).

## Authentication

All API calls require a Bearer JWT token. Get one via login:

```bash
curl -s -X POST "$RELAY_CP_URL/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email": "'$RELAY_EMAIL'", "password": "'$RELAY_PASSWORD'"}' \
  | jq -r '.access_token'
```

Response:
```json
{
  "access_token": "eyJ...",
  "refresh_token": "...",
  "token_type": "bearer",
  "expires_in": 3600
}
```

Use the `access_token` as `Authorization: Bearer <token>` header on all subsequent requests.

When the token expires (1 hour), refresh it:
```bash
curl -s -X POST "$RELAY_CP_URL/v1/auth/refresh" \
  -H "Content-Type: application/json" \
  -d '{"refresh_token": "'$REFRESH_TOKEN'"}'
```

## Listing shares

Shares are the access units — each share maps to a document or folder in the Obsidian vault.

```bash
curl -s "$RELAY_CP_URL/v1/shares" \
  -H "Authorization: Bearer $TOKEN" | jq
```

Response (array):
```json
[
  {
    "id": "a1b2c3d4-...",
    "kind": "doc",
    "path": "Projects/meeting-notes.md",
    "visibility": "private",
    "is_owner": true,
    "user_role": null,
    "web_published": false
  },
  {
    "id": "e5f6g7h8-...",
    "kind": "folder",
    "path": "Projects/",
    "visibility": "private",
    "is_owner": false,
    "user_role": "editor"
  }
]
```

Key fields:
- **`id`** — share UUID, used as `share_id` in all operations
- **`kind`** — `doc` (single file) or `folder` (directory)
- **`path`** — Obsidian vault-relative path
- **`user_role`** — `viewer` (read-only), `editor` (read-write), or `null` (owner)

Filter options: `?kind=doc`, `?owned_only=true`, `?member_only=true`, `?skip=0&limit=50`.

## Listing files in a folder share

```bash
scripts/list-files.sh <share_id>
```

Response:
```json
{
  "doc_id": "e5f6g7h8-...",
  "files": {
    "meeting-notes.md": {"doc_id": "abc123-...", "type": "markdown"},
    "project-plan.md": {"doc_id": "def456-...", "type": "markdown"}
  }
}
```

Each key is the file's path within the folder. The **`doc_id`** field is the document identifier used for content operations. The `share_id` for content requests is always the folder share's ID.

> **Note**: The API response uses `id` as the field name. This is the same as `doc_id` — use it wherever `doc_id` is needed.

## Reading files

### By path (recommended for folder shares)

```bash
scripts/read-file.sh <folder_share_id> "Marketing/plan.md"
```

This resolves the path to a doc_id internally and returns:
```json
{
  "doc_id": "abc123-...",
  "content": "# Marketing Plan\n\nContent here...",
  "format": "text",
  "path": "Marketing/plan.md"
}
```

### By doc_id (low-level)

```bash
scripts/read.sh <share_id> [doc_id] [key]
```

For doc shares, omit doc_id (defaults to share_id). For folder shares, pass the file's doc_id from `list-files.sh`.

## Writing files

### Folder shares — use upsert-file.sh

```bash
# Create or update — auto-detects which operation is needed
scripts/upsert-file.sh <folder_share_id> "note.md" "# Updated content"

# Pipe content from stdin
echo "# Content" | scripts/upsert-file.sh <folder_share_id> "note.md" -
```

Response includes an `operation` field: `"created"` or `"updated"`.

### Doc shares — use write.sh

```bash
scripts/write.sh <share_id> <share_id> "# Updated Notes"
```

> **write.sh refuses folder shares** — if you accidentally pass a folder share_id as doc_id, it detects this and exits with an error directing you to upsert-file.sh.

## Common workflows

### Read a specific note by path (most common)

```bash
# If you know the folder share_id:
scripts/read-file.sh <folder_share_id> "Marketing/docs/plan.md"

# If you need to find the share first:
scripts/list-shares.sh  # find the folder share
scripts/read-file.sh <share_id> "path/to/file.md"
```

### Create or update a file

```bash
# Always works, whether the file exists or not
scripts/upsert-file.sh <folder_share_id> "note.md" "# Content"
```

### Delete a file

```bash
scripts/delete-file.sh <folder_share_id> "old-note.md"
```

## Error codes

| Status | Meaning |
|--------|---------|
| 400 | Invalid share_id format |
| 401 | Missing or expired token — re-authenticate |
| 403 | Insufficient permissions (viewer trying to write, or non-member) |
| 404 | Share or file not found (check path spelling, use list-files.sh to verify) |
| 422 | Missing required field (share_id, content) |
| 502 | Relay server unavailable — retry later |

## Terminology

| Term | Meaning |
|------|---------|
| `share_id` | UUID of a share (doc or folder). Used for ACL checks in all requests. |
| `doc_id` | UUID of an individual document. For doc shares, equals share_id. For folder shares, each file has its own doc_id. |
| `id` | Same as `doc_id` — the API response field name. Use interchangeably. |
| `file_path` | Relative path within a folder share (e.g. `"Marketing/plan.md"`). |

## References

- `references/api.md` — full API reference with all endpoints
