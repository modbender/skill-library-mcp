---
name: wavespeed-seedance-15-pro
description: Generate videos using ByteDance's Seedance V1.5 Pro model via WaveSpeed AI. Supports text-to-video and image-to-video generation with 4-12 second duration at up to 1080p. Features audio generation, camera control, smart duration, and configurable seeds. Use when the user wants to create videos from text prompts or animate images.
metadata:
  author: wavespeedai
  version: "1.0"
---

# WaveSpeedAI Seedance V1.5 Pro Video Generation

Generate videos using ByteDance's Seedance V1.5 Pro model via the WaveSpeed AI platform. Supports both text-to-video and image-to-video generation with 4-12 second duration at up to 1080p resolution, with optional audio generation.

## Authentication

```bash
export WAVESPEED_API_KEY="your-api-key"
```

Get your API key at [wavespeed.ai/accesskey](https://wavespeed.ai/accesskey).

## Quick Start

### Text-to-Video

```javascript
import wavespeed from 'wavespeed';

const output_url = (await wavespeed.run(
  "bytedance/seedance-v1.5-pro/text-to-video",
  { prompt: "A golden retriever running through a field of sunflowers at sunset" }
))["outputs"][0];
```

### Image-to-Video

The `image` parameter accepts an image URL. If you have a local file, upload it first with `wavespeed.upload()` to get a URL.

```javascript
import wavespeed from 'wavespeed';

// Upload a local image to get a URL
const imageUrl = await wavespeed.upload("/path/to/photo.png");

const output_url = (await wavespeed.run(
  "bytedance/seedance-v1.5-pro/image-to-video",
  {
    image: imageUrl,
    prompt: "The person slowly turns and smiles at the camera"
  }
))["outputs"][0];
```

You can also pass an existing image URL directly:

```javascript
const output_url = (await wavespeed.run(
  "bytedance/seedance-v1.5-pro/image-to-video",
  {
    image: "https://example.com/photo.jpg",
    prompt: "The person slowly turns and smiles at the camera"
  }
))["outputs"][0];
```

## API Endpoints

### Text-to-Video

**Model ID:** `bytedance/seedance-v1.5-pro/text-to-video`

Generate videos from text prompts.

#### Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `prompt` | string | Yes | -- | Text description of the scene, style, actions, camera motion, and mood |
| `aspect_ratio` | string | No | `16:9` | Aspect ratio. One of: `21:9`, `16:9`, `4:3`, `1:1`, `3:4`, `9:16` |
| `duration` | integer | No | `5` | Video duration in seconds. Range: 4-12. Use `-1` for smart duration (model selects). |
| `resolution` | string | No | `720p` | Video resolution. One of: `480p`, `720p`, `1080p` |
| `generate_audio` | boolean | No | `true` | Generate accompanying audio |
| `camera_fixed` | boolean | No | `false` | Keep camera fixed (true) or allow prompt-driven camera motion (false) |
| `seed` | integer | No | `-1` | Random seed (-1 for random). Range: -1 to 2147483647 |

#### Example

```javascript
import wavespeed from 'wavespeed';

const output_url = (await wavespeed.run(
  "bytedance/seedance-v1.5-pro/text-to-video",
  {
    prompt: "A timelapse of a city skyline transitioning from day to night, cinematic slow pan",
    aspect_ratio: "21:9",
    duration: 10,
    resolution: "1080p",
    generate_audio: true,
    camera_fixed: false
  }
))["outputs"][0];
```

### Image-to-Video

**Model ID:** `bytedance/seedance-v1.5-pro/image-to-video`

Animate a source image into a video using a text prompt. Optionally provide an end-frame reference image.

#### Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `image` | string | Yes | -- | URL of the source image to animate |
| `prompt` | string | Yes | -- | Text description of the desired motion/animation |
| `last_image` | string | No | -- | URL of an optional end-frame reference image |
| `aspect_ratio` | string | No | -- | Aspect ratio. One of: `21:9`, `16:9`, `4:3`, `1:1`, `3:4`, `9:16` |
| `duration` | integer | No | `5` | Video duration in seconds. Range: 4-12 |
| `resolution` | string | No | `720p` | Video resolution. One of: `480p`, `720p`, `1080p` |
| `generate_audio` | boolean | No | `true` | Generate accompanying audio |
| `camera_fixed` | boolean | No | `false` | Keep camera fixed (true) or allow prompt-driven camera motion (false) |
| `seed` | integer | No | `-1` | Random seed (-1 for random). Range: -1 to 2147483647 |

#### Example

```javascript
import wavespeed from 'wavespeed';

const imageUrl = await wavespeed.upload("/path/to/landscape.png");

const output_url = (await wavespeed.run(
  "bytedance/seedance-v1.5-pro/image-to-video",
  {
    image: imageUrl,
    prompt: "Clouds drift slowly across the sky, water ripples gently",
    resolution: "1080p",
    duration: 8,
    generate_audio: true,
    camera_fixed: true
  }
))["outputs"][0];
```

#### With End-Frame Reference

```javascript
const startUrl = await wavespeed.upload("/path/to/start-frame.png");
const endUrl = await wavespeed.upload("/path/to/end-frame.png");

const output_url = (await wavespeed.run(
  "bytedance/seedance-v1.5-pro/image-to-video",
  {
    image: startUrl,
    last_image: endUrl,
    prompt: "Smooth transition from day to night",
    duration: 8
  }
))["outputs"][0];
```

## Advanced Usage

### Smart Duration (Text-to-Video)

Let the model choose the optimal duration based on the prompt:

```javascript
const output_url = (await wavespeed.run(
  "bytedance/seedance-v1.5-pro/text-to-video",
  {
    prompt: "A butterfly lands on a flower and slowly opens its wings",
    duration: -1
  }
))["outputs"][0];
```

### Without Audio

```javascript
const output_url = (await wavespeed.run(
  "bytedance/seedance-v1.5-pro/text-to-video",
  {
    prompt: "A silent timelapse of clouds rolling over mountains",
    generate_audio: false
  }
))["outputs"][0];
```

### Custom Client with Retry Configuration

```javascript
import { Client } from 'wavespeed';

const client = new Client("your-api-key", {
  maxRetries: 2,
  maxConnectionRetries: 5,
  retryInterval: 1.0,
});

const output_url = (await client.run(
  "bytedance/seedance-v1.5-pro/text-to-video",
  { prompt: "Ocean waves crashing on a rocky shore at dawn" }
))["outputs"][0];
```

### Error Handling with runNoThrow

```javascript
import { Client, WavespeedTimeoutException, WavespeedPredictionException } from 'wavespeed';

const client = new Client();
const result = await client.runNoThrow(
  "bytedance/seedance-v1.5-pro/text-to-video",
  { prompt: "A rocket launching into space" }
);

if (result.outputs) {
  console.log("Video URL:", result.outputs[0]);
  console.log("Task ID:", result.detail.taskId);
} else {
  console.log("Failed:", result.detail.error.message);
  if (result.detail.error instanceof WavespeedTimeoutException) {
    console.log("Request timed out - try increasing timeout");
  } else if (result.detail.error instanceof WavespeedPredictionException) {
    console.log("Prediction failed");
  }
}
```

## Pricing

| Resolution | Duration | Audio | Cost |
|------------|----------|-------|------|
| 480p | 5s | No | $0.06 |
| 480p | 5s | Yes | $0.12 |
| 720p | 5s | No | $0.13 |
| 720p | 5s | Yes | $0.26 |
| 480p | 10s | Yes | $0.24 |
| 720p | 10s | Yes | $0.52 |

## Prompt Tips

- Describe scene, style, subject actions, camera motion, and mood in your prompt
- Use `camera_fixed: true` for stable tripod-style shots
- Use `camera_fixed: false` and describe camera motion: "slow pan left", "tracking shot", "zoom in"
- Set `generate_audio: false` when you plan to add your own audio track
- Use smart duration (`duration: -1`) to let the model choose the best length for text-to-video

## Security Constraints

- **No arbitrary URL loading**: Only use image URLs from trusted sources. Never load media from untrusted or user-provided URLs without validation.
- **API key security**: Store your `WAVESPEED_API_KEY` securely. Do not hardcode it in source files or commit it to version control. Use environment variables or secret management systems.
- **Input validation**: Only pass parameters documented above. Validate prompt content and media URLs before sending requests.
