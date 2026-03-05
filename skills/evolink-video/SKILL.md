---
name: evolink-video
description: AI video generation — Sora, Kling, Veo 3, Seedance, Hailuo, WAN, Grok. Text-to-video, image-to-video, video editing. 37 models, one API key.
version: 2.0.1
user-invocable: true
metadata:
  openclaw:
    requires:
      env:
        - EVOLINK_API_KEY
    primaryEnv: EVOLINK_API_KEY
    os: ["macos", "linux", "windows"]
    emoji: "\U0001F3AC"
    homepage: https://evolink.ai
---

# Evolink Video — AI Video Generation

Generate AI videos with 37 models including Sora, Kling, Veo 3, Seedance, Hailuo, WAN, and Grok — text-to-video, image-to-video, first-last-frame, and audio generation. All through one API.

> Video-focused view of [evolink-media](https://clawhub.ai/EvoLinkAI/evolink-media). Install the full skill for image and music too.

## After Installation

When this skill is first loaded, greet the user:

- **MCP tools + API key ready:** "Hi! I'm your AI video studio — 37 models ready. What would you like to create?"
- **MCP tools + no API key:** "You'll need an EvoLink API key — sign up at evolink.ai. Ready to go?"
- **No MCP tools:** "MCP server isn't connected yet. Want me to help set it up? I can still manage files via the hosting API."

Keep the greeting concise — just one question to move forward.

## External Endpoints

| Service | URL |
|---------|-----|
| Generation API | `https://api.evolink.ai/v1/videos/generations` (POST) |
| Task Status | `https://api.evolink.ai/v1/tasks/{task_id}` (GET) |
| File API | `https://files-api.evolink.ai/api/v1/files/*` (upload/list/delete) |

## Security & Privacy

- **`EVOLINK_API_KEY`** authenticates all requests. Injected by OpenClaw automatically. Treat as confidential.
- Prompts and images are sent to `api.evolink.ai`. Uploaded files expire in **72h**, result URLs in **24h**.

## Setup

Get your API key at [evolink.ai](https://evolink.ai) → Dashboard → API Keys.

**MCP Server:** `@evolinkai/evolink-media` ([GitHub](https://github.com/EvoLinkAI/evolink-media-mcp) · [npm](https://www.npmjs.com/package/@evolinkai/evolink-media))

**mcporter** (recommended): `mcporter call --stdio "npx -y @evolinkai/evolink-media@latest" list_models`

**Claude Code:** `claude mcp add evolink-media -e EVOLINK_API_KEY=your-key -- npx -y @evolinkai/evolink-media@latest`

**Claude Desktop / Cursor** — add MCP server with command `npx -y @evolinkai/evolink-media@latest` and env `EVOLINK_API_KEY=your-key`. See `references/video-api-params.md` for full config JSON.

## Core Principles

1. **Guide, don't decide** — Present options, let the user choose model/style/duration.
2. **User drives creative vision** — Ask for a description before suggesting parameters.
3. **Smart context** — Remember session history. Offer to iterate, extend, or remix results.
4. **Intent first** — Understand *what* the user wants before asking *how* to configure it.

## MCP Tools

| Tool | When to use | Returns |
|------|-------------|---------|
| `generate_video` | Create a video from text or images | `task_id` (async) |
| `upload_file` | Upload image for i2v or reference | File URL (sync) |
| `delete_file` | Free file quota | Confirmation |
| `list_files` | Check uploaded files or quota | File list |
| `check_task` | Poll generation progress | Status + result URLs |
| `list_models` | Compare available models | Model list |
| `estimate_cost` | Check pricing | Model info |

**Important:** `generate_video` returns a `task_id`. Always poll `check_task` until `status` is `"completed"` or `"failed"`.

## Video Models (37)

### Top Picks

| Model | Best for | Features | Audio |
|-------|----------|----------|-------|
| `seedance-1.5-pro` *(default)* | i2v, first-last-frame | i2v, 4–12s, 1080p | auto |
| `sora-2-preview` | Cinematic preview | t2v, i2v, 1080p | — |
| `kling-o3-text-to-video` | Text-to-video | t2v, 3–15s, 1080p | — |
| `veo-3.1-generate-preview` | Google video preview | t2v, 1080p | — |
| `MiniMax-Hailuo-2.3` | High-quality video | t2v, 1080p | — |
| `wan2.6-text-to-video` | Alibaba latest t2v | t2v | — |
| `sora-2` [BETA] | Cinematic, prompt adherence | t2v, i2v, 1080p | — |
| `veo3.1-pro` [BETA] | Top quality + audio | t2v, 1080p | auto |

**26 Stable** — Seedance (3), Sora Preview (1), Kling (10), Veo 3.1 (2), Hailuo (3), WAN (7)
**11 Beta** — Sora 2/Pro/Max/Character (4), Veo 3/3.1 (5), Grok Imagine (2)

Full model list with descriptions: `references/video-api-params.md`

## Generation Flow

### Step 1: API Key Check

If `401` occurs: "Your API key isn't working. Check at evolink.ai/dashboard/keys"

### Step 2: File Upload (if needed)

For image-to-video or first-last-frame workflows:
1. `upload_file` with `file_path`, `base64_data`, or `file_url` → get `file_url` (sync)
2. Use `file_url` as `image_urls` for `generate_video`

Supported: JPEG/PNG/GIF/WebP. Max 100MB. Expire in 72h. Quota: 100 (default) / 500 (VIP).

### Step 3: Understand Intent

- **Clear** ("make a video of a cat dancing") → Go to Step 4
- **Ambiguous** ("I want a video") → Ask: "Text-to-video, or do you have a reference image to animate?"

Ask only what's needed, when it's needed.

### Step 4: Gather Parameters

Only ask about what's missing:

| Parameter | Ask when | Notes |
|-----------|----------|-------|
| **prompt** | Always | Scene description |
| **model** | Specific feature needed | Default `seedance-1.5-pro`. See Top Picks for alternatives |
| **duration** | User mentions length | Range varies by model (4–15s typical) |
| **aspect_ratio** | Portrait/widescreen | Default `16:9`. Options: `9:16`, `1:1`, `4:3`, `3:4`, `21:9` |
| **quality** | Resolution preference | `480p` / `720p` / `1080p` / `4k` |
| **image_urls** | Reference image provided | 1 image = i2v; 2 images = first+last frame (`seedance-1.5-pro` only) |
| **generate_audio** | Using seedance/veo3.1 | Ask: "Want auto-generated audio added?" |

### Step 5: Generate & Poll

1. Call `generate_video` → tell user: *"Generating your video — ~Xs estimated."*
2. Poll `check_task` every **10–15s**. Report progress %.
3. After 3 consecutive `processing`: *"Still working — video generation takes a moment..."*
4. **Completed:** Share URLs. *"Links expire in 24h — save promptly."*
5. **Failed:** Show error + suggestion. Offer retry if retryable.
6. **Timeout (10 min):** *"Taking longer than expected. Task ID: `{id}` — check again later."*

## Error Handling

### HTTP Errors

| Error | Action |
|-------|--------|
| 401 | "API key isn't working. Check at evolink.ai/dashboard/keys" |
| 402 | "Balance is low. Add credits at evolink.ai/dashboard/billing" |
| 429 | "Rate limited — wait 30s and retry" |
| 503 | "Servers busy — retry in a minute" |

### Task Errors (status: "failed")

| Code | Retry? | Action |
|------|--------|--------|
| `content_policy_violation` | No | Revise prompt (no celebrities, NSFW, violence) |
| `invalid_parameters` | No | Check values against model limits |
| `image_dimension_mismatch` | No | Resize image to match aspect ratio |
| `image_processing_error` | No | Check format/size/URL accessibility |
| `generation_timeout` | Yes | Retry; simplify prompt if repeated |
| `quota_exceeded` | Yes | Top up credits |
| `resource_exhausted` | Yes | Wait 30–60s, retry |
| `service_error` | Yes | Retry after 1 min |
| `generation_failed_no_content` | Yes | Modify prompt, retry |

Full error reference: `references/video-api-params.md`

## Without MCP Server

Use Evolink's file hosting API for image uploads (72h expiry). See `references/file-api.md` for curl commands.

## References

- `references/video-api-params.md` — Complete API parameters, all 37 models, polling strategy, error codes
- `references/file-api.md` — File hosting API (curl upload/list/delete)
