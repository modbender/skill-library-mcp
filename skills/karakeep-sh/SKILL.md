---
name: karakeep
description: Karakeep bookmark manager with full API support including notes, updates, and deletion. Requires KARAKEEP_SERVER_URL and KARAKEEP_API_KEY environment variables.
---

# Karakeep Skill

Advanced Karakeep bookmark management with full REST API support.

## Complete Function Reference

Use this script [karakeep-script.sh](scripts/karakeep-script.sh)

We have the functions below:

| Function | Description |
|----------|-------------|
| `kb-create` | Create bookmark (supports note) |
| `kb-update-note` | Update bookmark note |
| `kb-delete` | Delete bookmark |
| `kb-get` | Get bookmark details |
| `kb-list` | List all bookmarks (with limit) |
| `kb-content` | Get markdown content |
| `kb-search` | Search with qualifiers |
| `kb-lists` | List all lists |
| `kb-create-list` | Create new list |
| `kb-add-to-list` | Add to list |
| `kb-remove-from-list` | Remove from list |
| `kb-attach-tags` | Attach tags |
| `kb-detach-tags` | Detach tags |

## Available Operations

### Create Bookmark with Note

```bash
# Link bookmark with note
kb-create link "https://example.com" "Example Site" "My analysis and notes here..."

# Text bookmark with note
kb-create text "Text content here" "My Note" "Additional notes..."
```

### Update Bookmark Note

```bash
kb-update-note "bookmark_id" "Updated note content..."
```

### Delete Bookmark

```bash
kb-delete "bookmark_id"
```

### Get Bookmark

```bash
kb-get "bookmark_id"
```

### Search Operations

```bash
# Search with qualifiers (uses MeiliSearch backend)
kb-search "is:fav after:2023-01-01 #important"
kb-search "machine learning is:tagged"
kb-search "list:reading #work"

# Search with custom limit and sort order
kb-search "python" 50 "desc"  # 50 results, descending order

# Available qualifiers:
# - is:fav, is:archived, is:tagged, is:inlist
# - is:link, is:text, is:media
# - url:<value>, #<tag>, list:<name>
# - after:<YYYY-MM-DD>, before:<YYYY-MM-DD>

# Sort options: relevance (default), asc, desc
```

**API Parameters:**
- `q` (required): Search query string with qualifiers
- `limit` (optional): Results per page (default: server-controlled)
- `sortOrder` (optional): `asc` | `desc` | `relevance` (default)
- `cursor` (optional): Pagination cursor
- `includeContent` (optional): Include full content (default: true)

### List Management

```bash
# List all lists
kb-lists

# Create new list
kb-create-list "Reading List" "📚"

# Add bookmark to list
kb-add-to-list "bookmark_id" "list_id"

# Remove bookmark from list
kb-remove-from-list "bookmark_id" "list_id"
```

### Tag Management

```bash
# Attach tags
kb-attach-tags "bookmark_id" "important" "todo" "work"

# Detach tags
kb-detach-tags "bookmark_id" "oldtag" "anotherold"
```

## Notes

- All responses are in JSON format
- Bookmark IDs are returned in creation responses
- Use `jq` for pretty-printing JSON responses
- API rate limits may apply

