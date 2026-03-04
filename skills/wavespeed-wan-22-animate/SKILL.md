---
name: wavespeed-wan-22-animate
description: Animate characters from images using driving videos with WaveSpeed AI's Wan 2.2 Animate model. Supports animate mode (make image character move like video subject) and replace mode (swap video subject with image character). Outputs up to 120 seconds at 480p or 720p. Use when the user wants to animate a character from an image using a reference video.
metadata:
  author: wavespeedai
  version: "1.0"
---

# WaveSpeedAI Wan 2.2 Animate

Animate characters from images using driving videos via WaveSpeed AI's Wan 2.2 Animate model. Two modes: **animate** (make the image character move like the video subject) and **replace** (swap the video subject with the image character while preserving motion and scene).

## Authentication

```bash
export WAVESPEED_API_KEY="your-api-key"
```

Get your API key at [wavespeed.ai/accesskey](https://wavespeed.ai/accesskey).

## Quick Start

### Animate Mode

Make the character in an image move like the subject in a driving video:

```javascript
import wavespeed from 'wavespeed';

// Upload local image and video
const imageUrl = await wavespeed.upload("/path/to/character.png");
const videoUrl = await wavespeed.upload("/path/to/driving-video.mp4");

const output_url = (await wavespeed.run(
  "wavespeed-ai/wan-2.2/animate",
  {
    image: imageUrl,
    video: videoUrl
  }
))["outputs"][0];
```

### Replace Mode

Swap the subject in a video with a character from an image:

```javascript
const output_url = (await wavespeed.run(
  "wavespeed-ai/wan-2.2/animate",
  {
    image: imageUrl,
    video: videoUrl,
    mode: "replace"
  }
))["outputs"][0];
```

You can also pass existing URLs directly:

```javascript
const output_url = (await wavespeed.run(
  "wavespeed-ai/wan-2.2/animate",
  {
    image: "https://example.com/character.png",
    video: "https://example.com/driving-video.mp4"
  }
))["outputs"][0];
```

## API Endpoint

**Model ID:** `wavespeed-ai/wan-2.2/animate`

Animate a character from an image using a driving video.

### Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `image` | string | Yes | -- | URL of the character image to animate |
| `video` | string | Yes | -- | URL of the driving video providing motion reference |
| `prompt` | string | No | -- | Text prompt for additional guidance |
| `mode` | string | No | `animate` | Operation mode. `animate`: image character moves like video subject. `replace`: video subject is swapped with image character. |
| `resolution` | string | No | `480p` | Output resolution. One of: `480p`, `720p` |
| `seed` | integer | No | `-1` | Random seed (-1 for random). Range: -1 to 2147483647 |

### Example

```javascript
import wavespeed from 'wavespeed';

const imageUrl = await wavespeed.upload("/path/to/dancer.png");
const videoUrl = await wavespeed.upload("/path/to/dance-reference.mp4");

const output_url = (await wavespeed.run(
  "wavespeed-ai/wan-2.2/animate",
  {
    image: imageUrl,
    video: videoUrl,
    prompt: "a person dancing gracefully",
    mode: "animate",
    resolution: "720p",
    seed: 42
  }
))["outputs"][0];
```

### Replace Mode Example

```javascript
const characterUrl = await wavespeed.upload("/path/to/anime-character.png");
const sceneUrl = await wavespeed.upload("/path/to/scene-video.mp4");

const output_url = (await wavespeed.run(
  "wavespeed-ai/wan-2.2/animate",
  {
    image: characterUrl,
    video: sceneUrl,
    mode: "replace",
    resolution: "720p"
  }
))["outputs"][0];
```

## Advanced Usage

### Custom Client with Retry Configuration

```javascript
import { Client } from 'wavespeed';

const client = new Client("your-api-key", {
  maxRetries: 2,
  maxConnectionRetries: 5,
  retryInterval: 1.0,
});

const output_url = (await client.run(
  "wavespeed-ai/wan-2.2/animate",
  {
    image: imageUrl,
    video: videoUrl,
    mode: "animate"
  }
))["outputs"][0];
```

### Error Handling with runNoThrow

```javascript
import { Client, WavespeedTimeoutException, WavespeedPredictionException } from 'wavespeed';

const client = new Client();
const result = await client.runNoThrow(
  "wavespeed-ai/wan-2.2/animate",
  {
    image: imageUrl,
    video: videoUrl
  }
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

| Resolution | Cost per 5 seconds |
|------------|--------------------|
| 480p | $0.20 |
| 720p | $0.40 |

Output duration is 5-120 seconds. Minimum charge is 5 seconds. Per-second rate: $0.04/s (480p), $0.08/s (720p).

## Tips

- Match composition and pose between the input image and driving video for best results
- Use the same or similar aspect ratio between image and video
- Avoid heavy occlusion by hands, microphones, or props in the input media
- Start with `480p` for prototyping, then move to `720p` for production quality
- **Animate mode**: best when you want the image character to perform the motions from the video
- **Replace mode**: best when you want to keep the video's scene and motion but swap in a different character

## Security Constraints

- **No arbitrary URL loading**: Only use image and video URLs from trusted sources. Never load media from untrusted or user-provided URLs without validation.
- **API key security**: Store your `WAVESPEED_API_KEY` securely. Do not hardcode it in source files or commit it to version control. Use environment variables or secret management systems.
- **Input validation**: Only pass parameters documented above. Validate media URLs before sending requests.
