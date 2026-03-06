# Brave Search API Reference

## Plans & Limits

| Plan     | Req/month | Req/sec | Notes                        |
|----------|-----------|---------|------------------------------|
| Free     | 2,000     | 1       | Web search only              |
| Free AI  | 2,000     | 1       | AI summaries                 |
| Basic    | 2,000     | 1       | Web + news + images          |
| Pro      | 20,000+   | 20      | Full access                  |

## Endpoints

Base URL: `https://api.search.brave.com/res/v1`

- `GET /web/search` — Web results
- `GET /news/search` — News results  
- `GET /images/search` — Image results

## Common Query Parameters

| Param         | Description                         | Default |
|---------------|-------------------------------------|---------|
| `q`           | Search query (required)             | —       |
| `count`       | Results (1–20)                      | 10      |
| `offset`      | Pagination offset                   | 0       |
| `country`     | 2-letter country code               | us      |
| `search_lang` | 2-letter language code              | en      |
| `safesearch`  | off / moderate / strict             | moderate|
| `freshness`   | pd / pw / pm / py / date range      | —       |
| `text_decorations` | Bold matches in snippets       | true    |
| `spellcheck`  | Auto correct query                  | true    |

## Headers

```
Accept: application/json
Accept-Encoding: gzip
X-Subscription-Token: <your_api_key>
```

Response is gzip-compressed — decompress before parsing JSON.

## Rate Limit Response

HTTP 429: Too Many Requests — rotate to next key.
HTTP 403: Forbidden — key invalid or suspended.
