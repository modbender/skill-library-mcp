---
name: x-apify
version: 1.0.5
description: Fetch X/Twitter data via Apify actors. Search tweets, get user profiles, retrieve specific tweets with replies. Features local caching to save API costs. Works from any IP via Apify's proxy infrastructure.
tags: [twitter, x, apify, tweets, social-media, search, scraping, caching]
metadata: {"openclaw":{"requires":{"bins":["python3"],"env":{"APIFY_API_TOKEN":{"required":true,"description":"Apify API token from https://console.apify.com/account/integrations"},"APIFY_ACTOR_ID":{"required":false,"default":"quacker~twitter-scraper","description":"Apify actor ID to use (default: quacker~twitter-scraper)"},"X_APIFY_CACHE_DIR":{"required":false,"description":"Custom cache directory (default: .cache/ in skill dir)"}}}}}
---

# x-apify

Fetch X/Twitter data via Apify API (search tweets, user profiles, specific tweets).

## Why Apify?

X/Twitter's official API is expensive and restrictive. Apify provides reliable access to public tweet data through its actor ecosystem, with residential proxy support.

## Free Tier

- **$5/month free credits** (no credit card required)
- Cost varies by actor usage
- Perfect for personal use

## Links

- [Apify Pricing](https://apify.com/pricing)
- [Get API Key](https://console.apify.com/account/integrations)
- [Twitter Scraper Actor](https://apify.com/quacker/twitter-scraper)

## Setup

1. Create free Apify account: https://apify.com/
2. Get your API token: https://console.apify.com/account/integrations
3. Set environment variable:

```bash
# Add to ~/.bashrc or ~/.zshrc
export APIFY_API_TOKEN="apify_api_YOUR_TOKEN_HERE"

# Or use .env file (never commit this!)
echo 'APIFY_API_TOKEN=apify_api_YOUR_TOKEN_HERE' >> .env
```

## Usage

### Search Tweets

```bash
# Search for tweets containing keywords
python3 scripts/fetch_tweets.py --search "artificial intelligence"

# Search with hashtags
python3 scripts/fetch_tweets.py --search "#AI #MachineLearning"

# Limit results
python3 scripts/fetch_tweets.py --search "OpenAI" --max-results 10
```

### User Profiles

```bash
# Get tweets from a specific user
python3 scripts/fetch_tweets.py --user "elonmusk"

# Multiple users (comma-separated)
python3 scripts/fetch_tweets.py --user "OpenAI,AnthropicAI"
```

### Specific Tweet

```bash
# Get a specific tweet and its replies
python3 scripts/fetch_tweets.py --url "https://x.com/user/status/123456789"

# Also works with twitter.com URLs
python3 scripts/fetch_tweets.py --url "https://twitter.com/user/status/123456789"
```

### Output Formats

```bash
# JSON output (default)
python3 scripts/fetch_tweets.py --search "query" --format json

# Summary format (human-readable)
python3 scripts/fetch_tweets.py --search "query" --format summary

# Save to file
python3 scripts/fetch_tweets.py --search "query" --output results.json
```

### Caching

Tweets are cached locally by default to save API costs.

```bash
# First request: fetches from Apify (costs credits)
python3 scripts/fetch_tweets.py --search "query"

# Second request: uses cache (FREE!)
python3 scripts/fetch_tweets.py --search "query"
# Output: [cached] Results for: query

# Bypass cache (force fresh fetch)
python3 scripts/fetch_tweets.py --search "query" --no-cache

# View cache stats
python3 scripts/fetch_tweets.py --cache-stats

# Clear all cached results
python3 scripts/fetch_tweets.py --clear-cache
```

Cache TTL:
- Search results: 1 hour
- User profiles: 24 hours
- Specific tweets: 24 hours

Cache location: `.cache/` in skill directory (override with `X_APIFY_CACHE_DIR` env var)

## Output Examples

### JSON Format

```json
{
  "query": "OpenAI",
  "mode": "search",
  "fetched_at": "2026-02-11T10:30:00Z",
  "count": 20,
  "tweets": [
    {
      "id": "1234567890",
      "text": "OpenAI just announced...",
      "author": "techreporter",
      "author_name": "Tech Reporter",
      "created_at": "2026-02-11T09:00:00Z",
      "likes": 1500,
      "retweets": 300,
      "replies": 50,
      "url": "https://x.com/techreporter/status/1234567890"
    }
  ]
}
```

### Summary Format

```
=== X/Twitter Search Results ===
Query: OpenAI
Fetched: 2026-02-11 10:30:00 UTC
Results: 20 tweets

---
@techreporter (Tech Reporter)
2026-02-11 09:00
OpenAI just announced...
[Likes: 1500 | RTs: 300 | Replies: 50]
https://x.com/techreporter/status/1234567890

---
...
```

## Error Handling

The script handles common errors:
- Invalid search query
- User not found
- Tweet not found
- API quota exceeded
- Network errors

## Metadata

```yaml
metadata:
  openclaw:
    emoji: "X"
    requires:
      env:
        APIFY_API_TOKEN: required
        APIFY_ACTOR_ID: optional
        X_APIFY_CACHE_DIR: optional
      bins:
        - python3
```
