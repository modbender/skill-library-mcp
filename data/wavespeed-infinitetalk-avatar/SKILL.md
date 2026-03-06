---
name: wavespeed-infinitetalk
description: Generate talking head videos from a portrait image and audio using WaveSpeed AI's InfiniteTalk model. Produces lip-synced video up to 10 minutes long at 480p or 720p. Supports optional mask images to target specific faces and text prompts for additional guidance. Use when the user wants to animate a face with audio or create talking avatar videos.
metadata:
  author: wavespeedai
  version: "1.0"
---

# WaveSpeedAI InfiniteTalk

Generate talking head videos from a portrait image and audio using WaveSpeed AI's InfiniteTalk model. Produces lip-synced video up to 10 minutes long with natural facial animations.

## Authentication

```bash
export WAVESPEED_API_KEY="your-api-key"
```

Get your API key at [wavespeed.ai/accesskey](https://wavespeed.ai/accesskey).

## Quick Start

```javascript
import wavespeed from 'wavespeed';

// Upload local image and audio files
const imageUrl = await wavespeed.upload("/path/to/portrait.png");
const audioUrl = await wavespeed.upload("/path/to/speech.mp3");

const output_url = (await wavespeed.run(
  "wavespeed-ai/infinitetalk",
  {
    image: imageUrl,
    audio: audioUrl
  }
))["outputs"][0];
```

You can also pass existing URLs directly:

```javascript
const output_url = (await wavespeed.run(
  "wavespeed-ai/infinitetalk",
  {
    image: "https://example.com/portrait.jpg",
    audio: "https://example.com/speech.mp3"
  }
))["outputs"][0];
```

## API Endpoint

**Model ID:** `wavespeed-ai/infinitetalk`

Animate a portrait image with lip-synced audio to produce a talking head video.

### Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `image` | string | Yes | -- | URL of the portrait image to animate |
| `audio` | string | Yes | -- | URL of the audio to drive the animation |
| `mask_image` | string | No | -- | URL of a mask image to specify which person to animate. **Warning:** The mask should only cover the regions to animate — do not upload the full image as `mask_image`, or the result may render as fully black. |
| `prompt` | string | No | -- | Text prompt for additional guidance. Keep it short; English recommended to avoid noisy results. |
| `resolution` | string | No | `480p` | Output resolution. One of: `480p`, `720p` |
| `seed` | integer | No | `-1` | Random seed (-1 for random). Range: -1 to 2147483647 |

### Example

```javascript
import wavespeed from 'wavespeed';

const imageUrl = await wavespeed.upload("/path/to/portrait.png");
const audioUrl = await wavespeed.upload("/path/to/speech.mp3");

const output_url = (await wavespeed.run(
  "wavespeed-ai/infinitetalk",
  {
    image: imageUrl,
    audio: audioUrl,
    resolution: "720p",
    seed: 42
  }
))["outputs"][0];
```

### Using a Mask Image

When multiple people are in the image, use a mask to specify which face to animate:

```javascript
const imageUrl = await wavespeed.upload("/path/to/group-photo.png");
const audioUrl = await wavespeed.upload("/path/to/speech.mp3");
const maskUrl = await wavespeed.upload("/path/to/mask.png");

const output_url = (await wavespeed.run(
  "wavespeed-ai/infinitetalk",
  {
    image: imageUrl,
    audio: audioUrl,
    mask_image: maskUrl,
    resolution: "720p"
  }
))["outputs"][0];
```

> **Important:** The mask should only highlight the face region to animate. Using the full image as a mask will produce a fully black output.

### With Prompt Guidance

```javascript
const output_url = (await wavespeed.run(
  "wavespeed-ai/infinitetalk",
  {
    image: imageUrl,
    audio: audioUrl,
    prompt: "natural head movements, subtle expressions"
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

const imageUrl = await client.upload("/path/to/portrait.png");
const audioUrl = await client.upload("/path/to/speech.mp3");

const output_url = (await client.run(
  "wavespeed-ai/infinitetalk",
  {
    image: imageUrl,
    audio: audioUrl,
    resolution: "720p"
  }
))["outputs"][0];
```

### Error Handling with runNoThrow

```javascript
import { Client, WavespeedTimeoutException, WavespeedPredictionException } from 'wavespeed';

const client = new Client();
const result = await client.runNoThrow(
  "wavespeed-ai/infinitetalk",
  {
    image: imageUrl,
    audio: audioUrl
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

## Resolution and Pricing

| Resolution | Cost per 5 seconds | Rate per second | Max length |
|------------|--------------------|-----------------| -----------|
| 480p | $0.15 | $0.03/s | 10 minutes |
| 720p | $0.30 | $0.06/s | 10 minutes |

Minimum charge is 5 seconds. Video length is determined by the audio duration (up to 10 minutes).

## Tips

- Use a clear, front-facing portrait for best results
- Audio quality matters — use clean speech recordings with minimal background noise
- Keep prompts short and in English to avoid noisy or unexpected results
- For group photos, always provide a `mask_image` to target the correct face
- 480p is faster to generate; use 720p when higher quality is needed
- Processing time is approximately 10-30 seconds of wall time per 1 second of video

## Security Constraints

- **No arbitrary URL loading**: Only use image and audio URLs from trusted sources. Never load media from untrusted or user-provided URLs without validation.
- **API key security**: Store your `WAVESPEED_API_KEY` securely. Do not hardcode it in source files or commit it to version control. Use environment variables or secret management systems.
- **Input validation**: Only pass parameters documented above. Validate prompt content and media URLs before sending requests.
