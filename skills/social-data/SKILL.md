---
name: Macrocosmos SN13 API - Social Media Data Skill
description: Fetch real-time social media data from X (Twitter) and Reddit by
  keyword, username, date range, and filters with engagement metrics via
  Macrocosmos SN13 API on Bittensor.
---

# Macrocosmos SN13 API - Social Media Data Skill

Fetch real-time social media data from X (Twitter) and Reddit by keyword, username, date range, and filters with engagement metrics via Macrocosmos SN13 API on Bittensor.

## Metadata

- **name**: macrocosmos-social-data
- **version**: 1.0.1
- **homepage**: https://github.com/macrocosm-os/macrocosmos-mcp
- **source**: https://github.com/macrocosm-os/macrocosmos-mcp
- **pypi**: https://pypi.org/project/macrocosmos-mcp
- **subnet**: Bittensor SN13 (Data Universe)
- **author**: Macrocosmos AI
- **license**: MIT

## Required Environment Variables

| Variable | Required | Type | Description |
|----------|----------|------|-------------|
| `MC_API` | **Yes** | `secret` | Macrocosmos API key. Required for all API requests. Get your free key at https://app.macrocosmos.ai/account?tab=api-keys |

**Setup:** The `MC_API` key must be set as an environment variable. It is passed as a Bearer token in the `Authorization` header for REST calls, or provided directly to the Python SDK client.

---

## API Endpoint

```
POST https://constellation.api.cloud.macrocosmos.ai/sn13.v1.Sn13Service/OnDemandData
```

### Headers

```
Content-Type: application/json
Authorization: Bearer <YOUR_MC_API_KEY>
```

---

## Request Format

```json
{
  "source": "X",
  "usernames": ["@elonmusk"],
  "keywords": ["AI", "bittensor"],
  "start_date": "2026-01-01",
  "end_date": "2026-02-10",
  "limit": 10,
  "keyword_mode": "any"
}
```

### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `source` | string | Yes | `"X"` or `"REDDIT"` (case-sensitive) |
| `usernames` | array | No | Up to 5 usernames. `@` optional. **X only** (not available for Reddit) |
| `keywords` | array | No | Up to 5 keywords/hashtags. For Reddit: use subreddit format `"r/subreddit"` |
| `start_date` | string | No | `YYYY-MM-DD` or ISO format. Defaults to 24h ago |
| `end_date` | string | No | `YYYY-MM-DD` or ISO format. Defaults to now |
| `limit` | int | No | 1-1000 results. Default: 10 |
| `keyword_mode` | string | No | `"any"` (default) matches ANY keyword, `"all"` requires ALL keywords |

---

## Response Format

```json
{
  "data": [
    {
      "datetime": "2026-02-10T17:30:58Z",
      "source": "x",
      "text": "Tweet content here",
      "uri": "https://x.com/username/status/123456",
      "user": {
        "username": "example_user",
        "display_name": "Example User",
        "followers_count": 1500,
        "following_count": 300,
        "user_description": "Bio text",
        "user_blue_verified": true,
        "profile_image_url": "https://pbs.twimg.com/..."
      },
      "tweet": {
        "id": "123456",
        "like_count": 42,
        "retweet_count": 10,
        "reply_count": 5,
        "quote_count": 2,
        "view_count": 5000,
        "bookmark_count": 3,
        "hashtags": ["#AI", "#bittensor"],
        "language": "en",
        "is_reply": false,
        "is_quote": false,
        "conversation_id": "123456"
      }
    }
  ]
}
```

---

## curl Examples

### 1. Keyword Search on X

```bash
curl -s -X POST https://constellation.api.cloud.macrocosmos.ai/sn13.v1.Sn13Service/OnDemandData \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -d '{
    "source": "X",
    "keywords": ["bittensor"],
    "start_date": "2026-01-01",
    "limit": 10
  }'
```

### 2. Fetch Tweets from a Specific User

```bash
curl -s -X POST https://constellation.api.cloud.macrocosmos.ai/sn13.v1.Sn13Service/OnDemandData \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -d '{
    "source": "X",
    "usernames": ["@MacrocosmosAI"],
    "start_date": "2026-01-01",
    "limit": 10
  }'
```

### 3. Multi-Keyword AND Search

```bash
curl -s -X POST https://constellation.api.cloud.macrocosmos.ai/sn13.v1.Sn13Service/OnDemandData \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -d '{
    "source": "X",
    "keywords": ["chutes", "bittensor"],
    "keyword_mode": "all",
    "start_date": "2026-01-01",
    "limit": 20
  }'
```

### 4. Reddit Search

```bash
curl -s -X POST https://constellation.api.cloud.macrocosmos.ai/sn13.v1.Sn13Service/OnDemandData \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -d '{
    "source": "REDDIT",
    "keywords": ["r/MachineLearning", "transformers"],
    "start_date": "2026-02-01",
    "limit": 50
  }'
```

### 5. User + Keyword Filter

```bash
curl -s -X POST https://constellation.api.cloud.macrocosmos.ai/sn13.v1.Sn13Service/OnDemandData \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -d '{
    "source": "X",
    "usernames": ["@opentensor"],
    "keywords": ["subnet"],
    "start_date": "2026-01-01",
    "limit": 20
  }'
```

---

## Python Examples

### Using the `macrocosmos` SDK

```python
import asyncio
import macrocosmos as mc

async def search_tweets():
    client = mc.AsyncSn13Client(api_key="YOUR_API_KEY")

    response = await client.sn13.OnDemandData(
        source="X",
        keywords=["bittensor"],
        usernames=[],
        start_date="2026-01-01",
        end_date=None,
        limit=10,
        keyword_mode="any",
    )

    if hasattr(response, "model_dump"):
        data = response.model_dump()

    for tweet in data["data"]:
        print(f"@{tweet['user']['username']}: {tweet['text'][:100]}")
        print(f"  Likes: {tweet['tweet']['like_count']} | Views: {tweet['tweet']['view_count']}")

asyncio.run(search_tweets())
```

### Using `requests` (REST)

```python
import requests

url = "https://constellation.api.cloud.macrocosmos.ai/sn13.v1.Sn13Service/OnDemandData"
headers = {
    "Content-Type": "application/json",
    "Authorization": "Bearer YOUR_API_KEY"
}
payload = {
    "source": "X",
    "keywords": ["bittensor"],
    "start_date": "2026-01-01",
    "limit": 10
}

response = requests.post(url, json=payload, headers=headers)
data = response.json()

for tweet in data["data"]:
    print(f"@{tweet['user']['username']}: {tweet['text'][:100]}")
```

---

## Tips & Known Behaviors

### What works reliably
- **High-volume keyword searches**: Popular terms like "bittensor", "AI", "iran", "lfg" return fast
- **Wider date ranges**: Setting `start_date` further back (e.g., weeks/months) improves results
- **`keyword_mode: "all"`**: Great for finding intersection of two topics (e.g., "chutes" AND "bittensor")

### What can be flaky
- **Username-only queries**: Can timeout (DEADLINE_EXCEEDED). Adding `start_date` far back helps
- **Niche/low-volume keywords**: Very specific terms may timeout if miners don't have data indexed
- **No `start_date`**: Defaults to last 24h which can miss data; set explicitly for best results

### Best practices for LLM agents
1. **Always set `start_date`** — don't rely on the 24h default. Use at least 7 days back for user queries
2. **Prefer keywords over usernames** — keyword searches are more reliable
3. **For username queries, always include `start_date`** set weeks/months back
4. **Use `keyword_mode: "all"`** when combining a topic with a subtopic (e.g., "bittensor" + "chutes")
5. **Handle timeouts gracefully** — if a query times out, retry with broader date range or switch to keyword search
6. **Parse engagement metrics** — `view_count`, `like_count`, `retweet_count` help rank relevance
7. **Check `is_reply` and `is_quote`** — filter for original tweets vs replies depending on use case

---

## Gravity API (Large-Scale Collection)

For datasets larger than 1000 results, use the Gravity endpoints:

### Create Task
```
POST /gravity.v1.GravityService/CreateGravityTask
```
```json
{
  "gravity_tasks": [
    {"platform": "x", "topic": "#bittensor", "keyword": "dTAO"}
  ],
  "name": "Bittensor dTAO Collection"
}
```
**Note:** X topics MUST start with `#` or `$`. Reddit topics use subreddit format.

### Check Status
```
POST /gravity.v1.GravityService/GetGravityTasks
```
```json
{
  "gravity_task_id": "multicrawler-xxxx-xxxx",
  "include_crawlers": true
}
```

### Build Dataset
```
POST /gravity.v1.GravityService/BuildDataset
```
```json
{
  "crawler_id": "crawler-0-multicrawler-xxxx",
  "max_rows": 10000
}
```
**Warning:** Building stops the crawler permanently.

### Get Dataset Download
```
POST /gravity.v1.GravityService/GetDataset
```
```json
{
  "dataset_id": "dataset-xxxx-xxxx"
}
```
Returns Parquet file download URLs when complete.

---

## Workflow Summary

```
Quick Query (< 1000 results):
  OnDemandData → instant results

Large Collection (7-day crawl):
  CreateGravityTask → GetGravityTasks (monitor) → BuildDataset → GetDataset (download)
```

---

## Error Reference

| Error | Cause | Fix |
|-------|-------|-----|
| `401 Unauthorized` | Missing or invalid API key | Check `Authorization: Bearer` header |
| `500 Internal Server Error` | Server-side issue (often auth via gRPC) | Verify API key, retry |
| `DEADLINE_EXCEEDED` | Query timeout — miners can't fulfill request | Use broader date range, switch to keyword search |
| Empty `data` array | No matching results | Broaden search terms or date range |
