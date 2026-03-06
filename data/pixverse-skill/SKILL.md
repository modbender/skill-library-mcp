---
name: pixverse
description: Generate AI videos using Pixverse API
homepage: https://pixverse.ai/
metadata:
  openclaw:
    emoji: "🎬"
    requires:
      env: ["PIXVERSE_API_KEY"]
    primaryEnv: "PIXVERSE_API_KEY"
---

# Pixverse Video Generation

Generate AI videos using the Pixverse API.

## Setup

1. Get your API key from https://pixverse.ai/
2. Set the environment variable:
   ```bash
   export PIXVERSE_API_KEY="your-api-key-here"
   ```
   Or add to `~/.openclaw/openclaw.json`:
   ```json
   {
     "skills": {
       "pixverse": {
         "env": {
           "PIXVERSE_API_KEY": "your-api-key-here"
         }
       }
     }
   }
   ```

## Usage

### Generate Video from Text Prompt

```bash
curl -X POST https://api.pixverse.ai/v1/generate \
  -H "Authorization: Bearer $PIXVERSE_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "A group of hackers coding intensely in a futuristic lab",
    "aspect_ratio": "16:9",
    "duration": 4,
    "style": "realistic"
  }'
```

### Generate Video from Image

```bash
curl -X POST https://api.pixverse.ai/v1/generate \
  -H "Authorization: Bearer $PIXVERSE_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "image_url": "https://example.com/image.png",
    "prompt": "Make this image come alive with motion",
    "duration": 4
  }'
```

### Check Video Status

```bash
curl -X GET https://api.pixverse.ai/v1/tasks/{task_id} \
  -H "Authorization: Bearer $PIXVERSE_API_KEY"
```

### Download Video

Once the task is complete, download the video URL from the response.

## Parameters

- **prompt**: Text description of the video (required)
- **image_url**: Starting image URL (optional)
- **aspect_ratio**: "16:9", "9:16", "1:1" (default: "16:9")
- **duration**: 2-8 seconds (default: 4)
- **style**: "realistic", "anime", "3d", "cinematic" (default: "realistic")
- **motion_strength**: 0-10 (default: 5)

## Notes

⚠️ **Important**: 
- This is a template skill. You need to verify the actual Pixverse API endpoints
- Pixverse may require different authentication or have different API structure
- Check https://docs.pixverse.ai/ for the latest API documentation
- Video generation may take 1-5 minutes depending on complexity

## Alternative: Web UI Automation

If API access is not available, consider using browser automation to interact with the Pixverse web interface.
