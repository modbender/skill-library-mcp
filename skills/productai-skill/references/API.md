# ProductAI API Reference

Complete documentation for ProductAI.photo public API endpoints.

## Base URL

```
https://api.productai.photo/v1
```

## Authentication

All API requests require authentication via the `x-api-key` header:

```bash
curl -H "x-api-key: YOUR_API_KEY" https://api.productai.photo/v1/api/generate
```

**Rate Limiting:** 15 requests per minute per IP address.

---

## `/api/generate` — Generate AI Product Photos

Generate an AI-edited image from one or more input images with a text prompt.

### Endpoint

```
POST /api/generate
```

### Request Body

| Field           | Type                   | Required | Description                                                                                                                                                                              |
| --------------- | ---------------------- | -------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `image_url`     | `string` or `string[]` | Yes      | URL(s) of input image(s). Maximum 2 images.                                                                                                                                              |
| `prompt`        | `string`               | Yes      | Text prompt describing the desired edit/generation.                                                                                                                                      |
| `model`         | `string`               | Yes      | One of: `gpt-low`, `gpt-medium`, `gpt-high`, `kontext-pro`, `kontext-max`, `nanobanana`, `nanobananapro`, `seedream`                                                                    |
| `output_format` | `string`               | No       | `"png"` (default) or `"jpg"` / `"jpeg"`                                                                                                                                                 |
| `aspect_ratio`  | `string`               | No       | `"SQUARE"`, `"LANDSCAPE"`, `"PORTRAIT"`. For `nanobanana`/`nanobananapro` also supports: `"LANDSCAPE_4_3"`, `"LANDSCAPE_5_4"`, `"SQUARE_1_1"`, `"PORTRAIT_4_5"`, `"PORTRAIT_3_4"`, or direct ratios like `"4:3"`, `"9:16"`, etc. |
| `resolution`    | `string`               | No       | For `nanobanana`/`nanobananapro` only: `"1K"`, `"2K"` (default), or `"4K"`                                                                                                               |

### Models & Pricing

| Model          | Credits | Engine        |
| -------------- | ------- | ------------- |
| `gpt-low`      | 2       | GPT (Lambda)  |
| `gpt-medium`   | 3       | GPT (Lambda)  |
| `gpt-high`     | 8       | GPT (Lambda)  |
| `kontext-pro`  | 2       | FAL           |
| `kontext-max`  | 3       | FAL           |
| `nanobanana`   | 3       | FAL           |
| `nanobananapro`| 8       | FAL           |
| `seedream`     | 3       | FAL           |

### Example Request (Single Image)

```bash
curl -X POST https://api.productai.photo/v1/api/generate \
  -H "x-api-key: YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "image_url": "https://example.com/photo.jpg",
    "prompt": "Make the background a sunset beach",
    "model": "nanobananapro",
    "output_format": "png",
    "aspect_ratio": "LANDSCAPE",
    "resolution": "2K"
  }'
```

### Example Request (Multiple Images)

```bash
curl -X POST https://api.productai.photo/v1/api/generate \
  -H "x-api-key: YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "image_url": ["https://example.com/product1.jpg", "https://example.com/product2.jpg"],
    "prompt": "Place the first product on top of the second product",
    "model": "nanobanana",
    "output_format": "png"
  }'
```

### Response

```json
{
  "status": "OK",
  "data": {
    "id": 12345,
    "status": "RUNNING",
    "prompt": "Make the background a sunset beach"
  }
}
```

**Note:** Generation is **asynchronous** — use the job ID to poll for completion via `/api/job/:jobId`.

### Status Codes

| Code | Meaning |
|------|---------|
| `200` | Job created successfully |
| `400` | Invalid request (check image URLs, prompt, model) |
| `401` | Invalid API key |
| `429` | Rate limit exceeded (max 15 requests/minute) |
| `402` | Insufficient tokens |
| `500` | Server error |

---

## `/api/job/:jobId` — Check Job Status

Check the status of a generation job and retrieve the result.

### Endpoint

```
GET /api/job/:jobId
```

### Authentication

Requires `x-api-key` header. The job must belong to the authenticated user.

### Example Request

```bash
curl -H "x-api-key: YOUR_API_KEY" \
  https://api.productai.photo/v1/api/job/12345
```

### Response (In Progress)

```json
{
  "status": "OK",
  "data": {
    "id": 12345,
    "status": "RUNNING",
    "prompt": "Make the background a sunset beach"
  }
}
```

### Response (Completed)

```json
{
  "status": "OK",
  "data": {
    "id": 12345,
    "status": "COMPLETED",
    "prompt": "Make the background a sunset beach",
    "image_url": "https://cdn.productai.photo/generated/result.png"
  }
}
```

### Job Status Values

| Status | Description |
|--------|-------------|
| `NOT_STARTED` | Job queued but not processing yet |
| `RUNNING` | Currently generating |
| `COMPLETED` | Finished — `image_url` available |
| `ERROR` | Failed — check logs or contact support |

**Note:** The `image_url` field only appears when status is `"COMPLETED"`.

---

## `/api/upscale` — Upscale Image

Upscale an image using Magnific Precision Upscale AI.

### Endpoint

```
POST /api/upscale
```

### Request Body

| Field       | Type     | Required | Description |
|-------------|----------|----------|-------------|
| `image_url` | `string` | Yes      | URL of the image to upscale |

### Example Request

```bash
curl -X POST https://api.productai.photo/v1/api/upscale \
  -H "x-api-key: YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "image_url": "https://example.com/photo.jpg"
  }'
```

### Response

```json
{
  "status": "OK",
  "data": {
    "id": 67890,
    "status": "RUNNING"
  }
}
```

**Cost:** 20 tokens per upscale operation.

Poll `/api/job/:jobId` to retrieve the upscaled image URL when complete.

---

## `/api/generate-custom-model` — Generate with Custom Model

Generate images using a custom-trained model (e.g., brand-specific product models).

### Endpoint

```
POST /api/generate-custom-model
```

### Request Body

| Field       | Type     | Required | Description |
|-------------|----------|----------|-------------|
| `image_url` | `string` | Yes      | URL of input image |
| `prompt`    | `string` | Yes      | Generation prompt |
| `model`     | `string` | Yes      | Custom model identifier (e.g., `custom-owesa-avatars`) |

### Example Request

```bash
curl -X POST https://api.productai.photo/v1/api/generate-custom-model \
  -H "x-api-key: YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "image_url": "https://example.com/photo.jpg",
    "prompt": "Transform into brand style",
    "model": "custom-owesa-avatars"
  }'
```

### Response

Same format as `/api/generate` — returns a job ID to poll for completion.

---

## `/api/key-check` — Validate API Key

Verify that your API key is valid and check remaining token balance.

### Endpoint

```
GET /api/key-check
```

### Example Request

```bash
curl -H "x-api-key: YOUR_API_KEY" \
  https://api.productai.photo/v1/api/key-check
```

### Response

```json
{
  "status": "OK",
  "data": {
    "valid": true,
    "tokens_remaining": 1250,
    "plan": "standard"
  }
}
```

---

## Error Handling

All error responses follow this format:

```json
{
  "status": "ERROR",
  "message": "Descriptive error message",
  "code": "ERROR_CODE"
}
```

### Common Error Codes

| Code | HTTP Status | Meaning |
|------|-------------|---------|
| `INVALID_API_KEY` | 401 | API key missing or invalid |
| `OUT_OF_TOKENS` | 402 | Insufficient tokens in account |
| `RATE_LIMIT_EXCEEDED` | 429 | More than 15 requests/minute |
| `INVALID_IMAGE_URL` | 400 | Image URL inaccessible or invalid format |
| `INVALID_MODEL` | 400 | Model name not recognized |
| `JOB_NOT_FOUND` | 404 | Job ID doesn't exist or belongs to another user |

---

## Best Practices

### Asynchronous Workflow

1. **Submit job** via `/api/generate` or `/api/upscale`
2. **Store job ID** from response
3. **Poll `/api/job/:jobId`** every 3-5 seconds until status is `COMPLETED` or `ERROR`
4. **Download result** from `image_url` field

### Rate Limiting

- Maximum **15 requests per minute** per IP
- Use exponential backoff when hitting 429 errors
- For batch operations, space out requests (4-5 seconds apart)

### Image Requirements

- **Formats:** PNG, JPG, JPEG, WebP
- **Max size:** 10 MB
- **Max images per request:** 2 (only with `nanobanana`, `nanobananapro`, `seedream`)
- **URLs must be publicly accessible** (no authentication required)

### Token Management

- Tokens are deducted when jobs **start** (not on completion)
- Check balance via `/api/key-check` before large batches
- Failed jobs still consume tokens

---

## SDK & Integration Examples

For Python integration examples and helper scripts, see:
- `scripts/generate_photo.py` — Complete generation workflow
- `scripts/upscale_image.py` — Upscaling workflow
- `references/INTEGRATION_GUIDE.md` — Advanced patterns

---

## Support

- **API Issues:** support@productai.photo
- **Documentation:** https://www.productai.photo/docs
- **Status Page:** https://status.productai.photo
