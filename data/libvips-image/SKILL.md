---
name: libvips-image
description: High-performance image processing with libvips. Use for resizing, converting, watermarking, thumbnails, and batch image operations with low memory usage.
metadata:
  author: agiseek
  version: "1.0.1"
---

# libvips Image Processing

Fast, memory-efficient image processing using libvips via pyvips. Supports 300+ operations including resize, crop, rotate, convert, watermark, composite, and more. Ideal for batch processing large images.

## When to Use

- Resize, crop, or thumbnail images efficiently
- Convert between formats (JPEG, PNG, WebP, AVIF, HEIC, TIFF, PDF, SVG)
- Add watermarks or text overlays
- Batch process multiple images
- Handle large images with low memory usage
- Create image pipelines for web optimization

## Quick Start

### Install (One-Click)

```bash
# Recommended: Auto-detect OS and install everything
./scripts/install.sh
```

The install script will:
1. Detect your OS (macOS, Linux, Windows)
2. Install libvips system library
3. Install pyvips via **uv** (preferred) or pip
4. Verify the installation

### Manual Install

**macOS (Homebrew):**
```bash
brew install vips
uv pip install pyvips  # preferred
# or: pip install pyvips
```

**Ubuntu/Debian:**
```bash
sudo apt-get install libvips-dev
uv pip install pyvips  # preferred
# or: pip install pyvips
```

**Fedora/RHEL:**
```bash
sudo dnf install vips-devel
uv pip install pyvips
```

**Arch Linux:**
```bash
sudo pacman -S libvips
uv pip install pyvips
```

**Windows (PowerShell, recommended):**
```powershell
# One-click install (downloads libvips + installs pyvips)
.\scripts\install.ps1
```

**Windows (Manual):**
```powershell
# Option 1: winget (if available)
winget install libvips.libvips

# Option 2: scoop
scoop install libvips

# Option 3: Manual download
# Download from https://github.com/libvips/libvips/releases
# Extract to C:\vips or %LOCALAPPDATA%\vips
# Add bin\ to PATH

# Install pyvips
uv pip install pyvips
# or: pip install pyvips
```

**Install uv (if not installed):**
```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows (PowerShell)
irm https://astral.sh/uv/install.ps1 | iex
```

### Basic Usage

**macOS/Linux - Using run.sh wrapper (recommended):**
```bash
./scripts/run.sh vips_tool.py resize input.jpg output.jpg --width 800
./scripts/run.sh vips_tool.py convert input.jpg output.webp --quality 85
./scripts/run.sh vips_tool.py thumbnail input.jpg thumb.jpg --size 200
./scripts/run.sh vips_batch.py resize ./input ./output --width 800
```

**Windows - Using run.bat wrapper (recommended):**
```cmd
.\scripts\run.bat vips_tool.py resize input.jpg output.jpg --width 800
.\scripts\run.bat vips_tool.py convert input.jpg output.webp --quality 85
.\scripts\run.bat vips_tool.py thumbnail input.jpg thumb.jpg --size 200
.\scripts\run.bat vips_batch.py resize .\input .\output --width 800
```

**Cross-platform - Using uv (after `uv sync`):**
```bash
uv run python scripts/vips_tool.py resize input.jpg output.jpg --width 800
```

**Direct Python (if library paths are configured):**
```bash
python scripts/vips_tool.py resize input.jpg output.jpg --width 800
python scripts/vips_tool.py convert input.jpg output.webp --quality 85
python scripts/vips_tool.py thumbnail input.jpg thumb.jpg --size 200
python scripts/vips_tool.py watermark input.jpg output.jpg --text "Copyright 2024"
```

## Supported Formats

| Format | Read | Write | Notes |
|--------|------|-------|-------|
| JPEG | Yes | Yes | Quality 1-100 |
| PNG | Yes | Yes | Compression 0-9 |
| WebP | Yes | Yes | Lossy/lossless |
| AVIF | Yes | Yes | Modern, high compression |
| HEIC | Yes | Yes | Apple format |
| TIFF | Yes | Yes | Multi-page support |
| GIF | Yes | Yes | Animated support |
| PDF | Yes | Yes | Via poppler |
| SVG | Yes | No | Via librsvg |
| RAW | Yes | No | Via libraw |

## Operations

### 1) Resize

Resize images with various fit modes.

```bash
# Resize to exact width, maintain aspect ratio
python scripts/vips_tool.py resize input.jpg output.jpg --width 800

# Resize to exact height
python scripts/vips_tool.py resize input.jpg output.jpg --height 600

# Resize to fit within bounds
python scripts/vips_tool.py resize input.jpg output.jpg --width 800 --height 600

# Resize to cover (fill) dimensions
python scripts/vips_tool.py resize input.jpg output.jpg --width 800 --height 600 --mode cover

# Force exact dimensions (may distort)
python scripts/vips_tool.py resize input.jpg output.jpg --width 800 --height 600 --mode force
```

**Resize modes:**
- `fit` (default): Fit within bounds, maintain aspect ratio
- `cover`: Cover bounds, crop excess
- `force`: Force exact dimensions

### 2) Thumbnail

Create optimized thumbnails with smart cropping.

```bash
# Square thumbnail
python scripts/vips_tool.py thumbnail input.jpg thumb.jpg --size 200

# Attention-based smart crop
python scripts/vips_tool.py thumbnail input.jpg thumb.jpg --size 200 --crop attention

# Center crop
python scripts/vips_tool.py thumbnail input.jpg thumb.jpg --size 200 --crop centre
```

**Crop strategies:**
- `none`: No cropping, fit within size
- `centre`: Crop from center
- `attention`: Smart crop focusing on interesting areas
- `entropy`: Crop to maximize entropy

### 3) Convert

Convert between image formats with quality control.

```bash
# JPEG to WebP
python scripts/vips_tool.py convert input.jpg output.webp --quality 85

# PNG to AVIF (modern format, great compression)
python scripts/vips_tool.py convert input.png output.avif --quality 50

# JPEG to PNG (lossless)
python scripts/vips_tool.py convert input.jpg output.png

# With compression level for PNG
python scripts/vips_tool.py convert input.jpg output.png --compression 9
```

### 4) Crop

Extract a region from an image.

```bash
# Crop 400x300 region starting at (100, 50)
python scripts/vips_tool.py crop input.jpg output.jpg --left 100 --top 50 --width 400 --height 300

# Smart crop to aspect ratio
python scripts/vips_tool.py crop input.jpg output.jpg --width 800 --height 600 --smart
```

### 5) Rotate

Rotate images by any angle.

```bash
# Rotate 90 degrees clockwise
python scripts/vips_tool.py rotate input.jpg output.jpg --angle 90

# Rotate 45 degrees with background color
python scripts/vips_tool.py rotate input.jpg output.jpg --angle 45 --background "255,255,255"

# Auto-rotate based on EXIF
python scripts/vips_tool.py rotate input.jpg output.jpg --auto
```

### 6) Watermark

Add text or image watermarks.

```bash
# Text watermark
python scripts/vips_tool.py watermark input.jpg output.jpg --text "Copyright 2024"

# Position: top-left, top-right, bottom-left, bottom-right, center
python scripts/vips_tool.py watermark input.jpg output.jpg --text "Logo" --position bottom-right

# With opacity
python scripts/vips_tool.py watermark input.jpg output.jpg --text "Draft" --opacity 0.3

# Image watermark
python scripts/vips_tool.py watermark input.jpg output.jpg --image logo.png --position bottom-right --opacity 0.5
```

### 7) Composite

Combine multiple images.

```bash
# Overlay image on background
python scripts/vips_tool.py composite background.jpg overlay.png output.jpg

# With position offset
python scripts/vips_tool.py composite background.jpg overlay.png output.jpg --x 100 --y 50

# With blend mode
python scripts/vips_tool.py composite background.jpg overlay.png output.jpg --blend multiply
```

**Blend modes:** `over`, `multiply`, `screen`, `overlay`, `darken`, `lighten`

### 8) Adjust

Adjust brightness, contrast, saturation.

```bash
# Increase brightness
python scripts/vips_tool.py adjust input.jpg output.jpg --brightness 1.2

# Increase contrast
python scripts/vips_tool.py adjust input.jpg output.jpg --contrast 1.3

# Increase saturation
python scripts/vips_tool.py adjust input.jpg output.jpg --saturation 1.5

# Combine adjustments
python scripts/vips_tool.py adjust input.jpg output.jpg --brightness 1.1 --contrast 1.2 --saturation 1.1
```

### 9) Sharpen

Apply sharpening filter.

```bash
# Default sharpen
python scripts/vips_tool.py sharpen input.jpg output.jpg

# Custom sigma (blur radius)
python scripts/vips_tool.py sharpen input.jpg output.jpg --sigma 1.5

# Custom parameters
python scripts/vips_tool.py sharpen input.jpg output.jpg --sigma 1.5 --x1 2 --m2 3
```

### 10) Blur

Apply Gaussian blur.

```bash
# Default blur
python scripts/vips_tool.py blur input.jpg output.jpg

# Custom sigma
python scripts/vips_tool.py blur input.jpg output.jpg --sigma 5
```

### 11) Flip & Mirror

Flip images horizontally or vertically.

```bash
# Horizontal flip (mirror)
python scripts/vips_tool.py flip input.jpg output.jpg --horizontal

# Vertical flip
python scripts/vips_tool.py flip input.jpg output.jpg --vertical
```

### 12) Grayscale

Convert to grayscale.

```bash
python scripts/vips_tool.py grayscale input.jpg output.jpg
```

### 13) Info

Get image metadata.

```bash
python scripts/vips_tool.py info input.jpg
```

Output:
```
File: input.jpg
Format: jpeg
Width: 3840
Height: 2160
Bands: 3
Interpretation: srgb
Size: 2.4 MB
```

## Batch Processing

Process multiple images at once.

```bash
# Resize all JPEGs in a directory
python scripts/vips_batch.py resize ./input ./output --width 800 --pattern "*.jpg"

# Convert all images to WebP
python scripts/vips_batch.py convert ./input ./output --format webp --quality 85

# Create thumbnails for all images
python scripts/vips_batch.py thumbnail ./input ./thumbnails --size 200

# Custom batch with JSON config
python scripts/vips_batch.py --config batch_config.json
```

### Batch Config Format

```json
{
  "input_dir": "./input",
  "output_dir": "./output",
  "operations": [
    {"type": "resize", "width": 1920},
    {"type": "sharpen", "sigma": 0.5},
    {"type": "convert", "format": "webp", "quality": 85}
  ],
  "pattern": "*.{jpg,jpeg,png}",
  "recursive": true,
  "workers": 4
}
```

## Python API

### Basic Usage

```python
import pyvips

# Load image
image = pyvips.Image.new_from_file("input.jpg")

# Resize
resized = image.resize(0.5)  # 50% scale
resized = image.thumbnail_image(800)  # 800px width

# Save
resized.write_to_file("output.jpg", Q=85)  # JPEG quality 85
resized.write_to_file("output.webp", Q=85)  # WebP quality 85
```

### Chaining Operations

```python
import pyvips

# Load, process, save in one pipeline
image = pyvips.Image.new_from_file("input.jpg", access="sequential")
result = (
    image
    .thumbnail_image(1200)
    .sharpen(sigma=0.5)
    .write_to_file("output.webp", Q=85)
)
```

### Watermark with Text

```python
import pyvips

image = pyvips.Image.new_from_file("input.jpg")

# Create text overlay
text = pyvips.Image.text(
    "Copyright 2024",
    font="sans 24",
    rgba=True
)

# Composite at bottom-right
x = image.width - text.width - 20
y = image.height - text.height - 20
result = image.composite2(text, "over", x=x, y=y)
result.write_to_file("output.jpg")
```

### Batch Processing

```python
import pyvips
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

def process_image(input_path, output_dir, width=800):
    image = pyvips.Image.new_from_file(str(input_path), access="sequential")
    thumbnail = image.thumbnail_image(width)
    output_path = output_dir / f"{input_path.stem}.webp"
    thumbnail.write_to_file(str(output_path), Q=85)
    return output_path

input_dir = Path("./input")
output_dir = Path("./output")
output_dir.mkdir(exist_ok=True)

files = list(input_dir.glob("*.jpg"))
with ThreadPoolExecutor(max_workers=4) as executor:
    results = executor.map(lambda f: process_image(f, output_dir), files)
```

## CLI Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| `--width` | Target width in pixels | - |
| `--height` | Target height in pixels | - |
| `--size` | Thumbnail size (square) | 200 |
| `--quality` | Output quality (1-100) | 85 |
| `--compression` | PNG compression (0-9) | 6 |
| `--mode` | Resize mode: fit, cover, force | fit |
| `--crop` | Crop strategy | none |
| `--angle` | Rotation angle in degrees | 0 |
| `--sigma` | Blur/sharpen radius | 1.0 |
| `--opacity` | Watermark opacity (0-1) | 0.5 |
| `--position` | Watermark position | bottom-right |
| `--workers` | Batch processing threads | 4 |
| `--pattern` | File glob pattern | *.* |
| `--recursive` | Process subdirectories | false |

## Performance Tips

| Tip | Description |
|-----|-------------|
| Sequential access | Use `access="sequential"` for streaming |
| Pipeline operations | Chain operations before writing |
| Parallel processing | Use `ThreadPoolExecutor` for batches |
| Format selection | WebP/AVIF for web, JPEG for photos |
| Quality settings | 85 for quality, 75 for size |
| Thumbnail vs resize | `thumbnail_image` is faster for downscaling |

## Memory Usage

libvips uses a streaming architecture:
- Only loads pixels when needed
- Processes images in small chunks
- Memory usage independent of image size
- 10-100x less memory than ImageMagick/PIL for large images

## Troubleshooting

### Common Issues

| Issue | Solution |
|-------|----------|
| "Cannot find libvips" | Install via brew/apt, check PATH |
| Slow processing | Use sequential access, check disk I/O |
| Memory errors | Increase cache, reduce workers |
| Format not supported | Install optional dependencies |
| Poor quality | Increase quality parameter |
| HEIC not working | Install libheif: `brew install libheif` |
| SVG not rendering | Install librsvg: `brew install librsvg` |

### Windows-Specific Issues

| Issue | Solution |
|-------|----------|
| "cannot load library 'libvips-42.dll'" | Add vips `bin\` folder to PATH |
| DLL not found after install | Restart terminal/PowerShell |
| winget install fails | Use manual download or scoop |
| Permission denied | Run PowerShell as Administrator |
| PATH not updated | Log out and log back in, or restart |

**Windows PATH Setup (Manual):**
```powershell
# Add to current session
$env:PATH = "C:\vips\bin;$env:PATH"

# Add permanently (run as Admin or for current user)
[Environment]::SetEnvironmentVariable("PATH", "C:\vips\bin;$env:PATH", "User")
```

### macOS-Specific Issues

| Issue | Solution |
|-------|----------|
| "cannot load library 'libvips.42.dylib'" | Use `./scripts/run.sh` wrapper |
| DYLD_LIBRARY_PATH not working | macOS SIP blocks env vars; use run.sh |
| Homebrew Python issues | Use `/opt/homebrew/bin/python3` directly |

**macOS Library Path Setup:**
```bash
# Add to ~/.zshrc or ~/.bashrc
export DYLD_LIBRARY_PATH="/opt/homebrew/lib:$DYLD_LIBRARY_PATH"
```

### Linux-Specific Issues

| Issue | Solution |
|-------|----------|
| Package not found | Check distro-specific package name |
| ldconfig issues | Run `sudo ldconfig` after install |
| Permission denied | Use `sudo` for system packages |
