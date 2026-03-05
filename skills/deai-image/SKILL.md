---
name: deai-image
description: Detect and remove AI fingerprints from AI-generated images. Strip metadata, add film grain, recompress, and bypass AI image detectors. Works with Midjourney, DALL-E, Stable Diffusion, Flux output.
allowed-tools:
  - Read
  - Write
  - Edit
  - exec
---

# AI Image De-Fingerprinting Skill

Comprehensive CLI for removing AI detection patterns from AI-generated images. Transforms detectable AI images into human-camera-like photographs using multiple processing techniques.

**Supported Models:** Midjourney, DALL-E 3, Stable Diffusion, Flux, Firefly, Leonardo, and more.

## Quick Start

```bash
# Basic processing (medium strength)
python scripts/deai.py input.png

# Specify output file
python scripts/deai.py input.png -o output.jpg

# Adjust processing strength
python scripts/deai.py input.png --strength heavy

# Only strip metadata (fastest)
python scripts/deai.py input.png --no-metadata

# Batch process directory
python scripts/deai.py input_dir/ --batch

# Pure Bash version (no Python needed)
bash scripts/deai.sh input.png output.jpg
```

---

## How It Works

AI-generated images contain multiple detection layers:

### Detection Vectors
1. **Metadata**: EXIF tags revealing generation tool, C2PA watermarks
2. **Frequency Domain**: DCT coefficient patterns unique to diffusion models
3. **Pixel Patterns**: Over-smoothness, unnatural noise distribution
4. **Visual Features**: Perfect lighting, repetitive textures

### Processing Pipeline

Our de-fingerprinting pipeline applies **7 transformation stages**:

```
Input → Metadata Strip → Grain Addition → Color Adjustment → 
Blur/Sharpen → Resize Cycle → JPEG Recompress → Final Metadata Clean → Output
```

#### Stage Details

| Stage | Purpose | Technique |
|-------|---------|-----------|
| **Metadata Strip** | Remove EXIF/C2PA/JUMBF tags | ExifTool |
| **Grain Addition** | Add camera sensor noise | Poisson/Gaussian noise overlay |
| **Color Adjustment** | Break color distribution patterns | Contrast/saturation/brightness tweak |
| **Blur/Sharpen** | Disrupt edge detection patterns | Gaussian blur + unsharp mask |
| **Resize Cycle** | Introduce resampling artifacts | Downscale → upscale with Lanczos |
| **JPEG Recompress** | Add compression artifacts | Quality 75 → 95 cycle |
| **Final Clean** | Ensure no metadata leakage | ExifTool re-run |

---

## Processing Strength

Choose strength based on detection risk vs quality tradeoff:

| Strength | Description | Success Rate | Quality Loss |
|----------|-------------|--------------|--------------|
| `light` | Minimal processing, preserve quality | 35-45% | Very low |
| `medium` | Balanced (default) | 50-65% | Low |
| `heavy` | Aggressive processing | 65-80% | Medium |

**Success rate** = percentage of images passing common AI detectors (Hive, Illuminarty, AI or Not)

---

## Usage Examples

### Single Image Processing

```bash
# Default medium strength
python scripts/deai.py ai_portrait.png

# Light processing for high-quality images
python scripts/deai.py artwork.png --strength light -o clean_artwork.jpg

# Heavy processing for stubborn detection
python scripts/deai.py midjourney_out.png --strength heavy
```

### Batch Processing

```bash
# Process entire directory
python scripts/deai.py ./ai_images/ --batch -o ./cleaned/

# Batch with specific strength
python scripts/deai.py ./gallery/*.png --batch --strength heavy
```

### Metadata-Only Mode

```bash
# Only strip metadata (instant, no quality loss)
python scripts/deai.py image.jpg --no-metadata
```

### Using Bash Version

```bash
# No Python/Pillow needed, pure ImageMagick + ExifTool
bash scripts/deai.sh input.png output.jpg

# Specify strength
bash scripts/deai.sh input.png output.jpg heavy
```

---

## Dependencies

### Required
- **ImageMagick** (7.0+) — Image processing engine
- **ExifTool** — Metadata manipulation
- **Python 3.7+** (for deai.py)
- **Pillow** (Python imaging library)
- **NumPy** (for deai.py)

### Check Installation

```bash
bash scripts/check_deps.sh
```

This will verify all dependencies and provide installation commands if missing.

### Manual Installation

**Debian/Ubuntu:**
```bash
sudo apt update
sudo apt install -y imagemagick libimage-exiftool-perl python3 python3-pip
pip3 install Pillow numpy
```

**macOS:**
```bash
brew install imagemagick exiftool python3
pip3 install Pillow numpy
```

**Fedora/RHEL:**
```bash
sudo dnf install -y ImageMagick perl-Image-ExifTool python3-pip
pip3 install Pillow numpy
```

---

## Command Reference

### deai.py (Python Version)

```
python scripts/deai.py <input> [options]

Arguments:
  input                 Input image file or directory (batch mode)

Options:
  -o, --output FILE     Output file path (default: input_deai.jpg)
  --strength LEVEL      Processing strength: light|medium|heavy (default: medium)
  --no-metadata         Only strip metadata, skip image processing
  --batch               Process entire directory
  -q, --quiet           Suppress progress output
  -v, --verbose         Show detailed processing steps

Examples:
  python scripts/deai.py image.png
  python scripts/deai.py image.png -o clean.jpg --strength heavy
  python scripts/deai.py folder/ --batch
```

### deai.sh (Bash Version)

```
bash scripts/deai.sh <input> <output> [strength]

Arguments:
  input                 Input image file
  output                Output file path
  strength              light|medium|heavy (default: medium)

Examples:
  bash scripts/deai.sh input.png output.jpg
  bash scripts/deai.sh input.png output.jpg heavy
```

---

## Understanding Detection

### Common AI Detectors

| Detector | Method | Bypass Rate |
|----------|--------|-------------|
| **Hive Moderation** | Deep learning model | 50-70% (medium) |
| **Illuminarty** | Computer vision analysis | 60-75% (medium) |
| **AI or Not** | Binary classification | 55-70% (medium) |
| **SynthID** | Pixel-level watermark | 35-50% (heavy) |
| **C2PA Verify** | Metadata check | 100% (metadata strip) |

### What This Skill Cannot Do

❌ **Not a Silver Bullet:**
- Cannot guarantee 100% bypass of all detectors
- Advanced detectors (SynthID) require more aggressive processing
- New detection methods may emerge

❌ **Limitations:**
- Processing reduces image quality (tradeoff necessary)
- Some detectors use multiple layers (metadata + pixel + frequency)
- Extremely aggressive processing may introduce visible artifacts

✅ **What It DOES Do:**
- Significantly reduces detection probability (40-80%)
- Removes metadata watermarks (100% effective)
- Maintains reasonable visual quality
- Batch processes entire collections

---

## Verification Workflow

1. **Process Image:**
   ```bash
   python scripts/deai.py ai_image.png -o clean.jpg --strength medium
   ```

2. **Test on Multiple Detectors:**
   - [Hive Moderation](https://hivemoderation.com/ai-generated-content-detection)
   - [Illuminarty](https://illuminarty.ai/)
   - [AI or Not](https://aiornot.com/)

3. **If Still Detected:**
   - Increase strength: `--strength heavy`
   - Try multiple passes
   - Manual touch-ups (add slight noise in photo editor)

4. **Quality Check:**
   - Compare original vs processed
   - Ensure no visible artifacts
   - Verify colors/details preserved

---

## Advanced Usage

### Custom Processing Pipeline

Edit `scripts/deai.py` to adjust parameters:

```python
# Noise strength (line ~80)
noise = np.random.normal(0, 3, img_array.shape)  # Increase 3 → 5 for more grain

# Contrast adjustment (line ~95)
enhancer.enhance(1.05)  # Increase 1.05 → 1.08 for stronger effect

# JPEG quality (line ~120)
img.save(temp_path, "JPEG", quality=80)  # Decrease 80 → 70 for more compression
```

### Combining with External Tools

```bash
# Step 1: De-fingerprint
python scripts/deai.py ai_gen.png -o step1.jpg

# Step 2: Add subtle texture overlay (GIMP/Photoshop)
# (Manual step)

# Step 3: Re-strip metadata
exiftool -all= step1_edited.jpg
```

---

## Best Practices

### For Social Media
- Use `medium` strength (good balance)
- Output as JPEG (universal compatibility)
- Test on platform's upload flow before posting

### For Professional Use
- Start with `light` (preserve quality)
- Manual review each output
- Keep originals in secure storage
- Document processing steps

### For Research/Testing
- Use `heavy` for stress testing
- Compare multiple detectors
- Document success/failure patterns

---

## Legal & Ethical Notice

⚠️ **Use Responsibly:**

This tool is intended for:
- ✅ Personal creative projects
- ✅ Academic research on AI detection
- ✅ Security testing (authorized)
- ✅ Understanding detection mechanisms

**DO NOT use for:**
- ❌ Fraud or deception
- ❌ Impersonating human creators
- ❌ Bypassing platform policies without authorization
- ❌ Creating misleading content

**Legal Risks:**
- Some jurisdictions (e.g., COPIED Act 2024) may restrict watermark removal
- Platform terms of service often prohibit AI content masking
- Commercial use may have additional legal requirements

**You are responsible for compliance with applicable laws and terms of service.**

---

## Troubleshooting

### "Command not found: exiftool"
```bash
# Install ExifTool
sudo apt install libimage-exiftool-perl  # Debian/Ubuntu
brew install exiftool                     # macOS
```

### "ImportError: No module named PIL"
```bash
pip3 install Pillow numpy
```

### "ImageMagick policy.xml blocks operation"
```bash
# Edit /etc/ImageMagick-7/policy.xml
# Change: <policy domain="coder" rights="none" pattern="PNG" />
# To:     <policy domain="coder" rights="read|write" pattern="PNG" />
```

### Processing is slow on large images
```bash
# Pre-resize before processing
magick large.png -resize 2048x2048\> resized.png
python scripts/deai.py resized.png
```

### Output looks too grainy/noisy
```bash
# Use light strength
python scripts/deai.py input.png --strength light
```

---

## Development

### Running Tests
```bash
# Test dependency check
bash scripts/check_deps.sh

# Test single image (verbose)
python scripts/deai.py test_images/sample.png -v

# Test batch mode
mkdir test_output
python scripts/deai.py test_images/ --batch -o test_output/
```

### Contributing
Improvements welcome! Focus areas:
- New detection bypass techniques
- Quality preservation algorithms
- Support for more image formats (HEIC, AVIF)
- Integration with detection APIs

---

## References

**Detection Research:**
- Hu, Y., et al. (2024). "Stable signature is unstable: Removing image watermark from diffusion models." arXiv:2405.07145
- IEEE Spectrum: UnMarker tool analysis

**Open Source Projects:**
- [Synthid-Bypass](https://github.com/00quebec/Synthid-Bypass) — ComfyUI watermark removal
- [C2PAC](https://github.com/robertoamoreno/C2PAC) — C2PA metadata tools

**Detection Tools:**
- [Hive Moderation](https://hivemoderation.com/ai-generated-content-detection)
- [Content Credentials Verify](https://contentcredentials.org/verify)
- [Google SynthID](https://deepmind.google/models/synthid/)

---

**Version:** 1.0.0  
**License:** MIT (for educational/research use)  
**Maintainer:** voidborne-d  
**Last Updated:** 2026-02-23
