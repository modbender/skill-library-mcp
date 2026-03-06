---
name: stripfeed
description: Fetch any URL as clean, AI-ready Markdown with token counts and caching. Strip ads, nav, scripts, and noise from web pages.
version: 1.0.0
metadata:
  openclaw:
    requires:
      env: [STRIPFEED_API_KEY]
      bins: [curl]
    primaryEnv: STRIPFEED_API_KEY
    emoji: "📄"
    homepage: https://www.stripfeed.dev
---

# StripFeed

Convert any URL to clean Markdown optimized for LLM consumption. Strips ads, navigation, scripts, and noise. Returns token counts so you know exactly how much context you're using.

## When to use this skill

Use StripFeed whenever you need to read a web page, article, documentation, or any URL content. It produces much cleaner output than raw HTML fetching and tells you the token cost.

## Authentication

All requests require the `STRIPFEED_API_KEY` environment variable. Pass it as a Bearer token:

```
Authorization: Bearer $STRIPFEED_API_KEY
```

Get a free API key at https://www.stripfeed.dev (200 requests/month, no credit card).

## Fetch a single URL

```bash
curl -s "https://www.stripfeed.dev/api/v1/fetch?url=URL_HERE" \
  -H "Authorization: Bearer $STRIPFEED_API_KEY"
```

This returns clean Markdown directly as the response body (Content-Type: text/markdown).

### Parameters

| Parameter    | Required | Description                                                                               |
| ------------ | -------- | ----------------------------------------------------------------------------------------- |
| `url`        | Yes      | The URL to fetch (must be http or https)                                                  |
| `format`     | No       | Output format: `markdown` (default), `json`, `text`, `html`. Pro only except markdown.    |
| `selector`   | No       | CSS selector to extract specific content (e.g. `article`, `.content`, `#main`). Pro only. |
| `cache`      | No       | Set to `false` to bypass cache and force a fresh fetch                                    |
| `ttl`        | No       | Cache TTL in seconds (default: 3600, max: 86400 for Pro)                                  |
| `max_tokens` | No       | Truncate output to fit within this token budget                                           |
| `model`      | No       | AI model ID for cost tracking (e.g. `claude-sonnet-4-6`, `gpt-4o`)                        |

### JSON format (recommended for structured responses)

When you need metadata alongside the content, use `format=json`:

```bash
curl -s "https://www.stripfeed.dev/api/v1/fetch?url=URL_HERE&format=json" \
  -H "Authorization: Bearer $STRIPFEED_API_KEY"
```

JSON response includes:

```json
{
  "markdown": "# Page Title\n\nClean content...",
  "url": "https://example.com",
  "title": "Page Title",
  "tokens": 1250,
  "originalTokens": 15000,
  "savingsPercent": 91.7,
  "cached": false,
  "fetchMs": 430,
  "format": "json",
  "truncated": false,
  "selector": null,
  "model": null
}
```

### Response headers

Every response includes these headers:

- `X-StripFeed-Tokens` - Token count of the stripped content
- `X-StripFeed-Original-Tokens` - Token count of the raw HTML (before stripping)
- `X-StripFeed-Savings-Percent` - Percentage of tokens saved
- `X-StripFeed-Cache` - `HIT` or `MISS`
- `X-StripFeed-Fetch-Ms` - Time to fetch the URL (0 if cached)
- `X-StripFeed-Format` - Output format used

## Batch fetch (Pro plan)

Fetch up to 10 URLs in a single request:

```bash
curl -s -X POST "https://www.stripfeed.dev/api/v1/batch" \
  -H "Authorization: Bearer $STRIPFEED_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"urls": ["https://example.com", "https://example.org"]}'
```

URLs can also include selectors:

```json
{
  "urls": [
    { "url": "https://example.com", "selector": "article" },
    { "url": "https://example.org" }
  ],
  "model": "claude-sonnet-4-6"
}
```

Batch response:

```json
{
  "results": [
    { "url": "...", "markdown": "...", "tokens": 1250, "status": 200 },
    { "url": "...", "error": "Failed to fetch", "status": 502 }
  ],
  "total": 2,
  "success": 1,
  "failed": 1
}
```

Individual URL errors don't break the batch. Check each result's `status` field.

## Error handling

| Status | Meaning                                  |
| ------ | ---------------------------------------- |
| 401    | Missing or invalid API key               |
| 403    | Feature requires Pro plan                |
| 422    | Invalid URL, format, or parameter        |
| 429    | Rate limit or monthly quota exceeded     |
| 502    | Target URL unreachable or returned error |
| 504    | Target URL timed out (9s limit)          |

## Tips

- Default format is `markdown` which returns raw text. Use `format=json` when you need token counts and metadata in the response body.
- Responses are cached for 1 hour by default. Use `cache=false` for real-time content.
- The `max_tokens` parameter is useful to fit content within your context window budget.
- Use `selector` to grab only the main content (e.g. `selector=article` or `selector=.post-content`) and skip sidebars/footers.
- Free plan: 200 requests/month, markdown format only. Pro plan ($19/mo): 100K requests, all formats, selectors, batch endpoint.
