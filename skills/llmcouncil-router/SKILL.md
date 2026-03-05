---
name: llmcouncil-router
description: Route any prompt to the best-performing LLM using peer-reviewed council rankings from LLM Council
homepage: https://llmcouncil.ai
user-invocable: true
metadata: {"openclaw":{"requires":{"env":["LLMCOUNCIL_API_KEY"]},"emoji":"🧠"}}
---

# LLM Council Router

Route any prompt to the best-performing LLM. The API finds the top model for a given query based on thousands of peer-reviewed council deliberations — then you call that model directly.

## Base URL

```
https://clawbot.llmcouncil.ai
```

## Authentication

Use the `X-API-Key` header with your LLM Council API key.

```
X-API-Key: clwb_YOUR_KEY_HERE
```

Get a free key at [llmcouncil.ai/developers](https://llmcouncil.ai/developers).

## Endpoint: POST /v1/route

Find the best-performing model for a query.

### Request

```json
{
  "query": "Explain quantum entanglement simply",
  "k": 20
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `query` | string | Yes | The prompt or question to route |
| `k` | integer | No | Number of past evaluations to consider (default: 20) |

### Response

```json
{
  "query": "Explain quantum entanglement simply",
  "nearest_councils": 20,
  "model": "anthropic/claude-sonnet-4",
  "relevance": 0.8234,
  "confidence": 0.65,
  "model_rankings": [
    { "rank": 1, "model": "anthropic/claude-sonnet-4", "nearby_wins": 13, "nearby_appearances": 20 },
    { "rank": 2, "model": "openai/gpt-4.1", "nearby_wins": 5, "nearby_appearances": 18 }
  ]
}
```

| Field | Type | Description |
|-------|------|-------------|
| `model` | string | Top recommended model ID (matches OpenRouter catalogue) |
| `relevance` | float (0–1) | How closely matched evaluations relate to your query. Above 0.75 is strong. |
| `confidence` | float (0–1) | How decisively the top model outperforms alternatives. Higher = clearer winner. |
| `nearest_councils` | integer | Number of relevant past evaluations used |
| `model_rankings` | array | All models ranked by performance across matched evaluations |

## How to use this skill

When the user asks you to find the best model for a task, or when you need to decide which LLM to use:

1. **Call the routing API** with the user's query:

```bash
curl -X POST https://clawbot.llmcouncil.ai/v1/route \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $LLMCOUNCIL_API_KEY" \
  -d '{"query": "USER_QUERY_HERE"}'
```

2. **Read the response** — the `model` field is the best-performing model for that query type.

3. **Chain with OpenRouter** — model IDs match the OpenRouter catalogue directly, no mapping needed:

```python
import requests, os

# Step 1: Get the best model from LLM Council
route = requests.post(
    "https://clawbot.llmcouncil.ai/v1/route",
    headers={"X-API-Key": os.environ["LLMCOUNCIL_API_KEY"]},
    json={"query": "Write a Python web scraper"},
).json()

best_model = route["model"]       # e.g. "anthropic/claude-sonnet-4"
confidence = route["confidence"]   # e.g. 0.85

# Step 2: Call that model via OpenRouter
answer = requests.post(
    "https://openrouter.ai/api/v1/chat/completions",
    headers={"Authorization": f"Bearer {os.environ['OPENROUTER_API_KEY']}"},
    json={
        "model": best_model,
        "messages": [{"role": "user", "content": "Write a Python web scraper"}],
    },
).json()

print(answer["choices"][0]["message"]["content"])
```

## Rate Limits

| Tier | Daily Limit | Attribution |
|------|-------------|-------------|
| Free | 100 requests/day | Required |
| Pro | 10,000 requests/day | None |

## When to use this

- User asks "which model is best for X?"
- You need to pick the optimal model for a specific task type
- You want data-driven model selection instead of guessing
- You want to chain model routing with OpenRouter for automatic best-model dispatch
