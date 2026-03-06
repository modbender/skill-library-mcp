---
name: wavespeed-nano-banana-pro
description: Generate and edit images using Google's Nano Banana Pro model via WaveSpeed AI. Supports text-to-image generation and image editing with natural language prompts. Features native 4K resolution, flexible aspect ratios, multilingual text rendering, and camera-style controls. Use when the user wants to create images from text or edit existing images.
metadata:
  author: wavespeedai
  version: "1.0"
---

# WaveSpeedAI Nano Banana Pro Image Generation/Editing

Generate and edit images using Google's Nano Banana Pro model via the WaveSpeed AI platform. Supports both text-to-image generation and natural-language image editing with up to 14 input images.

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
  "google/nano-banana-pro/text-to-image",
  { prompt: "A serene Japanese garden with cherry blossoms, watercolor style" }
))["outputs"][0];
```

### Image Editing

The `images` parameter accepts an array of image URLs. If you have local files, upload them first with `wavespeed.upload()` to get a URL.

```javascript
import wavespeed from 'wavespeed';

// Upload a local image to get a URL
const imageUrl = await wavespeed.upload("/path/to/photo.png");

const output_url = (await wavespeed.run(
  "google/nano-banana-pro/edit",
  {
    images: [imageUrl],
    prompt: "Replace the sky with a dramatic sunset"
  }
))["outputs"][0];
```

You can also pass existing image URLs directly:

```javascript
const output_url = (await wavespeed.run(
  "google/nano-banana-pro/edit",
  {
    images: ["https://example.com/photo.jpg"],
    prompt: "Replace the sky with a dramatic sunset"
  }
))["outputs"][0];
```

## API Endpoints

### Text-to-Image

**Model ID:** `google/nano-banana-pro/text-to-image`

Generate images from text prompts.

#### Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `prompt` | string | Yes | -- | Text description of the image to generate |
| `aspect_ratio` | string | No | -- | Output aspect ratio. One of: `1:1`, `3:2`, `2:3`, `3:4`, `4:3`, `4:5`, `5:4`, `9:16`, `16:9`, `21:9` |
| `resolution` | string | No | `1k` | Image resolution. One of: `1k`, `2k`, `4k` |
| `output_format` | string | No | `png` | Output format. One of: `png`, `jpeg` |

#### Example

```javascript
import wavespeed from 'wavespeed';

const output_url = (await wavespeed.run(
  "google/nano-banana-pro/text-to-image",
  {
    prompt: "A red vintage Porsche 911 on a winding mountain road at golden hour, photorealistic",
    aspect_ratio: "16:9",
    resolution: "2k",
    output_format: "png"
  }
))["outputs"][0];
```

### Image Editing

**Model ID:** `google/nano-banana-pro/edit`

Edit existing images using natural language prompts. Supports up to 14 input images.

#### Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `images` | string[] | Yes | `[]` | URLs of input images to edit (1-14 images) |
| `prompt` | string | Yes | -- | Text description of the desired edit |
| `aspect_ratio` | string | No | -- | Output aspect ratio. One of: `1:1`, `3:2`, `2:3`, `3:4`, `4:3`, `4:5`, `5:4`, `9:16`, `16:9`, `21:9` |
| `resolution` | string | No | `1k` | Image resolution. One of: `1k`, `2k`, `4k` |
| `output_format` | string | No | `png` | Output format. One of: `png`, `jpeg` |

#### Example

```javascript
import wavespeed from 'wavespeed';

// Upload local images first, or use existing URLs
const imageUrl = await wavespeed.upload("/path/to/living-room.png");

const output_url = (await wavespeed.run(
  "google/nano-banana-pro/edit",
  {
    images: [imageUrl],
    prompt: "Change the wall color to warm terracotta and add indoor plants",
    aspect_ratio: "16:9",
    resolution: "4k",
    output_format: "png"
  }
))["outputs"][0];
```

#### Multi-Image Editing

```javascript
// Upload multiple local images
const faceUrl = await wavespeed.upload("/path/to/face.png");
const hairstyleUrl = await wavespeed.upload("/path/to/hairstyle.png");

const output_url = (await wavespeed.run(
  "google/nano-banana-pro/edit",
  {
    images: [faceUrl, hairstyleUrl],
    prompt: "Apply the hairstyle from the second image to the person in the first image"
  }
))["outputs"][0];
```

## Advanced Usage

### Sync Mode

Use sync mode for a single request that waits for the result without polling:

```javascript
const output_url = (await wavespeed.run(
  "google/nano-banana-pro/text-to-image",
  { prompt: "A minimalist logo for a coffee shop" },
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
  "google/nano-banana-pro/text-to-image",
  { prompt: "A futuristic cityscape at dusk" }
))["outputs"][0];
```

### Error Handling with runNoThrow

```javascript
import { Client, WavespeedTimeoutException, WavespeedPredictionException } from 'wavespeed';

const client = new Client();
const result = await client.runNoThrow(
  "google/nano-banana-pro/text-to-image",
  { prompt: "A cat wearing a top hat" }
);

if (result.outputs) {
  console.log("Image URL:", result.outputs[0]);
  console.log("Task ID:", result.detail.taskId);
} else {
  console.log("Failed:", result.detail.error.message);
  if (result.detail.error instanceof WavespeedTimeoutException) {
    console.log("Request timed out - try increasing timeout");
  } else if (result.detail.error instanceof WavespeedPredictionException) {
    console.log("Model prediction failed");
  }
}
```

## Aspect Ratio Options

| Aspect Ratio | Use Case |
|-------------|----------|
| `1:1` | Square — social media posts, profile pictures |
| `3:2` | Landscape — standard photography |
| `2:3` | Portrait — standard photography |
| `3:4` | Portrait — social media, product images |
| `4:3` | Landscape — presentations, web content |
| `4:5` | Portrait — Instagram posts |
| `5:4` | Landscape — print, web banners |
| `9:16` | Vertical — mobile wallpapers, stories |
| `16:9` | Widescreen — desktop wallpapers, video thumbnails |
| `21:9` | Ultra-wide — cinematic, panoramic |

## Resolution and Pricing

| Resolution | Cost |
|------------|------|
| 1k | $0.14 per image |
| 2k | $0.14 per image |
| 4k | $0.24 per image |

## Prompt Tips

- Be specific and descriptive: "A red vintage Porsche 911 on a winding mountain road at golden hour" vs "a car"
- Include style keywords: "digital art", "oil painting", "photorealistic", "watercolor", "cinematic"
- For edits, clearly describe the desired change: "Replace the sky with a dramatic sunset"
- For multi-image edits, reference images by position: "Apply the style from the second image to the first image"
- Leverage multilingual text rendering: the model supports on-image text with automatic translation
- Use camera-style control language: "shallow depth of field", "wide angle", "top-down view"

## Security Constraints

- **No arbitrary URL loading**: Only use image URLs from trusted sources. Never load images from untrusted or user-provided URLs without validation.
- **API key security**: Store your `WAVESPEED_API_KEY` securely. Do not hardcode it in source files or commit it to version control. Use environment variables or secret management systems.
- **Input validation**: Only pass parameters documented above. Validate prompt content and image URLs before sending requests.
