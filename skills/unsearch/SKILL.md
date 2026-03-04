---
name: unsearch
version: 1.0.0
description: Search the web, scrape content, and conduct deep research using the UnSearch API. Use when the user needs real-time web search results, content extraction from URLs, fact verification, or multi-source research for AI agents, RAG pipelines, or LLM applications.
metadata: {"openclaw":{"emoji":"🔍","homepage":"https://unsearch.dev","primaryEnv":"UNSEARCH_API_KEY","requires":{"env":["UNSEARCH_API_KEY"]}}}
---

# UnSearch Web Search Skill

Search the web, extract content, verify facts, and conduct deep research using the UnSearch API—an open-source Tavily/Exa alternative.

## Quick Start

Set your API key:
```bash
export UNSEARCH_API_KEY="uns_your_api_key"
```

Get a free API key at https://unsearch.dev (5,000 queries/month free).

## API Endpoints

**Base URL:** `https://api.unsearch.dev/api/v1`

All requests require header: `X-API-Key: $UNSEARCH_API_KEY`

---

## 1. Web Search

Search the web with optional content scraping.

```bash
curl -X POST "https://api.unsearch.dev/api/v1/search" \
  -H "X-API-Key: $UNSEARCH_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "your search query",
    "engines": ["google", "bing", "duckduckgo"],
    "max_results": 10,
    "scrape_content": true
  }'
```

### Key Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `query` | string | required | Search query (1-500 chars) |
| `engines` | string[] | ["google","bing","duckduckgo"] | Search engines |
| `max_results` | integer | 10 | Results to return (1-100) |
| `scrape_content` | boolean | true | Extract full page content |
| `language` | string | "en" | ISO 639-1 language code |

### Response

```json
{
  "results": [
    {
      "title": "Page Title",
      "url": "https://example.com",
      "snippet": "Search result snippet...",
      "scraped_content": {
        "text": "Full page content...",
        "word_count": 2500
      }
    }
  ],
  "processing_time_ms": 1500
}
```

---

## 2. Agent Search (Tavily-Compatible)

AI-optimized search with optional answer generation.

```bash
curl -X POST "https://api.unsearch.dev/api/v1/agent/search" \
  -H "X-API-Key: $UNSEARCH_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is machine learning?",
    "include_answer": true,
    "max_results": 5,
    "search_depth": "basic"
  }'
```

### Key Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `query` | string | required | Search query |
| `include_answer` | bool/string | false | Generate AI answer (`true`, `"basic"`, `"advanced"`, `"production"`) |
| `search_depth` | string | "basic" | `basic`, `advanced`, `fast` |
| `max_results` | integer | 5 | Results (1-20) |
| `include_raw_content` | boolean | false | Include full page content |
| `include_domains` | string[] | null | Only search these domains |
| `exclude_domains` | string[] | null | Exclude these domains |

### Response

```json
{
  "query": "What is machine learning?",
  "answer": "Machine learning is a subset of AI...",
  "results": [
    {
      "title": "Machine Learning - Wikipedia",
      "url": "https://en.wikipedia.org/wiki/Machine_learning",
      "content": "Machine learning is a branch of AI...",
      "score": 0.95
    }
  ],
  "response_time": 1.25
}
```

---

## 3. Content Extraction

Extract content from specific URLs.

```bash
curl -X POST "https://api.unsearch.dev/api/v1/agent/extract" \
  -H "X-API-Key: $UNSEARCH_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "urls": ["https://example.com/article"],
    "extract_depth": "basic"
  }'
```

### Response

```json
{
  "results": [
    {
      "url": "https://example.com/article",
      "raw_content": "Full article text...",
      "failed": false
    }
  ]
}
```

---

## 4. Deep Research

Multi-source research with AI synthesis.

```bash
curl -X POST "https://api.unsearch.dev/api/v1/agent/research" \
  -H "X-API-Key: $UNSEARCH_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Impact of AI on healthcare",
    "depth": "deep",
    "max_sources": 15,
    "include_analysis": true
  }'
```

### Depth Levels

| Depth | Sources | Use Case |
|-------|---------|----------|
| `quick` | 3-5 | Fast overview |
| `standard` | 5-10 | Balanced research |
| `deep` | 10-20 | Thorough analysis |
| `comprehensive` | 20-30 | Expert-level |

### Response

```json
{
  "executive_summary": "AI is transforming healthcare...",
  "key_findings": ["AI diagnostics show 95% accuracy..."],
  "sources": [...],
  "model_used": "qwq-32b"
}
```

---

## 5. Fact Verification

Verify claims against multiple sources.

```bash
curl -X POST "https://api.unsearch.dev/api/v1/verify/claim" \
  -H "X-API-Key: $UNSEARCH_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "claim": "GPT-4 was released in March 2023",
    "depth": "thorough"
  }'
```

### Response

```json
{
  "verdict": "true",
  "confidence": 95,
  "summary": "GPT-4 was released March 14, 2023.",
  "supporting_evidence": [...],
  "sources_checked": 12
}
```

Verdict values: `true`, `false`, `partially_true`, `misleading`, `unverifiable`

---

## Python Examples

```python
import httpx
import os

API_KEY = os.environ["UNSEARCH_API_KEY"]
BASE_URL = "https://api.unsearch.dev/api/v1"

async def search(query: str, scrape: bool = False):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BASE_URL}/search",
            headers={"X-API-Key": API_KEY},
            json={
                "query": query,
                "max_results": 10,
                "scrape_content": scrape
            }
        )
        return response.json()

async def agent_search(query: str, include_answer: bool = True):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BASE_URL}/agent/search",
            headers={"X-API-Key": API_KEY},
            json={
                "query": query,
                "include_answer": include_answer,
                "max_results": 5
            }
        )
        return response.json()

async def extract_urls(urls: list[str]):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BASE_URL}/agent/extract",
            headers={"X-API-Key": API_KEY},
            json={"urls": urls}
        )
        return response.json()
```

---

## JavaScript Examples

```javascript
const API_KEY = process.env.UNSEARCH_API_KEY;
const BASE_URL = "https://api.unsearch.dev/api/v1";

async function search(query, scrapeContent = false) {
  const response = await fetch(`${BASE_URL}/search`, {
    method: "POST",
    headers: {
      "X-API-Key": API_KEY,
      "Content-Type": "application/json"
    },
    body: JSON.stringify({
      query,
      max_results: 10,
      scrape_content: scrapeContent
    })
  });
  return response.json();
}

async function agentSearch(query, includeAnswer = true) {
  const response = await fetch(`${BASE_URL}/agent/search`, {
    method: "POST",
    headers: {
      "X-API-Key": API_KEY,
      "Content-Type": "application/json"
    },
    body: JSON.stringify({
      query,
      include_answer: includeAnswer,
      max_results: 5
    })
  });
  return response.json();
}
```

---

## Rate Limits

| Plan | Queries/Month | Rate Limit |
|------|---------------|------------|
| Free | 5,000 | 10/min |
| Pro | 25,000 | 60/min |
| Growth | 100,000 | 200/min |
| Scale | 500,000 | 1,000/min |

Rate limit headers in response:
- `X-RateLimit-Remaining`: Requests left
- `X-RateLimit-Reset`: Reset timestamp

---

## Privacy Mode

For sensitive queries, enable zero-retention:

```bash
curl -X POST "https://api.unsearch.dev/api/v1/search" \
  -H "X-API-Key: $UNSEARCH_API_KEY" \
  -H "X-Zero-Retention: true" \
  -H "Content-Type: application/json" \
  -d '{"query": "sensitive query"}'
```

---

## Error Handling

| Code | Description |
|------|-------------|
| 401 | Invalid API key |
| 429 | Rate limited (check `Retry-After` header) |
| 422 | Validation error |
| 500 | Server error |

---

## Additional Resources

- **Documentation:** https://docs.unsearch.dev
- **API Reference:** https://docs.unsearch.dev/api
- **Self-hosting:** https://github.com/unsearch-org/unsearch
- **Get API Key:** https://unsearch.dev
