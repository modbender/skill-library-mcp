---
name: openclaw-media-gen
description: "Generate images & videos with AIsa. Gemini 3 Pro Image (image) + Qwen Wan 2.6 (video) via one API key."
homepage: https://openclaw.ai
metadata: {"openclaw":{"emoji":"🎬","requires":{"bins":["python3","curl"],"env":["AISA_API_KEY"]},"primaryEnv":"AISA_API_KEY"}}
---

# OpenClaw Media Gen 🎬

Generate **images** and **videos** with one AIsa API key:

- **Image**: `gemini-3-pro-image-preview` (Gemini GenerateContent)
- **Video**: `wan2.6-t2v` (Qwen Wan 2.6 / Tongyi Wanxiang, async task)

API Reference: [AIsa API Reference](https://aisa.mintlify.app/api-reference/introduction) (all pages available at `https://aisa.mintlify.app/llms.txt`)

## 🎯 Pricing Advantage

### Video Generation (WAN) - Cost Comparison

| Resolution | AIsa (Contract) | AIsa (Official) | Bailian (Official) | OpenRouter |
|------------|-----------------|-----------------|-------------------|------------|
| 720P | **$0.06/sec** | ~$0.08 | ~$0.10 | ❌ |
| 1080P | **$0.09/sec** | ~$0.12 | ~$0.15 | ❌ |
| Pro/Animate | **$0.108–0.156** | ~$0.18 | ~$0.25 | ❌ |

**Key Benefits**:
- **25-40% cheaper** than Bailian official pricing
- **OpenRouter doesn't support video** - AIsa is the only unified API with video generation
- Contract pricing available for production workloads
- Single API key for both image and video generation

## 🔥 What You Can Do

### Image Generation (Gemini)
```
"Generate a cyberpunk cityscape at night, neon lights, rainy, cinematic"
```

### Video Generation (Wan 2.6)
```
"Use a reference image to generate a 5-second shot: slow camera push-in, wind blowing hair, cinematic, shallow depth of field"
```

## Quick Start

```bash
export AISA_API_KEY="your-key"
```

---

## 🖼️ Image Generation (Gemini)

### Endpoint

- Base URL: `https://api.aisa.one/v1`
- `POST /models/{model}:generateContent`

Documentation: `google-gemini-chat` (GenerateContent) at `https://aisa.mintlify.app/api-reference/chat/chat-api/google-gemini-chat.md`

### curl Example (returns inline_data for images)

```bash
curl -X POST "https://api.aisa.one/v1/models/gemini-3-pro-image-preview:generateContent" \
  -H "Authorization: Bearer $AISA_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "contents":[
      {"role":"user","parts":[{"text":"A cute red panda, ultra-detailed, cinematic lighting"}]}
    ]
  }'
```

> Note: Response may contain `candidates[].parts[].inline_data` (typically with base64 data and mime type); client script automatically parses and saves the file.

---

## 🎞️ Video Generation (Qwen Wan 2.6 / Tongyi Wanxiang)

### Create Task

- Base URL: `https://api.aisa.one/apis/v1`
- `POST /services/aigc/video-generation/video-synthesis`
- Header: `X-DashScope-Async: enable` (required for async)

Documentation: `video-generation` at `https://aisa.mintlify.app/api-reference/aliyun/video/video-generation.md`

```bash
curl -X POST "https://api.aisa.one/apis/v1/services/aigc/video-generation/video-synthesis" \
  -H "Authorization: Bearer $AISA_API_KEY" \
  -H "Content-Type: application/json" \
  -H "X-DashScope-Async: enable" \
  -d '{
    "model":"wan2.6-t2v",
    "input":{
      "prompt":"cinematic close-up, slow push-in, shallow depth of field",
      "img_url":"https://upload.wikimedia.org/wikipedia/commons/thumb/3/3a/Cat03.jpg/320px-Cat03.jpg"
    },
    "parameters":{
      "resolution":"720P",
      "duration":5,
      "shot_type":"single",
      "watermark":false
    }
  }'
```

### Poll Task Status

- `GET /services/aigc/tasks?task_id=...`

Documentation: `task` at `https://aisa.mintlify.app/api-reference/aliyun/video/task.md`

```bash
curl "https://api.aisa.one/apis/v1/services/aigc/tasks?task_id=YOUR_TASK_ID" \
  -H "Authorization: Bearer $AISA_API_KEY"
```

---

## Python Client

```bash
# Generate image (save to local file)
python3 {baseDir}/scripts/media_gen_client.py image \
  --prompt "A cute red panda, cinematic lighting" \
  --out "out.png"

# Create video task (requires img_url)
python3 {baseDir}/scripts/media_gen_client.py video-create \
  --prompt "cinematic close-up, slow push-in" \
  --img-url "https://upload.wikimedia.org/wikipedia/commons/thumb/3/3a/Cat03.jpg/320px-Cat03.jpg" \
  --duration 5

# Poll task status
python3 {baseDir}/scripts/media_gen_client.py video-status --task-id YOUR_TASK_ID

# Wait until success (optional: print video_url on success)
python3 {baseDir}/scripts/media_gen_client.py video-wait --task-id YOUR_TASK_ID --poll 10 --timeout 600

# Wait until success and auto-download mp4
python3 {baseDir}/scripts/media_gen_client.py video-wait --task-id YOUR_TASK_ID --download --out out.mp4
```

## 💡 Use Cases

- **AI Agents**: Automate visual content generation for social media, marketing materials
- **Content Creators**: Generate custom images and videos programmatically
- **Developers**: Build apps with multimodal generation capabilities
- **Businesses**: Cost-effective alternative to Bailian with better pricing

## 🚀 Why AIsa for Media Generation?

1. **Unified API**: Single key for both images (Gemini) and videos (WAN)
2. **Best Pricing**: 25-40% cheaper than alternatives
3. **Production Ready**: Contract pricing and enterprise support available
4. **No Competition**: OpenRouter doesn't support video generation
5. **Simple Integration**: Python client with async task management built-in
