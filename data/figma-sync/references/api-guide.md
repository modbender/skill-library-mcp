# Figma REST API Guide

## Authentication

Set `FIGMA_TOKEN` env var with a Personal Access Token or OAuth token.

```
Authorization: Bearer <FIGMA_TOKEN>
```

Get a token: https://www.figma.com/developers/api#access-tokens

## Endpoints Used

### Read Operations

| Endpoint | Purpose |
|---|---|
| `GET /v1/files/{key}` | Full file tree, styles, components |
| `GET /v1/files/{key}/nodes?ids=X,Y` | Specific nodes only |
| `GET /v1/images/{key}?ids=X&format=png` | Export node images/assets |
| `GET /v1/files/{key}/styles` | Published styles |
| `GET /v1/files/{key}/components` | Published components |

Base URL: `https://api.figma.com`

### Write Operations — Limitations

**The Figma REST API is read-only for file content.** There is no REST endpoint to modify
nodes, text, fills, or layout.

Write operations require one of:
1. **Figma Plugin API** — runs inside Figma desktop/web app via a plugin
2. **Figma Variables REST API** — can create/update variables and variable collections (limited)
3. **Figma Dev Mode API** — read-only, for developers

`figma_push.py` generates a **plugin-compatible operations spec** that can be consumed by
a companion Figma plugin. The script documents what each operation would do and validates
the patch spec, but actual mutations require the plugin bridge.

For operations that *can* be done via REST (variables, comments, webhooks), the script
uses those endpoints directly.

## Rate Limits

- ~30 requests/minute for personal tokens
- Figma returns `429` with `Retry-After` header
- Strategy: exponential backoff starting at 1s, max 60s, max 5 retries
- Use `If-None-Match` with ETags for conditional requests
- Check `X-FIGMA-CACHED` response header

## Caching

Cache directory: `.figma-cache/`

```
.figma-cache/
  {fileKey}/
    file.json        # full file response
    etag.txt         # ETag for conditional requests
    last_modified.txt
    images/          # exported images
```

## Error Codes

| Code | Meaning |
|---|---|
| 400 | Bad request (invalid node IDs, etc.) |
| 403 | Token invalid or no access to file |
| 404 | File or node not found |
| 429 | Rate limited — retry after delay |
| 500 | Figma server error — retry |
