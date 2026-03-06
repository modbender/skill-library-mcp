# xAI Grok Imagine API Reference

Based on:
- https://docs.x.ai/developers/model-capabilities/images/generation
- https://docs.x.ai/developers/model-capabilities/video/generation

## Base URL
```
https://api.x.ai/v1
```

## Authentication
All requests require an Authorization header with your xAI API key:
```
Authorization: Bearer YOUR_XAI_API_KEY
```

Get your API key from: https://console.x.ai/

## Endpoints

---

## Image Generation

### Generate Images

**POST** `/images/generations`

Generate one or more images from a text prompt.

**Request Body:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `model` | string | Yes | Must be `"grok-imagine-image"` |
| `prompt` | string | Yes | Text description of desired image |
| `n` | integer | No | Number of variations (1-10). Default: 1 |
| `aspect_ratio` | string | No | `"1:1"`, `"16:9"`, `"9:16"`, `"4:3"`, `"3:4"`, `"3:2"`, `"2:3"`, `"2:1"`, `"1:2"`, `"19.5:9"`, `"9:19.5"`, `"20:9"`, `"9:20"`, or `"auto"`. Default: `"1:1"` |
| `response_format` | string | No | `"url"` for temporary URL or `"b64_json"` for base64 data. Default: `"url"` |

**Example:**
```json
{
  "model": "grok-imagine-image",
  "prompt": "A collage of London landmarks in a stenciled street-art style",
  "n": 1,
  "aspect_ratio": "16:9"
}
```

**Response:**
```json
{
  "data": [
    {
      "url": "https://...",
      "respect_moderation": true
    }
  ],
  "model": "grok-imagine-image"
}
```

### Edit Images

**POST** `/images/edits`

Edit an existing image via natural language instruction.

**Request Body:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `model` | string | Yes | Must be `"grok-imagine-image"` |
| `prompt` | string | Yes | Natural language edit instruction |
| `image` | object | Yes | `{"url": "...", "type": "image_url"}` with a public URL or base64 data URI |
| `n` | integer | No | Number of variations (1-10). Default: 1 |
| `response_format` | string | No | `"url"` or `"b64_json"`. Default: `"url"` |

**Example:**
```json
{
  "model": "grok-imagine-image",
  "prompt": "Change the landmarks to be New York City landmarks",
  "image": {"url": "https://example.com/london.jpg", "type": "image_url"}
}
```

---

## Video Generation

### Start Video Generation

**POST** `/videos/generations`

Single endpoint for all video generation modes: text-to-video, image-to-video, and video editing. The mode is determined by which fields are provided.

**Request Body:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `model` | string | Yes | Must be `"grok-imagine-video"` |
| `prompt` | string | Yes | Text description or edit instruction |
| `duration` | integer | No | Duration in seconds (1-15). Default: 10. Ignored for video editing. |
| `aspect_ratio` | string | No | `"16:9"`, `"9:16"`, `"1:1"`, `"4:3"`, `"3:4"`, `"3:2"`, `"2:3"`. Default: `"16:9"` for text-to-video; editing uses source dimensions. |
| `resolution` | string | No | `"480p"` or `"720p"`. Default: `"480p"`. Editing capped at 720p. |
| `image` | object | No | For image-to-video: `{"url": "..."}` with a public URL or base64 data URI |
| `video_url` | string | No | For video editing: URL of the source video |

**Mode selection:**
- Text-to-video: provide `prompt` only (no `image` or `video_url`)
- Image-to-video: provide `prompt` + `image`
- Video editing: provide `prompt` + `video_url`

**Example — Text-to-video:**
```json
{
  "model": "grok-imagine-video",
  "prompt": "A beautiful sunset over the ocean",
  "duration": 10,
  "aspect_ratio": "16:9",
  "resolution": "720p"
}
```

**Example — Image-to-video:**
```json
{
  "model": "grok-imagine-video",
  "prompt": "Make the clouds move gently",
  "image": {"url": "https://example.com/image.jpg"},
  "duration": 10
}
```

**Example — Video editing:**
```json
{
  "model": "grok-imagine-video",
  "prompt": "Add a warm sunset filter and slow down the motion",
  "video_url": "https://example.com/video.mp4"
}
```

**Response:**
```json
{
  "request_id": "d97415a1-5796-b7ec-379f-4e6819e08fdf"
}
```

### Check Generation Status

**GET** `/videos/{request_id}`

Poll this endpoint to check if your video is ready.

**Response (pending):**
```json
{
  "status": "pending",
  "model": "grok-imagine-video"
}
```

**Response (done):**
```json
{
  "status": "done",
  "video": {
    "url": "https://vidgen.x.ai/.../video.mp4",
    "duration": 8,
    "respect_moderation": true
  },
  "model": "grok-imagine-video"
}
```

**Response (expired):**
```json
{
  "status": "expired",
  "model": "grok-imagine-video"
}
```

**Status values:**
- `pending`: Job is queued or processing
- `done`: Video is ready — download promptly as URLs are temporary
- `expired`: Request has expired

## Error Codes

| Code | Description |
|------|-------------|
| `unauthorized` | Invalid or missing API key |
| `rate_limit_exceeded` | Too many requests (60/min) |
| `invalid_prompt` | Prompt format or content is invalid |
| `content_policy_violation` | Prompt violates content policies |
| `invalid_image_url` | Image URL is inaccessible or invalid |
| `invalid_video_url` | Video URL is inaccessible or invalid |
| `invalid_parameters` | One or more parameters are out of range |
| `internal_error` | Server-side error |

## Rate Limits

- 60 requests per minute per API key
- Max 15 concurrent jobs per account

## Key Constraints

### Images
- Maximum 10 images per request
- Image URLs are temporary — download promptly after generation
- Image editing charges for both input and output images
- All images subject to content moderation

### Videos
- Text/image-to-video duration: 1-15 seconds
- Video editing: max 8.7 seconds input video
- Video editing output matches source aspect ratio and resolution (capped at 720p)
- Video URLs are temporary — download promptly after generation
- All videos subject to content moderation

## Content Policy

The API rejects prompts containing:
- Explicit sexual content
- Hate speech or harassment
- Violence or gore
- Illegal activities
- Copyrighted material

## Image Specifications

### Supported Aspect Ratios
- 1:1: Square (default)
- 16:9, 9:16: Landscape/Portrait
- 4:3, 3:4, 3:2, 2:3: Standard ratios
- 2:1, 1:2: Wide/Tall
- 19.5:9, 9:19.5, 20:9, 9:20: Ultra-wide/tall
- auto: Automatic selection

### Output Formats
- URL: Temporary download link (default)
- b64_json: Base64-encoded image data

---

## Video Specifications

### Supported Resolutions
- 480p (default, faster generation)
- 720p (higher quality)

### Aspect Ratios
- 16:9: Landscape (default for text-to-video)
- 9:16: Portrait
- 1:1: Square
- 4:3, 3:4, 3:2, 2:3: Additional ratios

### Duration Range
- Minimum: 1 second
- Maximum: 15 seconds
- Recommended: 5-10 seconds

### File Formats
- Output: MP4 (H.264 codec, AAC audio)
- Audio: Auto-generated with dialogue, ambience, and SFX
