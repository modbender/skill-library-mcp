---
name: pixeldojo
description: Generate AI images and videos using PixelDojo API. Supports 60+ models including Flux 2, WAN, Veo 3.1, Imagen 4, Kling, and more. Handles async job submission, status polling, and automatic downloading of results.
metadata:
  {
    "clawhub":
      {
        "requires": { 
          "env": ["PIXELDOJO_API_KEY"],
          "bins": ["curl", "jq"]
        },
        "homepage": "https://pixeldojo.ai",
        "source": "https://github.com/blovett80/pixeldojo-skill"
      }
  }
---

# PixelDojo Skill

Generate AI images and videos using the PixelDojo API platform.

## Setup

1. **Get API Key:** Sign up at [https://pixeldojo.ai/api-platform](https://pixeldojo.ai/api-platform)
2. **Buy Credits:** Purchase credits at [https://pixeldojo.ai/api-platform/buy-credits](https://pixeldojo.ai/api-platform/buy-credits)
   - **$5** = ~800 images with P-Image model
3. **Set Environment Variable:**
   ```bash
   export PIXELDOJO_API_KEY=your_api_key_here
   ```
   (Or copy `.env.example` to `.env` and fill in your key)

- **API Documentation:** [https://pixeldojo.ai/api-platform](https://pixeldojo.ai/api-platform)
- **Base URL:** `https://pixeldojo.ai/api/v1`

## Available Models

### Image Models
- `flux-1.1-pro` - Latest pro model with enhanced quality (recommended)
- `flux-1.1-pro-ultra` - Highest quality Flux model with raw mode
- `flux-dev` - Development model with configurable steps and LoRA support
- `flux-krea-dev` - Photorealistic, avoids oversaturated AI look
- `flux-kontext-pro` - Advanced model with editing capabilities
- `flux-kontext-max` - Premium model with maximum performance

### Video Models
- `wan-2.6-flash` - Fast video generation
- `wan-2.2` - Higher quality video
- `veo-3.1` - Google's Veo 3.1 with native audio
- `kling-2.5-turbo-pro` - Kling turbo
- `kling-pro` - Kling professional
- `minimax` - Minimax video

## Core Operations

### Generate Image

```bash
# Basic image generation
bash ~/.openclaw/skills/pixeldojo/generate.sh image "a serene mountain landscape at sunset" flux-2

# With options
bash ~/.openclaw/skills/pixeldojo/generate.sh image "cyberpunk city" flux-2 --aspect-ratio 16:9 --output ~/Desktop/cyberpunk.png
```

### Generate Video

```bash
# Text-to-video
bash ~/.openclaw/skills/pixeldojo/generate.sh video "ocean waves crashing on rocks" wan-2.6-flash --duration 5

# Image-to-video
bash ~/.openclaw/skills/pixeldojo/generate.sh video "make it cinematic" wan-2.6-flash --image-url https://example.com/image.png --duration 5
```

### Check Job Status

```bash
bash ~/.openclaw/skills/pixeldojo/status.sh job_abc123
```

### List Available Models

```bash
bash ~/.openclaw/skills/pixeldojo/models.sh
```

## API Reference

### Submit Job
- **Endpoint:** `POST /api/v1/models/{model}/run`
- **Headers:** `Authorization: Bearer {API_KEY}`, `Content-Type: application/json`
- **Body (Image):**
  ```json
  {
    "prompt": "description of image",
    "aspect_ratio": "16:9"
  }
  ```
- **Body (Video):**
  ```json
  {
    "prompt": "description of video",
    "image_url": "https://...",  // optional, for image-to-video
    "duration": 5,                // seconds
    "aspect_ratio": "16:9"
  }
  ```
- **Response:**
  ```json
  {
    "jobId": "job_abc123",
    "status": "pending",
    "statusUrl": "https://pixeldojo.ai/api/v1/jobs/job_abc123"
  }
  ```

### Check Status
- **Endpoint:** `GET /api/v1/jobs/{job_id}`
- **Headers:** `Authorization: Bearer {API_KEY}`
- **Response (completed):**
  ```json
  {
    "jobId": "job_abc123",
    "status": "completed",
    "output": {
      "image": "https://temp.pixeldojo.ai/...png",
      "video": "https://temp.pixeldojo.ai/...mp4"
    }
  }
  ```

### Download Result
Results are automatically downloaded to `~/Pictures/AI Generated/` with timestamped filenames for easy access.

## Workflow

1. **Submit:** Call generate endpoint, get job ID
2. **Poll:** Check status URL every 2-5 seconds
3. **Download:** Once `status === "completed"`, download from output URL
4. **Save:** Store in workspace with descriptive filename

## Error Handling

- Rate limit: 10 requests/minute (contact support for higher)
- Credits: Check dashboard for credit balance
- Timeouts: Video generation can take 30-120 seconds

## Example Usage

```bash
# Generate a cyberpunk portrait
bash ~/.openclaw/skills/pixeldojo/generate.sh image "cyberpunk samurai with neon lights, detailed, 8k" flux-2 --output ~/Desktop/samurai.png

# Animate a photo
bash ~/.openclaw/skills/pixeldojo/generate.sh video "slow motion drift, cinematic" wan-2.6-flash --image-url https://mycdn.com/photo.jpg --duration 5
```

## Output Location

All generated files are saved to your **Pictures folder** for easy access:
- `~/Pictures/AI Generated/images/`
- `~/Pictures/AI Generated/videos/`

With format: `{timestamp}_{prompt_snippet}.{ext}`

Use `--output <path>` to save to a custom location.
