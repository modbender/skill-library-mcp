# Instagram API Agent Skill — SPEC

## Goal

Implement the Instagram Graph API as a **skill that Claude Code / OpenAI Codex agents can invoke directly**. Agents execute individual scripts and interpret JSON results.

## Compatibility

Follows the [Agent Skills](https://agentskills.io) open standard. Both Claude Code and OpenAI Codex support this standard, so a single skill directory works on both platforms.

The project root itself is the skill directory. Symlink this project into `.claude/skills/instagram-api/` or `.agents/skills/instagram-api/` and `SKILL.md` at the root becomes the entrypoint.

| Platform | Installation | Notes |
|----------|-------------|-------|
| Claude Code | `ln -s <project-root> ~/.claude/skills/instagram-api` | Tool access controlled via `allowed-tools` |
| OpenAI Codex | `ln -s <project-root> ~/.agents/skills/instagram-api` | Additional config in `agents/openai.yaml` |

---

## Directory Structure

```
instagram-api/
├── SKILL.md                      # Skill entrypoint (agent instructions)
├── SPEC.md                       # This document
├── agents/
│   └── openai.yaml               # Codex additional config
├── scripts/
│   ├── _common.js                # Shared module
│   ├── refresh-token.js
│   ├── refresh-facebook-token.js
│   ├── get-profile.js
│   ├── get-posts.js
│   ├── get-post.js
│   ├── post-image.js
│   ├── post-video.js
│   ├── get-comments.js
│   ├── post-comment.js
│   └── reply-comment.js
├── .env                          # Instagram credentials
└── package.json
```

---

## Script Conventions

### Common Principles

1. **Every script refreshes the token before execution** (internally calls `refreshIgToken()` via `run()`). Exception: `refresh-token.js` and `refresh-facebook-token.js` call their respective refresh functions directly to avoid double-refresh.
2. **stdout outputs JSON only**. Human-readable logs go to stderr.
3. **Exit codes**: success `0`, failure `1`.
4. **Error format on stdout**:
   ```json
   { "error": "error message" }
   ```
5. Arguments are passed as command-line args. Complex inputs (captions, etc.) use named arguments like `--caption "text"`.
6. Assumes the project root as the working directory.
7. **All scripts support the `--env <path>` option**.
   - When specified: loads credentials from the given `.env` file and writes refreshed tokens to the same file.
   - When omitted: uses the project root `.env` (default).
   - Example: `node scripts/get-profile.js --env /home/user/.instagram-env`

### `scripts/_common.js` Exports

| Function / Constant | Description |
|---------------------|-------------|
| `log(msg)` | Write message to stderr (stdout is reserved for JSON) |
| `getConfig()` | Returns `{ ig, fb }`. `ig`: `{ accessToken, baseUrl }` from `INSTAGRAM_ACCESS_TOKEN` (`baseUrl` = `graph.instagram.com/v24.0`). `fb`: `{ appId, appSecret, accessToken, baseUrl }` from `FACEBOOK_*` env vars (`baseUrl` = `graph.facebook.com/v24.0`) |
| `apiGet(endpoint, params)` | GET request to Instagram Graph API (`ig.baseUrl`). Automatically appends `ig.accessToken` |
| `apiPost(endpoint, body)` | POST request to Instagram Graph API. Automatically appends `ig.accessToken` |
| `fbApiGet(endpoint, params)` | GET request to Facebook Graph API (`fb.baseUrl`). Uses `fb.accessToken`. Throws if `FACEBOOK_USER_ACCESS_TOKEN` is missing |
| `fbApiPost(endpoint, body)` | POST request to Facebook Graph API. Uses `fb.accessToken`. Throws if `FACEBOOK_USER_ACCESS_TOKEN` is missing |
| `refreshIgToken()` | Refresh Instagram long-lived token + save to `.env` file. Skips if token doesn't start with "IG" |
| `refreshFbToken()` | Refresh Facebook user token via `fb_exchange_token` grant + save to `.env` file |
| `getProfile()` | Fetch profile (id, username, name, account_type, media_count) |
| `getMyPosts(limit)` | Fetch post list (id, caption, media_type, timestamp, permalink) |
| `getPost(mediaId)` | Fetch post detail (includes like_count, comments_count) |
| `postImage(url, caption)` | Post URL image (create container → poll → publish). Returns `{ id, permalink }` |
| `postLocalImage(path, caption)` | Post local image (HTTP server + cloudflared tunnel). Returns `{ id, permalink }` |
| `postCarousel(urls, caption)` | Post URL carousel (child containers → carousel container → publish). Returns `{ id, permalink }` |
| `postLocalCarousel(paths, caption)` | Post local carousel. Returns `{ id, permalink }` |
| `validateVideoFile(filePath)` | Validate video file (existence, format, size). Returns `{ absolutePath, mimeType }` |
| `postVideo(url, caption, options?)` | Post URL video as Reels. options: `coverUrl`, `thumbOffset`, `shareToFeed`. Returns `{ id, permalink }` |
| `postLocalVideo(path, caption, options?)` | Post local video as Reels (HTTP server + cloudflared tunnel). Also serves local cover image. Returns `{ id, permalink }` |
| `postVideoCarousel(urls, caption)` | Post URL video carousel. Returns `{ id, permalink }` |
| `postLocalVideoCarousel(paths, caption)` | Post local video carousel. Returns `{ id, permalink }` |
| `VIDEO_CONTAINER_TIMEOUT` | 10 minute timeout for video container processing |
| `getComments(mediaId)` | Fetch comments + replies. For carousel posts, automatically falls back to child media comments if the parent has none |
| `postComment(mediaId, text)` | Create comment (uses Facebook Graph API via `fbApiPost`) |
| `replyToComment(commentId, text)` | Create reply (uses Facebook Graph API via `fbApiPost`) |
| `startTunnel(port)` | Start cloudflared quick tunnel. Returns public URL |
| `stopTunnel()` | Kill tunnel process |
| `run(fn, options?)` | Script entrypoint wrapper: parse args → load env → refresh token(s) → execute fn → JSON output / error handling. `options.refreshIg` (default `true`): call `refreshIgToken()`. `options.refreshFb` (default `false`): call `refreshFbToken()` (fails silently) |
| `parseArgs()` | Command-line args parser. Returns `{ named, positional }` |
| `loadEnv(envPath?)` | Load specified or default `.env`. Also sets the file path for `refreshIgToken()` to write to |

### Script Specifications

#### `scripts/refresh-token.js`

Refreshes the token and returns new expiration info.

```
node scripts/refresh-token.js
```

```json
{ "access_token": "IGQ...", "expires_in": 5184000, "expires_in_days": 60 }
```

#### `scripts/refresh-facebook-token.js`

Refreshes the Facebook user token (used for comment/reply flows) and returns new expiration info.

```
node scripts/refresh-facebook-token.js
```

```json
{ "access_token": "EAA...", "expires_in": 5184000, "expires_in_days": 60 }
```

#### `scripts/get-profile.js`

Fetches the user's profile.

```
node scripts/get-profile.js
```

```json
{
  "id": "12345",
  "username": "myaccount",
  "name": "My Name",
  "account_type": "BUSINESS",
  "media_count": 42,
  "profile_picture_url": "https://..."
}
```

#### `scripts/get-posts.js`

Fetches the user's post list.

```
node scripts/get-posts.js [--limit 10]
```

```json
{
  "data": [
    {
      "id": "17890...",
      "caption": "Post caption",
      "media_type": "IMAGE",
      "media_url": "https://...",
      "timestamp": "2026-02-16T00:00:00+0000",
      "permalink": "https://www.instagram.com/p/..."
    }
  ]
}
```

#### `scripts/get-post.js`

Fetches detail for a specific post.

```
node scripts/get-post.js <media-id>
```

```json
{
  "id": "17890...",
  "caption": "Post caption",
  "media_type": "IMAGE",
  "media_url": "https://...",
  "timestamp": "2026-02-16T00:00:00+0000",
  "permalink": "https://www.instagram.com/p/...",
  "like_count": 10,
  "comments_count": 3
}
```

#### `scripts/post-image.js`

Posts images. Automatically switches to carousel when given 2+ files.
Supports both URLs and local file paths (local files use cloudflared tunnel).

```
# Single image (URL)
node scripts/post-image.js --caption "Caption" https://example.com/photo.jpg

# Single image (local)
node scripts/post-image.js --caption "Caption" ./photos/image.png

# Carousel (multiple local)
node scripts/post-image.js --caption "Caption" ./img1.png ./img2.png ./img3.jpg
```

```json
{ "id": "18158...", "permalink": "https://www.instagram.com/p/...", "type": "IMAGE" }
```

```json
{ "id": "18068...", "permalink": "https://www.instagram.com/p/...", "type": "CAROUSEL" }
```

**Detection logic**:
- Starts with `http://` or `https://` → URL. Otherwise → local file path.
- Image count: 1 → single post, 2+ → carousel.
- Mixing URLs and local files is not supported.

#### `scripts/post-video.js`

Posts videos as Reels. Automatically switches to carousel when given 2+ files.
Supports both URLs and local file paths (local files use cloudflared tunnel).

```
# Single video (URL)
node scripts/post-video.js --caption "Caption" https://example.com/video.mp4

# Single video (local)
node scripts/post-video.js --caption "Caption" ./videos/clip.mp4

# With options (single video only)
node scripts/post-video.js --caption "Caption" --cover https://example.com/cover.jpg --thumb-offset 5000 --share-to-feed true https://example.com/video.mp4

# Carousel (multiple URLs)
node scripts/post-video.js --caption "Caption" https://example.com/a.mp4 https://example.com/b.mp4
```

```json
{ "id": "18158...", "permalink": "https://www.instagram.com/reel/...", "type": "REELS" }
```

```json
{ "id": "18068...", "permalink": "https://www.instagram.com/p/...", "type": "CAROUSEL" }
```

**Detection logic**:
- Starts with `http://` or `https://` → URL. Otherwise → local file path.
- Video count: 1 → Reels post, 2+ → carousel.
- Mixing URLs and local files is not supported.

**Options** (single video only):
- `--cover <url-or-path>`: Cover image URL or local file path.
- `--thumb-offset <ms>`: Thumbnail offset in milliseconds.
- `--share-to-feed <true|false>`: Whether to share the Reel to the main feed.

**Constraints**:
- Supported formats: mp4, mov.
- Maximum file size: 100MB per video.
- Video processing timeout: 10 minutes.

#### `scripts/get-comments.js`

Fetches comments and replies for a specific post. Uses the Facebook Graph API (`graph.facebook.com`) with `FACEBOOK_USER_ACCESS_TOKEN`.

For carousel posts, if the parent media has no comments, the script automatically fetches comments from each child media item as a fallback. In this case, each comment includes an additional `media_id` field indicating which child it belongs to, and a `meta.source: "carousel-children"` field is added.

```
node scripts/get-comments.js <media-id>
```

```json
{
  "data": [
    {
      "id": "17858...",
      "text": "Comment text",
      "username": "commenter",
      "timestamp": "2026-02-16T00:00:00+0000",
      "replies": {
        "data": [
          { "id": "17860...", "text": "Reply", "username": "replier", "timestamp": "..." }
        ]
      }
    }
  ]
}
```

#### `scripts/post-comment.js`

Creates a comment on a post. Uses the Facebook Graph API (`graph.facebook.com`) with `FACEBOOK_USER_ACCESS_TOKEN`.

```
node scripts/post-comment.js <media-id> --text "Comment text"
```

```json
{ "id": "17858..." }
```

#### `scripts/reply-comment.js`

Creates a reply to a comment. Uses the Facebook Graph API (`graph.facebook.com`) with `FACEBOOK_USER_ACCESS_TOKEN`.

```
node scripts/reply-comment.js <comment-id> --text "Reply text"
```

```json
{ "id": "17860..." }
```

---

## Codex Additional Config

### `agents/openai.yaml`

```yaml
interface:
  display_name: "Instagram"
  short_description: "Instagram 계정 관리 (게시, 댓글, 프로필)"
  brand_color: "#E4405F"

policy:
  allow_implicit_invocation: false
```

---

## Environment Requirements

| Item | Required | Description |
|------|----------|-------------|
| Node.js | Yes | v22+ |
| `.env` file | Yes | See environment variables below |
| `dotenv` | Yes | Included in `package.json` |
| `sharp` | Yes | Included in `package.json` (HEIC→JPEG conversion) |
| `cloudflared` | For local file posting | `brew install cloudflared` / `apt-get install cloudflared` |

### Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `INSTAGRAM_ACCESS_TOKEN` | Yes | Instagram long-lived user access token |
| `FACEBOOK_USER_ACCESS_TOKEN` | Recommended | Facebook user token for comment/reply flows via `graph.facebook.com` |
| `FACEBOOK_APP_ID` | For FB token refresh | Meta App ID for Facebook token exchange |
| `FACEBOOK_APP_SECRET` | For FB token refresh | Meta App Secret for Facebook token exchange |
