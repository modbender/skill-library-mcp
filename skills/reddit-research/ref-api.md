# Reddit API Reference

## The /.json Trick

Append `/.json` to any Reddit URL for full thread JSON with all replies to n-th depth. No API key, no auth, no rate limit (within reason).

```
# Any subreddit feed
https://www.reddit.com/r/thetagang/.json
https://www.reddit.com/r/thetagang/new/.json
https://www.reddit.com/r/thetagang/hot/.json
https://www.reddit.com/r/thetagang/top/.json?t=week

# Any specific thread — gets ALL comments
https://www.reddit.com/r/thetagang/comments/[post_id]/[slug]/.json

# With parameters
?limit=25        # number of posts (max 100)
?t=hour          # time filter: hour, day, week, month, year, all
?sort=top        # sort: hot, new, top, controversial
```

## Response Structure

```json
{
  "data": {
    "children": [
      {
        "data": {
          "title": "Post title",
          "selftext": "Post body",
          "score": 142,
          "url": "...",
          "permalink": "/r/thetagang/comments/...",
          "num_comments": 23,
          "created_utc": 1234567890
        }
      }
    ]
  }
}
```

For thread /.json, response is an array: `[post_data, comments_data]`. Comments are nested recursively under `replies`.

## Rate Limiting

Reddit's unofficial API allows roughly 1 request/second without auth. Space requests by 1-2 seconds when fetching multiple feeds. If you hit a 429, wait 60 seconds before retrying.

## Fallback If /.json Fails

1. Try fetching the mobile URL: `https://i.reddit.com/r/[subreddit]/new/`
2. Try web search: `site:reddit.com/r/[subreddit] [topic]`
3. Use Reddit MCP server if configured

## Reddit MCP (When Available)

If `reddit-mcp` auth profile is active, use MCP tools for deeper access:
- Thread reading with full comment trees
- Search within subreddits
- User post history (for researching what's already been covered)

MCP complements /.json — use /.json for bulk feed scanning, MCP for deep thread reads.
