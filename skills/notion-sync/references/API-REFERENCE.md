# Notion Sync API Reference

Detailed technical reference for all Notion sync scripts and utilities.

## Environment Setup

### Notion Token

All scripts require a Notion integration token. Supported sources (priority order):

1. `--token-file <path>` (supports `~` expansion)
2. `--token-stdin` (pipe token through stdin)
3. `~/.notion-token` (auto-detected if present)
4. `NOTION_API_KEY` env var

```bash
node scripts/search-notion.js "query" --token-file ~/.notion-token
# or

echo "$NOTION_API_KEY" | node scripts/search-notion.js "query" --token-stdin
```

## JSON Output Mode

All scripts accept `--json` to emit machine-readable output and suppress stderr progress logs.

- Success output is JSON
- Errors are JSON objects: `{ "error": "..." }`

## Scripts Reference

### search-notion.js

Search pages and databases by title or content.

**Signature:**
```bash
node scripts/search-notion.js "<query>" [--filter page|database] [--limit 10] [--json]
```

**Options:**
- `query` (required): Search term
- `--filter`: Restrict to `page` or `database`
- `--limit`: Max results (default: 10)

**Returns:** JSON array of matching pages/databases with id, title, url, lastEdited

### query-database.js

Query database contents with advanced filters and sorting.

**Signature:**
```bash
node scripts/query-database.js <database-id> [--filter <json>] [--sort <json>] [--limit 10] [--json]
```

**Filter Patterns:**

| Type | Example |
|------|---------|
| Select equals | `{"property": "Status", "select": {"equals": "Done"}}` |
| Multi-select contains | `{"property": "Tags", "multi_select": {"contains": "AI"}}` |
| Date after | `{"property": "Date", "date": {"after": "2024-01-01"}}` |
| Checkbox | `{"property": "Published", "checkbox": {"equals": true}}` |
| Number | `{"property": "Count", "number": {"greater_than": 100}}` |

**Sort Format:**
```json
[{"property": "Date", "direction": "descending"}]
```

### update-page-properties.js

Update database page properties.

**Signature:**
```bash
node scripts/update-page-properties.js <page-id> <property-name> <value> [--type <type>] [--json]
```

**Property Types:**
- `select`: Single selection (e.g., Status)
- `multi_select`: Multiple tags (comma-separated)
- `checkbox`: Boolean (true/false)
- `number`: Numeric value
- `url`: URL string
- `email`: Email address
- `date`: ISO date (YYYY-MM-DD)
- `rich_text`: Plain text

### batch-update.js

Batch update a property across multiple pages.

**Signatures:**
```bash
# Query + update
node scripts/batch-update.js <database-id> <property-name> <value> --filter '<json>' [--type <type>] [--dry-run] [--limit 100]

# IDs from stdin
echo "page-id-1\npage-id-2" | node scripts/batch-update.js --stdin <property-name> <value> [--type <type>] [--dry-run] [--limit 100]
```

**Options:**
- `--filter <json>`: Notion database query filter (required in query mode)
- `--stdin`: read page IDs (one per line) from stdin instead of querying a database
- `--type <type>`: `select`, `multi_select`, `checkbox`, `number`, `url`, `email`, `date`, `rich_text`
- `--dry-run`: no writes; prints page IDs + current values to stderr and returns preview JSON
- `--limit <n>`: max pages to process (default: 100)

**Behavior:**
- Uses database `data_source_id` when available
- Supports query pagination (`has_more` + `next_cursor`) up to `--limit`
- Adds 300ms delay between updates to reduce 429 rate limits
- Emits progress to stderr and JSON results to stdout (`[{id, url, updated}]`)

### md-to-notion.js

Convert markdown to Notion page.

**Signature:**
```bash
node scripts/md-to-notion.js "<markdown-file>" "<parent-page-id>" "<title>" [--json]
```

**Supported Markdown:**
- Headings: `#`, `##`, `###`
- Bold: `**text**`
- Italic: `*text*`
- Links: `[text](url)`
- Lists: `- item`
- Code: ` ```lang ... ``` `
- Dividers: `---`

**Output:** Notion page URL and ID

**Rich text safety:** markdown rich_text segments are automatically split to Notion's 2000-character per-item limit (plain, bold, italic, and links).

**Rate Limiting:** 350ms between batch uploads (100 blocks per batch)

### notion-to-md.js

Convert Notion page to markdown.

**Signature:**
```bash
node scripts/notion-to-md.js <page-id> [output-file] [--json]
```

**Output:** Writes markdown to file or stdout

### watch-notion.js

Monitor page for changes.

**Signature:**
```bash
node scripts/watch-notion.js [--state-file <path>] <page-id> <local-path> [--json]
```

**State File:** Default `memory/notion-watch-state.json` (relative to cwd), overridable with `--state-file` (supports `~` expansion)

**State Schema:**
```json
{
  "pages": {
    "<page-id>": {
      "lastEditedTime": "ISO timestamp",
      "lastChecked": "ISO timestamp",
      "title": "Page Title"
    }
  }
}
```

**Returns:** JSON with `hasChanges`, `localDiffers`, `actions`

### get-database-schema.js

Inspect database structure.

**Signature:**
```bash
node scripts/get-database-schema.js <database-id> [--json]
```

**Returns:** JSON with database properties and their types

### delete-notion-page.js

Archive page (soft delete).

**Signature:**
```bash
node scripts/delete-notion-page.js <page-id> [--json]
```

**Note:** Sets `archived: true`, doesn't permanently delete

## Notion API Utilities

### notion-utils.js

Shared utilities for all scripts.

**Exports:**

#### `notionRequest(path, method, body)`
Makes authenticated API requests to Notion.

**Parameters:**
- `path`: API endpoint (e.g., `/v1/pages`)
- `method`: HTTP method (GET, POST, PATCH, DELETE)
- `body`: Optional request body (object)

**Returns:** Promise resolving to response JSON

**Error Handling:** Throws actionable messages for common failures:
- Missing token: guidance for `--token-file`, `--token-stdin`, and `NOTION_API_KEY`
- 401: authentication/access guidance
- 404: page/database access/id guidance
- Network errors: connectivity guidance

#### `formatPropertyValue(type, value)`
Formats property values for Notion API write operations.

**Supported Types:**
- select, multi_select, checkbox, number, url, email, date, rich_text, title

**Returns:** Notion API property object

#### `normalizeId(id)`
Normalizes a Notion page/block ID to UUID format with hyphens.

**Input Formats:**
- With hyphens: `abc12345-6789-0123-4567-890abcdef012` (passes through)
- Without hyphens: `abc12345678901234567890abcdef012` (adds hyphens)
- Invalid length: returned as-is

**Returns:** UUID string with hyphens

## Rate Limits

Notion API limits:
- ~3 requests/second
- Scripts implement 350ms delays between batches
- Large operations (>100 blocks) auto-batch with delays

## Common Issues

### Authentication Errors

**Error:** `"Could not find page"`

**Solutions:**
1. Verify page/database is shared with your integration
2. Check page ID format (32 chars, no extra characters)
3. Confirm your integration token is valid and available via --token-file, --token-stdin, ~/.notion-token, or NOTION_API_KEY

### Property Update Failures

**Issue:** Property updates don't persist

**Cause:** Database is inline (embedded in a page) rather than standalone

**Solution:** Create standalone database or update properties manually in Notion UI

### Module Not Found

**Error:** `Cannot find module 'https'`

**Solution:** Ensure using Node.js v18+ (built-in modules)

## Page ID Extraction

From Notion URL:
```
https://notion.so/Page-Title-abc123-example-page-id-456def
                            └─────────── Extract this part ──────────┘
```

Both formats work:
- With hyphens: `abc123-example-page-id-456def`
- Without hyphens: `abc123examplepageid456def`

## Integration Permissions

Required Notion integration capabilities:
- ✓ Read content
- ✓ Update content
- ✓ Insert content
- ✓ Read comments (optional)

Share settings:
- Must explicitly share each page/database with the integration
- Child pages inherit parent permissions
- Databases require explicit sharing even if parent is shared
