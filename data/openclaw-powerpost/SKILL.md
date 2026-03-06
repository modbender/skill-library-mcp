---
name: powerpost
description: Generate social media content and publish to all major platforms from one command.
version: 0.1.1
metadata:
  openclaw:
    requires:
      env:
        - POWERPOST_API_KEY
        - POWERPOST_WORKSPACE_ID
      bins:
        - curl
    primaryEnv: POWERPOST_API_KEY
    emoji: "⚡"
    homepage: https://powerpost.ai
---

# PowerPost Skill

PowerPost writes social media captions, generates images, and publishes to Instagram, TikTok, X/Twitter, YouTube, Facebook, and LinkedIn through a single API.

## Setup

The user needs two credentials:

- `POWERPOST_API_KEY` — their API key (starts with `pp_live_sk_`). They can create one at https://powerpost.ai/settings/api
- `POWERPOST_WORKSPACE_ID` — their workspace ID. Found at https://powerpost.ai/settings/workspaces

There are two ways to configure these in OpenClaw. The API key can go in the Skills UI (the "API key" field) or via config. The workspace ID has to be set via config since the UI only has one field per skill:

```bash
openclaw config set skills.entries.powerpost.apiKey "pp_live_sk_YOUR_KEY"
openclaw config set skills.entries.powerpost.env.POWERPOST_WORKSPACE_ID "YOUR_WORKSPACE_ID"
```

API keys come in two types:
- `read_write` — full access, including publishing.
- `read_draft` — can generate content and create drafts, but publishing is blocked (returns 403). Good when a human should review before anything goes live.

New accounts start with 50 free credits. Pricing details at https://powerpost.ai/pricing

## First run

Before running any PowerPost command, make sure both credentials are set. If either is missing, walk the user through setup:

1. If `POWERPOST_API_KEY` is not set:
   - Ask if they have a PowerPost account. If not, they can sign up at https://powerpost.ai/login
   - Point them to https://powerpost.ai/settings/api to create an API key.
   - They can paste it into the "API key" field on the Skills page in the OpenClaw UI, or run: `openclaw config set skills.entries.powerpost.apiKey "pp_live_sk_..."`

2. If `POWERPOST_WORKSPACE_ID` is not set:
   - Point them to https://powerpost.ai/settings/workspaces to find it.
   - They need to run: `openclaw config set skills.entries.powerpost.env.POWERPOST_WORKSPACE_ID "their-workspace-id"` — there's no UI field for this one, it has to be set via config.

3. Once both are set, verify by calling `GET /account/credits`. If it returns a balance, you're good. If it returns 401, the API key is wrong.

Don't run any other PowerPost commands until both credentials are confirmed working.

## Base URL

All requests go to:

```
https://powerpost.ai/api/v1
```

## Authentication Headers

Every request needs `x-api-key` (or `Authorization: Bearer <key>`). All content endpoints also need `X-Workspace-Id`. The only exception is `GET /account/credits` which only needs `x-api-key`.

```
x-api-key: $POWERPOST_API_KEY
X-Workspace-Id: $POWERPOST_WORKSPACE_ID
```

## Core Workflow

The standard PowerPost flow is:

1. **Check credits** to make sure the user has enough balance.
2. **Generate content** from text, images, or video (async — returns a generation ID).
3. **Poll for results** every 2-3 seconds until status is `completed` or `failed`.
4. **Optionally generate images** from the captions or a text prompt (also async — poll for results).
5. **Create a post** combining the generated captions and images into a draft.
6. **Show the draft** to the user for review before publishing.
7. **Publish** the post to connected social platforms.

Always check credits before generating content. Always show the user what will be published and get confirmation before calling the publish endpoint.

---

## Endpoints

### 1. Check Credits

Use this to check how many credits the user has before starting any generation.

```bash
curl https://powerpost.ai/api/v1/account/credits \
  -H "x-api-key: $POWERPOST_API_KEY"
```

Note: This endpoint does NOT need the `X-Workspace-Id` header.

Response:

```json
{
  "balance": 47
}
```

Tell the user their current balance. If balance is low, warn them before they start a generation.

### Credit Costs

**Caption generation:**
- Regular research: 6 base credits + 1 per image + 6 per minute of video
- Deep research: 8 base credits + 1 per image + 6 per minute of video

Example: text input, regular research = 6 credits.
Example: 2-min video, deep research = 8 + 12 = 20 credits.

**Image generation (per image):** `flux2-flex` = 5 credits, `ideogram-3` = 6 credits, `nano-banana-2` = 6 credits, `gpt-image-1.5` = 14 credits. Multiply by quantity.

**Publishing:** Flat 1-credit base fee + 3-credit surcharge for X. Credits only charged for successfully published items.

Credits are refunded for failed generations and failed publish attempts.

---

### 2. Upload Media

Use this when the user wants to generate content from images or video, or when they want to attach media to a post.

```bash
curl -X POST https://powerpost.ai/api/v1/media/upload \
  -H "x-api-key: $POWERPOST_API_KEY" \
  -H "X-Workspace-Id: $POWERPOST_WORKSPACE_ID" \
  -F "file=@/path/to/file" \
  -F "type=image"
```

The `type` field must be `image` or `video`.

Supported formats:
- Images: JPEG, PNG, WebP (max 10 MB)
- Videos: MP4, MOV, WebM (max 500 MB)

Response:

```json
{
  "media_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "type": "image",
  "file_name": "photo.jpg",
  "file_size": 245000,
  "mime_type": "image/jpeg",
  "created_at": "2026-01-10T18:30:00Z"
}
```

Save the `media_id` from the response. You will need it for content generation (`media_ids` field) or for creating posts (`media_ids` in post items).

Tell the user the upload was successful and show the file name and size.

---

### 3. Generate Content

Use this when the user wants to create social media captions. This is the primary endpoint.

There are three input modes, determined by which fields you provide:
- **Text only:** Send `prompt` (required, 3-500 chars).
- **Image input:** Send `media_ids` with image IDs (+ optional `prompt` for context).
- **Video input:** Send `media_ids` with a video ID (+ optional `prompt` for context).

You must provide either `prompt` or `media_ids` (or both).

```bash
curl -X POST https://powerpost.ai/api/v1/content/generate \
  -H "x-api-key: $POWERPOST_API_KEY" \
  -H "X-Workspace-Id: $POWERPOST_WORKSPACE_ID" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "We just shipped dark mode across all our apps",
    "post_types": ["instagram-reel", "tiktok-video", "x-post"],
    "research_mode": "regular"
  }'
```

**Required fields:**
- `post_types` (string array) — At least one post type. See the post types table below.
- `research_mode` (string) — `"regular"` or `"deep"`. Use regular for quick tasks, deep for important posts.

**Optional fields:**
- `writing_style_id` (string) — A custom writing style ID created in the dashboard.
- `cta_text` (string, max 100 chars) — A custom call-to-action.

**Post types:**

| Platform  | Post Types                                            |
|-----------|-------------------------------------------------------|
| Instagram | `instagram-feed`, `instagram-reel`, `instagram-story` |
| TikTok    | `tiktok-video`, `tiktok-photos`                       |
| YouTube   | `youtube-video`, `youtube-short`                      |
| X         | `x-post`                                              |
| Facebook  | `facebook-post`, `facebook-reel`, `facebook-story`    |
| LinkedIn  | `linkedin-post`                                       |

Multiple post types from the same platform produce one shared caption for that platform. The post type declares publishing intent.

Response:

```json
{
  "generation_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "processing",
  "credits_used": 10,
  "remaining_credits": 90,
  "status_url": "/api/v1/content/generations/550e8400-e29b-41d4-a716-446655440000"
}
```

Tell the user the generation has started, how many credits it cost, and that you are waiting for it to complete. Then immediately start polling.

---

### 4. Get Generation Status (Polling)

After starting a generation, poll this endpoint every 2-3 seconds until `status` is `completed` or `failed`. Do not poll more than 60 times (about 2 minutes).

```bash
curl https://powerpost.ai/api/v1/content/generations/GENERATION_ID \
  -H "x-api-key: $POWERPOST_API_KEY" \
  -H "X-Workspace-Id: $POWERPOST_WORKSPACE_ID"
```

**While processing:**

```json
{
  "generation_id": "550e8400-...",
  "status": "processing",
  "prompt": "We just shipped dark mode",
  "platforms": ["tiktok", "instagram"],
  "research_mode": "regular",
  "credits_used": 10,
  "created_at": "2026-01-10T18:30:00Z"
}
```

If status is still `processing` or `pending`, wait 3 seconds and poll again.

**When completed:**

```json
{
  "generation_id": "550e8400-...",
  "status": "completed",
  "prompt": "We just shipped dark mode",
  "platforms": ["tiktok", "instagram"],
  "research_mode": "regular",
  "credits_used": 10,
  "created_at": "2026-01-10T18:30:00Z",
  "outputs": {
    "tiktok": "Dark mode activated! POV: your eyes at 2am finally getting some relief... #darkmode #tech",
    "instagram": "Dark mode is here!\n\nYour late-night scrolling just got easier on the eyes... #DarkMode #ProductUpdate"
  }
}
```

The `outputs` object is keyed by platform name (not post type). Each value is a string, EXCEPT YouTube which has a `title` and `description`:

```json
"youtube": {
  "title": "We Just Shipped Dark Mode",
  "description": "Dark mode is finally here across all our apps... #darkmode"
}
```

When completed, display all generated captions to the user, clearly labeled by platform.

**When failed:**

The response includes an `error` object with `code` and `message`. Credits are refunded on failure. Tell the user the generation failed and show the error message.

---

### 5. List Generations

Use this when the user wants to see their recent generations or search for a past generation.

```bash
curl "https://powerpost.ai/api/v1/content/generations?status=completed&limit=10" \
  -H "x-api-key: $POWERPOST_API_KEY" \
  -H "X-Workspace-Id: $POWERPOST_WORKSPACE_ID"
```

Query parameters (all optional):
- `status` — Filter by: `pending`, `processing`, `completed`, `failed`
- `limit` — Results per page, 1-100 (default 20)
- `cursor` — Pagination cursor from `next_cursor` in a previous response

Response:

```json
{
  "data": [
    {
      "generation_id": "550e8400-...",
      "status": "completed",
      "prompt": "We just shipped dark mode",
      "platforms": ["tiktok", "instagram"],
      "research_mode": "regular",
      "credits_used": 10,
      "created_at": "2026-01-10T18:30:00Z"
    }
  ],
  "next_cursor": "gen_cursor_abc123",
  "has_more": true
}
```

The list endpoint does NOT include `outputs`. To get the full content of a specific generation, use the get generation endpoint with its ID.

Show the user a summary table of their generations. If they want to see the content of a specific one, fetch it with the get endpoint.

---

### 6. Generate Images

Use this when the user wants to create AI-generated images. There are three input modes:

**Text mode:** Describe the image in `prompt`.
**Reference mode:** Provide `prompt` + `style_images` (media IDs of uploaded reference images, max 4).
**Post mode:** Provide `generation_id` to create images matching an existing caption generation (+optional `prompt` for extra direction and `source_post_type` to pick which platform caption to use).

```bash
curl -X POST https://powerpost.ai/api/v1/images/generate \
  -H "x-api-key: $POWERPOST_API_KEY" \
  -H "X-Workspace-Id: $POWERPOST_WORKSPACE_ID" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Minimalist workspace with laptop and coffee, warm morning light",
    "size": "square",
    "quantity": 2,
    "model": "flux2-flex"
  }'
```

**Fields:**
- `prompt` (string, max 2000 chars) — Required for text and reference modes. Optional for post mode.
- `size` (string) — `square` (1:1), `feed` (4:5), `portrait` (9:16), `landscape` (16:9). Default: `square`.
- `quantity` (number, 1-4) — How many images to generate. Default: 1.
- `model` (string) — `flux2-flex` (default, best for multi-reference and fine control), `ideogram-3` (best text rendering and logos), `gpt-image-1.5` (most photorealistic, best detail), `nano-banana-2` (fast generation, great text).
- `enhance_prompt` (boolean) — Let AI optimize the prompt. Default: false.
- `style_images` (string array) — Media IDs of reference images (max 4). For reference mode.
- `generation_id` (string) — Caption generation ID. For post mode.
- `source_post_type` (string) — Which platform's caption to use as source. For post mode only.

**Model and size compatibility:**
- `flux2-flex`: square, feed, portrait, landscape
- `ideogram-3`: square, feed, portrait, landscape
- `gpt-image-1.5`: square, portrait, landscape (NO feed)
- `nano-banana-2`: square, feed, portrait, landscape

If the user requests a model/size combo that is not supported, warn them and suggest an alternative.

Response:

```json
{
  "image_generation_id": "7a8b9c0d-e1f2-3456-abcd-ef7890123456",
  "status": "processing",
  "credits_used": 10,
  "remaining_credits": 36,
  "status_url": "/api/v1/images/generations/7a8b9c0d-e1f2-3456-abcd-ef7890123456"
}
```

Tell the user that image generation has started and begin polling.

---

### 7. Get Image Generation Status (Polling)

Poll this endpoint every 2-3 seconds until status is `completed` or `failed`.

```bash
curl https://powerpost.ai/api/v1/images/generations/IMAGE_GENERATION_ID \
  -H "x-api-key: $POWERPOST_API_KEY" \
  -H "X-Workspace-Id: $POWERPOST_WORKSPACE_ID"
```

**When completed:**

```json
{
  "image_generation_id": "7a8b9c0d-...",
  "status": "completed",
  "prompt": "Minimalist workspace with laptop and coffee",
  "size": "square",
  "quantity": 2,
  "created_at": "2026-01-10T18:30:00Z",
  "images": [
    {
      "media_id": "img-001-abcd-efgh",
      "url": "https://powerpost.ai/storage/images/img-001-abcd-efgh.webp",
      "thumbnail_url": "https://powerpost.ai/storage/images/img-001-abcd-efgh-thumb.jpg",
      "width": 1024,
      "height": 1024
    }
  ]
}
```

Each image has a `media_id` which you use to attach the image to a post. The `url` is a preview link valid for 7 days. Always use the `media_id`, not the URL, when creating posts.

Show the user the image URLs so they can preview. Save the `media_id` values for creating posts.

**Partial failure:** If some images fail while others succeed, you get a partial result with a partial credit refund. The response status will be `failed` but may still contain an `images` array with the successful ones.

---

### 8. Create Post

Use this to assemble captions and media into a draft post ready for review and publishing.

```bash
curl -X POST https://powerpost.ai/api/v1/posts \
  -H "x-api-key: $POWERPOST_API_KEY" \
  -H "X-Workspace-Id: $POWERPOST_WORKSPACE_ID" \
  -H "Content-Type: application/json" \
  -d '{
    "generation_id": "550e8400-e29b-41d4-a716-446655440000",
    "items": [
      {
        "post_type": "instagram-reel",
        "media_ids": ["img-001-abcd-efgh"]
      },
      {
        "post_type": "tiktok-video",
        "media_ids": ["img-001-abcd-efgh"]
      }
    ]
  }'
```

**Fields:**
- `generation_id` (string, optional) — Links to a completed caption generation. If provided, content is auto-filled from the generation outputs for each platform.
- `items` (array, required) — One item per post type you want to publish.

**Each item:**
- `post_type` (string, required) — The target post type (e.g., `instagram-reel`, `x-post`).
- `content` (string) — The caption text. Required if no `generation_id` is provided. If `generation_id` is provided, content is auto-filled but can be overridden.
- `title` (string) — Required for YouTube post types (`youtube-video`, `youtube-short`).
- `media_ids` (string array, optional) — Media to attach (uploaded or generated image IDs).

**Custom content example (no generation):**

```bash
curl -X POST https://powerpost.ai/api/v1/posts \
  -H "x-api-key: $POWERPOST_API_KEY" \
  -H "X-Workspace-Id: $POWERPOST_WORKSPACE_ID" \
  -H "Content-Type: application/json" \
  -d '{
    "items": [
      {
        "post_type": "x-post",
        "content": "Just shipped the biggest update of the year."
      },
      {
        "post_type": "linkedin-post",
        "content": "Excited to announce our biggest product update of the year..."
      }
    ]
  }'
```

Response:

```json
{
  "post_id": "post-550e8400-e29b-41d4-a716-446655440000",
  "status": "draft",
  "created_at": "2026-01-10T18:30:00Z",
  "items": [
    {
      "item_id": "item-001",
      "post_type": "instagram-reel",
      "platform": "instagram",
      "content": "Dark mode is here! Your late-night scrolling just got easier... #DarkMode",
      "media_ids": ["img-001-abcd-efgh"],
      "status": "draft"
    }
  ]
}
```

After creating a post, show the user a summary of every item (platform, content preview, attached media) and ask if they want to publish or make changes.

---

### 9. Get Post

Use this to check the status of a post, especially after publishing.

```bash
curl https://powerpost.ai/api/v1/posts/POST_ID \
  -H "x-api-key: $POWERPOST_API_KEY" \
  -H "X-Workspace-Id: $POWERPOST_WORKSPACE_ID"
```

Response includes the post with all items and their individual statuses. After publishing, each item will show `posting`, `posted`, or `failed` with an optional `platform_post_id` for successfully published items.

Post statuses: `draft`, `publishing`, `published`, `failed`.
Item statuses: `draft`, `posting`, `posted`, `failed`.

---

### 10. Publish Post

Use this to publish a draft post to connected social platforms. Always confirm with the user before calling this endpoint.

```bash
curl -X POST https://powerpost.ai/api/v1/posts/POST_ID/publish \
  -H "x-api-key: $POWERPOST_API_KEY" \
  -H "X-Workspace-Id: $POWERPOST_WORKSPACE_ID"
```

**Prerequisites:**
- The user's social platforms must be connected at https://powerpost.ai/settings/connections
- The post must be in `draft` status.
- The user must have sufficient credits.
- The API key must be `read_write` type (not `read_draft`).

Response:

```json
{
  "post_id": "post-550e8400-...",
  "status": "publishing",
  "credits_used": 1,
  "status_url": "/api/v1/posts/post-550e8400-..."
}
```

Publishing is asynchronous. After receiving the response, poll the Get Post endpoint every 3 seconds to check when each item has finished publishing.

Publishing costs: 1-credit base fee + 3-credit surcharge for X.

Tell the user how many credits were used and that publishing is in progress. When all items show `posted` or `failed`, summarize the results.

---

## Common User Commands

### "Post about X" / "Create a post about X"

Full flow:
1. Check credits.
2. Ask which platforms if not specified. Default to all if the user says "everywhere" or "all platforms".
3. Generate content with the user's topic as the prompt. Use `regular` research mode unless they ask for deep.
4. Poll until complete.
5. Show the generated captions.
6. Ask if they want to generate images too.
7. Create the post.
8. Show the draft and ask for confirmation.
9. Publish on confirmation.

### "Write captions about X" / "Generate content about X"

Partial flow (no publishing):
1. Check credits.
2. Generate content.
3. Poll until complete.
4. Show the captions to the user.

### "Create an image" / "Generate an image of X"

1. Check credits.
2. If the user provides a text description, use text mode. If they reference a previous generation, use post mode. If they have reference images, use reference mode.
3. Ask about size preference if not specified (square is a safe default).
4. Generate the image.
5. Poll until complete.
6. Show the image URLs to the user.

### "Check my credits" / "How many credits do I have?"

1. Call the credits endpoint.
2. Tell the user their balance.

### "Upload this image/video"

1. Upload the file using the media upload endpoint.
2. Tell the user the upload succeeded and show the media ID.
3. Ask what they want to do with it (generate captions from it, use it in a post, etc.).

### "Show my recent posts" / "List my generations"

1. Call the list generations endpoint.
2. Show a summary of recent generations.
3. If the user wants details on one, fetch it with the get generation endpoint.

### "Publish my post" / "Send it live"

1. If there is a draft post from this session, publish it.
2. If not, ask the user which post to publish.
3. Always confirm before publishing.

---

## Polling Strategy

Both content generation and image generation are asynchronous. After starting either one:

1. Wait 2 seconds.
2. Call the status endpoint.
3. If status is `processing` or `pending`, wait 3 seconds and poll again.
4. If status is `completed`, show the results.
5. If status is `failed`, show the error and tell the user credits were refunded.
6. Do not poll more than 60 times. If it times out, tell the user to try again later.

Publishing is also asynchronous. After calling publish:
1. Wait 3 seconds.
2. Poll the Get Post endpoint.
3. Check each item's status. When all are either `posted` or `failed`, stop polling.

---

## Error Handling

All errors return this format:

```json
{
  "error": {
    "message": "Human-readable error message",
    "code": "ERROR_CODE"
  }
}
```

Handle these errors:

| HTTP Status | Code                     | What to Tell the User                                                  |
|-------------|--------------------------|------------------------------------------------------------------------|
| 400         | `VALIDATION_ERROR`       | The request was invalid. Check the fields and try again.               |
| 401         | `INVALID_API_KEY`        | The API key is missing or invalid. Check POWERPOST_API_KEY.            |
| 402         | `INSUFFICIENT_CREDITS`   | Not enough credits. Check balance and suggest upgrading.               |
| 403         | `FORBIDDEN`              | Access denied. The API key may be `read_draft` and publishing was attempted. |
| 404         | `NOT_FOUND`              | The resource was not found. Check the ID.                              |
| 409         | `ALREADY_PUBLISHED`      | This post was already published.                                       |
| 413         | `FILE_TOO_LARGE`         | The file exceeds the size limit (10 MB for images, 500 MB for video).  |
| 413         | `STORAGE_QUOTA_EXCEEDED` | Storage quota exceeded (10 GB limit). Delete unused media or contact support. |
| 422         | `PLATFORM_NOT_CONNECTED` | The target platform is not connected. Direct user to https://powerpost.ai/settings/connections |
| 429         | `RATE_LIMIT_EXCEEDED`    | Too many requests. Wait the duration in `retryAfter` seconds and retry. |
| 500         | `INTERNAL_ERROR`         | Server error. Wait a moment and try again.                             |

For rate limit errors (429), the response includes a `retryAfter` field in seconds. Wait that long before retrying.

Every response includes an `X-Request-Id` header. If the user needs support, give them this ID.

---

## Things to know

- Always show the user what will be posted and where, and get explicit confirmation before publishing. This goes to real social accounts.
- YouTube posts need a `title` field in addition to the caption.
- If the user picks both `instagram-reel` and `instagram-feed`, they share one Instagram caption. The post type controls the publishing format, not the caption.
- Image URLs from generation expire after 7 days. Always use `media_id` when creating posts, not the URL.
- Credits are shared across all workspaces on an account.
- Workspaces are isolated from each other. Generations, posts, media, and connections in one workspace aren't visible in another.
- Users can set up webhooks at https://powerpost.ai/settings/api for real-time notifications instead of polling. Not needed for agent usage, but useful for production integrations.

## External endpoints

All requests go to one domain: `https://powerpost.ai/api/v1/*`. Nothing is sent anywhere else.

## Security and privacy

- Your API key and workspace ID are sent to `powerpost.ai` as HTTP headers with every request. They're not logged, displayed, or sent anywhere else.
- Prompts, uploaded media, and generated content are stored on PowerPost's servers, scoped to your workspace.
- This skill only uses `curl` over HTTPS. It doesn't write files, run scripts, or touch your system.

## Trust

When you use this skill, your prompts, images, videos, and credentials go to `powerpost.ai` over HTTPS. PowerPost uses third-party AI models on their servers to process your content. Their privacy policy is at https://powerpost.ai/terms and support is at https://powerpost.ai/contact

## Tips

- Always check the credit balance before starting a generation. Better to warn the user upfront than hit an insufficient credits error mid-flow.
- Default to `regular` research mode. Only use `deep` when the user asks for it or says the post matters.
- Default to `square` for image size if the user doesn't say. It works on most platforms.
- Default to `flux2-flex` for the image model. It supports all sizes and handles reference images well.
- If a generation fails, credits are refunded. Let the user know and suggest trying again.
- When the user says "all platforms," use one post type per platform: `instagram-feed`, `tiktok-video`, `youtube-short`, `x-post`, `facebook-post`, `linkedin-post`.
- If the user's image description is short or vague, suggest setting `enhance_prompt: true` to let the AI fill in the details.
