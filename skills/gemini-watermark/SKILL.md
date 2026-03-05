---
name: gemini-watermark
description: Remove visible Gemini AI watermarks from images via reverse alpha blending. Use for cleaning Gemini-generated images, removing the star/sparkle logo watermark, batch watermark removal.
metadata:
  author: agiseek
  version: "2.1.0"
---

# Gemini Watermark Remover

Remove the visible Gemini AI watermark (star/sparkle logo) from generated images using mathematically accurate reverse alpha blending.

**Fully offline — pure Python, no external binary downloads, no network access.**

## When to Use

- Remove the Gemini watermark from AI-generated images
- Batch process a directory of Gemini-generated images
- Clean images before publishing or sharing
- Automate watermark removal in pipelines

## Quick Start

### Install Dependencies (one-time)

```bash
pip install Pillow numpy

# Recommended: use uv for faster, isolated installs
uv pip install Pillow numpy
```

Requires: Python ≥ 3.9. No Rust toolchain, no compiled binaries, no downloads.

### Basic Usage

```bash
# Single image (auto-detect watermark, save as photo_cleaned.jpg)
python3 scripts/remove_watermark.py photo.jpg

# Specify output path
python3 scripts/remove_watermark.py photo.jpg -o clean_photo.jpg

# Batch process directory
python3 scripts/remove_watermark.py ./input_dir -o ./output_dir

# Force removal without detection
python3 scripts/remove_watermark.py photo.jpg -o clean.jpg --force
```

## How It Works

Gemini adds a semi-transparent white star/sparkle logo to generated images using alpha blending:

```
watermarked = alpha * 255 + (1 - alpha) * original
```

This tool reverses the equation to recover the original pixels:

```
original = (watermarked - alpha * 255) / (1 - alpha)
```

The alpha map (watermark transparency pattern) is generated mathematically as a
4-pointed star (central Gaussian core + 4 elongated cardinal rays) at two sizes:

- **48×48** with 32 px margin — images where either dimension ≤ 1024 px
- **96×96** with 64 px margin — images where both dimensions > 1024 px

For improved accuracy you can supply your own alpha map derived from a background
capture of the Gemini watermark on a white background (`--alpha-map`).

### Detection

Before removal, a three-stage algorithm checks whether a watermark is present:

1. **Spatial NCC** (50% weight) — normalised cross-correlation with the alpha map
2. **Gradient NCC** (30% weight) — edge signature matching via Sobel operators
3. **Variance Analysis** (20% weight) — texture dampening detection

Images without detected watermarks are automatically skipped.

## CLI Parameters

| Parameter | Short | Default | Description |
|-----------|-------|---------|-------------|
| `input` | | (required) | Input image file or directory |
| `--output` | `-o` | `{name}_cleaned.{ext}` | Output file or directory |
| `--force` | `-f` | `false` | Skip detection, process unconditionally |
| `--threshold` | `-t` | `0.35` | Detection confidence threshold (0.0–1.0) |
| `--force-small` | | `false` | Force 48×48 watermark size |
| `--force-large` | | `false` | Force 96×96 watermark size |
| `--alpha-map` | | (built-in) | Custom grayscale alpha map image |
| `--verbose` | `-v` | `false` | Enable detailed output |
| `--quiet` | `-q` | `false` | Suppress all non-error output |

## Supported Formats

| Format | Read | Write |
|--------|------|-------|
| JPEG (.jpg, .jpeg) | Yes | Yes (quality 100) |
| PNG (.png) | Yes | Yes |
| WebP (.webp) | Yes | Yes |
| BMP (.bmp) | Yes | Yes |

## Usage Examples

```bash
# Verbose output (shows detection confidence, watermark coordinates)
python3 scripts/remove_watermark.py photo.png -o clean.png -v

# Lower detection threshold (more sensitive)
python3 scripts/remove_watermark.py photo.jpg -t 0.15

# Force large watermark size regardless of image dimensions
python3 scripts/remove_watermark.py photo.jpg --force-large -o clean.jpg

# Batch process, quiet mode
python3 scripts/remove_watermark.py ./gemini_images/ -o ./cleaned/ -q

# Supply a custom alpha map for higher accuracy
python3 scripts/remove_watermark.py photo.jpg --alpha-map my_alpha.png
```

### Deriving a Custom Alpha Map

For pixel-perfect removal, capture the Gemini watermark on a pure white
background and compute:

```
alpha(x, y) = max(R, G, B) / 255
```

Save the result as a grayscale PNG and pass it via `--alpha-map`.

## Output

- **Single file** — saves to `-o` path, or `{name}_cleaned.{ext}` by default
- **Directory** — saves all processed images to the output directory
- **Skipped images** — images without detected watermarks are not modified (unless `--force`)
- **Exit code** — 0 on success, 1 if any image fails

## Troubleshooting

### "No watermark detected" on a watermarked image

- Try lowering the threshold: `-t 0.1`
- Or bypass detection entirely: `--force`
- Consider supplying a custom alpha map for your watermark variant

### Image looks distorted after removal

- The image may not have a Gemini watermark. Use detection (avoid `--force`)
- Try `--force-small` or `--force-large` to match the correct size
- Supply a custom alpha map for better precision

### "Image too small" warning

The image dimensions are smaller than the watermark region. This typically
means the image does not have a Gemini watermark.

### ModuleNotFoundError: Pillow or numpy

```bash
pip install Pillow numpy
# or
uv pip install Pillow numpy
```

## Limitations

- **Visible watermark only** — this tool removes the visible star/sparkle logo watermark
- **Cannot remove SynthID** — Google's invisible watermark (SynthID) is embedded at the pixel level during generation and cannot be reversed
- **Fixed position only** — handles watermarks in the standard bottom-right position only
- **Built-in alpha map is approximate** — use `--alpha-map` with a captured reference for exact results
