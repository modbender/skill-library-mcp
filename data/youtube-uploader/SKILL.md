---
name: youtube
description: Upload videos and custom thumbnails to YouTube. Use when the user wants to publish, upload, or post a video to YouTube, set a thumbnail, or manage YouTube channel authentication.
homepage: https://developers.google.com/youtube/v3
metadata:
  {
    "openclaw":
      {
        "emoji": "📺",
        "requires": { "bins": ["python3"] },
      },
  }
---

# YouTube Uploader

Upload videos with full metadata and custom thumbnails to YouTube via OAuth2.

## Setup (one-time)

The user needs a Google Cloud project with the YouTube Data API v3 enabled and an OAuth2 client ID (type "Desktop app"). Download the `client_secret.json` file.

### Authenticate

```bash
python3 {baseDir}/scripts/youtube-upload.py auth --client-secret /path/to/client_secret.json
```

This opens a browser for Google OAuth consent, then saves credentials to `~/.openclaw/youtube/channels.json`. Multiple channels can be authenticated by repeating the command with different Google accounts.

### List authenticated channels

```bash
python3 {baseDir}/scripts/youtube-upload.py channels
```

## Upload a video

```bash
python3 {baseDir}/scripts/youtube-upload.py upload \
  --file /path/to/video.mp4 \
  --title "Video Title" \
  --description "Video description" \
  --tags "tag1,tag2,tag3" \
  --category 22 \
  --privacy private \
  --channel-id UCxxxxxxxx
```

**Required**: `--file`, `--title`
**Optional**: `--description`, `--tags` (comma-separated), `--category` (default 22 = People & Blogs), `--privacy` (private/unlisted/public, default private), `--publish-at` (ISO 8601 for scheduled publish, requires privacy=private), `--made-for-kids`, `--channel-id` (uses first channel if omitted)

Returns JSON with `videoId` and `url`.

## Upload a custom thumbnail

```bash
python3 {baseDir}/scripts/youtube-upload.py thumbnail \
  --video-id VIDEO_ID \
  --file /path/to/thumbnail.jpg \
  --channel-id UCxxxxxxxx
```

Supports JPEG, PNG, BMP, GIF. Max 2MB per YouTube API. The channel must be verified for custom thumbnails.

## Refresh token manually

```bash
python3 {baseDir}/scripts/youtube-upload.py refresh --channel-id UCxxxxxxxx
```

## Workflow tips

- Always upload as `--privacy private` first, verify, then update privacy if needed.
- Upload thumbnail immediately after video upload using the returned `videoId`.
- If auth expires, re-run the `auth` subcommand.
- When the user doesn't specify a category, default to 22. See `references/categories.md` for the full list.

## References

- See `references/categories.md` for YouTube video category IDs.
