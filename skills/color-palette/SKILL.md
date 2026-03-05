---
name: color-palette
version: 1.1.1
description: Extract a color palette from an image and return HEX/RGB values with optional swatch image.
author: qrost
permissions:
  - shell:exec
---

# Color Palette

Extract dominant colors from a photo and get HEX/RGB values for use in design tools or mood boards.

## Dependencies

- `Pillow` (image handling; required)
- `colorgram` (optional; better dominant-color extraction; `pip install colorgram.py`)
- `matplotlib` (optional; only if generating swatch image with `--output`)

**Setup:** OpenClaw does not install Python packages automatically. After installing this skill, run once: `pip install -r requirements.txt` (from the skill folder or pass the path). If a script fails with `ModuleNotFoundError`, install the missing package.

## Usage

### Extract palette from an image

**Parameters:**

- `image`: Path to the image file (JPEG, PNG, etc.).
- `-n`, `--num-colors`: Number of colors to extract (default 5, max 20).
- `--output`: Optional path to save a swatch PNG.

```bash
python3 scripts/extract_palette.py /path/to/photo.jpg
python3 scripts/extract_palette.py /path/to/photo.jpg -n 8 --output palette_swatch.png
```

Output: one line per color with HEX and RGB (e.g. `#2A4B7C  RGB(42, 75, 124)`). If `--output` is set, a simple swatch image is saved.

## Sending images to Telegram

These skills are used from the OpenClaw Telegram conversation. To show the user a picture, the agent must (1) run the script with an **image output path** (PNG or JPG), then (2) **send that file** to the conversation using the OpenClaw message/media tool. For this skill: use `--output <path>.png` so you have an image to send; then send that PNG to the user.

**OpenClaw allowed paths:** The message tool only sends files from allowed dirs (`~/.openclaw/media/`, `~/.openclaw/agents/`, or system temp e.g. `/tmp`). Use e.g. `--output ~/.openclaw/media/palette.png` or `--output /tmp/palette.png`; do not use the skill install directory or sending will fail.

**Agent behavior:** When the user asks to extract colors from an image (or sends an image for a palette), **run the script directly** with `exec`: save the image to a temp path if needed, run `extract_palette.py <image_path> -n <N> --output <path>.png` with `<path>` under an allowed dir, return the HEX/RGB text and send the swatch PNG. Do not ask for confirmation; execute and return the palette and image.

## Examples

**User:** "Extract 5 colors from this image" (with image attached).  
**Action:** Save the image to a temp path, run `extract_palette.py <path> -n 5 --output /tmp/palette.png`, return the HEX/RGB list and send the swatch PNG.

**User:** "Give me a color palette from [image] and save the swatch as swatch.png."  
**Action:** Run with `--output swatch.png`, return the palette text and send the image.
