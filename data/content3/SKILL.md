---
name: content3
version: 1.0.4
description: Content3 API for creating videos, managing content, submitting reviews, and posting to social media.
homepage: https://content3.app/developers
metadata: {"clawdbot":{"emoji":"🎬"}}
---

# content3

Use the Content3 Agent API to create short-form videos, manage content libraries, submit reviews for human approval, and draft social media posts.

## Setup

1. Log in to your Content3 dashboard
2. Navigate to **Settings → API Keys**
3. Click **Create API Key** — copy the key (starts with `c3ak_`, shown only once)
4. Store it:
```bash
mkdir -p ~/.config/content3
echo "c3ak_your_key_here" > ~/.config/content3/api_key
```

## API Basics

Base URL: `https://api.content3.app/v1`

All requests need:
```bash
C3_KEY=$(cat ~/.config/content3/api_key)
curl -X GET "https://api.content3.app/v1/..." \
  -H "Authorization: Bearer $C3_KEY" \
  -H "Content-Type: application/json"
```

> **Note:** Agent API keys have scopes that control access. Default scopes: `content:read`, `social:generate`, `social:drafts:read`, `social:drafts:write`. Ask the user to grant additional scopes if needed.

## Authentication

**Verify your key:**
```bash
curl "https://api.content3.app/v1/me" \
  -H "Authorization: Bearer $C3_KEY"
```

Returns: `{ "userId", "keyId", "keyName", "scopes": [...] }`

### Scopes Reference

| Scope | Access |
|-------|--------|
| `content:read` | Read content items, render jobs, social connections, short-form options |
| `content:write` | Create/modify content |
| `reviews:read` | Read reviews |
| `reviews:write` | Create reviews and comments |
| `social:generate` | Generate AI social media content |
| `social:drafts:read` | Read social media drafts |
| `social:drafts:write` | Create social media drafts |
| `products:read` | Read products |
| `products:write` | Create/modify products |
| `*` | Full access (all scopes) |

## Short-Form Video Generation

This is the primary agent workflow — generate short-form videos from various sources.

**Get available options (voices, sources, aspect ratios):**
```bash
curl "https://api.content3.app/v1/agents/short-form/options" \
  -H "Authorization: Bearer $C3_KEY"
```

Returns source types (`quora`, `reddit`, `prompt`, `text`), voice options (Kore, Puck, Charon, Fenrir, Zephyr, Aoede, Orbit, Orus), and aspect ratios (`9:16`, `16:9`).

**Generate a video from a prompt:**
```bash
curl -X POST "https://api.content3.app/v1/agents/short-form/generate" \
  -H "Authorization: Bearer $C3_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "source": {
      "type": "prompt",
      "prompt": "Explain why cats always land on their feet"
    },
    "voiceId": "Kore",
    "aspectRatio": "9:16",
    "saveToLibrary": true
  }'
```

**Generate from a Reddit post:**
```bash
curl -X POST "https://api.content3.app/v1/agents/short-form/generate" \
  -H "Authorization: Bearer $C3_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "source": {
      "type": "reddit",
      "url": "https://reddit.com/r/..."
    },
    "voiceId": "Puck",
    "aspectRatio": "9:16"
  }'
```

**Generate from a Quora answer:**
```bash
curl -X POST "https://api.content3.app/v1/agents/short-form/generate" \
  -H "Authorization: Bearer $C3_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "source": {
      "type": "quora",
      "url": "https://quora.com/..."
    },
    "voiceId": "Zephyr"
  }'
```

**Generate from raw text:**
```bash
curl -X POST "https://api.content3.app/v1/agents/short-form/generate" \
  -H "Authorization: Bearer $C3_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "source": {
      "type": "text",
      "text": "Your script or content here..."
    },
    "voiceId": "Fenrir",
    "aspectRatio": "16:9"
  }'
```

Returns: `{ "success": true, "jobId": "uuid", "status": "queued", "taskName": "..." }`

## Render Jobs

Track the status of video generation jobs.

**List render jobs:**
```bash
curl "https://api.content3.app/v1/render-jobs?status=completed&limit=10" \
  -H "Authorization: Bearer $C3_KEY"
```

Query params: `status` (queued, processing, completed, failed), `agent_type`, `job_type`, `limit` (max 100), `offset`.

**Get a specific job:**
```bash
curl "https://api.content3.app/v1/render-jobs/{job_id}" \
  -H "Authorization: Bearer $C3_KEY"
```

Returns full job details including `payload`, `status`, `output_url`, timestamps.

## Content Items

Manage your content library.

**List content items:**
```bash
curl "https://api.content3.app/v1/content-items?type=video&limit=20" \
  -H "Authorization: Bearer $C3_KEY"
```

Query params: `type`, `limit` (max 100, default 20), `offset`.

Returns: `{ "items": [{ "id", "type", "title", "description", "source_url", "thumbnail_url", "created_at" }] }`

## Reviews (Human-in-the-Loop)

Submit content for human review and approval before publishing.

**Create a review:**
```bash
curl -X POST "https://api.content3.app/v1/reviews" \
  -H "Authorization: Bearer $C3_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Weekly video batch - Feb 18",
    "description": "5 short-form videos for review before publishing",
    "contentType": "video",
    "attachments": [
      {"url": "https://r2.example.com/video1.mp4", "label": "Cat facts video"},
      {"url": "https://r2.example.com/video2.mp4", "label": "Tech tips video"}
    ],
    "metadata": {
      "tags": ["short-form", "batch"],
      "notes": "Generated from trending Reddit posts"
    }
  }'
```

Content types: `pdf`, `video`, `image`, `slides`, `markdown`.

**List reviews:**
```bash
curl "https://api.content3.app/v1/reviews?status=pending&limit=10" \
  -H "Authorization: Bearer $C3_KEY"
```

Status values: `pending`, `approved`, `rejected`, `needs_revision`.

**Get review with comments:**
```bash
curl "https://api.content3.app/v1/reviews/{review_id}" \
  -H "Authorization: Bearer $C3_KEY"
```

**Add a comment to a review:**
```bash
curl -X POST "https://api.content3.app/v1/reviews/{review_id}/comments" \
  -H "Authorization: Bearer $C3_KEY" \
  -H "Content-Type: application/json" \
  -d '{"body": "Revised the thumbnail based on feedback"}'
```

### Update Review Status

**Update a review's status:**
```bash
curl -X PATCH "https://api.content3.app/v1/reviews/{review_id}" \
  -H "Authorization: Bearer $C3_KEY" \
  -H "Content-Type: application/json" \
  -d '{"status": "in_review"}'
```

Valid transitions: `pending` → `in_review`, `in_review` → `approved` / `rejected` / `changes_requested`, `changes_requested` → `in_review`.

Returns: `{ "review": { "id": "uuid", "status": "in_review", "updatedAt": "..." } }`

### Review Revisions

Submit updated attachments when changes are requested. The platform tracks all versions.

**Submit a revision:**
```bash
curl -X POST "https://api.content3.app/v1/reviews/{review_id}/revisions" \
  -H "Authorization: Bearer $C3_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "attachments": [
      {"url": "https://r2.example.com/video1-v2.mp4", "label": "Fixed background color"}
    ],
    "note": "Fixed the background color as requested"
  }'
```

If no revisions exist yet, revision 1 is automatically created from the current attachments (labeled "Original"). The new revision becomes the latest, and `reviews.attachments` is updated.

**List revisions:**
```bash
curl "https://api.content3.app/v1/reviews/{review_id}/revisions" \
  -H "Authorization: Bearer $C3_KEY"
```

Returns: `{ "revisions": [{ "revisionNumber": 1, "attachments": [...], "note": "Original", "agentKeyName": "...", "createdAt": "..." }, ...] }`

### Shareable Review Links

Generate a public share link for a review so humans can view and comment without logging in.

**Create or get a share link:**
```bash
curl -X POST "https://api.content3.app/v1/reviews/{review_id}/share" \
  -H "Authorization: Bearer $C3_KEY"
```

Returns: `{ "shareToken": "...", "shareUrl": "https://content3.app/review/...", "shareEnabled": true }`

If a share link already exists, this returns the existing link and ensures it is enabled.

**Toggle share link on/off:**
```bash
curl -X PATCH "https://api.content3.app/v1/reviews/{review_id}/share" \
  -H "Authorization: Bearer $C3_KEY" \
  -H "Content-Type: application/json" \
  -d '{"enabled": false}'
```

When disabled, anyone visiting the share URL sees a "not found" page. Re-enable with `{"enabled": true}`.

The share URL can be sent to any human for on-demand feedback — no Content3 account required. Public reviewers can view the content, change the review status, and leave comments.

### Promote Review to Content

After a review is approved, promote it to a content item so it can be used with social drafts.

**Promote an approved review:**
```bash
curl -X POST "https://api.content3.app/v1/reviews/{review_id}/promote" \
  -H "Authorization: Bearer $C3_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Optional override title",
    "description": "Optional override description"
  }'
```

The request body is optional — omit fields to use the review's title/description.

Returns: `{ "contentItem": { "id": "uuid", "type": "video", "title": "...", "sourceUrl": "...", "status": "ready", "reviewId": "uuid", "createdAt": "..." } }`

Returns `201` on first promote, `200` if already promoted (idempotent). Returns `422` if the review is not yet approved. Requires scopes: `reviews:read` + `content:write`.

## Social Media

Create drafts and generate AI-powered social media content.

**List connected social accounts:**
```bash
curl "https://api.content3.app/v1/social/connections" \
  -H "Authorization: Bearer $C3_KEY"
```

Returns connections for: `youtube`, `tiktok`, `instagram`, `pinterest`, `threads`.

**Generate AI social content for a content item:**
```bash
curl -X POST "https://api.content3.app/v1/social/generate-content" \
  -H "Authorization: Bearer $C3_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "contentItemId": "content-item-uuid",
    "platforms": ["tiktok", "youtube"],
    "userPrompt": "Make it engaging and use trending hashtags"
  }'
```

**Create a social media draft (format A — canonical):**
```bash
curl -X POST "https://api.content3.app/v1/social/drafts" \
  -H "Authorization: Bearer $C3_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "contentItemId": "content-item-uuid",
    "title": "Why cats always land on their feet",
    "description": "The science behind cat reflexes",
    "hashtags": ["cats", "science", "shorts"],
    "platforms": [
      {
        "connectionId": "connection-uuid",
        "platformTitle": "Cat Physics Explained",
        "platformDescription": "You won'\''t believe this! #cats #science"
      }
    ]
  }'
```

**Create a social media draft (format B — shorthand):**
```bash
curl -X POST "https://api.content3.app/v1/social/drafts" \
  -H "Authorization: Bearer $C3_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "contentItemId": "content-item-uuid",
    "title": "Why cats always land on their feet",
    "caption": "The science behind cat reflexes #cats #science",
    "hashtags": ["cats", "science", "shorts"],
    "platforms": ["tiktok", "youtube"],
    "connectionIds": ["connection-uuid-1", "connection-uuid-2"]
  }'
```

Both formats are accepted. `caption` maps to `description` if `description` is not provided. Use `GET /v1/social/connections` to get valid connection IDs.

**List drafts:**
```bash
curl "https://api.content3.app/v1/social/drafts?limit=20" \
  -H "Authorization: Bearer $C3_KEY"
```

**Publish a draft:**
```bash
curl -X POST "https://api.content3.app/v1/social/drafts/{draft_id}/publish" \
  -H "Authorization: Bearer $C3_KEY"
```

Enqueues the draft for publishing to all configured platforms. Only drafts with status `draft` can be published. Returns `422` if the post is not a draft or is missing content/platforms.

Returns: `{ "postId": "uuid", "jobId": "uuid", "status": "pending" }`

Poll `GET /render-jobs/{jobId}` to track publishing progress.

## Products

Manage products for content generation.

**Create a product:**
```bash
curl -X POST "https://api.content3.app/v1/products" \
  -H "Authorization: Bearer $C3_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "My SaaS Product",
    "description": "A tool that helps you do X",
    "url": "https://myproduct.com"
  }'
```

**List products:**
```bash
curl "https://api.content3.app/v1/products?limit=20" \
  -H "Authorization: Bearer $C3_KEY"
```

## Common Workflows

### Generate and Review a Video
1. Generate a video: `POST /agents/short-form/generate`
2. Poll job status: `GET /render-jobs/{jobId}` until `status: "completed"`
3. Submit for review: `POST /reviews` with the video URL from the completed job
4. Create a share link: `POST /reviews/{reviewId}/share` — send the `shareUrl` to a human for feedback
5. Check review status: `GET /reviews/{reviewId}` — wait for `approved`
6. If `changes_requested`: fix the content and submit a revision with `POST /reviews/{reviewId}/revisions`, then go back to step 5
7. Promote to content: `POST /reviews/{reviewId}/promote` — creates a content item from the approved review
8. Create social draft: `POST /social/drafts` with the `contentItem.id` from step 7
9. Publish draft: `POST /social/drafts/{draftId}/publish` — enqueues the draft for publishing

### Batch Content Generation
1. Get short-form options: `GET /agents/short-form/options`
2. Generate multiple videos with different sources/voices
3. Monitor all jobs: `GET /render-jobs?status=processing`
4. Submit a batch review with all completed video URLs
5. After approval, promote each review: `POST /reviews/{reviewId}/promote`
6. Generate social content and create drafts for each platform using the `contentItem.id` from step 5
7. Publish each draft: `POST /social/drafts/{draftId}/publish`

## Notes

- Job IDs are UUIDs returned when creating render jobs
- Video generation is async — poll `/render-jobs/{id}` for completion
- Review statuses can be set by humans in the dashboard or via the public share link
- Agents can generate share URLs with `POST /reviews/{id}/share` and send them to humans for on-demand feedback
- Rate limits apply — avoid rapid-fire requests
- The `saveToLibrary` flag on video generation automatically creates a content item
- Default aspect ratio is `9:16` (vertical/portrait) for short-form content
- Voice selection affects the TTS narration of generated videos
