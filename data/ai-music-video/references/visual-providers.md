# Visual Providers Reference

## Image Providers

### BytePlus Seedream 4.5 ⭐ Recommended
- Model: `seedream-4-5-251128`
- Endpoint: `POST https://ark.ap-southeast.bytepluses.com/api/v3/images/generations`
- Auth: `Authorization: Bearer $BYTEPLUS_API_KEY`
- Min size: 1920x1920 (use 2048x2048 for square)
- Pricing: **$0.045/image** (200 free images on signup)
- Sign up: [console.byteplus.com](https://console.byteplus.com) → ModelArk → Activate Seedream

```json
{
  "model": "seedream-4-5-251128",
  "prompt": "scene description",
  "size": "2048x2048",
  "response_format": "url",
  "watermark": false
}
```

### OpenAI GPT Image 1 / 1 Mini
- Models: `gpt-image-1` (premium) / `gpt-image-1-mini` (budget, default)
- Endpoint: `POST https://api.openai.com/v1/images/generations`
- Auth: `Authorization: Bearer $OPENAI_API_KEY`
- Sizes: 1024x1024, 1536x1024, 1024x1536
- Quality: low / medium / high

```json
{
  "model": "gpt-image-1-mini",
  "prompt": "scene description",
  "n": 1,
  "size": "1024x1024",
  "quality": "medium"
}
```

**Token-based pricing (actual cost per image, Feb 2026):**
| Model | Quality | 1024x1024 | 1536x1024 |
|-------|---------|-----------|-----------|
| gpt-image-1-mini | Low | **$0.002** | $0.004 |
| gpt-image-1-mini | Medium | **$0.009** | $0.013 |
| gpt-image-1 | Medium | $0.043 | $0.064 |
| gpt-image-1 | High | $0.167 | $0.250 |

*Note: OpenAI bills images by tokens, not flat per-image rate. Output tokens are fixed per quality (low=272, medium=1056, high=4160). The script tracks actual token usage for precise cost reporting.*

### Google Imagen 4.0 (via Together AI)
- Model: `google/imagen-4.0-generate-preview`
- Endpoint: `POST https://api.together.xyz/v1/images/generations`
- Auth: `Authorization: Bearer $TOGETHER_API_KEY`
- ~$0.04/MP (Preview), $0.02 (Fast), $0.06 (Ultra)

## Video Providers

### OpenAI Sora 2 (direct)
- Endpoint: `POST https://api.openai.com/v1/videos/generations`
- Auth: `Authorization: Bearer $OPENAI_API_KEY`
- Models: `sora-2` (720p, $0.10/sec), `sora-2-pro` (1080p, $0.30/sec)

### Via Together AI (unified endpoint)
- Endpoint: `POST https://api.together.xyz/v2/videos`
- Auth: `Authorization: Bearer $TOGETHER_API_KEY`
- Async: submit → poll by ID → download

**Models & Pricing (per clip, ~5-8 sec):**
| Model ID | Price/clip | Resolution |
|----------|-----------|------------|
| `openai/sora-2` | $0.80 | 720p |
| `openai/sora-2-pro` | $2.40 | 1080p |
| `ByteDance/Seedance-1.0-lite` | $0.14 | 720p |
| `ByteDance/Seedance-1.0-pro` | $0.57 | 1080p |
| `google/veo-3.0-generate-preview` | $1.60 | - |
| `google/veo-3.0-generate-preview` +audio | $3.20 | - |
| `google/veo-3.0-fast` | $0.80 | - |

### Together Video API Flow
```bash
# 1. Submit
curl -X POST https://api.together.xyz/v2/videos \
  -H "Authorization: Bearer $TOGETHER_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model":"ByteDance/Seedance-1.0-pro","prompt":"..."}'
→ {"id": "video_xxx", "status": "processing"}

# 2. Poll
curl https://api.together.xyz/v2/videos/video_xxx \
  -H "Authorization: Bearer $TOGETHER_API_KEY"
→ {"id":"video_xxx","status":"completed","output":{"video_url":"https://..."}}

# 3. Download video_url
```

## Provider Selection Guide

| Need | Best Choice | Fallback |
|------|-------------|----------|
| Best value images | **Seedream 4.5** ($0.045, 2K) | GPT Image 1 Mini medium ($0.009) |
| Cheapest images | GPT Image 1 Mini low ($0.002) | Imagen 4.0 Fast ($0.02) |
| Premium images | GPT Image 1 high ($0.17) | Imagen 4.0 Ultra ($0.06) |
| Budget video | Seedance 1.0 Lite ($0.14) | Sora 2 ($0.80) |
| Quality video | Sora 2 Pro ($2.40) | Seedance Pro ($0.57) |
| Video + audio sync | Veo 3.0 + Audio ($3.20) | - |

## API Key Requirements
| Provider | Env Variable | Required For |
|----------|-------------|--------------|
| sunoapi.org | `SUNO_API_KEY` | Music (always) |
| OpenAI | `OPENAI_API_KEY` | Images (mini/premium), Sora video |
| BytePlus | `BYTEPLUS_API_KEY` | Seedream images (recommended) |
| Together AI | `TOGETHER_API_KEY` | Seedance, Veo, Imagen |
