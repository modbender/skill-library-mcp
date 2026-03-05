---
name: inkdrop
description: Read, create, update, search, and delete notes in Inkdrop via its local HTTP server API. Use when the user asks to take notes, save ideas, manage project notes, read notes, search notes, or interact with Inkdrop in any way. Also use when organizing thoughts, project backlogs, or task lists that should persist in Inkdrop.
env:
  INKDROP_AUTH:
    required: true
    description: "Basic auth credentials (user:password) from Inkdrop preferences"
  INKDROP_URL:
    required: false
    description: "Inkdrop local server URL (default: http://localhost:19840)"
---

# Inkdrop Notes

Interact with Inkdrop's local HTTP server to manage notes, notebooks, and tags.

## Prerequisites

1. [Inkdrop](https://inkdrop.app) desktop app installed and running
2. Local HTTP server enabled in Inkdrop preferences (Preferences → API → Enable Local HTTP Server)
3. Note the port, username, and password from the Inkdrop preferences

## Setup

Set environment variables:

```bash
export INKDROP_URL="http://localhost:19840"   # default port
export INKDROP_AUTH="username:password"        # from Inkdrop preferences
```

For OpenClaw, store credentials in a secrets file (e.g., workspace `secrets.md`) and source them at runtime. Avoid persisting plaintext credentials in shell profiles.

## Connection

```
Base URL: http://localhost:19840 (or INKDROP_URL env var)
Auth: Basic auth via INKDROP_AUTH env var (user:password)
```

Verify connection:

```bash
curl -s -u "$INKDROP_AUTH" "${INKDROP_URL:-http://localhost:19840}/"
# Returns: {"version":"5.x.x","ok":true}
```

## API Reference

All endpoints use Basic auth. Replace `USER:PASS` with your `$INKDROP_AUTH` value.

### List Notes

```bash
curl -s -u $INKDROP_AUTH http://localhost:19840/notes
```

Query params:
- `keyword` — search text (same qualifiers as Inkdrop search)
- `limit` — max results (default: all)
- `skip` — offset for pagination
- `sort` — `updatedAt`, `createdAt`, or `title`
- `descending` — reverse order (boolean)

### Get Single Document

```bash
curl -s -u $INKDROP_AUTH "http://localhost:19840/<docid>"
```

The `docid` is the full `_id` (e.g., `note:abc123`, `book:xyz`). Works for notes, books, tags, files.

Optional params:
- `rev` — fetch specific revision
- `attachments` — include attachment data (boolean, use for file documents)

### Create Note

```bash
curl -s -u $INKDROP_AUTH -X POST http://localhost:19840/notes \
  -H "Content-Type: application/json" \
  -d '{
    "doctype": "markdown",
    "title": "Note Title",
    "body": "Markdown content here",
    "bookId": "book:inbox",
    "status": "none",
    "tags": []
  }'
```

`_id` is auto-generated. `bookId` is required — use `book:inbox` as default or look up notebooks first.

### Update Note

POST with `_id` and `_rev` (required to avoid conflicts):

```bash
# 1. Get current _rev
REV=$(curl -s -u $INKDROP_AUTH "http://localhost:19840/note:abc123" | python3 -c "import sys,json; print(json.load(sys.stdin)['_rev'])")

# 2. Update with _rev
curl -s -u $INKDROP_AUTH -X POST http://localhost:19840/notes \
  -H "Content-Type: application/json" \
  -d '{
    "_id": "note:abc123",
    "_rev": "'"$REV"'",
    "doctype": "markdown",
    "title": "Updated Title",
    "body": "Updated content",
    "bookId": "book:inbox",
    "status": "none"
  }'
```

### Delete Document

```bash
curl -s -u $INKDROP_AUTH -X DELETE "http://localhost:19840/<docid>"
```

### List Notebooks

```bash
curl -s -u $INKDROP_AUTH http://localhost:19840/books
```

### Create Notebook

```bash
curl -s -u $INKDROP_AUTH -X POST http://localhost:19840/books \
  -H "Content-Type: application/json" \
  -d '{"name": "My Notebook"}'
```

### List Tags

```bash
curl -s -u $INKDROP_AUTH http://localhost:19840/tags
```

### Create Tag

```bash
curl -s -u $INKDROP_AUTH -X POST http://localhost:19840/tags \
  -H "Content-Type: application/json" \
  -d '{"_id": "tag:mytag", "name": "mytag", "color": "blue"}'
```

### List/Create Files (Attachments)

```bash
curl -s -u $INKDROP_AUTH http://localhost:19840/files
```

Create with POST to `/files`. Files are primarily image attachments for notes.

### Changes Feed

```bash
curl -s -u $INKDROP_AUTH "http://localhost:19840/_changes?since=0&limit=50&include_docs=true"
```

Params: `since` (sequence number), `limit`, `descending`, `include_docs`, `conflicts`, `attachments`.

Returns changes in order they were made. Useful for syncing or watching for updates.

## Helper Script

The included `scripts/inkdrop.sh` wraps common operations:

```bash
export INKDROP_AUTH="username:password"

# List all notes
./scripts/inkdrop.sh notes

# Search notes
./scripts/inkdrop.sh search "project ideas"

# Get a specific note
./scripts/inkdrop.sh get "note:abc123"

# Create a note (title, bookId, body)
./scripts/inkdrop.sh create "My Note" "book:inbox" "Note content here"

# List notebooks
./scripts/inkdrop.sh books

# List tags
./scripts/inkdrop.sh tags

# Delete a document
./scripts/inkdrop.sh delete "note:abc123"
```

## Note Model

| Field | Type | Description |
|-------|------|-------------|
| `_id` | string | `note:<id>` (auto-generated) |
| `_rev` | string | Revision token (required for updates) |
| `title` | string | Note title |
| `body` | string | Markdown content |
| `doctype` | string | Always `"markdown"` |
| `bookId` | string | Notebook ID (e.g., `book:inbox`) |
| `tags` | string[] | Array of tag IDs |
| `status` | string | `none`, `active`, `onHold`, `completed`, `dropped` |
| `pinned` | boolean | Pin to top |
| `share` | string | `private` or `public` |
| `createdAt` | number | Unix timestamp (ms) |
| `updatedAt` | number | Unix timestamp (ms) |

## Status Values

- `none` — Default
- `active` — In progress
- `onHold` — Paused
- `completed` — Done
- `dropped` — Abandoned

## Conventions

- Default notebook for quick captures: `book:inbox`
- Use existing notebooks when context is clear (match by name via `GET /books`)
- Use markdown formatting in note bodies
- Always fetch `_rev` before updating to avoid conflicts
- Tag IDs use `tag:<name>` format
