# Evolink Music API — Parameter Reference

Complete API parameter reference for music generation tools.

**Base URL:** `https://api.evolink.ai`
**Auth:** `Authorization: Bearer {EVOLINK_API_KEY}`
**All generation endpoints are async** — they return `task_id` immediately; poll with `check_task`.

---

## generate_music

**Endpoint:** `POST /v1/audios/generations`

### Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `prompt` | string | **Yes** | — | **Simple mode:** music description (max 500 chars). **Custom mode:** full lyrics with section tags like `[Verse]`, `[Chorus]`, `[Bridge]`, `[Outro]` (max 3000 chars for v4, 5000 for v4.5+). |
| `model` | enum | No | `suno-v4` | See Music Models below. |
| `custom_mode` | boolean | **Yes** | — | `false` = AI generates lyrics and style from your description. `true` = you control style, title, and lyrics. **No default — always set explicitly.** |
| `instrumental` | boolean | **Yes** | — | `true` = no vocals (instrumental only). `false` = with vocals. **No default — always set explicitly.** |
| `style` | string | No* | — | Comma-separated genre/mood/tempo tags. e.g. `"pop, upbeat, female vocals, 120bpm"`. *Required when `custom_mode: true`. |
| `title` | string | No* | — | Song title. Max 80 characters. *Required when `custom_mode: true`. |
| `negative_tags` | string | No | — | Styles to exclude. e.g. `"heavy metal, distorted guitar"`. |
| `vocal_gender` | enum | No | — | `m` (male) or `f` (female). Only effective in custom mode. |
| `duration` | integer | No | model decides | Target length in seconds (30–240s). |

### Two Modes

**Simple mode** (`custom_mode: false`):
- Provide a text description in `prompt`
- AI automatically generates lyrics, picks style and arrangement
- Easiest to use — just describe what you want

**Custom mode** (`custom_mode: true`):
- Write full lyrics in `prompt` with section markers: `[Verse]`, `[Chorus]`, `[Bridge]`, `[Outro]`
- Set `style` (genre/mood/tempo tags) and `title` (required in custom mode)
- Optionally set `vocal_gender` for male/female vocals

### Music Models (5, all BETA)

| Model | Quality | Max duration | Notes |
|-------|---------|--------------|-------|
| `suno-v4` *(default)* | Good | 120s | Balanced quality, economical |
| `suno-v4.5` | Better | 240s | Improved style control |
| `suno-v4.5plus` | Better | 240s | Extended v4.5 features |
| `suno-v4.5all` | Better | 240s | Full v4.5 feature set |
| `suno-v5` | Best | 240s | Studio-grade, best quality |

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
| `results[]` | string[] | Direct result URLs — audio file download links |
| `result_data[].audio_url` | string | Audio download URL |
| `result_data[].stream_audio_url` | string | Streaming audio URL |
| `result_data[].title` | string | Music track title |
| `result_data[].duration` | number | Duration in seconds |
| `result_data[].tags` | string | Auto-generated style tags |
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

- **Supported:** Audio — MP3, WAV, FLAC, AAC, OGG, M4A, etc.
- **Max size:** 100MB
- **Expiry:** 72 hours
- **Quota:** 100 files (default) / 500 (VIP)

---

## Polling Strategy

| Type | Initial wait | Poll interval | Max wait |
|------|-------------|---------------|----------|
| Music | 5s | 5–10s | 5 minutes |

1. Submit `generate_music` → receive `task_id`
2. Wait 5 seconds
3. Call `check_task` → inspect `status`
4. If `pending`/`processing`: wait 5–10s, repeat
5. If `completed`: extract URLs from `results[]` + metadata from `result_data[]`
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
| `content_policy_violation` | No | Rephrase prompt or lyrics; avoid explicit content |
| `invalid_parameters` | No | Check param values — ensure `custom_mode` and `instrumental` are set |
| `model_unavailable` | No | Use `list_models` to find alternatives |
| `generation_timeout` | Yes | Retry; simplify prompt if repeated |
| `quota_exceeded` | Yes | Top up at evolink.ai/dashboard/billing |
| `resource_exhausted` | Yes | Wait 30–60s, retry |
| `service_error` | Yes | Retry after 1 minute |
| `generation_failed_no_content` | Yes | Modify prompt, retry |
| `upstream_error` | Yes | Retry after 1 minute |
| `unknown_error` | Yes | Retry; contact support if persistent |
