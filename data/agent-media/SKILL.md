---
name: agent-media
description: Generate AI-powered videos and images from the terminal using the `agent-media` CLI.
homepage: https://github.com/gitroomhq/agent-media
metadata: {"clawdbot":{"emoji":"🌎","requires":{"bins":[],"env":[]}}}
---

npm release: https://www.npmjs.com/package/agent-media-cli
agent-media cli github: https://github.com/gitroomhq/agent-media
official website: https://agent-media.ai

# agent-media — AI Video & Image Generation

Generate AI-powered videos and images from the terminal using the `agent-media` CLI.

## Prerequisites

The `agent-media` CLI must be installed and authenticated:

```bash
npm install -g agent-media-cli
agent-media login
```

Verify with `agent-media whoami`. If not logged in, run `agent-media login` and follow the OTP flow.

## Available Models

| Slug | Name | Type | Notes |
|------|------|------|-------|
| `kling3` | Kling 3.0 Pro | Video | text-to-video/image-to-video, 5-10s, 1080p |
| `veo3` | Veo 3.1 | Video | text-to-video/image-to-video, 4-8s, up to 4K |
| `sora2` | Sora 2 Pro | Video | text-to-video/image-to-video, 4-25s, 1080p |
| `seedance1` | Seedance 1.0 Pro | Video | text-to-video/image-to-video, 2-12s, 1080p |
| `flux2-pro` | Flux 2 Pro | Image | text-to-image |
| `flux2-flex` | Flux 2 Flex | Image | text-to-image |
| `grok-image` | Grok Imagine | Image | text-to-image |

## Core Commands

### Generate media

```bash
# Video generation
agent-media generate kling3 -p "A robot walking through a neon-lit city" --sync

# Image generation
agent-media generate flux2-pro -p "Cyberpunk samurai portrait" --sync

# Image-to-video (provide input image)
agent-media generate seedance1 -p "Make it dance" --input ./photo.jpg --sync

# With options
agent-media generate sora2 -p "Ocean waves at sunset" -d 10 -r 1080p --aspect-ratio 16:9 --sync
```

**Flags:**
- `-p, --prompt` — Generation prompt (required)
- `-d, --duration` — Video duration in seconds
- `-r, --resolution` — Output resolution (720p, 1080p)
- `--aspect-ratio` — Aspect ratio (16:9, 9:16, 1:1, etc.)
- `--input` — Input image for image-to-video
- `--sync, -s` — Wait for completion and print the output URL
- `--json` — Output as JSON (for parsing)

### Check credits and status

```bash
# Credit balance
agent-media credits

# Current plan
agent-media plan

# Job status
agent-media status <job-id>

# List recent jobs
agent-media list
agent-media list --status completed --limit 5
```

### Model info and pricing

```bash
# List all models
agent-media models

# Detailed pricing
agent-media pricing
agent-media pricing --model kling3
```

### Job management

```bash
# Download a completed job
agent-media download <job-id>

# Retry a failed job
agent-media retry <job-id>

# Cancel a running job
agent-media cancel <job-id>

# Delete a job
agent-media delete <job-id>
```

### Account

```bash
agent-media whoami          # Current user
agent-media credits         # Credit balance
agent-media plan            # Current subscription
agent-media subscribe              # Interactive plan/credits menu (waits for confirmation)
agent-media subscribe --plan starter  # Subscribe to a plan directly
agent-media subscribe --credits 500   # Buy a credit pack directly
agent-media subscribe --manage        # Open Stripe billing portal
agent-media apikey list     # List API keys
agent-media apikey create   # Create new API key
```

## Tips

- `agent-media subscribe` opens Stripe Checkout in the browser then polls for up to 2 minutes until the payment is confirmed, showing the new plan/credits on success.
- Always use `--sync` when you want to wait for the result and get the output URL.
- Use `--json` when you need to parse the output programmatically.
- Check `agent-media credits` before generating to ensure sufficient balance.
- For video, default duration is 5s and default resolution is 720p if not specified.
- Image models don't need duration — just prompt and optionally resolution.
- The `--sync` flag prints the public URL of the completed media.
