---
name: publer-post
description: Post content to social media via the Publer API. Use when scheduling or publishing posts to TikTok (carousels, videos), Instagram, Facebook, Twitter/X, or any Publer-supported platform. Handles media upload, post creation, scheduling, and job polling. Use for any task involving "post to TikTok", "schedule a post", "publish to social media", or "upload to Publer".
metadata:
  openclaw:
    emoji: 📱
    requires:
      bins: ["python3"]
      env: ["PUBLER_API_KEY", "PUBLER_WORKSPACE_ID"]
      packages: ["requests"]
    primaryEnv: PUBLER_API_KEY
    install:
      - id: python-requests
        kind: pip
        package: requests
        label: Install Python requests library
---

# Publer Post

Post and schedule social media content via the Publer API.

## Prerequisites

**Python Dependencies:**
```bash
pip install -r requirements.txt
```

**Environment Variables** (store in TOOLS.md or set before running):
- `PUBLER_API_KEY` — API key from Publer (Business plan required)
- `PUBLER_WORKSPACE_ID` — Your workspace ID
- `PUBLER_TIKTOK_ACCOUNT_ID` — TikTok account ID (optional, get via `accounts` command)

## Script: `scripts/publer.py`

### List accounts
```bash
python3 scripts/publer.py accounts
```
Use this first to discover account IDs.

### Upload media
```bash
python3 scripts/publer.py upload slide_1.jpg slide_2.jpg slide_3.jpg
```
Returns media IDs (one per line as JSON). Collect these for the post command.

### Post TikTok carousel (immediate)
```bash
python3 scripts/publer.py post \
  --account-id $PUBLER_TIKTOK_ACCOUNT_ID \
  --type photo \
  --title "Post title (max 90 chars)" \
  --text "Caption with #hashtags" \
  --media-ids id1,id2,id3,id4,id5,id6,id7,id8
```

### Schedule TikTok carousel
```bash
python3 scripts/publer.py post \
  --account-id $PUBLER_TIKTOK_ACCOUNT_ID \
  --type photo \
  --title "Post title" \
  --text "Caption" \
  --media-ids id1,id2,id3 \
  --schedule "2025-06-01T09:00:00Z"
```

### Dry run (preview payload)
Add `--dry-run` to print the JSON payload without sending.

### Check job status
```bash
python3 scripts/publer.py job-status <job_id>
```

## Workflow: Post a TikTok Carousel

1. Upload all slide images → collect media IDs
2. Run `post` with `--type photo`, title, caption+hashtags, and comma-separated media IDs
3. Script polls job until complete — confirm success

## Options
- `--privacy`: PUBLIC_TO_EVERYONE (default), MUTUAL_FOLLOW_FRIENDS, FOLLOWER_OF_CREATOR, SELF_ONLY
- `--auto-music` / `--no-auto-music`: auto-add music to carousel (default: on)
- `--no-poll`: submit without waiting for completion

## API Reference
For full endpoint details, see [references/api.md](references/api.md).
