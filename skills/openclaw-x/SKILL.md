---
name: openclaw-x
version: 0.1.0
description: Control your X/Twitter account — view timeline, search tweets, post, like, retweet, bookmark.
---

# OpenClaw X

Control your X/Twitter account via a local API.

## Prerequisites

1. Download the executable from [GitHub Release](https://github.com/bosshuman/openclaw-x/releases)
2. Export your X cookies from Chrome (using Cookie-Editor extension), save as `cookies.json` in the same directory
3. Run the executable, ensure the service is running at `http://localhost:19816`

## Available Actions

### 1. Get Home Timeline

```bash
curl http://localhost:19816/timeline?count=20
```

Returns the latest tweets including content, author, media URLs, etc.

### 2. Get Tweet Details

```bash
curl http://localhost:19816/tweet/{tweet_id}
```

Supports both tweet ID and full URL (e.g. `https://x.com/user/status/123456`).

### 3. Search Tweets

```bash
curl "http://localhost:19816/search?q=keyword&sort=Latest&count=20"
```

Parameters:
- `q`: Search keyword (required)
- `sort`: `Latest` or `Top`, default Latest
- `count`: Number of results, default 20

### 4. Post a Tweet

```bash
curl -X POST http://localhost:19816/tweet \
  -H "Content-Type: application/json" \
  -d '{"text": "Hello world"}'
```

Reply to a tweet:

```bash
curl -X POST http://localhost:19816/tweet \
  -H "Content-Type: application/json" \
  -d '{"text": "Reply content", "reply_to": "original_tweet_id"}'
```

### 5. Like a Tweet

```bash
curl -X POST http://localhost:19816/tweet/{tweet_id}/like
```

### 6. Retweet

```bash
curl -X POST http://localhost:19816/tweet/{tweet_id}/retweet
```

### 7. Bookmark a Tweet

```bash
curl -X POST http://localhost:19816/tweet/{tweet_id}/bookmark
```

### 8. Get User Info

```bash
curl http://localhost:19816/user/{username}
```

Returns username, avatar, bio, follower count, etc.

### 9. Get User Tweets

```bash
curl http://localhost:19816/user/{username}/tweets?count=20
```

## Common Use Cases

1. "Show me what's new on my timeline"
2. "Search for the latest tweets about AI Agents"
3. "Post a tweet saying: What a beautiful day!"
4. "Like this tweet https://x.com/xxx/status/123"
5. "Check what @elonmusk has been posting"
6. "Bookmark this tweet"
