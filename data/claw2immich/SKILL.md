---
name: claw2immich
description: Work with Immich photo library via MCP (claw2immich) - search photos by people, dates, locations, albums. Download assets via shared links. Handles multi-person search, CLIP smart search, and metadata queries.
homepage: https://github.com/JoeRu/claw2immich
metadata:
  openclaw:
    emoji: 📸
    requires:
      mcp: [immich]
---

# Immich Photo Library (via claw2immich)

Work with your Immich photo library via the **claw2immich** MCP server. Search by people, dates, locations, and albums. Download photos via shared links or inline base64. 249 tools available from the full Immich OpenAPI spec.

## Prerequisites

- **Immich instance** running (https://immich.app)
- **claw2immich MCP server** installed and running
  - Repository: https://github.com/JoeRu/claw2immich
  - Follow setup instructions in the repo README

- MCP server configured in `config/mcporter.json`:
  ```json
  {
    "mcpServers": {
      "immich": {
        "baseUrl": "http://your-claw2immich-host:port/sse"
      }
    }
  }
  ```

## Key Tools

| Tool | Description |
|------|-------------|
| `immich_searchassets` | Metadata search (date, people, location, etc.) |
| `immich_searchsmart` | CLIP-based natural language search |
| `immich_searchperson` | Find person by name |
| `immich_getassetinfo` | Get full asset details including `web_url` |
| `immich_viewasset` | Get thumbnail/preview as base64 (WebP) |
| `downloadAsset` | Download asset via shared link (default) or inline base64 |
| `immich_getallpeople` | List all people |
| `immich_getallalbums` | List all albums |
| `immich_createsharedlink` | Create shared link for album/assets |
| `tool_access_report` | Check which tools are available |

## Quick Start

### Find people by name
```
mcporter call immich immich_searchperson query_name="Maria"
```

### Search photos with multiple people (AND logic)
```
mcporter call immich immich_searchassets \
  'body_personIds=["person-uuid-1","person-uuid-2"]' \
  body_order=desc body_size=10
```

### CLIP smart search (natural language)
```
mcporter call immich immich_searchsmart \
  body_query="sunset at the beach" body_size=5
```

### Get asset info (includes web_url)
```
mcporter call immich immich_getassetinfo path_id=<asset-uuid>
```

### Download a photo (shared link)
```
mcporter call immich downloadAsset asset_id=<asset-uuid>
```
Returns a short-lived shared link (30 min, no auth needed).

### Get thumbnail for display
```
mcporter call immich immich_viewasset path_id=<asset-uuid> query_size=thumbnail
```
Returns `{encoding: "base64", content_type: "image/webp", size_bytes: ..., data: "..."}`.

## Web URLs

Tool responses for assets, albums, people, and places include a `web_url` field:
- Assets: `https://<domain>/photos/<asset-id>`
- Albums: `https://<domain>/albums/<album-id>`
- People: `https://<domain>/people/<person-id>`

This requires `IMMICH_EXTERNAL_DOMAIN` to be configured on the server.

## Common Workflows

### "Show me recent photos of X and Y together"

1. **Find person IDs:**
   ```
   mcporter call immich immich_searchperson query_name="Alice"
   mcporter call immich immich_searchperson query_name="Bob"
   ```

2. **Search photos (AND logic):**
   ```
   mcporter call immich immich_searchassets \
     'body_personIds=["alice-id","bob-id"]' \
     body_order=desc body_size=10
   ```

3. **Display a photo:**
   ```
   mcporter call immich immich_viewasset path_id=<asset-id> query_size=thumbnail
   ```
   Decode base64 data, save as .webp, send to user.

### "Find vacation photos from summer 2024"

```
mcporter call immich immich_searchassets \
  body_createdAfter="2024-06-01T00:00:00Z" \
  body_createdBefore="2024-08-31T23:59:59Z" \
  body_city="Barcelona" body_order=desc
```

### "Download a photo"

```
mcporter call immich downloadAsset asset_id=<asset-uuid>
```

Response:
```json
{
  "delivery_mode": "shared_link",
  "download_url": "https://immich.example.com/share/<token>",
  "expires_in_minutes": 30,
  "requires_auth": false
}
```

The shared link can be sent directly to users — no auth required.

### Displaying photos in chat

1. Get thumbnail via `immich_viewasset` (query_size=thumbnail, typically < 30KB)
2. Decode the base64 `data` field
3. Save as `.webp` file
4. Send via messaging tool

**Note:** `preview` size may exceed the 64KB MCP transport limit. Use `thumbnail` for reliable delivery.

## Key Parameters

### immich_searchassets (POST /api/search/assets)

**Filtering:**
- `body_personIds: ["uuid1", "uuid2"]` — Photos with these people (AND)
- `body_city: "string"` — Filter by city
- `body_country: "string"` — Filter by country
- `body_createdAfter: "ISO8601"` — Minimum date
- `body_createdBefore: "ISO8601"` — Maximum date
- `body_isFavorite: boolean` — Only favorites
- `body_albumIds: ["uuid"]` — Filter by albums

**Sorting & Pagination:**
- `body_order: "desc"` — Newest first
- `body_order: "asc"` — Oldest first
- `body_size: number` — Limit results
- `body_page: number` — Page number

### immich_searchsmart (POST /api/search/smart)

- `body_query: "string"` — Natural language query (CLIP-based)
- `body_size: number` — Limit results
- Same filter parameters as searchassets

### downloadAsset

- `asset_id: "uuid"` — Asset to download

Delivery mode is controlled server-side via `IMMICH_DOWNLOAD_ASSET_DELIVERY`:
- `shared_link` (default): Returns a tokenized shared link (30 min TTL, no auth)
- `inline_base64`: Returns base64-encoded file data (limited by 64KB transport)
- `immich_link`: Returns direct Immich URL (requires auth)

### immich_viewasset (GET /api/assets/{id}/thumbnail)

- `path_id: "uuid"` — Asset ID
- `query_size: "thumbnail"|"preview"` — Image size

Returns structured base64 response. Use `thumbnail` to stay under transport limits.

## Important Patterns

### Multi-Person Search (AND)
✅ **Correct:** Array in `body_personIds`
```json
{"body_personIds": ["person-1", "person-2"]}
```
❌ **Wrong:** Separate calls (that's OR, not AND)

### Parameter Prefixes
All OpenAPI tool parameters use prefixes:
- `path_<name>` — Path parameters
- `query_<name>` — Query parameters
- `body_<name>` — Body parameters (for POST endpoints)

### Date Filtering
Always use ISO 8601: `"2024-01-15T00:00:00Z"`

### 64KB Transport Limit
MCP responses are truncated at 64KB. This affects:
- `downloadAsset` with `inline_base64` mode (use `shared_link` instead)
- `immich_viewasset` with `query_size=preview` (use `thumbnail` instead)
- Large search results (reduce `body_size`)

## Access Profiles

Set `IMMICH_PROFILE` on the server to restrict tools:
- `read_only` — Only GET endpoints (search, browse)
- `read_write` — Read + write (upload, update, delete)
- `full_scope` — Everything including admin

Use `tool_access_report` to check available tools.

## Troubleshooting

**No results with multiple people:**
- Verify person IDs (search each person first)
- Add `body_isArchived: false` if photos might be archived

**downloadAsset returns error:**
- Check `tool_access_report` for permissions
- Shared link creation requires write access to shared-links API

**Thumbnail too large:**
- Use `query_size=thumbnail` instead of `preview`
- Thumbnails are typically 5-25 KB (WebP)

**MCP call fails:**
- Verify server is running: `mcporter call immich ping_server`
- Check config: `mcporter list immich`

## Reference

- **Immich:** https://immich.app
- **claw2immich:** https://github.com/JoeRu/claw2immich
- **Immich API docs:** https://immich.app/docs/api/
