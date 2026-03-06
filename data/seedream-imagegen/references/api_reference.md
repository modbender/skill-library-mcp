# Seedream API Reference

## Endpoint
```
POST https://ark.cn-beijing.volces.com/api/v3/images/generations
```

## Authentication
Header: `Authorization: Bearer {ARK_API_KEY}`

## Models

| Model | ID | Features |
|-------|----|----|
| Seedream 4.5 | `doubao-seedream-4-5-251128` | Best quality, enhanced editing |
| Seedream 4.0 | `doubao-seedream-4-0-250828` | Good quality, budget-friendly |

---

## Request Parameters

### Required
| Parameter | Type | Description |
|-----------|------|-------------|
| `model` | string | Model ID |
| `prompt` | string | Generation prompt (≤300 Chinese chars / 600 English words) |

### Optional - Image Input
| Parameter | Type | Description |
|-----------|------|-------------|
| `image` | string/array | Reference image(s) as URL or base64. Max 14 images. |

Base64 format: `data:image/{format};base64,{encoded_data}`
Supported formats: jpeg, png, webp, bmp, tiff, gif
Constraints: >14px sides, ≤10MB, ≤36MP total, aspect ratio [1/16, 16]

### Optional - Output Control
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `size` | string | 2048x2048 | `2K`, `4K`, or `WxH` format |
| `response_format` | string | url | `url` or `b64_json` |
| `watermark` | boolean | true | Add "AI生成" watermark |

**Size constraints for Seedream 4.5:**
- Total pixels: [3,686,400 - 16,777,216]
- Aspect ratio: [1/16, 16]

### Optional - Generation Mode
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `sequential_image_generation` | string | disabled | `auto` for multi-image, `disabled` for single |
| `sequential_image_generation_options.max_images` | int | 15 | Max output images [1-15] |

Note: input images + output images ≤ 15

### Optional - Prompt Enhancement
| Parameter | Type | Description |
|-----------|------|-------------|
| `optimize_prompt_options.mode` | string | `standard` (better quality) or `fast` (faster) |

---

## Response Format

### Success Response
```json
{
  "model": "doubao-seedream-4-5-251128",
  "created": 1234567890,
  "data": [
    {
      "url": "https://...",
      "size": "2048x2048"
    }
  ],
  "usage": {
    "generated_images": 1,
    "output_tokens": 16384,
    "total_tokens": 16384
  }
}
```

### Error Response
```json
{
  "error": {
    "code": "error_code",
    "message": "Error description"
  }
}
```

---

## Usage Limits

- Rate limit: 500 images/minute per model
- URL validity: 24 hours after generation
- Max reference images: 14
- Max output images: 15 (minus input count)

---

## Code Examples

### Python (requests)
```python
import os
import requests

response = requests.post(
    "https://ark.cn-beijing.volces.com/api/v3/images/generations",
    headers={
        "Content-Type": "application/json",
        "Authorization": f"Bearer {os.environ['ARK_API_KEY']}"
    },
    json={
        "model": "doubao-seedream-4-5-251128",
        "prompt": "A serene mountain landscape at sunset",
        "size": "2K",
        "watermark": False
    }
)
print(response.json()["data"][0]["url"])
```

### Python (OpenAI SDK)
```python
from openai import OpenAI

client = OpenAI(
    base_url="https://ark.cn-beijing.volces.com/api/v3",
    api_key=os.environ["ARK_API_KEY"]
)

response = client.images.generate(
    model="doubao-seedream-4-5-251128",
    prompt="A serene mountain landscape",
    size="2K",
    extra_body={"watermark": False}
)
print(response.data[0].url)
```

### cURL
```bash
curl https://ark.cn-beijing.volces.com/api/v3/images/generations \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $ARK_API_KEY" \
  -d '{
    "model": "doubao-seedream-4-5-251128",
    "prompt": "A serene mountain landscape",
    "size": "2K",
    "watermark": false
  }'
```
