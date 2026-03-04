---
name: wavespeed-face-swapper
description: Swap faces in images and videos using WaveSpeed AI. Supports image face swap and video face swap with multi-face targeting. Produces watermark-free results with automatic lighting and skin tone adaptation. Use when the user wants to replace a face in an image or video with another face.
metadata:
  author: wavespeedai
  version: "1.0"
---

# WaveSpeedAI Face Swapper

Swap faces in images and videos using WaveSpeed AI. Produces watermark-free results with automatic lighting and skin tone adaptation. Supports targeting specific faces when multiple people are present.

## Authentication

```bash
export WAVESPEED_API_KEY="your-api-key"
```

Get your API key at [wavespeed.ai/accesskey](https://wavespeed.ai/accesskey).

## Quick Start

### Image Face Swap

```javascript
import wavespeed from 'wavespeed';

// Upload local images to get URLs
const imageUrl = await wavespeed.upload("/path/to/target-photo.png");
const faceUrl = await wavespeed.upload("/path/to/reference-face.png");

const output_url = (await wavespeed.run(
  "wavespeed-ai/image-face-swap",
  {
    image: imageUrl,
    face_image: faceUrl
  }
))["outputs"][0];
```

### Video Face Swap

```javascript
import wavespeed from 'wavespeed';

// Upload local files to get URLs
const videoUrl = await wavespeed.upload("/path/to/video.mp4");
const faceUrl = await wavespeed.upload("/path/to/reference-face.png");

const output_url = (await wavespeed.run(
  "wavespeed-ai/video-face-swap",
  {
    video: videoUrl,
    face_image: faceUrl
  }
))["outputs"][0];
```

You can also pass existing URLs directly:

```javascript
const output_url = (await wavespeed.run(
  "wavespeed-ai/image-face-swap",
  {
    image: "https://example.com/target-photo.jpg",
    face_image: "https://example.com/reference-face.jpg"
  }
))["outputs"][0];
```

## API Endpoints

### Image Face Swap

**Model ID:** `wavespeed-ai/image-face-swap`

Replace a face in an image with a reference face.

#### Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `image` | string | Yes | -- | URL of the image containing the face to replace |
| `face_image` | string | Yes | -- | URL of the reference face image to swap in |
| `target_index` | integer | No | `0` | Which face to replace (0 = largest face, 1-10 for others) |
| `output_format` | string | No | `jpeg` | Output format. One of: `jpeg`, `png`, `webp` |

#### Example

```javascript
import wavespeed from 'wavespeed';

const imageUrl = await wavespeed.upload("/path/to/group-photo.png");
const faceUrl = await wavespeed.upload("/path/to/reference-face.png");

const output_url = (await wavespeed.run(
  "wavespeed-ai/image-face-swap",
  {
    image: imageUrl,
    face_image: faceUrl,
    target_index: 0,
    output_format: "png"
  }
))["outputs"][0];
```

#### Targeting a Specific Face

When multiple people are in the image, use `target_index` to select which face to replace:

```javascript
// Replace the second-largest face in the image
const output_url = (await wavespeed.run(
  "wavespeed-ai/image-face-swap",
  {
    image: imageUrl,
    face_image: faceUrl,
    target_index: 1
  }
))["outputs"][0];
```

### Video Face Swap

**Model ID:** `wavespeed-ai/video-face-swap`

Replace a face in a video with a reference face. Supports videos up to 10 minutes.

#### Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `video` | string | Yes | -- | URL of the video containing the face to replace. Must be publicly accessible. Max 10 minutes. |
| `face_image` | string | Yes | -- | URL of the reference face image to swap in |
| `target_index` | integer | No | `0` | Which face to replace (0 = largest face, 1-10 for others) |

#### Example

```javascript
import wavespeed from 'wavespeed';

const videoUrl = await wavespeed.upload("/path/to/video.mp4");
const faceUrl = await wavespeed.upload("/path/to/reference-face.png");

const output_url = (await wavespeed.run(
  "wavespeed-ai/video-face-swap",
  {
    video: videoUrl,
    face_image: faceUrl,
    target_index: 0
  }
))["outputs"][0];
```

## Advanced Usage

### Sync Mode (Image Face Swap only)

```javascript
const output_url = (await wavespeed.run(
  "wavespeed-ai/image-face-swap",
  {
    image: imageUrl,
    face_image: faceUrl
  },
  { enableSyncMode: true }
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
  "wavespeed-ai/image-face-swap",
  {
    image: imageUrl,
    face_image: faceUrl
  }
))["outputs"][0];
```

### Error Handling with runNoThrow

```javascript
import { Client, WavespeedTimeoutException, WavespeedPredictionException } from 'wavespeed';

const client = new Client();
const result = await client.runNoThrow(
  "wavespeed-ai/image-face-swap",
  {
    image: imageUrl,
    face_image: faceUrl
  }
);

if (result.outputs) {
  console.log("Output URL:", result.outputs[0]);
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

| Operation | Cost |
|-----------|------|
| Image face swap | $0.01 per image |
| Video face swap | $0.01 per second (minimum $0.05 / 5 seconds) |

Video face swap supports videos up to 10 minutes.

## Tips

- Use clear, front-facing portraits for the reference face for best results
- Consistent lighting between the target and reference face improves quality
- Anime or illustrated characters may produce lower quality output
- Use `target_index` to select specific faces when multiple people are present (0 = largest face)

## Security Constraints

- **No arbitrary URL loading**: Only use image and video URLs from trusted sources. Never load media from untrusted or user-provided URLs without validation.
- **API key security**: Store your `WAVESPEED_API_KEY` securely. Do not hardcode it in source files or commit it to version control. Use environment variables or secret management systems.
- **Input validation**: Only pass parameters documented above. Validate media URLs before sending requests.
