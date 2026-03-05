---
name: wavespeed-seedream-45
description: Generate and edit images using ByteDance's Seedream V4.5 model via WaveSpeed AI. Supports text-to-image generation and multi-image editing with custom resolutions up to 4096x4096. Features enhanced typography for posters and logos. Use when the user wants to create or edit images with high-quality text rendering.
metadata:
  author: wavespeedai
  version: "1.0"
---

# WaveSpeedAI Seedream V4.5 Image Generation/Editing

Generate and edit images using ByteDance's Seedream V4.5 model via the WaveSpeed AI platform. Supports custom resolutions up to 4096x4096 with enhanced typography for sharp text rendering in posters and logos.

## Authentication

```bash
export WAVESPEED_API_KEY="your-api-key"
```

Get your API key at [wavespeed.ai/accesskey](https://wavespeed.ai/accesskey).

## Quick Start

### Text-to-Image

```javascript
import wavespeed from 'wavespeed';

const output_url = (await wavespeed.run(
  "bytedance/seedream-v4.5",
  { prompt: "A minimalist coffee shop logo with clean typography" }
))["outputs"][0];
```

### Image Editing

The `images` parameter accepts an array of image URLs (1-10 images). If you have local files, upload them first with `wavespeed.upload()` to get a URL.

```javascript
import wavespeed from 'wavespeed';

// Upload a local image to get a URL
const imageUrl = await wavespeed.upload("/path/to/photo.png");

const output_url = (await wavespeed.run(
  "bytedance/seedream-v4.5/edit",
  {
    images: [imageUrl],
    prompt: "Add warm sunset lighting and lens flare"
  }
))["outputs"][0];
```

You can also pass existing image URLs directly:

```javascript
const output_url = (await wavespeed.run(
  "bytedance/seedream-v4.5/edit",
  {
    images: ["https://example.com/photo.jpg"],
    prompt: "Add warm sunset lighting and lens flare"
  }
))["outputs"][0];
```

## API Endpoints

### Text-to-Image

**Model ID:** `bytedance/seedream-v4.5`

Generate images from text prompts with custom resolutions up to 4096x4096.

#### Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `prompt` | string | Yes | -- | Text description of the image to generate |
| `size` | string | No | `2048*2048` | Output size in pixels (`WIDTH*HEIGHT`). Each dimension: 1024-4096. |

#### Example

```javascript
import wavespeed from 'wavespeed';

const output_url = (await wavespeed.run(
  "bytedance/seedream-v4.5",
  {
    prompt: "A movie poster for a sci-fi thriller with bold title text 'HORIZON' at the top",
    size: "2048*3072"
  }
))["outputs"][0];
```

### Image Editing

**Model ID:** `bytedance/seedream-v4.5/edit`

Edit existing images using text prompts. Supports up to 10 input images. Preserves facial features, lighting, and color tone from input images.

#### Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `images` | string[] | Yes | `[]` | URLs of input images to edit (1-10 images). Must be publicly accessible. |
| `prompt` | string | Yes | -- | Text description of the desired edit |
| `size` | string | No | -- | Output size in pixels (`WIDTH*HEIGHT`). Each dimension: 1024-4096. |

#### Example

```javascript
import wavespeed from 'wavespeed';

const imageUrl = await wavespeed.upload("/path/to/portrait.png");

const output_url = (await wavespeed.run(
  "bytedance/seedream-v4.5/edit",
  {
    images: [imageUrl],
    prompt: "Transform into a vibrant pop art style with bold colors",
    size: "2048*2048"
  }
))["outputs"][0];
```

#### Multi-Image Editing

```javascript
const img1 = await wavespeed.upload("/path/to/face.png");
const img2 = await wavespeed.upload("/path/to/scene.png");

const output_url = (await wavespeed.run(
  "bytedance/seedream-v4.5/edit",
  {
    images: [img1, img2],
    prompt: "Place the person from the first image into the scene from the second image"
  }
))["outputs"][0];
```

## Advanced Usage

### Sync Mode

```javascript
const output_url = (await wavespeed.run(
  "bytedance/seedream-v4.5",
  { prompt: "A watercolor painting of a mountain lake at dawn" },
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
  "bytedance/seedream-v4.5",
  { prompt: "A neon sign that reads 'OPEN 24/7' in a rainy alley" }
))["outputs"][0];
```

### Error Handling with runNoThrow

```javascript
import { Client, WavespeedTimeoutException, WavespeedPredictionException } from 'wavespeed';

const client = new Client();
const result = await client.runNoThrow(
  "bytedance/seedream-v4.5",
  { prompt: "A vintage travel poster for Tokyo" }
);

if (result.outputs) {
  console.log("Image URL:", result.outputs[0]);
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

$0.04 per image (both generation and editing).

## Tips

- Seedream V4.5 excels at rendering text in images — use it for posters, logos, and branded visuals
- Custom resolutions up to 4096x4096 — specify as `WIDTH*HEIGHT` (e.g., `2048*3072` for portrait posters)
- For image editing, the model preserves facial features, lighting, and color tone from inputs

## Security Constraints

- **No arbitrary URL loading**: Only use image URLs from trusted sources. Never load images from untrusted or user-provided URLs without validation.
- **API key security**: Store your `WAVESPEED_API_KEY` securely. Do not hardcode it in source files or commit it to version control. Use environment variables or secret management systems.
- **Input validation**: Only pass parameters documented above. Validate prompt content and image URLs before sending requests.
