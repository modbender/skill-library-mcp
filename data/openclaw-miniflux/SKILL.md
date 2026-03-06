---
name: miniflux
description: >
  Manage RSS feeds and entries on a Miniflux instance. Handles requests like
  "show my unread articles", "list my feeds", "rename this category",
  "unsubscribe from this feed", "import my OPML", "mark these entries as read",
  or "bookmark this article". Uses openclaw-miniflux-mcp for all operations.
---

# Miniflux

## What it does

Provides access to a Miniflux RSS reader instance through 13 read tools
and 10 write tools. Agents can browse feeds, search entries by status
or date, read specific articles, check categories, and (if not in read-only
mode) create/update/delete feeds and categories, import OPML, mark entries
as read, and toggle bookmarks.

## Inputs needed

- For listing entries: status, date range, starred, pagination (all optional)
- For feed-specific queries: feed ID
- For single items: entry ID, feed ID, or user ID
- For discovery: a URL to scan for feeds
- For creating categories: a title
- For updating categories: category ID and new title
- For deleting categories: category ID
- For subscribing to feeds: a feed URL and category ID
- For updating feeds: feed ID, plus optional title, category_id, feed_url, site_url, user_agent
- For deleting feeds: feed ID
- For OPML import: an OPML XML string
- For writes: entry IDs + status, or entry ID for bookmark toggle

## Prerequisites

### `openclaw-miniflux-mcp` binary

Download the latest binary for your platform from
[GitHub Releases](https://github.com/sinhong2011/openclaw-skill-miniflux/releases):

| Platform | Binary |
|----------|--------|
| Linux x86_64 | `openclaw-miniflux-mcp-x86_64-unknown-linux-gnu` |
| Linux ARM64 | `openclaw-miniflux-mcp-aarch64-unknown-linux-gnu` |
| macOS x86_64 | `openclaw-miniflux-mcp-x86_64-apple-darwin` |
| macOS ARM64 | `openclaw-miniflux-mcp-aarch64-apple-darwin` |

Or install via Cargo:

```bash
cargo install openclaw-miniflux-mcp
```

### MCP server configuration

Add the MCP server to your client configuration:

**With API token (recommended):**

```json
{
  "mcpServers": {
    "miniflux": {
      "command": "/path/to/openclaw-miniflux-mcp",
      "args": [],
      "env": {
        "MINIFLUX_URL": "http://localhost:8080",
        "MINIFLUX_API_TOKEN": "<your-api-token>"
      }
    }
  }
}
```

**With username/password:**

```json
{
  "mcpServers": {
    "miniflux": {
      "command": "/path/to/openclaw-miniflux-mcp",
      "args": [],
      "env": {
        "MINIFLUX_URL": "http://localhost:8080",
        "MINIFLUX_USERNAME": "<username>",
        "MINIFLUX_PASSWORD": "<password>"
      }
    }
  }
}
```

**Read-only mode** (disables write tools):

```json
{
  "mcpServers": {
    "miniflux": {
      "command": "/path/to/openclaw-miniflux-mcp",
      "args": ["--read-only"],
      "env": {
        "MINIFLUX_URL": "http://localhost:8080",
        "MINIFLUX_API_TOKEN": "<your-api-token>"
      }
    }
  }
}
```

The user will need to:
1. Replace the binary path with wherever they downloaded/installed it
2. Replace `MINIFLUX_URL` with their Miniflux instance URL
3. Get an API token from Miniflux: **Settings > API Keys > Create a new API key**
4. Restart their MCP client after saving

## Workflow

### Browsing feeds

1. Call `miniflux_get_feeds` to see all subscriptions
2. Call `miniflux_get_feed_entries` with a feed ID to see its entries
3. Call `miniflux_get_entry` to read a specific article

### Searching entries

Call `miniflux_get_entries` with filters:
- `status`: `"unread"`, `"read"`, or `"removed"`
- `starred`: `true` for bookmarked entries
- `after` / `before`: Unix timestamps for date ranges
- `limit`: Number of results (default varies, recommend 20)
- `order`: `"published_at"` and `direction`: `"desc"` for newest first

### Triaging unread articles

1. Call `miniflux_get_entries` with `status: "unread"`, `limit: 20`
2. Read interesting entries with `miniflux_get_entry`
3. Mark reviewed entries as read: `miniflux_update_entry_status` with `status: "read"`
4. Bookmark important ones: `miniflux_toggle_bookmark`

### Adding new feeds

1. Call `miniflux_discover_subscription` with a website URL to find available feeds
2. Present discovered feeds to the user
3. If needed, call `miniflux_create_category` to create a new category
4. Call `miniflux_create_feed` with the feed URL and category ID to subscribe

### Managing feeds

- **Update:** `miniflux_update_feed` with feed ID and any fields to change (title, category_id, feed_url, site_url, user_agent)
- **Delete:** `miniflux_delete_feed` with feed ID to unsubscribe
- **Refresh:** `miniflux_refresh_feed` with feed ID to fetch new entries now

### Managing categories

- **List:** `miniflux_get_categories` to see all categories
- **Create:** `miniflux_create_category` with a title
- **Rename:** `miniflux_update_category` with category ID and new title
- **Delete:** `miniflux_delete_category` with category ID (feeds move to default category)

### Importing/Exporting

- **Export:** `miniflux_export_opml` to get all feeds as OPML XML
- **Import:** `miniflux_import_opml` with an OPML XML string to bulk-add feeds

## Guardrails

- Default to small page sizes (limit=20) to avoid overwhelming responses
- On 401/403 errors, tell the user to check their API token or credentials
- On connection errors, tell the user to verify their MINIFLUX_URL
- Confirm with the user before marking large batches of entries as read
- In read-only mode, explain the limitation clearly when a write is attempted
- When listing returns empty results, suggest checking filters or confirming the instance has data
