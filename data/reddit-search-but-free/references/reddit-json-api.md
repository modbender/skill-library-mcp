# Reddit JSON API Reference

Reddit exposes JSON data by appending `.json` to any `old.reddit.com` URL.

## Base URL
`https://old.reddit.com`

## Auth
None required. Set `User-Agent` header to avoid 429 errors.

## Endpoints

### Search
- `GET /search.json?q=<query>&sort=<sort>&t=<time>&limit=<n>`
- `GET /r/<sub>/search.json?q=<query>&restrict_sr=on&sort=<sort>&t=<time>`

Sort: `relevance`, `hot`, `top`, `new`, `comments`
Time: `hour`, `day`, `week`, `month`, `year`, `all`

### Subreddit Feeds
- `GET /r/<sub>/hot.json?limit=<n>`
- `GET /r/<sub>/new.json?limit=<n>`
- `GET /r/<sub>/rising.json?limit=<n>`
- `GET /r/<sub>/top.json?t=<time>&limit=<n>`
- `GET /r/<sub>/controversial.json?t=<time>&limit=<n>`

### Multi Feed
- `GET /r/<sub1>+<sub2>+<sub3>/hot.json?limit=<n>`

### Thread + Comments
- `GET /r/<sub>/comments/<post_id>.json?sort=<sort>&limit=<n>&depth=<n>`

Comment sort: `top`, `best`, `new`, `controversial`, `old`, `qa`

### Subreddit Info
- `GET /r/<sub>/about.json`

### User
- `GET /user/<name>/about.json` — profile
- `GET /user/<name>.json` — overview (posts + comments)
- `GET /user/<name>/submitted.json` — posts only
- `GET /user/<name>/comments.json` — comments only

### Subreddit Discovery
- `GET /subreddits/search.json?q=<query>&limit=<n>`
- `GET /subreddits/popular.json?limit=<n>`

### Duplicates
- `GET /duplicates/<post_id>.json`

### Wiki
- `GET /r/<sub>/wiki/<page>.json`

## Pagination
All listing endpoints return `after` token for pagination:
`GET /r/<sub>/hot.json?after=<token>&limit=25`

## Rate Limits
- ~60 req/min without auth
- 429 status = rate limited (retry with backoff)
- `User-Agent` header required

## Response Format
All endpoints return Listing objects:
```json
{
  "kind": "Listing",
  "data": {
    "children": [{ "kind": "t3", "data": { ... } }],
    "after": "t3_abc123",
    "dist": 25
  }
}
```

Kind prefixes: `t1` = comment, `t2` = account, `t3` = link/post, `t4` = message, `t5` = subreddit
