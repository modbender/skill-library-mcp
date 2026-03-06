---
name: searxng-web
description: searxng-web exposes a single, minimal tool that proxies queries to
  a locally hosted searxng instance running at
  http://host.docker.internal:8081/search?format=json&q=... and returns
  normalized resu...
---

# searxng-web

searxng-web exposes a single, minimal tool that proxies queries to a locally hosted searxng instance running at `http://host.docker.internal:8081/search?format=json&q=...` and returns normalized results.

## what it provides
- tool: `searxng_search(query, count=5)`
- runner: node script `searxng_search.js`
- output: json `{ query, count, results: [{ title, url, snippet, source }] }`

## usage examples

### simple call
input:
```json
{ "query": "zillow rentals", "count": 3 }

docker exec -it openclaw sh -lc 