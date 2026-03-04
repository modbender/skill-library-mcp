---
description: Compress, resize, and convert images using ImageMagick. Batch process with quality control.
---

# Image Optimizer

Optimize images via compression, resizing, and format conversion.

**Use when** compressing images, batch converting formats, or resizing for web/social media.

## Requirements

- ImageMagick 7+ (`magick`) or ImageMagick 6 (`convert`)
- Optional: `cwebp` (WebP), `optipng` (PNG), `jpegoptim` (JPEG)
- No API keys needed

## Instructions

1. **Check image info** before processing:
   ```bash
   magick identify -format "%f | %wx%h | %b | %m\n" image.png
   ```

2. **Compress** — reduce file size:
   ```bash
   # JPEG (80% quality is a good default)
   magick input.jpg -quality 80 -strip output.jpg

   # PNG (lossless optimization)
   optipng -o5 image.png          # in-place
   magick input.png -strip output.png

   # WebP (lossy, excellent compression)
   cwebp -q 80 input.png -o output.webp
   ```

3. **Resize** — scale to specific dimensions:
   ```bash
   # Exact dimensions (may distort)
   magick input.jpg -resize 800x600! output.jpg

   # Fit within bounds (preserve aspect ratio)
   magick input.jpg -resize 800x600 output.jpg

   # By percentage
   magick input.jpg -resize 50% output.jpg

   # Thumbnail (crop to fill)
   magick input.jpg -resize 300x300^ -gravity center -extent 300x300 thumb.jpg
   ```

4. **Format conversion**:
   ```bash
   magick input.png output.webp    # PNG → WebP
   magick input.jpg output.avif    # JPEG → AVIF
   ```

5. **Batch processing**:
   ```bash
   # Convert all PNGs to WebP in a directory
   for f in *.png; do magick "$f" -quality 80 "${f%.png}.webp"; done

   # Resize all images to max 1200px width
   for f in *.jpg; do magick "$f" -resize "1200>" "$f"; done
   ```

6. **Output format** — report results:
   ```
   ## 🖼️ Optimization Results
   | File | Original | Optimized | Savings |
   |------|----------|-----------|---------|
   | hero.jpg | 2.4 MB | 680 KB | 72% |
   | logo.png | 340 KB | 89 KB | 74% |
   **Total: 2.74 MB → 769 KB (72% reduction)**
   ```

## Preset Sizes

| Use Case | Dimensions | Notes |
|----------|-----------|-------|
| Web hero | 1920×1080 | JPEG q80 or WebP |
| Thumbnail | 300×300 | Crop to fill |
| Social (OG) | 1200×630 | Facebook/Twitter preview |
| Profile pic | 400×400 | Square crop |
| Email | 600px wide | Resize width only |

## Edge Cases

- **Animated GIF**: Use `magick input.gif -coalesce -resize 50% output.gif` (preserve animation).
- **EXIF data**: `-strip` removes metadata including GPS. Use `-auto-orient -strip` to preserve rotation.
- **Transparency**: Converting PNG (with alpha) to JPEG loses transparency. Add `-background white -flatten`.
- **Very large files**: Process in batches to avoid memory issues.
- **Already optimized**: Check if compression actually reduces size — skip if negligible.

## Security

- Sanitize filenames before processing — avoid shell injection via crafted filenames.
- Use `magick` not `convert` to avoid path conflicts with Windows `convert.exe`.
