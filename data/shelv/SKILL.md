---
name: shelv
description: Convert PDFs into structured Markdown filesystems and hydrate them into your workspace for exploration with standard Unix tools
version: 1.0.3
metadata:
  openclaw:
    requires:
      env: [SHELV_API_KEY]
      bins: [curl, tar, jq, shasum]
    primaryEnv: SHELV_API_KEY
    emoji: "📚"
    homepage: https://shelv.dev
    os: [macos, linux]
---

# Shelv

Shelv converts PDF documents (contracts, books, research papers, regulations) into structured Markdown filesystems. Upload a PDF, wait for processing, then hydrate the result into your workspace as real files you can explore with `ls`, `cat`, `grep`, and `find`.

**API base URL:** `https://api.shelv.dev`
**Auth:** `Authorization: Bearer $SHELV_API_KEY` on every request.

Get your API key at [shelv.dev](https://shelv.dev) → Settings → API Keys.

## Core Workflows

### 1. Upload a document

Upload a PDF to create a new shelf. Processing runs asynchronously.

```bash
SHELF_ID=$({baseDir}/scripts/shelv-upload.sh /path/to/document.pdf --name "My Document")
```

With options:

```bash
# Use a structuring template
SHELF_ID=$({baseDir}/scripts/shelv-upload.sh document.pdf --name "Q4 Contract" --template legal-contract)

# Enable review mode (pause before finalizing)
SHELF_ID=$({baseDir}/scripts/shelv-upload.sh document.pdf --review)

# Upload and wait for processing to complete
SHELF_ID=$({baseDir}/scripts/shelv-upload.sh document.pdf --wait)
```

The script prints the shelf public ID (e.g. `shf_0123456789abcdef01234567`) to stdout.

**Available templates:** `book`, `legal-contract`, `academic-paper`. Omit to let Shelv auto-detect structure.

**Inline alternative** (without the script):

```bash
curl -X POST "https://api.shelv.dev/v1/shelves" \
  -H "Authorization: Bearer $SHELV_API_KEY" \
  -F "file=@document.pdf" \
  -F "name=My Document"
```

Response (201):

```json
{
  "publicId": "shf_0123456789abcdef01234567",
  "name": "My Document",
  "status": "uploading",
  "template": null,
  "reviewMode": false,
  "pageCount": null,
  "createdAt": "2025-01-15T10:30:00.000Z",
  "updatedAt": "2025-01-15T10:30:00.000Z"
}
```

### 2. Poll for processing completion

Wait for a shelf to finish processing:

```bash
{baseDir}/scripts/shelv-poll-status.sh shf_0123456789abcdef01234567
```

The script polls `GET /v1/shelves/{id}` every 5 seconds and prints the current status. It exits 0 when the shelf reaches `ready` or `review`, and exits 1 on `failed` (with error details) or timeout (10 minutes).

**Processing flow:** `uploading` → `parsing` → `structuring` → `verifying` → `ready`

If `review` mode is enabled, the flow pauses at `review` instead of `ready`.

**Inline alternative:**

```bash
curl -s "https://api.shelv.dev/v1/shelves/$SHELF_ID" \
  -H "Authorization: Bearer $SHELV_API_KEY" | jq '.status'
```

### 3. Hydrate a shelf into the workspace

Download and extract the shelf's Markdown filesystem into your workspace:

```bash
{baseDir}/scripts/shelv-hydrate.sh shf_0123456789abcdef01234567
```

This downloads the archive, verifies its checksum, and extracts it to `~/.openclaw/workspace/shelves/<name>/`. The script prints a file listing after extraction.

Override the directory name:

```bash
{baseDir}/scripts/shelv-hydrate.sh shf_0123456789abcdef01234567 --name my-contract
```

Replace an existing shelf (required if the directory already exists):

```bash
{baseDir}/scripts/shelv-hydrate.sh shf_0123456789abcdef01234567 --force
```

After hydration, explore the files:

```bash
ls ~/.openclaw/workspace/shelves/my-contract/
cat ~/.openclaw/workspace/shelves/my-contract/README.md
find ~/.openclaw/workspace/shelves/my-contract/ -name "*.md"
grep -r "force majeure" ~/.openclaw/workspace/shelves/my-contract/
```

### 4. List and browse existing shelves

List all shelves:

```bash
curl -s "https://api.shelv.dev/v1/shelves?page=1&limit=20" \
  -H "Authorization: Bearer $SHELV_API_KEY" | jq '.data[] | {publicId, name, status}'
```

Get the file tree (flat JSON map of path → content):

```bash
curl -s "https://api.shelv.dev/v1/shelves/$SHELF_ID/tree" \
  -H "Authorization: Bearer $SHELV_API_KEY" | jq '.files | keys[]'
```

Response shape:

```json
{
  "shelfPublicId": "shf_0123456789abcdef01234567",
  "name": "My Contract",
  "fileCount": 8,
  "files": {
    "README.md": "# My Contract\n...",
    "clauses/force-majeure.md": "# Force Majeure\n..."
  }
}
```

### 5. Read individual files without hydration

Read a single file by path (useful for targeted lookups without downloading the full archive):

```bash
curl -s "https://api.shelv.dev/v1/shelves/$SHELF_ID/files/README.md" \
  -H "Authorization: Bearer $SHELV_API_KEY"
```

```bash
curl -s "https://api.shelv.dev/v1/shelves/$SHELF_ID/files/clauses/force-majeure.md" \
  -H "Authorization: Bearer $SHELV_API_KEY"
```

Returns raw Markdown content (`text/markdown`).

## Workspace Conventions

Hydrated shelves live at:

```
~/.openclaw/workspace/shelves/{name}/
```

The `{name}` is derived from the shelf's display name (lowercased, spaces and special characters replaced with hyphens). Override with `--name` when hydrating.

If a directory already exists at the target path, the script will refuse to overwrite it unless `--force` is passed.

After hydration, use standard Unix tools to explore:

```bash
# List all files
find ~/.openclaw/workspace/shelves/{name}/ -type f

# Read a specific file
cat ~/.openclaw/workspace/shelves/{name}/README.md

# Search across all files
grep -r "keyword" ~/.openclaw/workspace/shelves/{name}/

# Count files
find ~/.openclaw/workspace/shelves/{name}/ -type f | wc -l
```

## Async Operations

Shelf processing is asynchronous. After uploading, the shelf progresses through:

```
uploading → parsing → structuring → verifying → ready
```

Use the poll script to wait for completion:

```bash
{baseDir}/scripts/shelv-poll-status.sh $SHELF_ID
```

If the shelf reaches `failed`, the error message and failed step are printed. You can retry:

```bash
curl -X POST "https://api.shelv.dev/v1/shelves/$SHELF_ID/retry" \
  -H "Authorization: Bearer $SHELV_API_KEY"
```

For `review` mode shelves, approve to finalize:

```bash
curl -X POST "https://api.shelv.dev/v1/shelves/$SHELF_ID/approve" \
  -H "Authorization: Bearer $SHELV_API_KEY"
```

Or regenerate the structure:

```bash
curl -X POST "https://api.shelv.dev/v1/shelves/$SHELF_ID/regenerate" \
  -H "Authorization: Bearer $SHELV_API_KEY"
```

## Status-Gated Endpoint Matrix

Not all endpoints are available in every status. The archive, tree, and file endpoints require `ready` or `review`:

| Endpoint               | Processing | `review` | `ready` | `failed` |
| ---------------------- | ---------- | -------- | ------- | -------- |
| `GET /v1/shelves/{id}` | Yes        | Yes      | Yes     | Yes      |
| `GET .../tree`         | No         | Yes      | Yes     | No       |
| `GET .../files/*`      | No         | Yes      | Yes     | No       |
| `GET .../archive-url`  | No         | Yes      | Yes     | No       |
| `POST .../approve`     | No         | Yes      | No      | No       |
| `POST .../regenerate`  | No         | Yes      | No      | No       |
| `POST .../retry`       | No         | No       | No      | Yes      |

A `409 Conflict` is returned if you call an endpoint outside its allowed statuses.

## Rate Limits

| Scope                | Limit              |
| -------------------- | ------------------ |
| Reads (GET)          | 120 requests / min |
| Writes (POST/DELETE) | 20 requests / min  |
| Shelf creation       | 10 / hour          |

On `429 Too Many Requests`, back off and retry after the indicated period.

## Reference Pointers

For detailed API documentation, error codes, and lifecycle diagrams, see:

- `{baseDir}/references/api-reference.md` — Full endpoint docs and response shapes
- `{baseDir}/references/shelf-lifecycle.md` — Status flow, review mode, template behavior
- `{baseDir}/references/error-handling.md` — Error codes, retry strategies
