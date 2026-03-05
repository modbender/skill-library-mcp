# Runway (Gen-3 Alpha / Gen-4.5)

**Best for:** Complex motion, professional quality, motion brushes

**API:** https://docs.dev.runwayml.com/

## Setup

1. Get API key: https://dev.runwayml.com/
2. Install SDK: `npm install @runwayml/sdk` or `pip install runwayml`

## Quick Start (Node.js)

```javascript
import RunwayML from '@runwayml/sdk';

const client = new RunwayML();
const task = await client.imageToVideo.create({
  model: 'gen4.5',
  promptText: 'A serene mountain landscape at sunrise',
  ratio: '1280:720',
  duration: 5,
}).waitForTaskOutput();

console.log('Video URL:', task.output[0]);
```

## Models

- `gen4.5` — Latest, best quality
- `gen3a_turbo` — Faster, requires input image

## Pricing

- ~$0.05 per second generated
- Enterprise tiers available

## Limits

- Max 10 seconds per generation
- Rate limits vary by plan
