---
name: worthclip
description: "AI-powered YouTube video scoring. Scores videos 1-10 based on your learning goals and persona. Use when the user wants to evaluate YouTube videos, check their scored feed, manage tracked channels, or check API usage. Get AI summaries, alignment analysis, and a curated video feed. Keywords: YouTube, video, score, persona, feed, summary, AI, learning, channels. Requires a WorthClip API key from https://worthclip.com/developers."
license: MIT
homepage: https://worthclip.com
allowed-tools: Bash Read
disable-model-invocation: true
metadata: {"clawdbot":{"emoji":"bullseye","primaryEnv":"WORTHCLIP_API_KEY","requires":{"bins":["curl","jq"],"env":["WORTHCLIP_API_KEY"]}}}
---

# WorthClip - YouTube Video Scoring

Score YouTube videos 1-10 based on your personalized learning goals. Get AI-powered summaries, alignment analysis, and a curated feed.

## Setup

1. Sign up at https://worthclip.com
2. Go to Settings > API Keys
3. Generate an API key
4. Set it: `export WORTHCLIP_API_KEY="wc_your_key_here"`

## Commands

### Score a video

Scores a YouTube video against the user's persona and goals. Handles async scoring automatically with polling.

```bash
bash {baseDir}/scripts/score.sh "VIDEO_ID"
```

The script submits the video for scoring, polls for completion (up to 60 seconds), and returns the completed score JSON. If the video was already scored, it returns the existing score immediately.

### Get your feed

Returns scored videos sorted by relevance, with optional filters.

```bash
bash {baseDir}/scripts/feed.sh [--min-score N] [--verdict VERDICT] [--limit N] [--cursor N]
```

Options:
- `--min-score N` - Only return videos scored N or above (1-10)
- `--verdict VERDICT` - Filter by verdict (e.g., "watch", "skip")
- `--limit N` - Number of results per page
- `--cursor N` - Pagination cursor from previous response

### Check usage

Shows current billing period usage stats and limits.

```bash
bash {baseDir}/scripts/usage.sh
```

## API Reference

Base URL: `https://greedy-mallard-11.convex.site/api/v1`

The API is hosted on Convex (convex.site), WorthClip's serverless backend. The domain `greedy-mallard-11.convex.site` is WorthClip's production Convex deployment. You can verify this by visiting https://worthclip.com/developers.

All requests (except /health) require `Authorization: Bearer YOUR_API_KEY` header.

| Endpoint | Method | Description |
|----------|--------|-------------|
| /health | GET | Health check (no auth required) |
| /score | POST | Score a video (async, returns 202 with jobId) |
| /score/:jobId | GET | Poll scoring job status |
| /videos/:ytId/summary | GET | Get video summary (summarization) |
| /videos/:ytId | GET | Get video detail with full score |
| /feed | GET | Paginated scored feed with filters |
| /channels | GET | List tracked channels |
| /channels/lookup | POST | Lookup channel by YouTube URL |
| /channels/track | POST | Track a new channel |
| /persona | GET | Get current persona and goals |
| /persona | PUT | Update persona description |
| /goals | PUT | Update learning goals |
| /usage | GET | Current billing period usage stats |

## Rate Limits

- **General:** 60 requests/minute (all endpoints)
- **Scoring:** 20 requests/minute (POST /score and GET /score/:jobId)

Response headers:
- `X-RateLimit-Limit` - Maximum requests per window
- `X-RateLimit-Remaining` - Requests remaining in current window
- `Retry-After` - Seconds to wait before retrying (only on 429 responses)

## Error Format

All errors return a consistent JSON structure with an appropriate HTTP status code:

```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable description of the error"
  }
}
```

Common error codes:
- `UNAUTHORIZED` (401) - Missing or invalid API key
- `RATE_LIMITED` (429) - Too many requests
- `NOT_FOUND` (404) - Resource not found
- `VALIDATION_ERROR` (400) - Invalid request parameters
- `INTERNAL_ERROR` (500) - Server error

## Base URL

```
https://greedy-mallard-11.convex.site/api/v1
```
