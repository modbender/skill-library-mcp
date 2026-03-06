---
name: twitter
description: "X/Twitter messaging management via API. Read tweets, post tweets, reply, send DMs, search, and view analytics. Use when the user wants to interact with X/Twitter: (1) posting or scheduling tweets, (2) reading timeline/mentions/DMs, (3) replying to tweets, (4) searching tweets/users/hashtags, (5) checking engagement analytics. Requires Twitter API credentials (API key, API secret, access token, access secret) or Bearer token."
---

# Twitter/X API Skill

Interact with X (Twitter) via API v2 for reading, posting, replying, DMs, search, and analytics.

## Setup

### Credentials

Store credentials in environment variables or `~/.config/twitter/credentials.json`:

```bash
export TWITTER_API_KEY="your-api-key"
export TWITTER_API_SECRET="your-api-secret"
export TWITTER_ACCESS_TOKEN="your-access-token"
export TWITTER_ACCESS_SECRET="your-access-secret"
export TWITTER_BEARER_TOKEN="your-bearer-token"  # For read-only operations
```

Or create credentials file:

```bash
mkdir -p ~/.config/twitter
cat > ~/.config/twitter/credentials.json << 'EOF'
{
  "api_key": "your-api-key",
  "api_secret": "your-api-secret",
  "access_token": "your-access-token",
  "access_secret": "your-access-secret",
  "bearer_token": "your-bearer-token"
}
EOF
chmod 600 ~/.config/twitter/credentials.json
```

### Install Dependencies

```bash
pip install tweepy
```

## Quick Reference

| Task | Command |
|------|---------|
| Post tweet | `{baseDir}/scripts/tweet.py post "text"` |
| Post with image | `{baseDir}/scripts/tweet.py post "text" --media image.png` |
| Reply | `{baseDir}/scripts/tweet.py reply TWEET_ID "text"` |
| Thread | `{baseDir}/scripts/tweet.py thread "tweet1" "tweet2" ...` |
| Get timeline | `{baseDir}/scripts/tweet.py timeline [--count 20]` |
| Get mentions | `{baseDir}/scripts/tweet.py mentions [--count 20]` |
| Get DMs | `{baseDir}/scripts/tweet.py dms [--count 20]` |
| Send DM | `{baseDir}/scripts/tweet.py dm USERNAME "message"` |
| Search | `{baseDir}/scripts/tweet.py search "query" [--count 20]` |
| User info | `{baseDir}/scripts/tweet.py user USERNAME` |
| Tweet info | `{baseDir}/scripts/tweet.py show TWEET_ID` |
| Analytics | `{baseDir}/scripts/tweet.py analytics TWEET_ID` |

## Scripts

### tweet.py

Main script for all Twitter operations. Run with `--help` for details:

```bash
{baseDir}/scripts/tweet.py --help
{baseDir}/scripts/tweet.py post --help
```

### Common Workflows

**Post a simple tweet:**

```bash
{baseDir}/scripts/tweet.py post "Hello, world!"
```

**Post with image:**

```bash
{baseDir}/scripts/tweet.py post "Check this out!" --media photo.png
{baseDir}/scripts/tweet.py post "Multiple images" --media img1.png --media img2.png
```

**Reply to a tweet:**

```bash
{baseDir}/scripts/tweet.py reply 1234567890 "Great point!"
```

**Post a thread:**

```bash
{baseDir}/scripts/tweet.py thread \
  "First tweet in thread" \
  "Second tweet" \
  "Third tweet"
```

**Read your mentions:**

```bash
{baseDir}/scripts/tweet.py mentions --count 50
```

**Search for tweets:**

```bash
{baseDir}/scripts/tweet.py search "openclaw agent" --count 20
{baseDir}/scripts/tweet.py search "#AI lang:en" --count 20
```

**Get user info:**

```bash
{baseDir}/scripts/tweet.py user elonmusk
```

**Send a DM:**

```bash
{baseDir}/scripts/tweet.py dm username "Hello from OpenClaw!"
```

**View tweet analytics:**

```bash
{baseDir}/scripts/tweet.py analytics 1234567890
```

## API Tiers & Limits

| Tier | Cost | Read | Write | Search |
|------|------|------|-------|--------|
| Free | $0 | Limited | - | - |
| Basic | $100/mo | 10k/mo | 1.5k/mo | 50/mo |
| Pro | $5000/mo | 1M/mo | 300k/mo | 500/mo |

**Free tier** can only post tweets (no read access to timeline/mentions).
**Basic tier** required for reading mentions, timeline, and search.
**Write-only operations** work on free tier.

See `{baseDir}/references/api-limits.md` for detailed rate limits.

## Error Handling

Common errors:

| Error | Cause | Solution |
|-------|-------|----------|
| 403 Forbidden | Insufficient tier | Upgrade API tier or check endpoint access |
| 429 Too Many Requests | Rate limit hit | Wait and retry; check rate limit headers |
| 401 Unauthorized | Invalid credentials | Verify API keys and tokens |
| 404 Not Found | Tweet/user deleted | Handle gracefully, inform user |
| 422 Unprocessable | Duplicate tweet | Wait before posting same content |

## Notes

- **Rate limits**: X API has strict rate limits. Scripts include retry logic.
- **Media uploads**: Images must be <5MB (PNG/JPG) or <15MB (GIF). Videos <512MB.
- **Character limit**: 280 characters per tweet. Threads for longer content.
- **DMs**: Require OAuth 1.0a user context (not Bearer token).
- **Search operators**: `{baseDir}/references/search-operators.md` for advanced queries.

## Related Files

- `{baseDir}/scripts/tweet.py` - Main CLI for all operations
- `{baseDir}/references/api-limits.md` - Detailed rate limits by endpoint
- `{baseDir}/references/search-operators.md` - Twitter search syntax