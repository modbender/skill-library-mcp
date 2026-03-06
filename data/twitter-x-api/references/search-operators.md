# Twitter Search Operators

## Basic Operators

| Operator | Example | Description |
|----------|---------|-------------|
| keyword | openclaw | Contains "openclaw" |
| "exact phrase" | "openclaw agent" | Exact phrase match |
| -exclude | openclaw -spam | Excludes tweets with "spam" |
| OR | openclaw OR "ai agent" | Match either term |

## User Operators

| Operator | Example | Description |
|----------|---------|-------------|
| from:user | from:openclaw_ai | Tweets from @openclaw_ai |
| to:user | to:elonmusk | Replies to @elonmusk |
| @user | @openclaw_ai | Mentions @openclaw_ai |

## Content Operators

| Operator | Example | Description |
|----------|---------|-------------|
| has:media | has:media | Contains media (image/video) |
| has:images | has:images | Contains images |
| has:videos | has:videos | Contains videos |
| has:links | has:links | Contains links |
| has:mentions | has:mentions | Contains @mentions |
| has:hashtags | has:hashtags | Contains hashtags |
| url:domain | url:github.com | Links to github.com |

## Engagement Operators

| Operator | Example | Description |
|----------|---------|-------------|
| min_retweets:N | min_retweets:100 | At least 100 retweets |
| min_faves:N | min_faves:50 | At least 50 likes |
| min_replies:N | min_replies:10 | At least 10 replies |

## Language & Location

| Operator | Example | Description |
|----------|---------|-------------|
| lang:code | lang:en | English tweets |
| lang:de | lang:de | German tweets |
| place:country | place:US | Tweets from USA |
| place:city | place:London | Tweets from London |
| near:city | near:Berlin | Geo-tagged near Berlin |
| within:radius | within:10km | Within radius of location |

## Time Operators

| Operator | Example | Description |
|----------|---------|-------------|
| since:YYYY-MM-DD | since:2024-01-01 | After this date |
| until:YYYY-MM-DD | until:2024-12-31 | Before this date |

## Type Operators

| Operator | Example | Description |
|----------|---------|-------------|
| is:retweet | is:retweet | Only retweets |
| is:quote | is:quote | Only quote tweets |
| is:reply | is:reply | Only replies |
| is:verified | is:verified | From verified accounts |

## Combining Operators

Build complex queries by combining operators:

```
# AI tweets from verified users with 100+ likes
"AI agent" is:verified min_faves:100 lang:en

# Recent tweets about OpenClaw with images
openclaw has:images since:2024-01-01

# Threads (replies from same user)
from:user is:reply to:user
```

## Query Limits

- Maximum query length: 512 characters
- Maximum operators: 50 (varies by tier)
- Boolean operators: AND, OR, NOT (also `-`)

## Common Patterns

### Find viral content
```
"topic" min_retweets:1000 min_faves:5000
```

### Find questions
```
"topic" ?
```

### Find original content (no retweets)
```
"topic" -is:retweet
```

### Find threads
```
from:username is:reply to:username
```

### Find recent news
```
"topic" has:links since:2024-01-15 lang:en
```

## Notes

- Search requires Basic tier or higher
- `search_recent_tweets`: Last 7 days (Basic tier)
- `search_all_tweets`: Full archive (Pro tier)
- Operators are case-insensitive
- Parentheses for grouping: `(openclaw OR "AI agent") -spam`