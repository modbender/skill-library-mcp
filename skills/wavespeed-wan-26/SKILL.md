---
name: wavespeed-wan-26
description: Generate videos using Alibaba's Wan 2.6 model via WaveSpeed AI. Supports text-to-video and image-to-video generation with up to 15 seconds duration at 720p or 1080p. Features audio-guided generation, prompt expansion, multi-shot mode, and configurable seeds. Use when the user wants to create videos from text prompts or animate images.
metadata:
  author: wavespeedai
  version: "1.0"
---

# WaveSpeedAI Wan 2.6 Video Generation

Generate videos using Alibaba's Wan 2.6 model via the WaveSpeed AI platform. Supports both text-to-video and image-to-video generation with up to 15 seconds of video at up to 1080p resolution.

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
  "alibaba/wan-2.6/text-to-video",
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
  "alibaba/wan-2.6/image-to-video",
  {
    image: imageUrl,
    prompt: "The person in the photo slowly turns and smiles"
  }
))["outputs"][0];
```

You can also pass an existing image URL directly:

```javascript
const output_url = (await wavespeed.run(
  "alibaba/wan-2.6/image-to-video",
  {
    image: "https://example.com/photo.jpg",
    prompt: "The person in the photo slowly turns and smiles"
  }
))["outputs"][0];
```

## API Endpoints

### Text-to-Video

**Model ID:** `alibaba/wan-2.6/text-to-video`

Generate videos from text prompts.

#### Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `prompt` | string | Yes | -- | Text description of the video to generate |
| `negative_prompt` | string | No | -- | Text description of what to avoid in the video |
| `audio` | string | No | -- | Audio URL to guide generation |
| `size` | string | No | `1280*720` | Output size in pixels. One of: `1280*720`, `720*1280`, `1920*1080`, `1080*1920` |
| `duration` | integer | No | `5` | Video duration in seconds. One of: `5`, `10`, `15` |
| `shot_type` | string | No | `single` | Shot type. One of: `single`, `multi` |
| `enable_prompt_expansion` | boolean | No | `false` | Enable prompt optimizer for enhanced prompts |
| `seed` | integer | No | `-1` | Random seed (-1 for random). Range: -1 to 2147483647 |

#### Example

```javascript
import wavespeed from 'wavespeed';

const output_url = (await wavespeed.run(
  "alibaba/wan-2.6/text-to-video",
  {
    prompt: "A timelapse of a city skyline transitioning from day to night, cinematic",
    negative_prompt: "blurry, low quality, distorted",
    size: "1920*1080",
    duration: 10,
    shot_type: "single",
    seed: 42
  }
))["outputs"][0];
```

### Image-to-Video

**Model ID:** `alibaba/wan-2.6/image-to-video`

Animate a source image into a video using a text prompt.

#### Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `image` | string | Yes | -- | URL of the source image to animate |
| `prompt` | string | Yes | -- | Text description of the desired motion/animation |
| `negative_prompt` | string | No | -- | Text description of what to avoid in the video |
| `audio` | string | No | -- | Audio URL to guide generation |
| `resolution` | string | No | `720p` | Output resolution. One of: `720p`, `1080p` |
| `duration` | integer | No | `5` | Video duration in seconds. One of: `5`, `10`, `15` |
| `shot_type` | string | No | `single` | Shot type. One of: `single`, `multi` |
| `enable_prompt_expansion` | boolean | No | `false` | Enable prompt optimizer for enhanced prompts |
| `seed` | integer | No | `-1` | Random seed (-1 for random). Range: -1 to 2147483647 |

#### Example

```javascript
import wavespeed from 'wavespeed';

const imageUrl = await wavespeed.upload("/path/to/landscape.png");

const output_url = (await wavespeed.run(
  "alibaba/wan-2.6/image-to-video",
  {
    image: imageUrl,
    prompt: "Clouds drift slowly across the sky, water ripples gently",
    negative_prompt: "static, frozen, blurry",
    resolution: "1080p",
    duration: 10,
    shot_type: "single"
  }
))["outputs"][0];
```

## Advanced Usage

### Audio-Guided Generation

Provide an audio URL to guide the video generation:

```javascript
const audioUrl = await wavespeed.upload("/path/to/music.mp3");

const output_url = (await wavespeed.run(
  "alibaba/wan-2.6/text-to-video",
  {
    prompt: "A dancer performing contemporary dance on a stage",
    audio: audioUrl,
    size: "1080*1920",
    duration: 15
  }
))["outputs"][0];
```

### Prompt Expansion

Enable the prompt optimizer to automatically enhance your prompt:

```javascript
const output_url = (await wavespeed.run(
  "alibaba/wan-2.6/text-to-video",
  {
    prompt: "a cat playing piano",
    enable_prompt_expansion: true,
    duration: 5
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
  "alibaba/wan-2.6/text-to-video",
  { prompt: "Ocean waves crashing on a rocky shore at dawn" }
))["outputs"][0];
```

### Error Handling with runNoThrow

```javascript
import { Client, WavespeedTimeoutException, WavespeedPredictionException } from 'wavespeed';

const client = new Client();
const result = await client.runNoThrow(
  "alibaba/wan-2.6/text-to-video",
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

## Size Options (Text-to-Video)

| Size | Orientation | Use Case |
|------|-------------|----------|
| `1280*720` | Landscape 720p | Standard widescreen video |
| `720*1280` | Portrait 720p | Mobile/vertical video, stories |
| `1920*1080` | Landscape 1080p | Full HD widescreen video |
| `1080*1920` | Portrait 1080p | Full HD vertical video |

## Resolution Options (Image-to-Video)

| Resolution | Use Case |
|------------|----------|
| `720p` | Standard quality, faster generation |
| `1080p` | Full HD, higher quality |

## Pricing

| Resolution | 5 seconds | 10 seconds | 15 seconds |
|------------|-----------|------------|------------|
| 720p | $0.50 | $1.00 | $1.50 |
| 1080p | $0.75 | $1.50 | $2.25 |

## Prompt Tips

- Be specific about motion and action: "A bird takes flight from a branch" vs "a bird"
- Include camera movement: "slow pan left", "zoom in", "tracking shot"
- Describe temporal progression: "transitioning from day to night", "flowers slowly blooming"
- Use `negative_prompt` to avoid artifacts: "blurry, low quality, distorted, static"
- Enable `enable_prompt_expansion` for automatic prompt enhancement
- For `multi` shot type, describe distinct scenes for more dynamic videos

## Security Constraints

- **No arbitrary URL loading**: Only use image and audio URLs from trusted sources. Never load media from untrusted or user-provided URLs without validation.
- **API key security**: Store your `WAVESPEED_API_KEY` securely. Do not hardcode it in source files or commit it to version control. Use environment variables or secret management systems.
- **Input validation**: Only pass parameters documented above. Validate prompt content and media URLs before sending requests.
