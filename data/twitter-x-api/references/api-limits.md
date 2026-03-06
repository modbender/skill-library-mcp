# Twitter API v2 Rate Limits

## Endpoint Limits by Tier

### Free Tier ($0/month)

| Endpoint | Limit | Window |
|----------|-------|--------|
| Post tweet | 50 | 24 hours |
| Delete tweet | 50 | 24 hours |
| Get user info | 25 | 15 minutes |

**Note:** No read access to timeline, mentions, or search on Free tier.

### Basic Tier ($100/month)

| Endpoint | Limit | Window |
|----------|-------|--------|
| Post tweet | 1,500 | 24 hours |
| Delete tweet | 1,500 | 24 hours |
| Get timeline | 60 | 15 minutes |
| Get mentions | 60 | 15 minutes |
| Search recent tweets | 60 | 15 minutes |
| Get user info | 60 | 15 minutes |
| Get tweet info | 60 | 15 minutes |

### Pro Tier ($5,000/month)

| Endpoint | Limit | Window |
|----------|-------|--------|
| Post tweet | 300,000 | 24 hours |
| Get timeline | 900 | 15 minutes |
| Get mentions | 900 | 15 minutes |
| Search recent tweets | 900 | 15 minutes |
| Search full archive | 300 | 15 minutes |
| Get user info | 900 | 15 minutes |

## Monthly Tweet Caps

| Tier | Posts/Month |
|------|-------------|
| Free | 1,500 |
| Basic | 3,000 |
| Pro | 300,000 |

## Rate Limit Headers

Twitter includes these headers in responses:

- `x-rate-limit-limit`: Maximum requests per window
- `x-rate-limit-remaining`: Requests remaining in window
- `x-rate-limit-reset`: Unix timestamp when limit resets

## Handling Rate Limits

```python
import time
import tweepy

def with_retry(func, max_retries=3):
    for attempt in range(max_retries):
        try:
            return func()
        except tweepy.errors.TooManyRequests as e:
            reset = int(e.response.headers.get('x-rate-limit-reset', 0))
            wait = max(reset - time.time(), 60)
            print(f"Rate limited. Waiting {wait:.0f}s...")
            time.sleep(wait)
    raise Exception("Max retries exceeded")
```

## Best Practices

1. **Cache results** - Don't re-fetch the same data repeatedly
2. **Use Bearer token** for read-only operations (doesn't consume user quota)
3. **Batch operations** - Combine multiple lookups into single requests
4. **Monitor headers** - Track remaining limits proactively
5. **Implement backoff** - Exponential backoff for rate limit errors

## Error Codes

| Code | Meaning | Action |
|------|---------|--------|
| 429 | Rate limit exceeded | Wait for reset, retry |
| 403 | Forbidden (tier issue) | Check API access, upgrade tier |
| 401 | Unauthorized | Verify credentials |
| 404 | Not found | Tweet/user deleted or private |
| 422 | Unprocessable | Duplicate tweet, wait before reposting |