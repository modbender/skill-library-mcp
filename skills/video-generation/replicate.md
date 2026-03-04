# Replicate (Multi-Provider)

**Best for:** Quick testing, model variety, pay-per-use

**API:** https://replicate.com/

## Setup

```bash
pip install replicate
export REPLICATE_API_TOKEN=r8_xxx
```

## Quick Start

```python
import replicate

output = replicate.run(
    "stability-ai/stable-video-diffusion:3f0457e4619daac51203dedb472816fd4af51f3149fa7a9e0b5ffcf1b8172438",
    input={"input_image": open("image.png", "rb")}
)
```

## Available Models

- Stable Video Diffusion
- Kling (v1.6)
- Mochi 1
- CogVideoX
- Pyramid Flow

## Pricing

- Varies by model
- Kling v1.6: ~$0.28 per 5 seconds
- SVD: ~$0.10 per run
