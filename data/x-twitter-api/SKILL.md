---
name: x-twitter
description: X (Twitter) API client for searching tweets, retrieving article content, and fetching trending topics. Supports both Bearer Token (app-only) and OAuth 2.0 authentication.
homepage: https://developer.x.com
metadata: { "openclaw": { "emoji": "𝕏", "requires": { "bins": ["python3"] }, "env": ["X_BEARER_TOKEN"], "primaryEnv": "X_BEARER_TOKEN" } }
---

# X (Twitter) API

Search tweets, retrieve article content, and fetch trending topics from X (Twitter).

## Features

- **Search Tweets**: Search recent tweets (last 7 days) with advanced query operators
- **Get Article Content**: Retrieve tweet and article details by URL or ID
- **Trending Topics**: Fetch trending topics (requires Basic tier or higher)
- **User Info**: Get user profile and tweet history

## Setup

```bash
# Set environment variable
export X_BEARER_TOKEN="your_bearer_token_here"

# Or temporarily for this session
X_BEARER_TOKEN="your_token" python3 scripts/search_tweets.py
```

**Get API Token:**
1. Visit https://developer.x.com
2. Create a project and app
3. Generate Bearer Token in "Keys and Tokens" tab
4. Set the environment variable

## Usage

### Search Tweets
```bash
# Basic search
python3 scripts/search_tweets.py --query "AI OR 人工智能"

# Advanced search (Chinese original tweets only)
python3 scripts/search_tweets.py --query "AI -is:retweet lang:zh" --count 10

# Search by user
python3 scripts/search_tweets.py --query "from:elonmusk" --count 5

# Search hashtags
python3 scripts/search_tweets.py --query "#Crypto OR #Blockchain"
```

**Query Operators:**
- `-is:retweet` - Original tweets only
- `lang:zh` - Chinese language
- `from:username` - Tweets from specific user
- `has:links` - Tweets with links
- `is:verified` - Verified users only

### Get Article/Tweet Content
```bash
# By URL (article or tweet)
python3 scripts/get_article.py --url "https://x.com/username/article/123456789"

# By Tweet ID
python3 scripts/get_article.py --id "123456789"
```

### Get Trending Topics
```bash
# Global trends
python3 scripts/get_trends.py

# Trends by WOEID (Yahoo Where On Earth ID)
python3 scripts/get_trends.py --woeid 1  # Global
python3 scripts/get_trends.py --woeid 23424977  # USA
```

## API Limits

| Tier | Cost | Tweets/Month | Notes |
|------|------|--------------|-------|
| Free | $0 | 500 | 1 request/day, testing only |
| Basic | $200 | 500,000 | Minimum production tier |
| Pro | $5,000 | 2,000,000+ | Real-time streaming |

**Free tier restrictions:**
- 500 tweets/month (~16-17/day)
- 1 request/day per endpoint
- No publishing/liking
- Suitable for development testing only

## Output Formats

- **JSON**: Structured data with all fields
- **Pretty**: Human-readable formatted text
- **Save**: Optional file export (JSON/Markdown)

## Error Handling

The scripts automatically handle:
- Rate limiting (429 errors)
- Invalid tokens (401 errors)
- Network errors with retry logic
- Missing required parameters

## Examples

### Example 1: Search AI tweets
```bash
python3 scripts/search_tweets.py --query "AI OR 人工智能 -is:retweet" --count 5 --output pretty
```

### Example 2: Monitor specific user
```bash
python3 scripts/search_tweets.py --query "from:username" --count 10 --save output.json
```

### Example 3: Get article and analyze
```bash
python3 scripts/get_article.py --url "https://x.com/user/article/id" --output markdown --save article.md
```
