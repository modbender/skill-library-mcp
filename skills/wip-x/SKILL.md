---
name: wip-x
version: 1.0.1
description: X Platform API. Read posts, search tweets, post, upload media.
homepage: https://github.com/wipcomputer/wip-x
metadata:
  category: social,api
  api_base: https://api.x.com/2
  capabilities:
    - api
    - fetch-posts
    - search-tweets
    - bookmarks
    - post-tweets
    - upload-media
  dependencies:
    - "@xdevplatform/xdk"
  interface: REST
openclaw:
  emoji: "🐦"
  install:
    env:
      - X_BEARER_TOKEN
      - X_API_KEY
      - X_API_SECRET
      - X_ACCESS_TOKEN
      - X_ACCESS_TOKEN_SECRET
author:
  name: Parker Todd Brooks
---

# wip-x

X Platform API. Sensor (read) + Actuator (write). All X Platform functions in one tool.

## When to Use This Skill

### Sensor: Read

**Use fetch_post for:**
- Getting the full content of a specific tweet by URL or ID
- Reading replies, quotes, engagement metrics
- Extracting tweet data for processing

**Use search_recent for:**
- Finding tweets matching a query (last 7 days)
- Searching by hashtags, mentions, or keywords
- Getting raw tweet data (not AI-summarized... use wip-grok search_x for that)

**Use get_bookmarks for:**
- Reading the user's bookmarked tweets
- Reviewing saved content

**Use get_user for:**
- Looking up a user's profile, bio, follower count
- Checking if an account exists

### Actuator: Write

**Use post_tweet for:**
- Posting new tweets
- Replying to existing tweets
- Quote-tweeting with commentary
- Posting with images or video (upload first)

**Use upload_media for:**
- Uploading images (PNG, JPG, GIF, WebP)
- Uploading video (MP4)
- Getting media IDs for use in post_tweet

**Use delete_tweet for:**
- Removing a previously posted tweet

**Use bookmark_post for:**
- Saving a tweet for later

### Do NOT Use For

- AI-powered search summarization (use wip-grok search_web or search_x instead)
- Image generation (use wip-grok generate_image)
- Video generation (use wip-grok generate_video)
- Trending topic analysis (use wip-grok search_x for AI-summarized trends)

## API Reference

### fetch_post(options)

```javascript
const result = await fetch_post({ id_or_url: 'https://x.com/user/status/123' });
// result: { data, includes, errors }
```

Options: id_or_url (required). Accepts tweet ID or full URL.

### search_recent(options)

```javascript
const result = await search_recent({ query: 'AI agents', max_results: 20 });
// result: { data, includes, meta, errors }
```

Options: query (required), max_results (10-100), start_time, end_time, sort_order

### get_bookmarks(options)

```javascript
const result = await get_bookmarks({ max_results: 20 });
```

Options: max_results, pagination_token. Requires OAuth.

### get_user(options)

```javascript
const result = await get_user({ username_or_id: 'parkertoddbrooks' });
```

Options: username_or_id (required). Accepts username (with or without @) or numeric ID.

### post_tweet(options)

```javascript
const result = await post_tweet({ text: 'Hello world', reply_to: '123', media_ids: ['456'] });
// result: { data: { id, text }, errors }
```

Options: text (required), reply_to, media_ids, quote_tweet_id. Requires OAuth.

### upload_media(options)

```javascript
const result = await upload_media({ file_path: './photo.jpg' });
// result: { data: { id }, errors }
```

Options: file_path (required), media_type (auto-detected), media_data (base64 alternative)

### delete_tweet(options)

```javascript
const result = await delete_tweet({ id: '123456' });
```

Options: id (required). Requires OAuth.

## Troubleshooting

### "X Platform API credentials not found"
Set X_BEARER_TOKEN for read-only, or all four OAuth tokens for read+write.
1Password: vault "Agent Secrets", item "X Platform API".

### "Could not resolve authenticated user ID"
Bookmarks and write operations need OAuth 1.0a (all four tokens), not just bearer token.

### 403 Forbidden on post/delete
Your app needs "Read and Write" permissions in the X Developer Portal. Check at https://developer.x.com/en/portal/dashboard

### Rate limits
X API v2 has per-endpoint rate limits. The SDK handles rate limit headers automatically. If you hit limits, back off and retry.

## API Documentation

- X API v2: https://docs.x.com/x-api
- XDK SDK: https://github.com/xdevplatform/xdk
- Authentication: https://docs.x.com/resources/authentication
