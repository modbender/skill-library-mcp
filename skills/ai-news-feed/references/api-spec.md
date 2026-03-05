# AI News Feed API — Response Schemas

## Post Object

Every feed/trending/account-posts endpoint returns an array of Post objects:

```json
{
  "id": "2027386252555919386",
  "content": "We have raised a $110 billion round of funding from Amazon, NVIDIA, and SoftBank.",
  "summary": "该公司从亚马逊、英伟达和软银处获得了1100亿美元的融资。",
  "description": "该公司宣布已从亚马逊、英伟达和软银处筹集了高达1100亿美元的资金。这笔巨额投资表明了对该公司愿景和能力的强烈信心。",
  "tags": ["funding"],
  "importance": 9,
  "media": [],
  "metrics": {
    "likes": 38942,
    "retweets": 2651,
    "replies": 4123,
    "views": 8440977
  },
  "tweetUrl": "https://x.com/sama/status/2027386252555919386",
  "tweetedAt": "2026-02-27T14:12:04.000Z",
  "account": {
    "handle": "sama",
    "name": "Sam Altman",
    "category": "researcher"
  }
}
```

### Field Reference

| Field | Type | Description |
|---|---|---|
| `id` | string | Tweet ID |
| `content` | string | Original tweet text (always English, as posted) |
| `summary` | string \| null | One-line LLM summary. Language depends on `lang` query param. |
| `description` | string \| null | Detailed 2-4 sentence LLM analysis. Language depends on `lang` param. May be null for older posts. |
| `tags` | string[] | Topic classification tags. Possible values: `paper`, `product_launch`, `model_release`, `funding`, `opinion`, `tutorial`, `benchmark`, `open_source`, `regulation`, `industry` |
| `importance` | integer | Composite score 1-10. Combines LLM importance (40%) + absolute engagement (30%) + relative engagement vs account baseline (30%). |
| `media` | string[] | Array of media URLs (images/videos) attached to the tweet. |
| `metrics.likes` | integer | Like count |
| `metrics.retweets` | integer | Retweet count |
| `metrics.replies` | integer | Reply count |
| `metrics.views` | integer | View/impression count |
| `tweetUrl` | string | Direct link to original tweet on X/Twitter |
| `tweetedAt` | string | ISO 8601 timestamp of when the tweet was posted **(always UTC with `Z` suffix — convert to user's local timezone before displaying)** |
| `account.handle` | string | Twitter handle (without @) |
| `account.name` | string | Display name |
| `account.category` | string | One of: `official`, `researcher`, `media`, `kol` |

## Feed Response — `GET /v1/feed`

```json
{
  "items": [Post, ...],
  "count": 20,
  "offset": 0,
  "lang": "en"
}
```

## Trending Response — `GET /v1/feed/trending`

```json
{
  "items": [Post, ...],
  "hours": 24,
  "count": 10,
  "lang": "en"
}
```

## Accounts Response — `GET /v1/accounts`

```json
{
  "items": [
    { "handle": "OpenAI", "name": "OpenAI", "category": "official" },
    { "handle": "karpathy", "name": "Andrej Karpathy", "category": "researcher" }
  ],
  "count": 57
}
```

## Account Posts Response — `GET /v1/accounts/{handle}/posts`

```json
{
  "account": { "handle": "karpathy", "name": "Andrej Karpathy", "category": "researcher" },
  "items": [Post, ...],
  "count": 20,
  "offset": 0,
  "lang": "en"
}
```

## Tags Response — `GET /v1/tags`

```json
{
  "items": [
    { "tag": "model_release", "count": 142 },
    { "tag": "product_launch", "count": 98 },
    { "tag": "funding", "count": 45 }
  ]
}
```

## Importance Score Breakdown

The `importance` field (1-10) is a composite of three signals:

- **LLM importance (40%)**: How newsworthy the content is, scored by Gemini
- **Absolute engagement (30%)**: Raw likes/views compared to all posts (log-normalized)
- **Relative engagement (30%)**: How this post compares to the same account's median engagement

This means a small researcher's viral post can score higher than a routine corporate announcement, even if the corporate post has more absolute engagement.

## Available Tags

| Tag | Description |
|---|---|
| `paper` | Academic paper, research result |
| `model_release` | New model released or updated |
| `product_launch` | New product or feature launch |
| `funding` | Investment, fundraising, acquisition |
| `opinion` | Commentary, analysis, hot take |
| `tutorial` | How-to, guide, educational content |
| `benchmark` | Performance comparison, leaderboard |
| `open_source` | Open-source release or contribution |
| `regulation` | Policy, law, government action related to AI |
| `industry` | General industry news, partnerships, hiring |
