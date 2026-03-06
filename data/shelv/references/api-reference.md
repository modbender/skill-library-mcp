# API Reference

Base URL: `https://api.shelv.dev`

All requests require `Authorization: Bearer $SHELV_API_KEY`.

## Endpoints

### Create a shelf

```
POST /v1/shelves
Content-Type: multipart/form-data
```

| Field      | Type   | Required | Description                                           |
| ---------- | ------ | -------- | ----------------------------------------------------- |
| `file`     | File   | Yes      | PDF file to process (max 300 MB)                      |
| `name`     | string | No       | Display name (defaults to filename without extension) |
| `template` | string | No       | `book`, `legal-contract`, or `academic-paper`         |
| `review`   | string | No       | `"true"` to pause in review before finalizing         |

**Response (201):**

```json
{
  "publicId": "shf_0123456789abcdef01234567",
  "userId": "user_abc123",
  "name": "My Contract",
  "status": "uploading",
  "template": "legal-contract",
  "pageCount": null,
  "storageSizeBytes": null,
  "originalFileName": "contract.pdf",
  "mimeType": "application/pdf",
  "errorMessage": null,
  "failedAtStep": null,
  "reviewMode": false,
  "createdAt": "2025-01-15T10:30:00.000Z",
  "updatedAt": "2025-01-15T10:30:00.000Z"
}
```

### List shelves

```
GET /v1/shelves?page=1&limit=20
```

| Param   | Type   | Default | Description             |
| ------- | ------ | ------- | ----------------------- |
| `page`  | number | 1       | Page number             |
| `limit` | number | 20      | Items per page (max 50) |

**Response (200):**

```json
{
  "data": [ShelfResponse, ...],
  "pagination": {
    "page": 1,
    "limit": 20,
    "total": 42,
    "totalPages": 3
  }
}
```

### Get a shelf

```
GET /v1/shelves/{shelfPublicId}
```

**Response (200):** `ShelfResponse` (see shape above)

### Delete a shelf

```
DELETE /v1/shelves/{shelfPublicId}
```

**Response (200):**

```json
{ "success": true }
```

### Get shelf file tree

```
GET /v1/shelves/{shelfPublicId}/tree
```

Requires status `ready` or `review`.

**Response (200):**

```json
{
  "shelfPublicId": "shf_0123456789abcdef01234567",
  "name": "My Contract",
  "fileCount": 8,
  "files": {
    "README.md": "# My Contract\n...",
    "clauses/force-majeure.md": "# Force Majeure\n...",
    "metadata.json": "{\"title\":\"Voyage Charter\"}"
  }
}
```

### Read a single file

```
GET /v1/shelves/{shelfPublicId}/files/{path}
```

Requires status `ready` or `review`. The `{path}` is the relative file path within the shelf (e.g. `clauses/force-majeure.md`).

**Response (200):** Raw file content with appropriate `Content-Type` (`text/markdown`, `application/json`, or `text/plain`).

### Get presigned archive URL

```
GET /v1/shelves/{shelfPublicId}/archive-url?ttl=300
```

Requires status `ready` or `review`.

| Param | Type   | Default | Description                        |
| ----- | ------ | ------- | ---------------------------------- |
| `ttl` | number | 300     | URL expiry in seconds (60 to 3600) |

**Response (200) — archive ready:**

```json
{
  "url": "https://...",
  "expiresAt": "2025-01-15T10:35:00.000Z",
  "sha256": "abc123...",
  "sizeBytes": 102400,
  "version": "2025-01-15T10:30:00.000Z"
}
```

**Response (202) — archive generating:**

```json
{
  "status": "generating",
  "retryAfter": 5
}
```

Poll after `retryAfter` seconds until you get a 200.

### Approve a shelf

```
POST /v1/shelves/{shelfPublicId}/approve
Content-Type: application/json (optional)
```

Requires status `review`. Transitions the shelf to `ready`.

Optional body with file operations to apply before finalizing:

```json
{
  "operations": [
    { "type": "rename", "from": "old-name.md", "to": "new-name.md" },
    { "type": "delete", "path": "unwanted-file.md" },
    { "type": "mkdir", "path": "new-directory" },
    { "type": "write", "path": "notes.md", "content": "# Notes\n..." }
  ]
}
```

**Response (200):** `ShelfResponse` with `status: "ready"`

### Regenerate shelf structure

```
POST /v1/shelves/{shelfPublicId}/regenerate
```

Requires status `review`. Re-runs structuring and verification.

**Response (200):** `ShelfResponse` with `status: "structuring"`

### Retry a failed shelf

```
POST /v1/shelves/{shelfPublicId}/retry
```

Requires status `failed`. Re-triggers the full processing pipeline.

**Response (200):** `ShelfResponse` with `status: "uploading"`

### Download helper script

```
GET /v1/helpers/download.sh
```

Returns a portable shell script for downloading and verifying shelf archives. No auth required for the script itself.

## ShelfResponse Shape

Every shelf endpoint returns or includes this shape:

```json
{
  "publicId": "shf_0123456789abcdef01234567",
  "userId": "user_abc123",
  "name": "My Contract",
  "status": "ready",
  "template": "legal-contract",
  "pageCount": 24,
  "storageSizeBytes": 102400,
  "originalFileName": "contract.pdf",
  "mimeType": "application/pdf",
  "errorMessage": null,
  "failedAtStep": null,
  "reviewMode": false,
  "createdAt": "2025-01-15T10:30:00.000Z",
  "updatedAt": "2025-01-15T10:32:00.000Z"
}
```

| Field              | Type        | Description                                                                     |
| ------------------ | ----------- | ------------------------------------------------------------------------------- |
| `publicId`         | string      | Unique shelf ID (prefix `shf_`)                                                 |
| `userId`           | string      | Owner user ID                                                                   |
| `name`             | string      | Display name                                                                    |
| `status`           | string      | `uploading`, `parsing`, `structuring`, `verifying`, `review`, `ready`, `failed` |
| `template`         | string/null | Template used for structuring                                                   |
| `pageCount`        | number/null | PDF page count (set after parsing)                                              |
| `storageSizeBytes` | number/null | Total storage size of generated files                                           |
| `originalFileName` | string      | Original uploaded filename                                                      |
| `mimeType`         | string      | MIME type of uploaded file                                                      |
| `errorMessage`     | string/null | Error details (only when `failed`)                                              |
| `failedAtStep`     | string/null | Pipeline step that failed                                                       |
| `reviewMode`       | boolean     | Whether review mode was enabled                                                 |
| `createdAt`        | string      | ISO 8601 timestamp                                                              |
| `updatedAt`        | string      | ISO 8601 timestamp                                                              |
