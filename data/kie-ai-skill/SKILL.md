---
name: kie-ai
version: 1.0.1
description: |
  Unified API access to multiple AI models via kie.ai - image generation (Nano Banana Pro, Flux, 4o-image) at 30-80% lower cost than official APIs. Includes local storage, Google Drive upload, usage tracking, and task resume.
files:
  - "kie-ai.sh"
  - "lib/*"
  - "models.json"
  - "config.example.json"
metadata:
  author: jon-xo
  repository: https://github.com/jon-xo/kie-ai-skill
  clawdbot:
    emoji: "🍌"
    homepage: https://github.com/jon-xo/kie-ai-skill
    primaryEnv: KIE_API_KEY
    requires:
      env:
        - KIE_API_KEY
      bins:
        - python3
---

# kie.ai API Wrapper

Unified access to multiple AI models through kie.ai's API. Generate images, videos, and music at 30-80% lower cost than official APIs.

## Features

- 🎨 **Image Generation**: Nano Banana Pro (Gemini 3 Pro), Flux, 4o-image
- 📤 **Google Drive Upload**: Optional automatic upload to Drive folder
- 📊 **Usage Tracking**: Local task history and cost estimation
- 💾 **Local Storage**: All files saved to `images/` before optional upload
- 🎬 **Video Generation** *(coming soon)*: Veo 3.1, Runway Gen-4 Aleph
- 🎵 **Music Generation** *(coming soon)*: Suno V4/V4.5

## Quick Start

```bash
# Generate an image
./kie-ai.sh generate-image "A serene Japanese garden at sunset"

# With custom options
./kie-ai.sh generate-image "Cyberpunk city" --resolution 2K --aspect 16:9

# Upload to Google Drive
./kie-ai.sh generate-image "Space nebula" --upload-drive

# Check usage
./kie-ai.sh balance
```

## Installation

### Prerequisites

1. **kie.ai API Key**:
   - Sign up at https://kie.ai
   - Get API key from dashboard
   - Add to `~/.openclaw/openclaw.json`:
     ```json
     "env": {
       "vars": {
         "KIE_API_KEY": "your-key-here"
       }
     }
     ```

2. **(Optional) Maton API Key** for Google Drive uploads:
   - Sign up at https://maton.ai
   - Get API key from https://maton.ai/settings
   - Set up Google Drive connection at https://ctrl.maton.ai
   - Add to config:
     ```json
     "MATON_API_KEY": "your-maton-key"
     ```

### Setup

```bash
# Clone to ~/src
cd ~/src
git clone https://github.com/jon-xo/kie-ai-skill.git
cd kie-ai-skill

# Make executable
chmod +x kie-ai.sh lib/*.py

# Create symlink for OpenClaw
ln -s ~/src/kie-ai-skill ~/.openclaw/workspace/skills/kie-ai-skill

# Test it
./kie-ai.sh generate-image "test image"
```

## Configuration

### Google Drive Upload (Optional)

```bash
# View/edit config
./kie-ai.sh config

# Edit config.json
{
  "drive": {
    "enabled": true,
    "folder_id": "YOUR_GOOGLE_DRIVE_FOLDER_ID"
  }
}
```

Get your folder ID from the Google Drive URL:
```
https://drive.google.com/drive/folders/1abc...xyz
                                          ^^^^ this part
```

## Commands

### generate-image

Generate images with various models.

```bash
./kie-ai.sh generate-image <prompt> [options]

Options:
  --model <name>         Model: nano-banana-pro (default), google/nano-banana, flux-kontext, 4o-image
  --resolution <res>     Resolution: 1K (default), 2K, 4K
  --aspect <ratio>       Aspect ratio: 1:1 (default), 16:9, 9:16, 4:3, etc.
  --upload-drive         Upload to Google Drive after generation (requires config)
```

**Examples:**

```bash
# Basic generation
./kie-ai.sh generate-image "A red apple on a wooden table"

# High resolution
./kie-ai.sh generate-image "Mountain landscape" --resolution 4K

# Widescreen
./kie-ai.sh generate-image "Cinematic scene" --resolution 2K --aspect 16:9

# 16-bit pixel art
./kie-ai.sh generate-image "Cyberpunk lobster, 16-bit pixel art, no text" --aspect 16:9

# Generate and upload
./kie-ai.sh generate-image "Abstract art" --upload-drive
```

### balance

Check credit usage and remaining balance.

```bash
./kie-ai.sh balance
```

Shows:
- Link to web UI for actual balance
- Local task history
- Estimated credit consumption
- USD equivalent

### status

Show active/pending tasks.

```bash
./kie-ai.sh status
```

### models

List available models and pricing.

```bash
./kie-ai.sh models
```

### config

View/configure Google Drive upload settings.

```bash
./kie-ai.sh config
```

## Pricing

Approximate costs (kie.ai vs official):

| Model | kie.ai | Official | Savings |
|-------|--------|----------|---------|
| Nano Banana Pro | ~18-24 credits ($0.09-$0.12) | $0.15 | 20-40% |
| Veo 3.1 | Variable | N/A | — |
| Flux Kontext | ~50 credits ($0.25) | $0.30 | ~17% |
| Suno V4 | Variable | $0.10/track | Comparable |

**Credit pricing:** ~$0.005 per credit (1,000 credits = $5)

Check exact costs at: https://docs.kie.ai/pricing

## File Storage

Generated files are saved to the `images/` directory (gitignored):

```
~/src/kie-ai-skill/images/
  2026-02-11-12-05-01-1.png
  2026-02-11-12-09-56-1.png
  ...
```

Format: `YYYY-MM-DD-HH-MM-SS-{index}.png`

**Retention:**
- Local: Forever (or until you delete)
- kie.ai CDN: 14 days
- Google Drive: Forever (if uploaded)

## Task State

Tasks are tracked in:
```
~/src/kie-ai-skill/.task-state.json
```

Used for:
- Resume interrupted tasks
- Usage tracking
- Preventing duplicate submissions

## Available Models

### Image Generation
- `nano-banana-pro` - Gemini 3 Pro Image (1K/2K/4K)
- `google/nano-banana` - Gemini 2.5 Flash Image (cheaper)
- `flux-kontext` - Flux by Black Forest Labs
- `4o-image` - OpenAI GPT-4o Image

### Video Generation *(coming soon)*
- `veo-3.1` - Google Veo 3.1 (cinematic)
- `veo-3.1-fast` - Veo 3.1 Fast (cheaper)
- `runway-aleph` - Runway Gen-4 Aleph

### Music Generation *(coming soon)*
- `suno-v4` - Suno V4 (up to 8min)
- `suno-v4.5` - Suno V4.5 Plus

See https://docs.kie.ai for full list.

## Troubleshooting

### "KIE_API_KEY not set"

Add to `~/.openclaw/openclaw.json`:
```json
"env": {
  "vars": {
    "KIE_API_KEY": "your-key-here"
  }
}
```

### "Credits insufficient"

Top up at: https://kie.ai/billing

### "MATON_API_KEY not set" (Drive upload)

1. Sign up at https://maton.ai
2. Add `MATON_API_KEY` to openclaw.json
3. Create Google Drive connection at https://ctrl.maton.ai

### "Drive upload failed"

1. Check MATON_API_KEY is set
2. Verify Google Drive connection is active at https://ctrl.maton.ai
3. Ensure folder_id in config.json is correct
4. Try generating without `--upload-drive` first

## Integration with OpenClaw

Use via exec or directly in OpenClaw agent conversations:

```bash
# From OpenClaw chat
Generate a cyberpunk city image with kie.ai

# The agent will run:
cd ~/src/kie-ai-skill && ./kie-ai.sh generate-image "cyberpunk city"
```

## Security

### Environment Variables

| Variable | Required | Purpose |
|---|---|---|
| `KIE_API_KEY` | Yes | Authenticates all requests to `api.kie.ai` |
| `MATON_API_KEY` | No | Authenticates Google Drive uploads via `gateway.maton.ai` |

### External Endpoints

| Endpoint | Method | Data Sent | Used By |
|---|---|---|---|
| `https://api.kie.ai/api/v1/jobs/createTask` | POST | prompt, model, resolution, aspect ratio | `generate-image.py` |
| `https://api.kie.ai/api/v1/jobs/recordInfo` | GET | task ID | `generate-image.py`, `watch_task.py` |
| `https://api.kie.ai/api/v1/chat/credit` | GET | — (auth header only) | `balance.py` |
| `https://gateway.maton.ai/google-drive/upload/...` | POST | image file bytes, filename | `upload-drive.py` (optional) |

### Data Leaving This Machine

- **Prompt text** is sent to `api.kie.ai` to generate images.
- **Generated image files** are sent to `gateway.maton.ai` only when `--upload-drive` is explicitly passed.
- **API keys** are transmitted as `Authorization: Bearer` headers and are never logged or written to disk by this skill.
- No telemetry, analytics, or usage data is collected by this skill itself.

### Trust Statement

This skill sends data to two third-party services: [kie.ai](https://kie.ai) for AI generation and [maton.ai](https://maton.ai) as an OAuth gateway for Google Drive. Review their respective privacy policies before use. Drive upload is strictly opt-in via `--upload-drive`.

### Autonomous Invocation

This skill can be invoked autonomously by an OpenClaw agent when asked to generate images. It does not execute autonomously on its own — it must be called explicitly. To prevent autonomous invocation, remove the skill symlink from your OpenClaw workspace.

## Links

- **kie.ai Dashboard**: https://kie.ai
- **Documentation**: https://docs.kie.ai
- **Pricing**: https://docs.kie.ai/pricing
- **Logs/Balance**: https://kie.ai/logs
- **Billing**: https://kie.ai/billing
- **Maton (for Drive)**: https://maton.ai
- **GitHub Repo**: https://github.com/jon-xo/kie-ai-skill

## License

MIT

## Support

Issues: https://github.com/jon-xo/kie-ai-skill/issues
