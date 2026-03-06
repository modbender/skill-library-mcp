---
name: x-oauth-api
description: Post to X (Twitter) using the official OAuth 1.0a API. Free tier compatible.
metadata:
  { "openclaw": { "requires": { "env": ["X_API_KEY", "X_API_SECRET", "X_ACCESS_TOKEN", "X_ACCESS_TOKEN_SECRET"] } } }
---

# X OAuth API Skill

Post to X (formerly Twitter) using the official X API with OAuth 1.0a authentication.

## Overview

This skill provides direct access to X API v2 for posting tweets, managing threads, and monitoring mentions. No proxy or third-party service required — uses your X API credentials directly.

**Use when:**
- User says "post to X", "tweet this", "post on Twitter"
- Need to create threads or media posts
- Want to check mentions or engage with replies

## Quick Start

### 1. Configure X API Credentials

Store these environment variables (from your X Developer Account):
```
X_API_KEY              # Consumer Key (API Key)
X_API_SECRET           # Consumer Secret
X_ACCESS_TOKEN         # Access Token
X_ACCESS_TOKEN_SECRET  # Access Token Secret
X_USER_ID              # Optional: Your numeric user ID (speeds up mentions)
```

### Free Tier vs Paid Tier

**Free tier supports:**
- ✅ Posting tweets and threads
- ✅ Deleting tweets
- ✅ Account info lookup (`x me`)

**Requires Basic+ tier:**
- 🔒 Search tweets
- 🔒 Fetch mentions
- 🔒 Media uploads

### 2. Basic Usage

```bash
# Post a simple tweet
x post "Hello from X API"

# Post a thread
x thread "First tweet" "Second tweet" "Third tweet"

# Check mentions
x mentions --limit 10

# Search recent tweets
x search "AI agents" --limit 5
```

## Commands

### `x post <text>`
Post a single tweet.

**Options:**
- `--reply-to <tweet-id>` - Reply to a specific tweet
- `--quote <tweet-id>` - Quote tweet
- `--media <file>` - Attach image/video

**Example:**
```bash
x post "Check this out" --media image.jpg
```

### `x thread <tweet1> <tweet2> ...`
Post a tweet thread.

**Example:**
```bash
x thread \
  "Thread about AI" \
  "Here's what I learned" \
  "Most important takeaway"
```

### `x mentions [options]`
Get recent mentions of your account.

**Options:**
- `--limit <n>` - Number of mentions (default: 10, max: 100)
- `--since <tweet-id>` - Only mentions after this ID
- `--format json` - Output as JSON

**Note:** Requires `X_USER_ID` env var OR will fetch it automatically (slower).

### `x search <query> [options]`
Search recent tweets.

**Options:**
- `--limit <n>` - Number of results (default: 10, max: 100)
- `--format json` - Output as JSON

### `x delete <tweet-id>`
Delete a tweet.

### `x me`
Show current account info (name, username, follower counts, user ID).

## API Rate Limits

X API v2 has rate limits per endpoint:

| Endpoint | Limit | Window |
|----------|-------|--------|
| POST /2/tweets | 200 | 15 min (Free tier) |
| GET /2/tweets/search/recent | 100 | 15 min (Free tier) |
| GET /2/users/:id/mentions | 100 | 15 min (Free tier) |

Rate limits vary by access tier. See [X API documentation](https://developer.twitter.com/en/docs/twitter-api/rate-limits) for details.

## Authentication

OAuth 1.0a is handled transparently. Just provide your credentials via environment variables. The skill will sign all requests automatically.

## Examples

### Post with media
```bash
x post "Check out this screenshot" --media screenshot.png
```

### Reply to a tweet
```bash
x post "Great point!" --reply-to 1234567890123456789
```

### Create a 3-tweet thread
```bash
x thread \
  "Just launched x-oauth-api skill" \
  "It lets you post to X directly from your agent" \
  "No proxies, direct OAuth 1.0a authentication"
```

### Search and reply
```bash
# Find interesting tweets
x search "agent framework"

# Reply to one
x post "Have you tried this?" --reply-to 1234567890123456789
```

## Troubleshooting

**"Unauthorized" error**
- Check X API credentials are correct
- Verify credentials are set in environment
- Ensure your app has write permissions in X Developer Portal

**"Rate limit exceeded"**
- Wait 15 minutes for limit to reset
- Reduce request frequency
- Check your tier limits at https://developer.twitter.com/en/portal/dashboard

**"This endpoint requires a paid X API tier"**
- Search and mentions require Basic+ tier on X API
- Free tier only supports posting, deleting, and account lookup
- Upgrade at https://developer.twitter.com/en/portal/products

**Tweet not posting**
- Check tweet is < 280 characters (or < 4000 with X Premium)
- Verify no special formatting issues
- Check X API status at https://api.twitterstat.us/

## Requirements

- X Developer Account with API access
- OAuth 1.0a credentials configured
- Network access to api.twitter.com

## Cost

Free. X API is free for basic usage. Check your app's rate limits in X Developer Portal.

## Support

For X API issues, see: https://developer.twitter.com/en/docs/twitter-api
