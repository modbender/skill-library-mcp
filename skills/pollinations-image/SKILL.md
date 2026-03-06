---
name: 🎨 Pollinations Image Generation Skill
description: A clean, modular, and user-friendly image generation tool powered
  by Pollinations.ai.
---

# 🎨 Pollinations Image Generation Skill

A clean, modular, and user-friendly image generation tool powered by [Pollinations.ai](https://pollinations.ai).

## ✨ Features

- 🎁 **5,000 free images/month** with pollen grants
- 🔄 **Easy model switching** - change anytime
- 💾 **Persistent defaults** - remember your preferences
- 📊 **Clear model comparison** - quality, speed, cost
- 🔧 **Modular design** - easy to extend

## 🚀 Quick Start

### First Time Setup

```bash
# 1. Clone or copy the skill
cd pollinations-image/

# 2. (Optional) Configure your API key
cp .env.example .env
# Edit .env and add your key from https://enter.pollinations.ai

# 3. (Optional) Set your default model  
cp .user.conf.example .user.conf
# Edit .user.conf to change DEFAULT_IMAGE_MODEL

# 4. List all available models
./generate.sh models

# 5. Generate your first image
./generate.sh "a cute purple cat"
```

### Already Configured?

```bash
# List all available models
./generate.sh models

# Set your default model (optional)
./generate.sh set-model flux

# Generate an image
./generate.sh generate --prompt "a cute purple cat"

# Or use the shortcut
./generate.sh "a cute purple cat"
```

## 📋 Available Models

| Model | Type | Speed | Quality | Cost |
|-------|------|-------|---------|------|
| `flux` | 🎁 Free | ⚡⚡ | ⭐⭐⭐⭐⭐ | ~0.0002 pollen/img |
| `zimage` | 🎁 Free | ⚡ | ⭐⭐⭐⭐ | ~0.0002 pollen/img |
| `klein` | 💰 Paid | ⚡⚡ | ⭐⭐⭐⭐⭐ | ~0.008 pollen/img |
| `klein-large` | 💰 Paid | ⚡⚡⚡ | ⭐⭐⭐⭐⭐⭐ | ~0.012 pollen/img |
| `gptimage` | 💰 Paid | ⚡⚡ | ⭐⭐⭐⭐⭐ | 2.0-8.0 pollen/M |

## 📖 Commands

### `generate` (or `g`)
Generate an image with your prompt.

```bash
# Full command
./generate.sh generate --prompt "a sunset over mountains" --model flux --width 1024 --height 1024

# Short options
./generate.sh g -p "a sunset" -m zimage -w 512 -h 512

# Even shorter (prompt only)
./generate.sh "a cute cat"
```

**Options:**
- `--prompt, -p` - Image description (required)
- `--model, -m` - Model to use (overrides default)
- `--width, -w` - Image width (default: 1024)
- `--height, -h` - Image height (default: 1024)
- `--seed, -s` - Random seed for reproducibility
- `--filename, -f` - Custom output filename
- `--nologo` - Remove Pollinations watermark
- `--enhance` - Let AI improve your prompt

### `models` (or `m`)
Display all available models with ratings.

```bash
./generate.sh models
```

### `model MODEL_NAME`
Show detailed information about a specific model.

```bash
./generate.sh model klein-large
```

### `set-model MODEL_NAME`
Set your default model for all future generations.

```bash
./generate.sh set-model zimage
```

**Note:** This saves to `.user.conf` and persists across sessions.

### `config`
Display your current configuration.

```bash
./generate.sh config
```

### `help`
Show help message.

```bash
./generate.sh help
```

## ⚙️ Configuration

User preferences are stored in `.user.conf`:

```bash
# Example .user.conf
DEFAULT_IMAGE_MODEL=flux
```

API keys are stored in `.env` (not tracked in git):

```bash
# Example .env
POLLINATIONS_API_KEY=your_key_here
```

## 📁 Structure

```
pollinations-image/
├── generate.sh        # Main entry point
├── lib/
│   └── models.sh      # Model registry and metadata
├── .env               # API keys (private)
├── .user.conf         # User preferences
└── SKILL.md           # This documentation
```

## 🎯 Recommended Workflows

### Draft → Refine → Final

```bash
# 1. Quick draft with fast model
./generate.sh g -p "concept sketch of a dragon" -m zimage -w 512

# 2. Refine with better model
./generate.sh g -p "detailed dragon in a castle" -m flux -w 1024

# 3. Final high-quality render
./generate.sh g -p "masterpiece, highly detailed dragon..." -m klein-large
```

### Daily Driver Setup

```bash
# Set fast model for daily use
./generate.sh set-model zimage

# All future generations use zimage by default
./generate.sh "quick concept"

# Override for special occasion
./generate.sh "important artwork" --model klein-large
```

## 🔑 Getting an API Key

1. Visit [enter.pollinations.ai](https://enter.pollinations.ai)
2. Create an account
3. Request a pollen grant (free tier: 5K images/month)
4. Generate an API key
5. Save it to `.env`: `POLLINATIONS_API_KEY=your_key`

## 🤝 Contributing & Sharing

This skill is designed to be shared! 

### Files to Include

When sharing the skill, include:
- ✅ `generate.sh` — Main script
- ✅ `lib/models.sh` — Model registry
- ✅ `.env.example` — Example API key file
- ✅ `.user.conf.example` — Example user config
- ✅ `SKILL.md` — Documentation

### Files to Exclude (Private)

Do NOT share these (they contain personal data):
- ❌ `.env` — Your private API key
- ❌ `.user.conf` — Your personal preferences
- ❌ `.first-run-complete` — Setup marker

### Adding a New Model

1. Edit `lib/models.sh`
2. Add your model to `MODELS_LIST` following the format:
   ```
   model_id|Display Name|type|cost|speed|quality|Description
   ```
3. Test with `./generate.sh model your_model_id`

### First-Time User Experience

When someone first runs the skill without config files, they'll see a welcome message guiding them through setup. The skill works out-of-the-box with sensible defaults:
- **Default model:** `flux` (free, high quality)
- **API key:** Optional (works with public endpoint)
## 📝 License

MIT - Feel free to use, modify, and share!

---

Made with 🫐 for the OpenClaw community.
