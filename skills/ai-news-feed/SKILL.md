---
name: ai-news-feed
description: Query the AI News Feed API for real-time AI/ML news from 57+ curated Twitter/X accounts. Use when the user asks about AI news, trending AI topics, what's happening in AI/ML, or wants to build news-powered features. Provides pre-enriched bilingual (EN/ZH) summaries, importance scores, and topic tags via REST API hosted on RapidAPI.
---

# AI News Feed API

Query pre-aggregated, LLM-enriched AI/ML news from 57+ Twitter/X accounts. Data is updated every 2 hours.

## API Access & Setup

**Before making any API call**, check if the user has a RapidAPI key configured. If not, guide them through these steps:

1. **Sign up / Log in** at <https://rapidapi.com> (free)
2. **Subscribe** to the API at <https://rapidapi.com/jiachenfred/api/twitter-ai-news-feed> (free tier available, no credit card needed)
3. After subscribing, go to the API's **Endpoints** tab on RapidAPI — the `X-RapidAPI-Key` will be auto-filled in the code snippets on the right side. Copy it.
4. Store the key for future use (e.g. in an environment variable `RAPIDAPI_KEY`)

**All requests must include these headers:**
```
X-RapidAPI-Key: <user's own key from step 3>
X-RapidAPI-Host: twitter-ai-news-feed.p.rapidapi.com
```

**Base URL**: `https://twitter-ai-news-feed.p.rapidapi.com`

**Response format**: All endpoints return JSON. See [references/api-spec.md](references/api-spec.md) for full response schemas.

## Endpoints

### Get Feed — `GET /v1/feed`

Latest posts sorted by recency.

| Param | Type | Default | Description |
|---|---|---|---|
| `lang` | `en` \| `zh` | `en` | Response language |
| `limit` | 1-100 | 20 | Number of posts |
| `offset` | int | 0 | Pagination |
| `tags` | string | — | Comma-separated filter: `paper`, `model_release`, `funding`, `product_launch`, `opinion`, `tutorial`, `benchmark`, `open_source`, `regulation`, `industry` |
| `min_importance` | 1-10 | — | Minimum importance score |
| `since` | unix ts | — | Posts after this timestamp |

Example: `GET /v1/feed?lang=zh&limit=5&tags=model_release,paper&min_importance=7`

### Get Trending — `GET /v1/feed/trending`

Top posts ranked by importance within a time window.

| Param | Type | Default | Description |
|---|---|---|---|
| `lang` | `en` \| `zh` | `en` | Response language |
| `limit` | 1-50 | 10 | Number of posts |
| `hours` | 1-168 | 24 | Time window (168 = 7 days) |

Example: `GET /v1/feed/trending?lang=zh&hours=48&limit=10`

### Get Accounts — `GET /v1/accounts`

List all 57+ monitored accounts.

| Param | Type | Description |
|---|---|---|
| `category` | `official` \| `researcher` \| `media` \| `kol` | Filter by category |

### Get Account Posts — `GET /v1/accounts/{handle}/posts`

Posts from a specific account (e.g. `/v1/accounts/karpathy/posts`).

| Param | Type | Default | Description |
|---|---|---|---|
| `lang` | `en` \| `zh` | `en` | Response language |
| `limit` | 1-100 | 20 | Number of posts |
| `offset` | int | 0 | Pagination |

### Get Tags — `GET /v1/tags`

All tags with post counts. No parameters.

### Health Check — `GET /health`

Returns `{"status": "ok", "timestamp": "..."}`.

## Key Response Fields

Each post in the response contains:

- `content` — Original tweet text
- `summary` — One-line LLM summary (language follows `lang` param)
- `description` — Detailed 2-4 sentence LLM analysis (language follows `lang` param)
- `tags` — Array of topic tags
- `importance` — Score 1-10 (composite of LLM analysis + engagement metrics)
- `metrics` — `{likes, retweets, replies, views}`
- `tweetUrl` — Link to original tweet
- `tweetedAt` — ISO 8601 publish time **(UTC, convert to user's local timezone before displaying)**
- `account` — `{handle, name, category}`

For complete JSON schemas, see [references/api-spec.md](references/api-spec.md).

## Making Requests

Example curl (replace `YOUR_KEY` with the user's RapidAPI key):

```bash
curl "https://twitter-ai-news-feed.p.rapidapi.com/v1/feed/trending?lang=zh&limit=5" \
  -H "X-RapidAPI-Key: YOUR_KEY" \
  -H "X-RapidAPI-Host: twitter-ai-news-feed.p.rapidapi.com"
```

## Common Use Cases

1. **Get today's top AI news in Chinese**: `GET /v1/feed/trending?lang=zh&hours=24&limit=10`
2. **Find new model releases**: `GET /v1/feed?tags=model_release&min_importance=5`
3. **Track a specific researcher**: `GET /v1/accounts/karpathy/posts?lang=zh`
4. **Get funding news only**: `GET /v1/feed?tags=funding&min_importance=6`
5. **Weekly digest**: `GET /v1/feed/trending?hours=168&limit=20&lang=en`

## Monitored Account Categories

- **Official** (23): OpenAI, Anthropic, Google AI, Meta AI, NVIDIA, Hugging Face, Mistral, xAI, Stability AI, Runway, Perplexity, ElevenLabs, Cursor, Replit, etc.
- **Researcher** (13): Karpathy, Yann LeCun, Andrew Ng, Jeff Dean, Ilya Sutskever, Jim Fan, Demis Hassabis, Jeremy Howard, etc.
- **KOL** (12): Swyx, Simon Willison, Logan Kilpatrick, Emad Mostaque, Linus Ekenstam, etc.
- **Media** (9): MIT Tech Review, WIRED, The Verge, AI Breakfast, Ben's Bites, The Rundown AI, etc.
