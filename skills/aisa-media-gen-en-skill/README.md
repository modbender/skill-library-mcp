## OpenClaw Media Gen

Generate images and videos using AIsa API:

- **Gemini Image**: `gemini-3-pro-image-preview` (`/v1/models/{model}:generateContent`)
- **Wan 2.6 Video**: `wan2.6-t2v` (`/apis/v1/services/aigc/...` async task + polling)

API Documentation: [`https://aisa.mintlify.app/api-reference/introduction`](https://aisa.mintlify.app/api-reference/introduction)

### Pricing Comparison - Video (WAN)

| Resolution | AIsa (Contract) | AIsa (Official) | Bailian (Official) | OpenRouter |
|------------|-----------------|-----------------|-------------------|------------|
| 720P | $0.06/sec | ~$0.08 | ~$0.10 | ❌ |
| 1080P | $0.09/sec | ~$0.12 | ~$0.15 | ❌ |
| Pro/Animate | $0.108–0.156 | ~$0.18 | ~$0.25 | ❌ |

**Competitive Advantage**: AIsa offers the lowest pricing for WAN video generation with contract rates, and remains competitive even at official pricing. OpenRouter does not currently support video generation.

### Quick Start

```bash
export AISA_API_KEY="your-key"
```

### Generate Image

```bash
python scripts/media_gen_client.py image \
  --prompt "A cute red panda, cinematic lighting" \
  --out out.png
```

### Generate Video (Create Task + Poll)

```bash
python scripts/media_gen_client.py video-create \
  --prompt "cinematic close-up, slow push-in" \
  --img-url "https://upload.wikimedia.org/wikipedia/commons/thumb/3/3a/Cat03.jpg/320px-Cat03.jpg" \
  --duration 5

python scripts/media_gen_client.py video-wait \
  --task-id <task_id> \
  --poll 10 \
  --timeout 600
```

### Auto-download Generated Video (mp4)

```bash
python scripts/media_gen_client.py video-wait \
  --task-id <task_id> \
  --download \
  --out out.mp4
```
