# Bookmarks — Karakeep

Karakeep (formerly Hoarder) is a self-hosted bookmark manager with AI-powered tagging and summarization.

## Environment Variables

```
KARAKEEP_URL       — Karakeep base URL (e.g., http://10.0.0.5:3000)
KARAKEEP_API_KEY   — Bearer token from Settings > API Keys
```

## Authentication

All requests use Bearer token auth. Generate a key in the Karakeep web UI at **Settings > API Keys**.

```bash
# Verify auth
curl -s "$KARAKEEP_URL/api/v1/users/me" \
  -H "Authorization: Bearer $KARAKEEP_API_KEY"
```

## Common Operations

### Save a Bookmark

```bash
# Save a link
curl -s -X POST "$KARAKEEP_URL/api/v1/bookmarks" \
  -H "Authorization: Bearer $KARAKEEP_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"type": "link", "url": "https://example.com"}'

# Save a text note (Markdown supported)
curl -s -X POST "$KARAKEEP_URL/api/v1/bookmarks" \
  -H "Authorization: Bearer $KARAKEEP_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"type": "text", "text": "# My Note\nSome content here"}'
```

### List Bookmarks

```bash
curl -s "$KARAKEEP_URL/api/v1/bookmarks?limit=20" \
  -H "Authorization: Bearer $KARAKEEP_API_KEY"
```

Response uses cursor-based pagination. Use `nextCursor` from the response for the next page.

### Search Bookmarks

```bash
curl -s "$KARAKEEP_URL/api/v1/bookmarks/search?q=QUERY" \
  -H "Authorization: Bearer $KARAKEEP_API_KEY"
```

**Query language:**
- Free text: `machine learning`
- Tag filter: `#ai`
- Status: `is:archived`, `is:favourited`
- URL filter: `url:github.com`
- Boolean: `#ai and is:favourited`
- Grouped: `(#ai or #automation) and is:archived`

### Get / Update / Delete a Bookmark

```bash
# Get
curl -s "$KARAKEEP_URL/api/v1/bookmarks/BOOKMARK_ID" \
  -H "Authorization: Bearer $KARAKEEP_API_KEY"

# Update (e.g., archive)
curl -s -X PATCH "$KARAKEEP_URL/api/v1/bookmarks/BOOKMARK_ID" \
  -H "Authorization: Bearer $KARAKEEP_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"archived": true}'

# Delete — destructive, confirm with user first
curl -s -X DELETE "$KARAKEEP_URL/api/v1/bookmarks/BOOKMARK_ID" \
  -H "Authorization: Bearer $KARAKEEP_API_KEY"
```

## Tags

```bash
# List all tags (sorted by usage)
curl -s "$KARAKEEP_URL/api/v1/tags" \
  -H "Authorization: Bearer $KARAKEEP_API_KEY"

# Tag a bookmark
curl -s -X POST "$KARAKEEP_URL/api/v1/bookmarks/BOOKMARK_ID/tags" \
  -H "Authorization: Bearer $KARAKEEP_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"tags": [{"tagName": "my-tag"}]}'

# Remove tag from bookmark
curl -s -X DELETE "$KARAKEEP_URL/api/v1/bookmarks/BOOKMARK_ID/tags" \
  -H "Authorization: Bearer $KARAKEEP_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"tags": [{"tagName": "my-tag"}]}'
```

Tags track `attachedBy` (ai or human) with counts in `numBookmarksByAttachedType`.

## Lists

```bash
# List all lists
curl -s "$KARAKEEP_URL/api/v1/lists" \
  -H "Authorization: Bearer $KARAKEEP_API_KEY"

# Create a manual list
curl -s -X POST "$KARAKEEP_URL/api/v1/lists" \
  -H "Authorization: Bearer $KARAKEEP_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"name": "Reading List", "icon": "📚"}'

# Create a smart list (auto-populated by query)
curl -s -X POST "$KARAKEEP_URL/api/v1/lists" \
  -H "Authorization: Bearer $KARAKEEP_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"name": "AI Articles", "icon": "🤖", "type": "smart", "query": "#ai"}'

# Add bookmark to list
curl -s -X PUT "$KARAKEEP_URL/api/v1/lists/LIST_ID/bookmarks/BOOKMARK_ID" \
  -H "Authorization: Bearer $KARAKEEP_API_KEY"
```

## AI Features

```bash
# Trigger AI summarization
curl -s -X POST "$KARAKEEP_URL/api/v1/bookmarks/BOOKMARK_ID/summarize" \
  -H "Authorization: Bearer $KARAKEEP_API_KEY"
```

AI tagging runs automatically on new bookmarks. Summary and tags appear in the bookmark's `summary`, `tags`, `taggingStatus`, and `summarizationStatus` fields.

## User Stats

```bash
curl -s "$KARAKEEP_URL/api/v1/users/me/stats" \
  -H "Authorization: Bearer $KARAKEEP_API_KEY"
```

## Common Agent Tasks

### "Save this link"

POST to `/api/v1/bookmarks` with `type: "link"` and the URL. AI tagging and summarization run automatically.

### "Search my bookmarks"

Use the search endpoint with the query language. Combine free text, tags, and status filters.

### "What are my most-used tags?"

GET `/api/v1/tags` — returns tags sorted by usage count by default.
