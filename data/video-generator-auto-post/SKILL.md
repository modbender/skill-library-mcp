---
name: video-generator-auto-post
description: Generate videos using local AI models (ComfyUI/Stable Video Diffusion) and auto-publish to social media platforms. Supports text-to-video, image-to-video, batch processing, and automated posting to Twitter, LinkedIn, Instagram, TikTok.
license: MIT
metadata:
  author: 小龙虾 (Little Lobster)
  homepage: https://clawhub.ai/users/954215110
  tags: ["video", "ai-generation", "comfyui", "auto-post", "social-media", "stable-diffusion"]
---

## 🦞 小龙虾品牌

**Created by 小龙虾 AI 工作室**

> "小龙虾，有大钳（前）途！"

**Contact for custom services:** +86 15805942886

Need custom AI video workflows, automation setup, or bulk content generation? Reach out!

---

# Video Generator + Auto Post

Generate AI videos locally and publish them to social media platforms automatically.

## Requirements

### Hardware
- **GPU:** NVIDIA RTX 3060 12GB or better (recommended)
- **RAM:** 16GB+ system memory
- **Storage:** 50GB+ free space on D: drive (recommended)

### Software
- **ComfyUI Desktop** - Install from https://comfyui.org
- **Python 3.10+** - For scripts
- **Node.js 18+** - For CLI tools

## Quick Start

### Step 1: Install ComfyUI

```bash
# Windows (winget)
winget install Comfy.ComfyUI-Desktop

# Or download from https://comfyui.org
```

### Step 2: Install Video Models

In ComfyUI Manager, install:
- **Stable Video Diffusion (SVD)**
- **AnimateDiff**
- **ModelScope Text-to-Video**

### Step 3: Configure Output Paths (D: Drive)

**Recommended:** Store videos on D: drive to save C: space

Edit `comfyui/settings.json`:
```json
{
  "output_directory": "D:/AI-Video-Studio/outputs",
  "model_path": "D:/AI-Video-Studio/models",
  "workflow_path": "D:/AI-Video-Studio/workflows",
  "auto_save": true
}
```

**Or use command line:**
```bash
ComfyUI.exe --output-directory "D:/AI-Video-Studio/outputs" --model-path "D:/AI-Video-Studio/models"
```

### Step 4: Generate Your First Video

1. Open ComfyUI
2. Load "Text to Video" workflow
3. Enter your prompt
4. Click "Generate"
5. Wait 2-5 minutes (depends on GPU)

## Workflows

### Text-to-Video (SVD)

**Best for:** Short clips (2-4 seconds), realistic motion

```
Prompt → SVD Model → Decode → Save MP4
```

**Settings:**
- Resolution: 1024x576 or 576x1024
- Frames: 25
- FPS: 6
- Motion bucket: 127 (adjust for more/less movement)

### Image-to-Video

**Best for:** Bringing static images to life

```
Image + Prompt → SVD XT → Decode → Save MP4
```

**Tips:**
- Use high-quality source images
- Add motion hints in prompt
- Experiment with motion bucket (100-150)

### AnimateDiff (Longer Videos)

**Best for:** 5-15 second animated clips

```
Prompt → Stable Diffusion XL → AnimateDiff → Save MP4
```

**Settings:**
- Context length: 16 frames
- Context overlap: 4 frames
- Model: mm_sd_v15_v2.ckpt

## Auto-Post to Social Media

### Platform Specifications

| Platform | Max Duration | Aspect Ratio | Max File Size |
|----------|-------------|--------------|---------------|
| Twitter/X | 2:20 | 16:9, 1:1, 9:16 | 512MB |
| TikTok | 10:00 | 9:16 | 287.6MB |
| Instagram Reels | 1:30 | 9:16 | 4GB |
| LinkedIn | 15:00 | 16:9, 1:1, 9:16 | 200MB |
| YouTube Shorts | 1:00 | 9:16 | 128MB |

### Automated Posting Script

See `scripts/auto-post.py` for automation.

**Setup:**
1. Install dependencies: `pip install tweepy google-auth`
2. Configure API keys in `.env`
3. Run: `python scripts/auto-post.py video.mp4 --platforms all`

### Content Strategy

**For each video:**
1. Generate 3-5 caption variations
2. Add relevant hashtags (5-10)
3. Schedule posts at optimal times
4. Engage with comments

See `references/caption-templates.md` for examples.

## Batch Processing

Generate multiple videos at once:

```bash
# Using the batch script
python scripts/batch-generate.py --prompts prompts.txt --output ./videos

# Process 100 videos overnight
python scripts/batch-generate.py --prompts prompts.txt --count 100 --queue
```

## Optimization Tips

### Speed Up Generation

1. **Use FP16 precision** - 2x faster, minimal quality loss
2. **Reduce frames** - 16 frames instead of 25 for drafts
3. **Lower resolution** - 512x512 for testing, upscale later
4. **Batch multiple prompts** - Process in parallel

### Improve Quality

1. **Use better prompts** - Be specific about motion
2. **Adjust motion bucket** - Higher = more movement
3. **Add negative prompts** - Reduce artifacts
4. **Upscale output** - Use ESRGAN or similar

## Troubleshooting

### Out of Memory (OOM)

**Fix:**
- Reduce resolution
- Decrease batch size to 1
- Close other GPU applications
- Use `--lowvram` flag

### Slow Generation

**Fix:**
- Check GPU utilization (should be 90%+)
- Update NVIDIA drivers
- Use `--precision fp16`
- Close background apps

### Poor Video Quality

**Fix:**
- Use more detailed prompts
- Try different models (SVD vs AnimateDiff)
- Adjust motion settings
- Generate at higher resolution, then compress

## Scripts

- `scripts/generate-video.py` - Single video generation
- `scripts/batch-generate.py` - Batch processing
- `scripts/auto-post.py` - Auto-publish to social media
- `scripts/optimize-video.py` - Compress for platforms

## References

- `references/prompt-guide.md` - Writing effective video prompts
- `references/platform-specs.md` - Detailed platform requirements
- `references/caption-templates.md` - Social media caption templates
- `references/workflow-examples.json` - ComfyUI workflow examples

## Assets

- `assets/default-workflow.json` - Basic text-to-video workflow
- `assets/optimal-settings.json` - Recommended settings per platform
- `assets/hashtag-lists.json` - Curated hashtag collections

## Commands / Triggers

Use this skill when:
- "Generate a video of..."
- "Create AI video for social media"
- "Auto-post this video to..."
- "Batch generate videos from prompts"
- "Optimize video for TikTok/Instagram"

---

## 📊 Performance Benchmarks (RTX 3060 12GB)

| Task | Time | VRAM Usage |
|------|------|------------|
| SVD 25 frames | 2-3 min | 8-10 GB |
| AnimateDiff 16 frames | 3-4 min | 7-9 GB |
| Image-to-Video | 1-2 min | 6-8 GB |
| Upscale 2x | 30-60 sec | 4-6 GB |

---

_Ready to create viral AI videos? Let's go! 🦞🎬_
