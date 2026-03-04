# kie.ai API Wrapper for OpenClaw

Unified access to multiple AI models through [kie.ai](https://kie.ai)'s API. Generate images, videos, and music at 30-80% lower cost than official APIs.

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.6+-blue.svg)

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

1. **Python 3.6+** (usually pre-installed on macOS/Linux)
2. **kie.ai API Key**:
   - Sign up at https://kie.ai
   - Get API key from dashboard

### Setup

```bash
# Clone the repo
cd ~/src
git clone https://github.com/jon-xo/kie-ai-skill.git
cd kie-ai-skill

# Make executable
chmod +x kie-ai.sh lib/*.py

# Set your API key
export KIE_API_KEY="your-key-here"

# Test it
./kie-ai.sh generate-image "test image"
```

### OpenClaw Integration

If using with OpenClaw:

1. Add API key to `~/.openclaw/openclaw.json`:
   ```json
   "env": {
     "vars": {
       "KIE_API_KEY": "your-key-here"
     }
   }
   ```

2. Create symlink:
   ```bash
   ln -s ~/src/kie-ai-skill ~/.openclaw/workspace/skills/kie-ai-skill
   ```

## Usage

### Image Generation

```bash
./kie-ai.sh generate-image <prompt> [options]

Options:
  --model <name>         Model (default: nano-banana-pro)
  --resolution <res>     1K, 2K, 4K (default: 1K)
  --aspect <ratio>       1:1, 16:9, 9:16, etc. (default: 1:1)
  --upload-drive         Upload to Google Drive after generation
```

**Examples:**

```bash
# Basic
./kie-ai.sh generate-image "A red apple on a wooden table"

# High resolution widescreen
./kie-ai.sh generate-image "Mountain landscape" --resolution 4K --aspect 16:9

# 16-bit pixel art style
./kie-ai.sh generate-image "Cyberpunk lobster, 16-bit pixel art, no text"

# Generate and upload to Drive
./kie-ai.sh generate-image "Abstract art" --upload-drive
```

### Check Balance

```bash
./kie-ai.sh balance
```

Shows:
- Local task history
- Estimated credit consumption  
- USD equivalent
- Links to web UI for actual balance

### List Models

```bash
./kie-ai.sh models
```

### Configure Google Drive (Optional)

```bash
# View config help
./kie-ai.sh config

# Edit config.json
nano config.json

# Set:
# - enabled: true
# - folder_id: "YOUR_GOOGLE_DRIVE_FOLDER_ID"
```

**Google Drive Setup:**
1. Sign up at https://maton.ai (OAuth gateway)
2. Add `MATON_API_KEY` to environment
3. Create Google Drive connection at https://ctrl.maton.ai
4. Get folder ID from Drive URL

## Pricing

Approximate costs (kie.ai vs official APIs):

| Model | kie.ai | Official | Savings |
|-------|--------|----------|---------|
| Nano Banana Pro | $0.09-$0.12 | $0.15 | 20-40% |
| Flux Kontext | $0.25 | $0.30 | ~17% |

**Credit pricing:** ~$0.005 per credit  
**Packages:** 1,000 credits = $5

## Available Models

### 🎨 Image Generation
- `nano-banana-pro` - Gemini 3 Pro Image (1K/2K/4K)
- `google/nano-banana` - Gemini 2.5 Flash (cheaper)
- `flux-kontext` - Flux by Black Forest Labs
- `4o-image` - OpenAI GPT-4o Image

### 🎬 Video Generation *(coming soon)*
- `veo-3.1` - Google Veo 3.1 (cinematic)
- `veo-3.1-fast` - Veo Fast (cheaper)
- `runway-aleph` - Runway Gen-4 Aleph

### 🎵 Music Generation *(coming soon)*
- `suno-v4` - Suno V4 (up to 8min)
- `suno-v4.5` - Suno V4.5 Plus

See https://docs.kie.ai for full list.

## File Storage

Generated files are saved locally to the `images/` directory (gitignored):

```
~/src/kie-ai-skill/images/YYYY-MM-DD-HH-MM-SS-{index}.png
```

**Retention:**
- **Local**: Forever (until deleted)
- **kie.ai CDN**: 14 days
- **Google Drive**: Forever (if uploaded)

## Architecture

```
kie-ai-skill/
├── kie-ai.sh                 # Main CLI wrapper
├── lib/
│   ├── generate-image.py     # Image generation
│   ├── upload-drive.py       # Google Drive upload
│   ├── balance.py            # Balance/usage tracking
│   ├── state_manager.py      # Task state tracking
│   └── watch_task.py         # Task polling
├── config.json               # Configuration (Drive, etc.)
├── SKILL.md                  # OpenClaw skill documentation
└── README.md                 # This file
```

## Troubleshooting

### "KIE_API_KEY not set"

Set environment variable:
```bash
export KIE_API_KEY="your-key-here"
```

Or add to shell profile (`~/.zshrc`, `~/.bashrc`):
```bash
echo 'export KIE_API_KEY="your-key-here"' >> ~/.zshrc
source ~/.zshrc
```

### "Credits insufficient"

Top up at: https://kie.ai/billing

### "Drive upload failed"

1. Ensure `MATON_API_KEY` is set
2. Create Google Drive connection at https://ctrl.maton.ai
3. Verify folder ID in `config.json`

## Links

- **kie.ai Dashboard**: https://kie.ai
- **Documentation**: https://docs.kie.ai
- **Logs/Balance**: https://kie.ai/logs
- **Billing**: https://kie.ai/billing
- **Maton (Drive)**: https://maton.ai

## License

MIT License - see LICENSE file

## Contributing

Issues and PRs welcome at https://github.com/jon-xo/kie-ai-skill

## Acknowledgments

- Built for [OpenClaw](https://openclaw.ai)
- Powered by [kie.ai](https://kie.ai)
- Drive integration via [maton.ai](https://maton.ai)
