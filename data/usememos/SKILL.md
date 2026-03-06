---
name: memos
description: >
  Create, read, update, and delete memos on a Memos instance (usememos/memos).
  Handles requests like "save this as a memo", "list my recent memos",
  "update memo #123", or "delete memo #456".
  Uses openclaw-memos-mcp for all operations.
---

# Memos

## What it does

Provides full CRUD operations on a self-hosted Memos instance through 5 MCP
tools. Agents can create quick notes, search existing memos, update content
or visibility, and delete memos they no longer need.

## Inputs needed

- For creating: content (required), visibility (optional, defaults to PRIVATE)
- For listing: filter expression (optional), page size (optional)
- For get/update/delete: memo ID (required)

## Prerequisites

### `openclaw-memos-mcp` MCP server

This skill requires the `openclaw-memos-mcp` MCP server to be running. Before
using any `memos_*` tool, check if the tools are available. If not, tell the
user they need to add the MCP server to their configuration:

```json
{
  "mcpServers": {
    "memos": {
      "command": "npx",
      "args": ["openclaw-memos-mcp"],
      "env": {
        "MEMOS_API_URL": "http://localhost:5230",
        "MEMOS_TOKEN": "<your-access-token>"
      }
    }
  }
}
```

Tell the user to:
1. Replace `MEMOS_API_URL` with their Memos instance URL
2. Get an access token from Memos: **Settings > Access Tokens > Create**
3. Replace `<your-access-token>` with the token
4. Restart their MCP client after saving the configuration

## Workflow

### Creating a memo

Call `memos_create` with the content and optional visibility.

- `content`: Markdown text. Supports `#hashtags` which Memos auto-extracts as tags.
- `visibility`: `PRIVATE` (default), `PROTECTED` (logged-in users), or `PUBLIC` (everyone).

### Listing memos

Call `memos_list` to browse or search memos.

- `pageSize`: Number of results (default 20).
- `pageToken`: For pagination, use the `nextPageToken` from a previous response.
- `filter`: CEL filter expression. Examples:
  - `tag == "work"` — memos tagged #work
  - `visibility == "PUBLIC"` — public memos only
  - `creator == "users/1"` — memos by a specific user

### Reading a specific memo

Call `memos_get` with the memo ID. The ID is the part after `memos/` in the
resource name (e.g., if the name is `memos/abc123`, the ID is `abc123`).

### Updating a memo

Call `memos_update` with the memo ID and the fields to change. Only specify
fields you want to update — unspecified fields remain unchanged.

- `content`: New Markdown content
- `visibility`: New visibility level
- `pinned`: `true` to pin, `false` to unpin

### Deleting a memo

Call `memos_delete` with the memo ID. **This is irreversible.** Always confirm
with the user before deleting.

## Guardrails

- Default visibility to `PRIVATE` — never create public memos unless explicitly asked
- Validate content is non-empty before creating
- Confirm with the user before deleting any memo
- On 401/403 errors, tell the user to check their `MEMOS_TOKEN`
- On connection errors, tell the user to check their `MEMOS_API_URL`
- When listing returns empty results, suggest the user check their filter or confirm the Memos instance has data
