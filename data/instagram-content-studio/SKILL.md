---
name: instagram-api
description: Manage an Instagram account. View profile, list posts, publish images/carousels, publish videos/Reels, and read/write comments. Use when the user requests any Instagram-related task.
allowed-tools: Bash(node scripts/*)
compatibility: Requires node (v22+), npm, and cloudflared (for local file uploads). Requires env var INSTAGRAM_ACCESS_TOKEN in a .env file. Requires internet access to graph.instagram.com.
metadata:
  version: "1.0"
---

# Instagram API Skill

A skill for managing an Instagram account via the Instagram Graph API. Supports profile viewing, post management, image publishing, video/Reels publishing, and comment operations.

## Prerequisites

- A `.env` file with credentials must be configured.
  - Required: `INSTAGRAM_ACCESS_TOKEN`
  - Recommended (for comment/reply via Facebook Graph): `FACEBOOK_USER_ACCESS_TOKEN`
  - Required for FB token refresh: `FACEBOOK_APP_ID`, `FACEBOOK_APP_SECRET`
- `cloudflared` must be installed for local image/video posting.
- If the user specifies a `.env` file path, append `--env <path>` to every command.
  - Example: `node scripts/get-profile.js --env /home/user/.instagram-env`
- All scripts must be run with this project root as the working directory.

## Available Commands

All commands automatically refresh the token before execution. No manual refresh needed.

### Refresh Token

```bash
# Instagram token refresh
node scripts/refresh-token.js

# Facebook user token refresh (for comments/replies flow)
node scripts/refresh-facebook-token.js
```

Manually refreshes token(s) and returns expiration info.

### View Profile

```bash
node scripts/get-profile.js
```

Returns profile info (name, username, account type, media count).

### List Posts

```bash
node scripts/get-posts.js [--limit 10]
```

Returns the user's post list. Use `--limit` to set the count (default: 10).

### View Post Detail

```bash
node scripts/get-post.js <media-id>
```

Returns post detail including like count and comment count.

### Publish Image

```bash
# Single image (URL)
node scripts/post-image.js --caption "Caption" https://example.com/photo.jpg

# Single image (local file)
node scripts/post-image.js --caption "Caption" ./photos/image.png

# Carousel — multiple images (URL)
node scripts/post-image.js --caption "Caption" https://example.com/a.jpg https://example.com/b.jpg

# Carousel — multiple images (local files)
node scripts/post-image.js --caption "Caption" ./img1.png ./img2.png ./img3.jpg
```

- 1 image → single post, 2+ images → automatically posted as carousel (max 10).
- Both URLs (`http://`, `https://`) and local file paths are supported, but mixing is not allowed.
- Supported local file formats: jpg, jpeg, png, gif, webp, heic/heif (HEIC is automatically converted to JPEG).

### Publish Video (Reels)

```bash
# Single video (URL)
node scripts/post-video.js --caption "Caption" https://example.com/video.mp4

# Single video (local file)
node scripts/post-video.js --caption "Caption" ./videos/clip.mp4

# With cover image and options
node scripts/post-video.js --caption "Caption" --cover https://example.com/cover.jpg --thumb-offset 5000 --share-to-feed true https://example.com/video.mp4

# Video carousel — multiple videos (URL)
node scripts/post-video.js --caption "Caption" https://example.com/a.mp4 https://example.com/b.mp4

# Video carousel — multiple videos (local files)
node scripts/post-video.js --caption "Caption" ./clip1.mp4 ./clip2.mov
```

- 1 video → Reels post, 2+ videos → automatically posted as carousel (max 10).
- Both URLs and local file paths are supported, but mixing is not allowed.
- Supported formats: mp4, mov (max 100MB per file).
- `--cover`, `--thumb-offset`, `--share-to-feed` options are only available for single video posts (not carousels).
- Video processing takes longer than images; the script waits up to 10 minutes.

### View Comments

```bash
node scripts/get-comments.js <media-id>
```

Returns comments and replies for a specific post.

### Post Comment

```bash
node scripts/post-comment.js <media-id> --text "Comment text"
```

### Reply to Comment

```bash
node scripts/reply-comment.js <comment-id> --text "Reply text"
```

## Workflow Guidelines

- When publishing images or videos, always confirm the caption with the user before executing.
- After publishing, report the result ID and permalink to the user (both are included in the output).
- Video processing takes longer than images. Inform the user that it may take a few minutes.
- When writing comments/replies, confirm the content with the user before executing.
- All command outputs are in JSON format.

## Error Handling

If the output contains an `error` field, an error has occurred. Explain the cause to the user and suggest a resolution.

```json
{ "error": "error message" }
```

## Security

### Token storage
- `refreshIgToken()` and `refreshFbToken()` overwrite tokens in the `.env` file in plaintext. Do not commit `.env` to version control.
- Create a dedicated Meta app with minimum required permissions (see below).

### Local file upload
- Local image/video posting starts a temporary [cloudflared Quick Tunnel](https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/get-started/create-local-tunnel/) to expose files so Instagram servers can download them.
- The tunnel is active only during the upload and is shut down immediately after.
- Only provide file paths you are comfortable briefly exposing to the internet.

### Minimum required permissions
When creating your Meta app, grant only these permissions:
- `instagram_business_basic` — profile and media read
- `instagram_content_publish` — image/video publishing
- `instagram_manage_comments` — comment read/write
- `pages_read_engagement` — required for comment API via Facebook Graph
- `pages_show_list` — required for page-linked Instagram accounts
