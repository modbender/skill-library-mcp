# Context7 API Reference

## Base URL

```
https://context7.com/api
```

## Authentication

Authentication is optional but recommended for higher rate limits.

**Header:** `Authorization: Bearer <API_KEY>`

Get a free API key at: https://context7.com/dashboard

API keys start with the prefix `ctx7sk`.

Alternative header names also accepted:
- `Context7-API-Key: <key>`
- `X-API-Key: <key>`

---

## Endpoints

### POST /search

Searches for libraries matching a given name and ranks results by relevance to a query.

**Request Body (JSON):**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `query` | string | Yes | The user's question or task. Used for relevance ranking. |
| `libraryName` | string | Yes | The library/package name to search for. |

**Example Request:**

```bash
curl -s "https://context7.com/api/search" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ctx7sk_YOUR_KEY" \
  -d '{
    "query": "How to create a REST API",
    "libraryName": "express"
  }'
```

**Response:**

Returns an array (or `{results: [...]}` object) of matching libraries. Each result includes:

| Field | Type | Description |
|-------|------|-------------|
| `id` / `libraryId` | string | Context7-compatible library ID (e.g., `/expressjs/express`) |
| `name` / `title` | string | Human-readable library name |
| `description` | string | Short summary of the library |
| `codeSnippets` / `snippetCount` | number | Number of available code examples |
| `benchmarkScore` / `benchmark` | number | Quality indicator (0–100, higher is better) |
| `sourceReputation` / `reputation` | string | Authority level: "High", "Medium", "Low", or "Unknown" |
| `versions` | array | Available version-specific IDs (e.g., `/org/project/v1.2.3`) |

**Selection Guidance:**

When multiple results are returned, select based on:
1. **Name similarity** — Exact matches first
2. **Description relevance** — Best match to the user's intent
3. **Code Snippets** — Higher counts mean more examples available
4. **Benchmark Score** — Higher is better quality
5. **Source Reputation** — Prefer "High" or "Medium"

---

### POST /context

Retrieves documentation and code examples for a specific library, filtered by a query.

**Request Body (JSON):**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `query` | string | Yes | The question or task to get relevant docs for. Be specific. |
| `libraryId` | string | Yes | Context7 library ID from `/search` or user-provided. |

**Example Request:**

```bash
curl -s "https://context7.com/api/context" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ctx7sk_YOUR_KEY" \
  -d '{
    "query": "How to set up middleware for authentication",
    "libraryId": "/expressjs/express"
  }'
```

**Response:**

Returns documentation content. The response may include:

| Field | Type | Description |
|-------|------|-------------|
| `data` / `text` / `content` | string | Documentation text with code examples |

The content typically includes:
- Relevant documentation sections
- Code examples and snippets
- API signatures and parameter descriptions
- Links to source documentation

---

## Rate Limiting

- **Without API key:** Lower rate limits apply (suitable for occasional use)
- **With API key:** Higher rate limits (free key available at context7.com/dashboard)
- **HTTP 429 response:** Rate limit exceeded; wait and retry

## Best Practices

1. **Be specific with queries.** The API uses the query to rank and filter results. More specific queries yield more relevant documentation.
2. **Limit calls.** Do not call `/search` or `/context` more than 3 times per user question.
3. **Do not send sensitive data.** Queries are processed by the Context7 API. Never include API keys, passwords, credentials, or personal data.
4. **Use versioned library IDs** when the user specifies a particular version.

## Error Responses

| HTTP Code | Meaning |
|-----------|---------|
| 400 | Bad request — check your request body |
| 401 | Unauthorized — invalid API key |
| 404 | Library not found — verify the library ID |
| 429 | Rate limited — wait and retry, or add an API key |
| 500 | Server error — retry after a moment |
