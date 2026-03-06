---
name: gemini-nano-images
description: Generate ultra-realistic images and Instagram content using Gemini 2.0 Flash Experimental. Use when creating photorealistic images, social media content, or visual assets for Instagram workflows. Supports standalone image generation and complete Instagram post creation (image + caption).
---

# Gemini Nano Images

Generate ultra-realistic, photorealistic images using Google's Gemini 2.0 Flash Experimental model with native image generation capabilities.

## Quick Start

### 1. Set API Key

```bash
export GEMINI_API_KEY="your-api-key-here"
```

Get your API key at: https://aistudio.google.com/app/apikey

### 2. Generate Single Image

```bash
python3 scripts/generate_image.py "A cozy family breakfast scene with warm morning light"
```

### 3. Generate Full Instagram Post

```bash
python3 scripts/generate_instagram_post.py "Morning routine with kids" --mood cozy
```

## Scripts

### generate_image.py

Creates ultra-realistic images from text prompts.

**Usage:**
```bash
python3 scripts/generate_image.py "PROMPT" [options]
```

**Options:**
- `-o, --output DIR` - Output directory (default: current)
- `-k, --api-key KEY` - Gemini API key
- `--style {realistic,artistic,minimal}` - Style preset

**Example:**
```bash
python3 scripts/generate_image.py "Father reading bedtime story to child" -o ~/images
```

### generate_instagram_post.py

Creates complete Instagram posts: image + caption.

**Usage:**
```bash
python3 scripts/generate_instagram_post.py "TOPIC" [options]
```

**Options:**
- `-m, --mood MOOD` - Post mood: inspiring, cozy, energetic, calm, family, productive
- `-o, --output DIR` - Output directory (default: ~/.openclaw/workspace/assets)
- `-k, --api-key KEY` - Gemini API key

**Example:**
```bash
python3 scripts/generate_instagram_post.py "Organized family calendar" --mood productive
```

## Mood Presets

| Mood | Description |
|------|-------------|
| `inspiring` | Uplifting, motivational, golden hour |
| `cozy` | Warm, comfortable, soft lighting |
| `energetic` | Vibrant, dynamic, bright colors |
| `calm` | Peaceful, serene, soft pastels |
| `family` | Loving family moments, candid |
| `productive` | Organized, clean, modern aesthetic |

## Output

- **Images**: Saved as PNG with timestamp prefix
- **Captions**: Saved as .txt file alongside image
- **Location**: Default is `~/.openclaw/workspace/assets`

## Integration with Instagram Workflow

Generated content can be directly used with the Social Media Suite:

1. Generate content:
   ```bash
   python3 scripts/generate_instagram_post.py "Weekend family adventure"
   ```

2. Results saved to assets folder, ready for posting

3. Use with instagram-poster or instagrapi workflow

### Stock-Only Mode (Community Building Phase)

Für 1-2 Wochen nur Stockfotos posten (keine KI-Generierung):

```bash
# Stock-Only Mode für 14 Tage aktivieren
cd ~/.openclaw/workspace/skills/ig-automation
python3 smart_poster_v4.py --set-mode stock_only --stock-days 14

# Stockfotos in Ordner legen
mkdir -p assets/stock
cp ~/deine-stockfotos/*.jpg assets/stock/

# Jetzt werden nur Stockfotos gepostet (zufällige Auswahl, keine Doppelungen)
python3 smart_poster_v4.py

# Nach 14 Tagen automatischer Wechsel zu "auto" (KI + Stock)
```

**Modes:**
- `auto` - Bevorzugt KI, Fallback zu Stock
- `stock_only` - Nur Stockfotos aus `assets/stock/`
- `ai_only` - Nur KI-generierte Bilder

**Wichtig:** Bei Stockfotos kein Wasserzeichen (Logo) - sieht authentischer aus!

## Requirements

```bash
pip install google-genai
```

## Model Details

- **Model**: Gemini 2.0 Flash Experimental
- **Capability**: Native image generation
- **Resolution**: Up to 1024x1024
- **Style**: Photorealistic by default

See [references/gemini_api.md](references/gemini_api.md) for API details.
