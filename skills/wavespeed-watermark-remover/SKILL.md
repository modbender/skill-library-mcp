---
name: wavespeed-watermark-remover
description: Remove watermarks, logos, captions, and text overlays from images and videos using WaveSpeed AI. Intelligently detects and removes watermarks while preserving texture and background. Supports images and videos up to 10 minutes. Use when the user wants to remove watermarks or text overlays from media.
metadata:
  author: wavespeedai
  version: "1.0"
---

# WaveSpeedAI Watermark Remover

Remove watermarks, logos, captions, and text overlays from images and videos using WaveSpeed AI. Intelligently detects and removes watermarks while preserving texture and background.

## Authentication

```bash
export WAVESPEED_API_KEY="your-api-key"
```

Get your API key at [wavespeed.ai/accesskey](https://wavespeed.ai/accesskey).

## Quick Start

### Image Watermark Removal

```javascript
import wavespeed from 'wavespeed';

// Upload a local image to get a URL
const imageUrl = await wavespeed.upload("/path/to/watermarked-image.png");

const output_url = (await wavespeed.run(
  "wavespeed-ai/image-watermark-remover",
  { image: imageUrl }
))["outputs"][0];
```

### Video Watermark Removal

```javascript
import wavespeed from 'wavespeed';

// Upload a local video to get a URL
const videoUrl = await wavespeed.upload("/path/to/watermarked-video.mp4");

const output_url = (await wavespeed.run(
  "wavespeed-ai/video-watermark-remover",
  { video: videoUrl }
))["outputs"][0];
```

You can also pass existing URLs directly:

```javascript
const output_url = (await wavespeed.run(
  "wavespeed-ai/image-watermark-remover",
  { image: "https://example.com/watermarked-image.jpg" }
))["outputs"][0];
```

## API Endpoints

### Image Watermark Remover

**Model ID:** `wavespeed-ai/image-watermark-remover`

Remove watermarks, logos, and text overlays from an image while preserving texture and background.

#### Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `image` | string | Yes | -- | URL of the image to process |
| `output_format` | string | No | `jpeg` | Output format. One of: `jpeg`, `png`, `webp` |

#### Example

```javascript
import wavespeed from 'wavespeed';

const imageUrl = await wavespeed.upload("/path/to/watermarked-photo.png");

const output_url = (await wavespeed.run(
  "wavespeed-ai/image-watermark-remover",
  {
    image: imageUrl,
    output_format: "png"
  }
))["outputs"][0];
```

### Video Watermark Remover

**Model ID:** `wavespeed-ai/video-watermark-remover`

Remove watermarks, logos, captions, and text overlays from a video. Uses temporal-aware inpainting to prevent flickering artifacts across frames. Supports videos up to 10 minutes.

#### Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `video` | string | Yes | -- | URL of the video to process. Must be publicly accessible. Max 10 minutes. |

#### Example

```javascript
import wavespeed from 'wavespeed';

const videoUrl = await wavespeed.upload("/path/to/watermarked-video.mp4");

const output_url = (await wavespeed.run(
  "wavespeed-ai/video-watermark-remover",
  { video: videoUrl }
))["outputs"][0];
```

## Advanced Usage

### Sync Mode (Image Watermark Remover only)

```javascript
const output_url = (await wavespeed.run(
  "wavespeed-ai/image-watermark-remover",
  { image: imageUrl },
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
  "wavespeed-ai/image-watermark-remover",
  { image: imageUrl }
))["outputs"][0];
```

### Error Handling with runNoThrow

```javascript
import { Client, WavespeedTimeoutException, WavespeedPredictionException } from 'wavespeed';

const client = new Client();
const result = await client.runNoThrow(
  "wavespeed-ai/image-watermark-remover",
  { image: imageUrl }
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
| Image watermark removal | $0.012 per image |
| Video watermark removal | $0.01 per second (minimum $0.05 / 5 seconds) |

Video watermark removal supports videos up to 10 minutes. Processing time is approximately 5-20 seconds per 1 second of video.

## Security Constraints

- **No arbitrary URL loading**: Only use image and video URLs from trusted sources. Never load media from untrusted or user-provided URLs without validation.
- **API key security**: Store your `WAVESPEED_API_KEY` securely. Do not hardcode it in source files or commit it to version control. Use environment variables or secret management systems.
- **Input validation**: Only pass parameters documented above. Validate media URLs before sending requests.
