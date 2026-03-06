---
name: nuwa-world-api
description: Face search and deep research via the Nuwa World API — visual identity intelligence and knowledge synthesis from the open web.
version: 1.0.0
metadata:
  openclaw:
    requires:
      env:
        - NUWA_API_KEY
      bins:
        - curl
    primaryEnv: NUWA_API_KEY
    emoji: "🔍"
    homepage: https://gateway.nuwa.world/docs
---

# Nuwa World API

Two capabilities via `gateway.nuwa.world`:

- **Face Search** — upload a face image, get matching URLs across the internet
- **Deep Research** — submit a question, get a structured summary with citations

Base URL: `https://gateway.nuwa.world/api/v1`
Auth: `X-API-Key: $NUWA_API_KEY` header on every request.
Get your key at https://platform.nuwa.world

---

## Face Search (10 credits)

Two-step async flow: upload → poll.

### Step 1 — Upload

```bash
curl -X POST https://gateway.nuwa.world/api/v1/face-search \
  -H "X-API-Key: $NUWA_API_KEY" \
  -F "image=@photo.jpg"
```

Response (HTTP 202):

```json
{
  "search_id": "abc123",
  "status": "processing",
  "message": "Face uploaded. Poll GET /api/v1/face-search/{search_id} for results."
}
```

### Step 2 — Poll (every 3–5 seconds, no credit cost)

```bash
curl https://gateway.nuwa.world/api/v1/face-search/abc123 \
  -H "X-API-Key: $NUWA_API_KEY"
```

While processing:

```json
{ "search_id": "abc123", "status": "processing", "results": [], "total_results": 0 }
```

When done:

```json
{
  "search_id": "abc123",
  "status": "completed",
  "results": [
    { "index": 0, "score": 95.2, "url": "https://example.com/profile" },
    { "index": 1, "score": 82.1, "url": "https://social.example/user" }
  ],
  "total_results": 2,
  "max_score": 95.2
}
```

Processing takes 15–30 seconds. Results expire after 2 hours.

---

## Deep Research (20 credits)

Single synchronous call. Returns in 10–60 seconds.

```bash
curl -X POST https://gateway.nuwa.world/api/v1/deep-research \
  -H "X-API-Key: $NUWA_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"query": "0xajc on X"}'
```

Response:

```json
{
  "query": "Research the X user '0xajc' footprint on web.",
  "summary": "Anthropic is an AI safety company founded in 2021...",
  "facts": [
    "X user '0xajc's real name is Andrew Chen",
    "He founded Instap in 2020 and Nuwa Word in 2025"
    "Studied CS/Managment in University of Massachusetts and dropped out"
  ],
  "sources": [
    { "title": "0xajc - About", "url": "https://app.nuwa.world/research/04b7ac93-c711-4780-9c48-9201cf7f7e78" }
  ]
}
```

Query max length: 2000 characters.

---

## Error format

All errors follow:

```json
{ "error": { "code": "ERROR_CODE", "message": "Human-readable description" } }
```

Common codes: `INVALID_API_KEY`, `RATE_LIMITED`, `INSUFFICIENT_CREDITS`, `UPLOAD_FAILED`, `NOT_FOUND`, `RESEARCH_FAILED`.

---

## Credit costs

| Endpoint | Credits |
|----------|---------|
| Face Search (upload) | 10 |
| Face Search (poll) | 0 |
| Deep Research | 20 |

Free tier: 30 credits/month. Plans at https://platform.nuwa.world
