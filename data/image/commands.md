# Image Processing Commands

**Note:** These are reference commands for manual use. This skill does not execute commands automatically — it provides examples for the user to run themselves.

## Requirements

These commands require locally installed tools:
- `imagemagick` — for convert/mogrify commands
- `python` with `pillow` — for Python examples

---

## ImageMagick

### Resize
```bash
# Resize to max width/height (maintain aspect)
convert input.jpg -resize 1920x1080\> output.jpg

# Exact dimensions (may distort)
convert input.jpg -resize 800x600! output.jpg

# Resize by percentage
convert input.jpg -resize 50% output.jpg
```

### Format Conversion
```bash
# JPEG to WebP
convert input.jpg -quality 80 output.webp

# PNG to JPEG (with white background for transparency)
convert input.png -background white -flatten output.jpg

# To AVIF
convert input.jpg -quality 75 output.avif
```

### Compression
```bash
# JPEG quality
convert input.jpg -quality 75 output.jpg

# PNG optimization
convert input.png -strip -quality 85 output.png

# Aggressive WebP
convert input.jpg -quality 70 -define webp:method=6 output.webp
```

### Color Profile
```bash
# Convert to sRGB
convert input.jpg -profile sRGB.icc output.jpg

# Strip and convert to sRGB
convert input.jpg -strip -colorspace sRGB output.jpg
```

### EXIF / Metadata
```bash
# Strip all metadata
convert input.jpg -strip output.jpg

# Preserve orientation, strip rest
convert input.jpg -auto-orient -strip output.jpg

# View EXIF
identify -verbose input.jpg | grep -i exif
```

### Auto-Orient (EXIF rotation fix)
```bash
convert input.jpg -auto-orient output.jpg
```

### Batch Processing
```bash
# All JPGs to WebP
mogrify -format webp -quality 80 *.jpg

# Resize all in folder
mogrify -resize 1920x1080\> *.jpg
```

---

## Python PIL/Pillow

### Basic Operations
```python
from PIL import Image

# Open and resize
img = Image.open('input.jpg')
img = img.resize((800, 600), Image.Resampling.LANCZOS)
img.save('output.jpg', quality=85)

# Convert format
img = Image.open('input.png')
img.convert('RGB').save('output.jpg', quality=85)
```

### Handle EXIF Rotation
```python
from PIL import Image, ExifTags

def fix_orientation(img):
    try:
        exif = img._getexif()
        if exif:
            for tag, value in exif.items():
                if ExifTags.TAGS.get(tag) == 'Orientation':
                    if value == 3:
                        img = img.rotate(180, expand=True)
                    elif value == 6:
                        img = img.rotate(270, expand=True)
                    elif value == 8:
                        img = img.rotate(90, expand=True)
    except:
        pass
    return img
```

### WebP Conversion
```python
img = Image.open('input.jpg')
img.save('output.webp', 'WEBP', quality=80, method=6)
```

### Transparency to White Background
```python
img = Image.open('input.png')
if img.mode in ('RGBA', 'LA', 'P'):
    background = Image.new('RGB', img.size, (255, 255, 255))
    background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
    img = background
img.save('output.jpg', quality=85)
```

### Thumbnail with Aspect Ratio
```python
img = Image.open('input.jpg')
img.thumbnail((300, 300), Image.Resampling.LANCZOS)
img.save('thumb.jpg', quality=75)
```

---

## Common Traps

### EXIF Rotation
Images display correctly in viewers but save rotated:
```bash
# Always auto-orient before processing
convert input.jpg -auto-orient output.jpg
```

### Transparency Loss
Converting PNG→JPEG loses transparency:
```bash
# Add white background
convert input.png -background white -flatten output.jpg
```

### Color Space Issues
Washed out colors = wrong color profile:
```bash
# Convert to sRGB for web
convert input.jpg -colorspace sRGB output.jpg
```

### Animated WebP/GIF
Each frame must be processed:
```bash
# Convert animated GIF to WebP
convert input.gif output.webp
```

### SVG Rasterization
```bash
# SVG to PNG at specific size
convert -density 300 input.svg -resize 1000x1000 output.png
```

---

## Resize Algorithms

| Algorithm | Use For |
|-----------|---------|
| LANCZOS | Best quality downscaling |
| BICUBIC | Good balance speed/quality |
| NEAREST | Pixel art (no smoothing) |
| BILINEAR | Fast, acceptable quality |

**Rule:** Always use LANCZOS for final output.

---

## Quick Commands

```bash
# Check image info
identify image.jpg

# Get dimensions only
identify -format '%wx%h' image.jpg

# Get file size
identify -format '%b' image.jpg

# Strip metadata + optimize JPEG
convert input.jpg -strip -quality 80 output.jpg

# Create responsive set
for size in 320 640 1024 1920; do
  convert input.jpg -resize ${size}x\> output-${size}.jpg
done
```
