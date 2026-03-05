---
name: dxf-to-image
version: 1.0.0
description: Convert DXF to PNG, JPG, or SVG for sharing (e.g. Telegram) or further editing.
author: qrost
permissions:
  - shell:exec
---

# DXF to Image / SVG

Convert DXF (CAD) files to PNG, JPG, or SVG. Useful when you have DXF from map-grabber, Rhino, or other CAD tools and need a raster image to send in chat or a vector SVG for editing.

## Dependencies

- `ezdxf` (DXF read + drawing add-on)
- `matplotlib` (for PNG/JPG only)
- `Pillow` (for JPG only)

**Setup:** OpenClaw does not install Python packages automatically. After installing this skill, run once: `pip install -r requirements.txt` (from the skill folder). If a script fails with `ModuleNotFoundError`, install the missing package.

## Usage

### Convert DXF to PNG, JPG, or SVG

**Parameters:**

- `input`: Path to the DXF file.
- `-o`, `--output`: Output file path (default: same name as input with .png, .jpg, or .svg).
- `-f`, `--format`: `png` (default), `jpg`, or `svg`.
- `--width`, `--height`: Output size in pixels for PNG/JPG only (keeps aspect ratio if only one is set).
- `--dpi`: DPI for PNG/JPG (default 150).
- `--margin`: Margin in mm for SVG (default 2).

```bash
# DXF to PNG (default)
python3 scripts/convert_dxf.py drawing.dxf -o drawing.png

# DXF to SVG (vector, no matplotlib for this path)
python3 scripts/convert_dxf.py site.dxf -f svg -o site.svg

# DXF to JPG
python3 scripts/convert_dxf.py site.dxf -f jpg -o site.jpg

# Fixed width 800px (height auto)
python3 scripts/convert_dxf.py map.dxf -o map.png --width 800
```

## Sending images to Telegram

Used from the OpenClaw Telegram conversation. Run the script with `-o <path>.png` or `-o <path>.jpg`, then **send that file** to the user via the OpenClaw message/media tool.

**OpenClaw allowed paths:** The message tool only sends files from allowed dirs (`~/.openclaw/media/`, `~/.openclaw/agents/`, or `/tmp`). Use e.g. `-o ~/.openclaw/media/out.png` or `-o /tmp/out.png`; do not use the skill install directory or sending will fail.

**Agent behavior:** When the user asks to convert a DXF to PNG, JPG, or SVG (or "send DXF as image"), **run the script directly** with `exec`: use `convert_dxf.py <dxf_path> -o <output>` with `-f png`/`jpg`/`svg` and output path under an allowed dir; then send the generated file. Do not ask for confirmation; execute and return the file.

## Examples

**User:** "Convert this DXF to PNG so I can send it in Telegram."  
**Action:** Run `convert_dxf.py <path> -o /tmp/out.png`, then send the PNG to the user.

**User:** "Export the DXF as SVG."  
**Action:** Run `convert_dxf.py <path> -f svg -o /tmp/out.svg`, then send or return the SVG path.

**User:** "Turn the site DXF into a JPG, 1200px wide."  
**Action:** Run with `-f jpg -o /tmp/site.jpg --width 1200`, then send the JPG.
