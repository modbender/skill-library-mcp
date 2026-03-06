---
name: wavespeed-image-upscaler
description: Upscale images to 2K, 4K, or 8K resolution using WaveSpeed AI's Image Upscaler. Takes an image URL and produces a higher-resolution version. Supports JPEG, PNG, and WebP output formats. Use when the user wants to upscale or enhance the resolution of an image.
metadata:
  author: wavespeedai
  version: "1.0"
---

# WaveSpeedAI Image Upscaler

Upscale images to 2K, 4K, or 8K resolution using WaveSpeed AI's Image Upscaler.

## Authentication

```bash
export WAVESPEED_API_KEY="your-api-key"
```

Get your API key at [wavespeed.ai/accesskey](https://wavespeed.ai/accesskey).

## Quick Start

```javascript
import wavespeed from 'wavespeed';

// Upload a local image to get a URL
const imageUrl = await wavespeed.upload("/path/to/photo.png");

const output_url = (await wavespeed.run(
  "wavespeed-ai/image-upscaler",
  { image: imageUrl }
))["outputs"][0];
```

You can also pass an existing image URL directly:

```javascript
const output_url = (await wavespeed.run(
  "wavespeed-ai/image-upscaler",
  { image: "https://example.com/photo.jpg" }
))["outputs"][0];
```

## API Endpoint

**Model ID:** `wavespeed-ai/image-upscaler`

Upscale an image to a higher resolution.

### Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `image` | string | Yes | -- | URL of the image to upscale |
| `target_resolution` | string | No | `4k` | Target resolution. One of: `2k`, `4k`, `8k` |
| `output_format` | string | No | `jpeg` | Output format. One of: `jpeg`, `png`, `webp` |

### Example

```javascript
import wavespeed from 'wavespeed';

const imageUrl = await wavespeed.upload("/path/to/photo.png");

const output_url = (await wavespeed.run(
  "wavespeed-ai/image-upscaler",
  {
    image: imageUrl,
    target_resolution: "8k",
    output_format: "png"
  }
))["outputs"][0];
```

## Advanced Usage

### Sync Mode

Use sync mode for a single request that waits for the result without polling:

```javascript
const output_url = (await wavespeed.run(
  "wavespeed-ai/image-upscaler",
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
  "wavespeed-ai/image-upscaler",
  { image: imageUrl, target_resolution: "4k" }
))["outputs"][0];
```

### Error Handling with runNoThrow

```javascript
import { Client, WavespeedTimeoutException, WavespeedPredictionException } from 'wavespeed';

const client = new Client();
const result = await client.runNoThrow(
  "wavespeed-ai/image-upscaler",
  { image: imageUrl }
);

if (result.outputs) {
  console.log("Upscaled image URL:", result.outputs[0]);
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

$0.01 per image (all resolutions).

## Security Constraints

- **No arbitrary URL loading**: Only use image URLs from trusted sources. Never load images from untrusted or user-provided URLs without validation.
- **API key security**: Store your `WAVESPEED_API_KEY` securely. Do not hardcode it in source files or commit it to version control. Use environment variables or secret management systems.
- **Input validation**: Only pass parameters documented above. Validate image URLs before sending requests.
