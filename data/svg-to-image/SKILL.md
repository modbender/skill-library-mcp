---
name: svg-to-image
version: 1.1.1
description: Convert SVG to PNG or JPG for quick sharing (e.g. Telegram) or print.
author: qrost
permissions:
  - shell:exec
---

# SVG to Image

Convert SVG files to PNG or JPG. Useful when you have vector graphics (e.g. from map-grabber, diagrams, or design tools) and need a raster image to send in chat or use in documents.

## Dependencies

- `cairosvg` (SVG rendering)
- `Pillow` (only for JPG output)

**Setup:** OpenClaw does not install Python packages automatically. After installing this skill, run once: `pip install -r requirements.txt` (from the skill folder). On Linux (e.g. Ubuntu/Debian), install the Cairo library first: `sudo apt install libcairo2`. If a script fails with `ModuleNotFoundError` or a cairo library error, install the missing package or system library.

## Usage

### Convert SVG to PNG or JPG

**Parameters:**

- `input`: Path to the SVG file.
- `-o`, `--output`: Output file path (default: same name as input with .png or .jpg).
- `-f`, `--format`: `png` (default) or `jpg`.
- `--width`, `--height`: Optional output size in pixels (keeps aspect ratio if only one is set).
- `--dpi`: Scale for rasterization (default 96).

```bash
# SVG to PNG (default)
python3 scripts/convert_svg.py drawing.svg -o drawing.png

# SVG to JPG
python3 scripts/convert_svg.py drawing.svg -f jpg -o drawing.jpg

# Fixed width 800px (height auto)
python3 scripts/convert_svg.py map.svg -o map.png --width 800
```

## Sending images to Telegram

Used from the OpenClaw Telegram conversation. Run the script with `-o <path>.png` or `-o <path>.jpg`, then **send that file** to the user via the OpenClaw message/media tool.

**OpenClaw allowed paths:** The message tool only sends files from allowed dirs (`~/.openclaw/media/`, `~/.openclaw/agents/`, or `/tmp`). Use e.g. `-o ~/.openclaw/media/out.png` or `-o /tmp/out.png`; do not use the skill install directory or sending will fail.

**Agent behavior:** When the user asks to convert an SVG to PNG or JPG (or "send as image"), **run the script directly** with `exec`: use `convert_svg.py <svg_path> -o <output>.png` (or `-f jpg`) with output path under an allowed dir, then send the generated image. Do not ask for confirmation; execute and return the image.

## Examples

**User:** "Convert this SVG to PNG so I can send it in Telegram."  
**Action:** Run `convert_svg.py <path> -o /tmp/out.png`, then send the PNG to the user.

**User:** "Turn map.svg into a JPG, 1200px wide."  
**Action:** Run with `-f jpg -o /tmp/map.jpg --width 1200`, then send the JPG.
