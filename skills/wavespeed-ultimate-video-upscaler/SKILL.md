---
name: wavespeed-ultimate-video-upscaler
description: Upscale videos to 720p, 1080p, 2K, or 4K resolution using WaveSpeed AI's Ultimate Video Upscaler. Takes a video URL and produces a higher-resolution version. Supports videos up to 10 minutes. Use when the user wants to upscale or enhance the resolution of a video.
metadata:
  author: wavespeedai
  version: "1.0"
---

# WaveSpeedAI Ultimate Video Upscaler

Upscale videos to 720p, 1080p, 2K, or 4K resolution using WaveSpeed AI's Ultimate Video Upscaler. Supports videos up to 10 minutes long.

## Authentication

```bash
export WAVESPEED_API_KEY="your-api-key"
```

Get your API key at [wavespeed.ai/accesskey](https://wavespeed.ai/accesskey).

## Quick Start

```javascript
import wavespeed from 'wavespeed';

// Upload a local video to get a URL
const videoUrl = await wavespeed.upload("/path/to/video.mp4");

const output_url = (await wavespeed.run(
  "wavespeed-ai/ultimate-video-upscaler",
  { video: videoUrl }
))["outputs"][0];
```

You can also pass an existing video URL directly:

```javascript
const output_url = (await wavespeed.run(
  "wavespeed-ai/ultimate-video-upscaler",
  { video: "https://example.com/video.mp4" }
))["outputs"][0];
```

## API Endpoint

**Model ID:** `wavespeed-ai/ultimate-video-upscaler`

Upscale a video to a higher resolution.

### Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `video` | string | Yes | -- | URL of the video to upscale. Must be publicly accessible. |
| `target_resolution` | string | No | `1080p` | Target resolution. One of: `720p`, `1080p`, `2k`, `4k` |

### Example

```javascript
import wavespeed from 'wavespeed';

const videoUrl = await wavespeed.upload("/path/to/video.mp4");

const output_url = (await wavespeed.run(
  "wavespeed-ai/ultimate-video-upscaler",
  {
    video: videoUrl,
    target_resolution: "4k"
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

const videoUrl = await client.upload("/path/to/video.mp4");

const output_url = (await client.run(
  "wavespeed-ai/ultimate-video-upscaler",
  { video: videoUrl, target_resolution: "4k" }
))["outputs"][0];
```

### Error Handling with runNoThrow

```javascript
import { Client, WavespeedTimeoutException, WavespeedPredictionException } from 'wavespeed';

const client = new Client();
const result = await client.runNoThrow(
  "wavespeed-ai/ultimate-video-upscaler",
  { video: videoUrl }
);

if (result.outputs) {
  console.log("Upscaled video URL:", result.outputs[0]);
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

| Target Resolution | Cost per 5 seconds |
|-------------------|--------------------|
| 720p | $0.10 |
| 1080p | $0.15 |
| 2K | $0.25 |
| 4K | $0.40 |

Minimum charge is 5 seconds. Videos up to 10 minutes supported. Processing time is approximately 10-30 seconds per 1 second of video.

## Security Constraints

- **No arbitrary URL loading**: Only use video URLs from trusted sources. Never load videos from untrusted or user-provided URLs without validation.
- **API key security**: Store your `WAVESPEED_API_KEY` securely. Do not hardcode it in source files or commit it to version control. Use environment variables or secret management systems.
- **Input validation**: Only pass parameters documented above. Validate video URLs before sending requests.
