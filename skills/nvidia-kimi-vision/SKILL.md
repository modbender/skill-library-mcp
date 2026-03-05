---
name: nvidia-kimi-vision
description: Analyze images using NVIDIA Kimi K2.5 vision model via NVIDIA NIM API. Perfect for adding vision to non-vision models like MiniMax M2.5, GLM-5, or any model without native image support. Supports png, jpg, jpeg, webp.
metadata:
  {
    "openclaw":
      {
        "requires": { "bins": ["python3"] },
        "install":
          [
            {
              "id": "python",
              "kind": "system",
              "label": "Install Python dependencies (requests)",
            },
          ],
      },
  }
---

# NVIDIA Kimi Vision

Fast image analysis using Kimi K2.5 multimodal model from NVIDIA NIM.

## Why This Skill?

- **Fast** - NVIDIA NIM inference 
- **Quality** - Kimi K2.5 is a solid vision model
- **Simple** - Just pass an image and prompt
- **Free tier** - Available through NVIDIA build.nvidia.com

## API Setup (IMPORTANT)

When using this skill, if no API key is found, it will automatically guide the user through setup:

### Step 1: Get a Free API Key
1. Go to **https://build.nvidia.com**
2. Sign up / Log in with GitHub or Google
3. Search for "Kimi K2.5" 
4. Click on the model and get your free API key

### Step 2: Save the Key
```bash
# Option A: Save to file (recommended)
mkdir -p ~/.config
echo 'your-api-key-here' > ~/.config/nvidia-kimi-api-key

# Option B: Pass directly when running
python3 scripts/analyze_image.py photo.jpg "What's this?" sk-your-key-here
```

### First Time Setup (for agents)
When a user tries to use this skill without an API key, the script will output clear setup instructions. Guide them through:
1. Visiting https://build.nvidia.com
2. Getting their free API key
3. Saving it to ~/.config/nvidia-kimi-api-key

## Usage

```bash
python3 scripts/analyze_image.py <image_path> "<prompt>" [api_key]
```

### Examples

```bash
# What's in this image?
python3 scripts/analyze_image.py "/path/to/image.jpg" "Describe what's in this image"

# Extract text from screenshot
python3 scripts/analyze_image.py "/path/screenshot.png" "Extract all text"

# Analyze a meme
python3 scripts/analyze_image.py "/path/meme.jpg" "Explain this meme"

# With API key inline
python3 scripts/analyze_image.py photo.jpg "What's this?" sk-xxxxx
```

## Image Formats

Supports: png, jpg, jpeg, webp

## Rate Limits

The free tier through NVIDIA NIM has some limits, but they're not clearly documented on the site. Check https://build.nvidia.com for the latest info on your specific key's limits.
