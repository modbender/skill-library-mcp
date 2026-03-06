# X (Twitter) API Skill

OpenClaw skill for accessing X (Twitter) API v2.

## Overview

This skill provides scripts to interact with X (Twitter) API for:
- **Search**: Query recent tweets with advanced filters
- **Articles**: Retrieve tweet/article content by URL or ID
- **Trends**: Fetch trending topics
- **Users**: Get user profiles and tweets

## Prerequisites

- Python 3.6+
- X (Twitter) Developer account
- Bearer Token (Basic tier recommended for production)

## Installation

The skill should be installed in:
```
~/.openclaw/workspace/skills/x-twitter/
```

## Configuration

Set the `X_BEARER_TOKEN` environment variable:

```bash
# Add to ~/.bashrc or ~/.zshrc
export X_BEARER_TOKEN="your_bearer_token_here"

# Reload
source ~/.bashrc
```

## Scripts

### scripts/search_tweets.py
Search recent tweets (last 7 days).

**Usage:**
```bash
python3 scripts/search_tweets.py --query "your query" --count 10
```

**Options:**
- `--query`: Search query with operators (required)
- `--count`: Number of results (default: 10, max: 100)
- `--output`: Output format (json|pretty) (default: pretty)
- `--save`: Save results to file

**Example:**
```bash
python3 scripts/search_tweets.py \
  --query "AI OR 人工智能 -is:retweet lang:zh" \
  --count 5 \
  --output pretty
```

### scripts/get_article.py
Retrieve article/tweet content by URL or ID.

**Usage:**
```bash
# By URL
python3 scripts/get_article.py --url "https://x.com/user/article/id"

# By ID
python3 scripts/get_article.py --id "123456789"
```

**Options:**
- `--url`: Article/tweet URL
- `--id`: Tweet ID (alternative to URL)
- `--output`: Output format (json|pretty|markdown) (default: pretty)
- `--save`: Save results to file

### scripts/get_trends.py
Fetch trending topics.

**Usage:**
```bash
python3 scripts/get_trends.py --woeid 1
```

**Options:**
- `--woeid`: Yahoo Where On Earth ID (default: 1 for Global)
  - 1 = Global
  - 23424977 = USA
  - 23424975 = UK

**Note:** Trending topics require Basic tier or higher.

## API Pricing

| Plan | Cost | Requests/Month | Tweets/Month |
|------|------|----------------|--------------|
| Free | $0 | Limited | 500 |
| Basic | $200 | 15,000 | 500,000 |
| Pro | $5,000 | 1,000,000 | 2,000,000+ |

## Common Issues

### "Unauthorized" (401)
- Check Bearer Token is correct
- Ensure token hasn't been revoked

### "Rate limit exceeded" (429)
- Free tier: 1 request/day per endpoint
- Wait 24 hours or upgrade to Basic tier

### "Forbidden" (403)
- Your account tier doesn't support this endpoint
- Trending topics require Basic tier or higher

## Query Operators Reference

| Operator | Description | Example |
|----------|-------------|---------|
| `from:user` | Tweets from user | `from:elonmusk` |
| `to:user` | Replies to user | `to:openai` |
| `-is:retweet` | Original tweets only | `AI -is:retweet` |
| `lang:xx` | Language code | `lang:zh` |
| `has:links` | Has URL | `has:links` |
| `is:verified` | Verified users | `is:verified AI` |
| `#hashtag` | Hashtag | `#Crypto` |

## Support

- X API Docs: https://docs.x.com
- Get API Key: https://developer.x.com
- Skill Issues: Check script error messages first

## Changelog

### 1.0.0 (2026-02-13)
- Initial release
- Search tweets functionality
- Get article content
- Get trending topics
