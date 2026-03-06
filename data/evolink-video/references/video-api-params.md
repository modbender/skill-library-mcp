# Evolink Video API — Parameter Reference

Complete API parameter reference for video generation tools.

**Base URL:** `https://api.evolink.ai`
**Auth:** `Authorization: Bearer {EVOLINK_API_KEY}`
**All generation endpoints are async** — they return `task_id` immediately; poll with `check_task`.

---

## generate_video

**Endpoint:** `POST /v1/videos/generations`

### Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `prompt` | string | **Yes** | — | Video description. Max 5000 characters. |
| `model` | enum | No | `seedance-1.5-pro` | See Video Models below. |
| `duration` | integer | No | model default | Duration in seconds. Range varies by model. |
| `quality` | enum | No | model default | `480p` / `720p` / `1080p` / `4k`. Availability varies by model. |
| `aspect_ratio` | enum | No | `16:9` | `16:9` / `9:16` / `1:1` / `4:3` / `3:4` / `21:9` / `adaptive` |
| `image_urls` | string[] | No | — | Reference images. **1 image** = image-to-video. **2 images** = first-frame + last-frame (`seedance-1.5-pro` only). Max 9 images. JPEG/PNG/WebP, ≤30MB each. |
| `generate_audio` | boolean | No | model default | Auto-generate synchronized audio. Supported by `seedance-1.5-pro` (default: `true`) and `veo3.1-pro` [BETA]. |

### Video Models (37)

#### Stable (26)

| Model | Description | Key features |
|-------|-------------|--------------|
| `seedance-1.5-pro` *(default)* | ByteDance Seedance 1.5 Pro | t2v, i2v, first-last-frame, 4–12s, 1080p, audio |
| `seedance-2.0` | ByteDance Seedance 2.0 (placeholder, API pending) | t2v, i2v |
| `doubao-seedance-1.0-pro-fast` | ByteDance Seedance 1.0 Pro Fast | t2v, fast |
| `sora-2-preview` | OpenAI Sora 2 Preview | t2v, i2v, 1080p |
| `kling-o3-text-to-video` | Kuaishou Kling O3 — text-to-video | t2v, 3–15s, 1080p |
| `kling-o3-image-to-video` | Kuaishou Kling O3 — image-to-video | i2v, 1080p |
| `kling-o3-reference-to-video` | Kuaishou Kling O3 — reference-guided | ref2v, 1080p |
| `kling-o3-video-edit` | Kuaishou Kling O3 — video editing | video-edit, 1080p |
| `kling-v3-text-to-video` | Kuaishou Kling V3 — text-to-video | t2v, 1080p |
| `kling-v3-image-to-video` | Kuaishou Kling V3 — image-to-video | i2v, 1080p |
| `kling-o1-image-to-video` | Kuaishou Kling O1 — image-to-video | i2v |
| `kling-o1-video-edit` | Kuaishou Kling O1 — video editing | video-edit |
| `kling-o1-video-edit-fast` | Kuaishou Kling O1 — fast video editing | video-edit, fast |
| `kling-custom-element` | Kuaishou Kling — custom element video | custom-element |
| `veo-3.1-generate-preview` | Google Veo 3.1 — generation preview | t2v, 1080p |
| `veo-3.1-fast-generate-preview` | Google Veo 3.1 — fast generation preview | t2v, fast, 1080p |
| `MiniMax-Hailuo-2.3` | MiniMax Hailuo 2.3 — high-quality | t2v, 1080p |
| `MiniMax-Hailuo-2.3-Fast` | MiniMax Hailuo 2.3 Fast | t2v, fast, 1080p |
| `MiniMax-Hailuo-02` | MiniMax Hailuo 02 | t2v |
| `wan2.5-t2v-preview` | Alibaba WAN 2.5 — t2v preview | t2v |
| `wan2.5-i2v-preview` | Alibaba WAN 2.5 — i2v preview | i2v |
| `wan2.5-text-to-video` | Alibaba WAN 2.5 — text-to-video | t2v |
| `wan2.5-image-to-video` | Alibaba WAN 2.5 — image-to-video | i2v |
| `wan2.6-text-to-video` | Alibaba WAN 2.6 — text-to-video | t2v |
| `wan2.6-image-to-video` | Alibaba WAN 2.6 — image-to-video | i2v |
| `wan2.6-reference-video` | Alibaba WAN 2.6 — reference-guided | ref2v |

#### Beta (11)

| Model | Description | Key features |
|-------|-------------|--------------|
| `sora-2` [BETA] | OpenAI Sora 2 — cinematic video | t2v, i2v, 1080p |
| `sora-2-pro` [BETA] | OpenAI Sora 2 Pro — premium cinematic | t2v, i2v, 1080p, premium |
| `sora-2-beta-max` [BETA] | OpenAI Sora 2 Beta Max — maximum quality | t2v, 1080p, max-quality |
| `sora-character` [BETA] | OpenAI Sora Character — character-consistent | t2v, character-consistency |
| `veo3.1-pro` [BETA] | Google Veo 3.1 Pro — top-tier cinematic + audio | t2v, 1080p, audio |
| `veo3.1-fast` [BETA] | Google Veo 3.1 Fast — fast high-quality | t2v, fast, 1080p |
| `veo3.1-fast-extend` [BETA] | Google Veo 3.1 Fast Extend — extended generation | t2v, fast, extend |
| `veo3` [BETA] | Google Veo 3 — cinematic video | t2v, 1080p |
| `veo3-fast` [BETA] | Google Veo 3 Fast — fast video | t2v, fast |
| `grok-imagine-text-to-video` [BETA] | xAI Grok Imagine — text-to-video | t2v |
| `grok-imagine-image-to-video` [BETA] | xAI Grok Imagine — image-to-video | i2v |

---

## check_task

**Endpoint:** `GET /v1/tasks/{task_id}`

### Response Fields

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Task ID |
| `model` | string | Model used for generation |
| `status` | enum | `pending` / `processing` / `completed` / `failed` |
| `progress` | integer | Progress percentage (0–100) |
| `results[]` | string[] | Direct result URLs — video MP4 download links |
| `result_data[].video_url` | string | Video download URL |
| `task_info.estimated_time` | integer | Estimated seconds remaining |
| `task_info.can_cancel` | boolean | Whether the task can be cancelled |
| `usage.credits_reserved` | number | Credits charged for this task |
| `error.code` | string | Error code (only when `status: "failed"`) |
| `error.message` | string | Error description (only when `status: "failed"`) |

All result URLs expire in **24 hours**.

### Status Values

| Status | Meaning | Action |
|--------|---------|--------|
| `pending` | Queued, not started | Continue polling |
| `processing` | Generation in progress | Continue polling, report `progress` |
| `completed` | Generation finished | Extract URLs from `results[]` or `result_data[]` |
| `failed` | Generation failed | Read `error.code` + `error.message`, surface to user |

---

## File Management API

**Base URL:** `https://files-api.evolink.ai`
**Auth:** `Authorization: Bearer {EVOLINK_API_KEY}` (same API key)

All file endpoints are **synchronous**.

### upload_file

| Method | Endpoint | Use when |
|--------|----------|----------|
| Base64 | `POST /api/v1/files/upload/base64` | Have base64 data |
| Stream | `POST /api/v1/files/upload/stream` | Have a local file |
| URL | `POST /api/v1/files/upload/url` | Have a remote URL |

**MCP Tool Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `file_path` | string | One of three | Local file path |
| `base64_data` | string | One of three | Base64-encoded data |
| `file_url` | string | One of three | Remote URL |

### File Constraints

- **Supported:** Images (JPEG/PNG/GIF/WebP), Video (all formats)
- **Max size:** 100MB
- **Expiry:** 72 hours
- **Quota:** 100 files (default) / 500 (VIP)

---

## Polling Strategy

| Type | Initial wait | Poll interval | Max wait |
|------|-------------|---------------|----------|
| Video | 15s | 10–15s | 10 minutes |

1. Submit `generate_video` → receive `task_id`
2. Wait 15 seconds
3. Call `check_task` → inspect `status`
4. If `pending`/`processing`: wait 10–15s, repeat
5. If `completed`: extract URLs from `results[]` or `result_data[].video_url`
6. If `failed`: read `error.code`, surface to user

---

## Error Codes

### HTTP Status Codes

| Code | Meaning | Resolution |
|------|---------|------------|
| 400 | Bad request | Check required fields; revise prompt |
| 401 | Invalid API key | Verify at evolink.ai/dashboard/keys |
| 402 | Insufficient credits | Top up at evolink.ai/dashboard/billing |
| 429 | Rate limit exceeded | Wait 30–60s, retry |
| 500 | Server error | Retry after 1 minute |
| 503 | Service unavailable | Retry after 1–2 minutes |

### Task Error Codes

| Code | Retryable | Resolution |
|------|-----------|------------|
| `content_policy_violation` | No | Rephrase prompt; avoid NSFW, violence, real person names |
| `invalid_parameters` | No | Check param values against model limits |
| `image_dimension_mismatch` | No | Resize image to match requested aspect ratio |
| `image_processing_error` | No | Check format (JPG/PNG/WebP), size (<30MB), URL accessibility |
| `model_unavailable` | No | Use `list_models` to find alternatives |
| `generation_timeout` | Yes | Retry; simplify prompt or lower resolution if repeated |
| `quota_exceeded` | Yes | Top up at evolink.ai/dashboard/billing |
| `resource_exhausted` | Yes | Wait 30–60s, retry |
| `service_error` | Yes | Retry after 1 minute |
| `generation_failed_no_content` | Yes | Modify prompt, retry |
| `upstream_error` | Yes | Retry after 1 minute |
| `unknown_error` | Yes | Retry; contact support if persistent |
