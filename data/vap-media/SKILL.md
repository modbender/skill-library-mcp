---
name: vap-media
description: AI image, video, and music generation + editing via VAP API. Flux, Veo 3.1, Suno V5.
metadata: {"openclaw":{"emoji":"🎬","requires":{"bins":["curl"]},"primaryEnv":"VAP_API_KEY"},"source":"https://github.com/vapagentmedia/vap-showcase","homepage":"https://vapagent.com"}
---

# VAP Media - AI Media Generation & Editing

> **Integration Note:** VAP Media is an API aggregator that provides unified access to multiple AI providers:
> - **Images:** Generated via Black Forest Labs Flux.2 Pro
> - **Videos:** Generated via Google Veo 3.1
> - **Music:** Generated via Suno V5
> 
> All generation requests go through VAP's API (`api.vapagent.com`), which routes to the appropriate backend provider.

Generate images, videos, and music. Edit with inpaint, ai_edit, upscale, background removal, video trim/merge.

## Mode Selection

Check if `VAP_API_KEY` is set:

- **VAP_API_KEY not set** → Use Free Mode (images only, 3/day)
- **VAP_API_KEY set** → Use Full Mode (all features, unlimited)

---

## Free Mode (No API Key)

Generate images for free. No signup required. 3 per day.

### Generate Image

```bash
curl -s -X POST https://api.vapagent.com/v3/trial/generate \
  -H "Content-Type: application/json" \
  -d '{"prompt":"PROMPT"}'
```

Returns `{"task_id":"UUID","status":"pending","remaining":2}`.

### Poll Result

```bash
curl -s https://api.vapagent.com/v3/trial/status/TASK_ID
```

Returns `{"status":"completed","image_url":"https://..."}` when done.

### Free Mode Errors

- `429` → Daily limit reached. Suggest upgrading: `export VAP_API_KEY=vap_xxx`
- `503` → Trial service temporarily unavailable.

---

## Full Mode (With API Key)

Unlimited images, video, music, and editing operations.

### Create Task

```bash
curl -s -X POST https://api.vapagent.com/v3/tasks \
  -H "Authorization: Bearer $VAP_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"type":"TYPE","params":{"description":"PROMPT"}}'
```

Returns `{"task_id":"UUID","status":"pending"}`.

### Poll Result

```bash
curl -s https://api.vapagent.com/v3/tasks/TASK_ID \
  -H "Authorization: Bearer $VAP_API_KEY"
```

Returns `{"status":"completed","result":{"output_url":"https://..."}}` when done.

### Task Types & Parameters

#### Image (`image` or `image_generation`)

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| `description` | string | required | Image description |
| `aspect_ratio` | enum | `1:1` | `1:1`, `16:9`, `9:16`, `4:3`, `3:4`, `3:2`, `2:3`, `21:9`, `9:21` |
| `quality` | enum | `standard` | `standard` or `high` |

**Tip:** Aspect ratio is auto-detected from prompt text. "a wide landscape photo" → 16:9 automatically.

#### Video (`video` or `video_generation`) — Tier 2+

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| `description` | string | required | Video description |
| `duration` | int | `8` | `4`, `6`, or `8` seconds |
| `aspect_ratio` | enum | `16:9` | `16:9` (landscape) or `9:16` (portrait) |
| `generate_audio` | bool | `true` | Include audio track |
| `resolution` | enum | `720p` | `720p` or `1080p` |
| `negative_prompt` | string | `""` | What to avoid |

#### Music (`music` or `music_generation`) — Tier 2+

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| `description` | string | required | Music description (genre, mood, instruments) |
| `duration` | int | `120` | 30-480 seconds |
| `instrumental` | bool | `false` | No vocals |
| `audio_format` | enum | `mp3` | `mp3` or `wav` (lossless) |
| `loudness_preset` | enum | `streaming` | `streaming` (-14 LUFS), `apple` (-16 LUFS), `broadcast` (-23 LUFS) |
| `style` | string | none | Genre/style (max 1000 chars) |
| `title` | string | none | Song title |
| `custom_mode` | bool | `false` | Enable custom lyrics + style mode |

### Full Mode Errors

- `401` → Invalid API key.
- `402` → Insufficient balance. Top up at https://vapagent.com/dashboard/signup.html
- `403` → Tier too low for this task type.

---

## Operations (Edit & Enhance)

Post-production editing operations. Tier 1+ required.

### Create Operation

```bash
curl -s -X POST https://api.vapagent.com/v3/operations \
  -H "Authorization: Bearer $VAP_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"operation":"OPERATION","media_url":"URL","prompt":"INSTRUCTION"}'
```

### Poll Operation

```bash
curl -s https://api.vapagent.com/v3/operations/OPERATION_ID \
  -H "Authorization: Bearer $VAP_API_KEY"
```

### Available Operations

| Operation | Required Params | Description |
|-----------|-----------------|-------------|
| `inpaint` | `media_url`, `prompt` | AI editing (optional: `mask_url`) |
| `ai_edit` | `media_url`, `prompt` | AI-powered image editing with text instructions (optional: `additional_images`) |
| `background_remove` | `media_url` | Remove background |
| `upscale` | `media_url` | Enhance resolution (`scale`: 2 or 4) |
| `video_trim` | `media_url`, `start_time`, `end_time` | Trim video |
| `video_merge` | `media_urls` (array, min 2) | Merge video clips |

---

## Instructions

When a user asks to create/generate/make an image, video, or music:

1. **Improve the prompt** — Add style, lighting, composition, mood details
2. **Check mode** — Is `VAP_API_KEY` set?
3. **Choose endpoint**:
   - Single asset → `/v3/tasks` (or `/v3/trial/generate` for free)
   - Edit/enhance → `/v3/operations`
   - Campaign (video+music+thumbnail) → `/v3/execute` with preset
4. **Set aspect ratio** — Match the content need (portrait for social, widescreen for YouTube)
5. **Poll for result** — Check task/operation status until completed
6. **Return the media URL** to the user
7. If free mode limit is hit, tell the user: "You've used your 3 free generations today. For unlimited access, set up an API key: https://vapagent.com/dashboard/signup.html"

When a user asks to edit/enhance/modify an existing image or video:

1. **Identify the operation** — inpaint, ai_edit, upscale, background remove, trim, merge
2. **Get the media URL** — From a previous generation or user-provided URL
3. **Submit operation** → `/v3/operations`
4. **Poll for result** — Return the output URL

### Free Mode Example

```bash
# Create (no auth needed)
curl -s -X POST https://api.vapagent.com/v3/trial/generate \
  -H "Content-Type: application/json" \
  -d '{"prompt":"A fluffy orange tabby cat on a sunlit windowsill, soft bokeh, golden hour light, photorealistic"}'

# Poll
curl -s https://api.vapagent.com/v3/trial/status/TASK_ID
```

### Full Mode Examples

```bash
# Image (widescreen)
curl -s -X POST https://api.vapagent.com/v3/tasks \
  -H "Authorization: Bearer $VAP_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"type":"image","params":{"description":"A fluffy orange tabby cat on a sunlit windowsill, soft bokeh, golden hour light, photorealistic","aspect_ratio":"16:9"}}'

# Video (portrait, for social media)
curl -s -X POST https://api.vapagent.com/v3/tasks \
  -H "Authorization: Bearer $VAP_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"type":"video","params":{"description":"Drone shot over misty mountains at sunrise","duration":8,"aspect_ratio":"9:16","resolution":"1080p"}}'

# Music (instrumental WAV)
curl -s -X POST https://api.vapagent.com/v3/tasks \
  -H "Authorization: Bearer $VAP_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"type":"music","params":{"description":"Upbeat lo-fi hip hop beat, warm vinyl crackle, chill vibes","duration":120,"instrumental":true,"audio_format":"wav","loudness_preset":"streaming"}}'

# Inpaint (edit an image)
curl -s -X POST https://api.vapagent.com/v3/operations \
  -H "Authorization: Bearer $VAP_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"operation":"inpaint","media_url":"https://example.com/photo.jpg","prompt":"Remove the person in the background"}'

# Upscale (4x)
curl -s -X POST https://api.vapagent.com/v3/operations \
  -H "Authorization: Bearer $VAP_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"operation":"upscale","media_url":"https://example.com/photo.jpg","options":{"scale":4}}'

# Background Remove
curl -s -X POST https://api.vapagent.com/v3/operations \
  -H "Authorization: Bearer $VAP_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"operation":"background_remove","media_url":"https://example.com/photo.jpg"}'

# Poll (use task_id or operation_id from response)
curl -s https://api.vapagent.com/v3/tasks/TASK_ID \
  -H "Authorization: Bearer $VAP_API_KEY"
```

### Production Presets (Multi-Asset)

For content campaigns, use `/v3/execute` to generate multiple assets from one prompt:

```bash
curl -s -X POST https://api.vapagent.com/v3/execute \
  -H "Authorization: Bearer $VAP_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"preset":"streaming_campaign","prompt":"PROMPT"}'
```

Returns all assets when complete:
```json
{"status":"completed","outputs":{"video":"https://...","music":"https://...","thumbnail":"https://..."}}
```

| Preset | Includes |
|--------|----------|
| `streaming_campaign` | video + music + thumbnail + metadata |
| `full_production` | video + music + thumbnail + metadata + SEO |
| `video.basic` | video only |
| `music.basic` | music only |
| `image.basic` | image only |

---

## Prompt Tips

- **Style:** "oil painting", "3D render", "watercolor", "photograph", "flat illustration"
- **Lighting:** "golden hour", "neon lights", "soft diffused light", "dramatic shadows"
- **Composition:** "close-up", "aerial view", "wide angle", "rule of thirds"
- **Mood:** "serene", "energetic", "mysterious", "whimsical"
- **Aspect ratio in prompt:** Mentioning "widescreen", "portrait", or "16:9" in your prompt auto-sets the aspect ratio.

## Setup (Optional — for Full Mode)

1. Sign up: https://vapagent.com/dashboard/signup.html
2. Get API key from dashboard
3. Set: `export VAP_API_KEY=vap_xxxxxxxxxxxxxxxxxxxx`

## Links

- [Try Free](https://vapagent.com/try)
- [API Docs](https://api.vapagent.com/docs)
- [GitHub](https://github.com/vapagentmedia/vap-showcase)