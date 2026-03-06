# WaveSpeed AI Model Reference

API Base: `https://api.wavespeed.ai/api/v3/`
Auth: `Authorization: Bearer $WAVESPEED_API_KEY`

## Image Generation (text-to-image)

| Alias | Model ID | Notes |
|-------|----------|-------|
| `flux` | `wavespeed-ai/flux-dev` | Fast, general purpose |
| `flux-schnell` | `wavespeed-ai/flux-schnell` | Ultra fast, lower quality |
| `flux-pro` | `wavespeed-ai/flux-pro-v1.1-ultra` | Highest quality FLUX |
| `sdxl` | `wavespeed-ai/stable-diffusion-xl` | Classic SDXL |
| `seedream` | `bytedance/seedream-v3.1` | ByteDance, photorealistic |
| `qwen` | `wavespeed-ai/qwen-image/text-to-image` | 20B model, very detailed |

## Image Editing (image-to-image)

| Alias | Model ID | Notes |
|-------|----------|-------|
| `nbp` / `nbp-edit` | `google/nano-banana-pro/edit` | **Best face/portrait editing**, Gemini 3 Pro |
| `nb-edit` | `google/nano-banana/edit` | Gemini 2.5 Flash, faster & cheaper |

**Params for edit endpoints:**
```json
{
  "prompt": "change white bathrobe to black hoodie, dark background",
  "images": ["https://cdn.example.com/photo.jpg"]
}
```

## Video Generation

| Alias | Model ID | Notes |
|-------|----------|-------|
| `wan-i2v` | `wavespeed-ai/wan-2.2/i2v-720p` | Image-to-video 720p, fast |
| `wan-t2v` | `alibaba/wan-2.6/image-to-video-pro` | High quality, cinematic |
| `kling` | `kling-ai/kling-o1/image-to-video-pro` | Premium Kling O1 |
| `veo` | `google/veo-3.1/text-to-video` | Google Veo 3.1, 1080p |
| `sora` | `openai/sora-2/text-to-video` | OpenAI Sora 2 |
| `hailuo` | `minimax/hailuo-02/i2v-standard` | Minimax Hailuo 1080p |

## Utilities

| Alias | Model ID | Notes |
|-------|----------|-------|
| `upscale` | `wavespeed-ai/ultimate-video-upscaler` | 4K video upscaling |

## API Flow

### 1. Submit task
```bash
POST https://api.wavespeed.ai/api/v3/{model-id}
Authorization: Bearer $KEY
Content-Type: application/json

{"prompt": "...", "images": ["..."]}
```
Response: `{ "code": 200, "data": { "id": "task_id", "urls": { "get": "..." } } }`

### 2. Poll result
```bash
GET https://api.wavespeed.ai/api/v3/predictions/{task-id}/result
```
Response when done: `{ "data": { "status": "completed", "outputs": ["https://cdn.wavespeed.ai/..."] } }`

Status values: `created` → `processing` → `completed` / `failed`

## Pricing (approximate)
- Image generation: ~$0.003-0.05 per image
- Video generation: ~$0.10-2.00 per video
- Image editing: ~$0.01-0.05 per edit

## Full model catalog
Browse 700+ models at: https://wavespeed.ai/models
