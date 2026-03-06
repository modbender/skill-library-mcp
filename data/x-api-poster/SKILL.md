---
name: x-api-poster
description: Post tweets to X/Twitter via API v2 with OAuth 1.0a — text, images,
  replies, and threads.
---


# X API Poster

Post to X (Twitter) using the official API v2 with OAuth 1.0a authentication.

## Requirements

- Python 3.8+
- `requests` library (`pip install requests`)
- X API credentials (Consumer Key/Secret + Access Token/Secret)

## Quick Start

```bash
# Post a tweet
python3 {skill_dir}/post.py "Hello from OpenClaw!"

# Post with image
python3 {skill_dir}/post.py "Check this out" /path/to/image.png

# Reply to a tweet
python3 {skill_dir}/post.py "Reply text" 1234567890123456789

# Reply with image
python3 {skill_dir}/post.py "Reply with pic" 1234567890123456789 /path/to/image.png
```

## Configuration

### Required Environment Variables

| Variable | Description |
|----------|-------------|
| `X_CONSUMER_KEY` | API Consumer Key |
| `X_CONSUMER_SECRET` | API Consumer Secret |
| `X_ACCESS_TOKEN` | OAuth 1.0a Access Token |
| `X_ACCESS_TOKEN_SECRET` | OAuth 1.0a Access Token Secret |

Store in `~/.openclaw/secrets.env` with `chmod 600`.

### Getting API Keys

1. Visit [developer.x.com](https://developer.x.com/)
2. Create a project and app
3. Enable OAuth 1.0a with **Read and Write** permissions
4. Generate Consumer Keys and Access Tokens
5. Add to `~/.openclaw/secrets.env`

## API Details

- **Post**: `POST https://api.twitter.com/2/tweets` (v2)
- **Media upload**: `POST https://upload.twitter.com/1.1/media/upload.json` (v1.1)
- **Auth**: OAuth 1.0a with HMAC-SHA1 signature (built-in, no external OAuth library needed)

## Edge Cases & Troubleshooting

- **280 char limit**: Validate text length before posting. URLs count as ~23 chars (t.co wrapping).
- **Duplicate tweet**: X rejects identical tweets in quick succession. Vary the text or wait.
- **Image format**: Supports PNG, JPEG, GIF, WEBP. Max 5MB for images, 15MB for GIFs.
- **401 Unauthorized**: Tokens expired or permissions insufficient. Regenerate at developer.x.com.
- **403 Forbidden**: App may need elevated access. Check project tier.
- **429 Rate limited**: Free tier allows ~50 tweets/24h. Back off and retry after `x-rate-limit-reset` header.
- **Missing env vars**: Script should check all 4 vars exist before attempting to post. Fail with clear error.

## Security

- **Never log or display API credentials** — mask in any error output.
- Store credentials in `secrets.env` with `chmod 600`, never in code or git.
- Validate tweet content before posting (no accidental credential leaks).
- Review posts before sending — automated posting should have human approval.
