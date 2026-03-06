# Pika Labs

**Best for:** Stylized content, fast iterations, artistic effects

**API:** Via Fal.ai: https://fal.ai/models/pika

## Setup

1. Get Fal.ai API key
2. Use Pika models through Fal endpoint

## Quick Start

```bash
curl -X POST https://queue.fal.run/fal-ai/pika/text-to-video \
  -H "Authorization: Key $FAL_KEY" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "a cat dancing"}'
```

## Features

- Pikaformance — lip-sync and expressions
- Effects (inflate, explode, melt, etc.)
- Fast generation (~30s for 3s clip)

## Pricing

- Via Fal.ai: ~$0.10-0.20 per generation
- Consumer: 150 credits/month free
