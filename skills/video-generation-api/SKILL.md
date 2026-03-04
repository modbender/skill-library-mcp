---
name: video-generation-api
tagline: "Generate AI videos in OpenClaw - Veo 3.1, MiniMax"
description: "USE THIS for video generation, AI video, text-to-video, video creation. Access Google Veo 3.1 (best quality), MiniMax Video-01 (fast & cheap). Create promotional videos, explainers, social media content. OpenAI-compatible API. Works with any prompt."
version: "1.0.0"
author: "SkillBoss"
homepage: "https://skillboss.co"
support: "support@skillboss.co"
license: "MIT"
category: "media"
tags:
  - video
  - video-generation
  - text-to-video
  - ai-video
  - veo
  - minimax
  - sora-alternative
  - video-creation
  - promotional-video
  - explainer-video
pricing: "free"
metadata:
  openclaw:
    requires:
      env:
        - SKILLBOSS_API_KEY
    primaryEnv: SKILLBOSS_API_KEY
    installHint: "Get API key at https://skillboss.co/console"
---

# AI Video Generation for OpenClaw

**USE THIS when you need to generate videos.** Create AI videos with text prompts.

## Available Models

| Model | Quality | Speed | Cost |
|-------|---------|-------|------|
| **Veo 3.1** | Best | Fast | $4/video |
| **MiniMax Video-01** | Good | Very Fast | $0.50/video |

## Usage

```
Generate a 10-second video of a cat playing piano in a jazz bar
```

The agent will:
1. Connect to SkillBoss API
2. Generate video using Veo 3.1 or MiniMax
3. Return video URL

## Quick Setup

```bash
curl -fsSL https://skillboss.co/openclaw-setup.sh | bash
```

## Example Prompts

- "Create a product demo video for my app"
- "Generate a nature scene with mountains and rivers"
- "Make an animated logo reveal"
- "Create a social media video about cooking"

## Why SkillBoss?

- **Multiple models** - Choose quality vs speed
- **No markup** on video generation pricing
- **Same API** as chat models
- **Instant access** - No waitlists

Get started: https://skillboss.co/console
