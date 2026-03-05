---
description: Schedule and automate social media posts to X/Twitter with cron-based queue management.
---

# SNS Auto Poster

Automated social media posting with cron scheduling and queue management.

## Requirements

- Python 3.8+
- `requests` library (`pip install requests`)
- Platform API credentials (see Configuration)
- OpenClaw cron (for scheduling)

## Quick Start

```bash
# Add a post to the queue
python3 {skill_dir}/poster.py add --platform x --text "Hello world!" --schedule "2025-01-15 09:00"

# Add with image
python3 {skill_dir}/poster.py add --platform x --text "Check this out" --image /path/to/img.png

# Process pending posts now
python3 {skill_dir}/poster.py run

# List queued posts
python3 {skill_dir}/poster.py list

# Clear completed posts
python3 {skill_dir}/poster.py clean
```

## Cron Setup

```bash
# Process queue every 15 minutes
openclaw cron add --schedule "*/15 * * * *" --command "python3 {skill_dir}/poster.py run"

# Daily morning post from template
openclaw cron add --schedule "0 9 * * *" --command "python3 {skill_dir}/poster.py run-template morning"
```

## Configuration

### Required Environment Variables

| Variable | Platform | Description |
|----------|----------|-------------|
| `X_CONSUMER_KEY` | X/Twitter | API Consumer Key |
| `X_CONSUMER_SECRET` | X/Twitter | API Consumer Secret |
| `X_ACCESS_TOKEN` | X/Twitter | OAuth Access Token |
| `X_ACCESS_TOKEN_SECRET` | X/Twitter | OAuth Access Token Secret |

Store in `~/.openclaw/secrets.env` — never commit to git.

### Post Queue (`queue.json`)

```json
[{"id": "uuid", "platform": "x", "text": "Hello!", "image": null, "schedule": "2025-01-15T09:00:00", "status": "pending"}]
```

### Templates (`templates/morning.json`)

```json
{"platform": "x", "text": "☀️ Good morning! Today is {date}. {custom_message}", "schedule_time": "09:00"}
```

## Supported Platforms

| Platform | Status | Auth |
|----------|--------|------|
| X (Twitter) | ✅ Ready | OAuth 1.0a |
| Bluesky | 🔜 Planned | App Password |
| Mastodon | 🔜 Planned | OAuth 2.0 |

## Edge Cases & Troubleshooting

- **Duplicate posts**: X API rejects identical tweets within a short window. Add a timestamp or vary text.
- **Rate limits**: X allows ~300 tweets/3 hours. The queue processor respects this.
- **Image too large**: X max image size is 5MB. Compress before posting.
- **Expired tokens**: If posting fails with 401, tokens need regeneration at developer.x.com.
- **Queue corruption**: If `queue.json` is malformed, back it up and recreate.
- **Missed schedule**: Posts scheduled in the past are posted on next `run` — they don't expire.

## Security

- **Never log or display API credentials** in output.
- Store credentials in `secrets.env` with `chmod 600`.
- Validate post content before sending (check character limits: X=280 chars).
- Review queued posts before enabling automated cron processing.
