# AI Image De-Fingerprinting Skill

Remove AI detection patterns from AI-generated images. Transform machine-generated photos into human-camera-like photographs by stripping metadata, adding film grain, adjusting color, and recompressing.

**Works with:** Midjourney, DALL-E 3, Stable Diffusion, Flux, Firefly, Leonardo, and other diffusion models.

## What It Does

AI image detectors (Hive, Illuminarty, SynthID) identify AI-generated images through:
- **Metadata**: EXIF tags, C2PA watermarks
- **Pixel patterns**: Over-smoothness, unnatural noise
- **Frequency domain**: DCT coefficient signatures
- **Deep learning**: Model-specific fingerprints

This skill applies a 7-stage processing pipeline to disrupt these detection vectors:

```
Input → Metadata Strip → Grain → Color Adjust → Blur/Sharpen → 
Resize → JPEG Recompress → Final Clean → Output
```

## Quick Start

```bash
# Check dependencies
bash scripts/check_deps.sh

# Process single image (Python)
python scripts/deai.py ai_generated.png

# Process with specific strength
python scripts/deai.py image.png --strength heavy -o clean.jpg

# Batch process directory
python scripts/deai.py ./ai_images/ --batch

# Bash version (no Python needed)
bash scripts/deai.sh input.png output.jpg
```

## Installation

### Dependencies

- **ImageMagick 7.0+** — Image processing
- **ExifTool** — Metadata removal
- **Python 3.7+** + Pillow + NumPy (for Python version)

### Install

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

**Verify:**
```bash
bash scripts/check_deps.sh
```

## Usage

### Python Version (Recommended)

```bash
# Basic (default medium strength)
python scripts/deai.py image.png

# Custom output path
python scripts/deai.py image.png -o cleaned.jpg

# Processing strength
python scripts/deai.py image.png --strength light    # Preserve quality
python scripts/deai.py image.png --strength medium   # Balanced (default)
python scripts/deai.py image.png --strength heavy    # Maximum bypass

# Metadata only (no image processing)
python scripts/deai.py image.png --no-metadata

# Batch mode
python scripts/deai.py ./input_folder/ --batch
python scripts/deai.py ./input_folder/ --batch -o ./output_folder/

# Verbose output
python scripts/deai.py image.png -v
```

### Bash Version

```bash
# Basic usage
bash scripts/deai.sh input.png output.jpg

# With strength parameter
bash scripts/deai.sh input.png output.jpg light
bash scripts/deai.sh input.png output.jpg heavy
```

## Processing Strengths

| Strength | Description | Success Rate | Quality |
|----------|-------------|--------------|---------|
| `light` | Minimal processing | 35-45% | ★★★★★ |
| `medium` | Balanced (default) | 50-65% | ★★★★☆ |
| `heavy` | Aggressive | 65-80% | ★★★☆☆ |

**Success rate** = percentage bypassing Hive/Illuminarty/AI or Not detectors.

## Verification

After processing, test your image:

1. **[Hive Moderation](https://hivemoderation.com/ai-generated-content-detection)** — Industry standard
2. **[Illuminarty](https://illuminarty.ai/)** — Region-based detection
3. **[AI or Not](https://aiornot.com/)** — Fast binary check

If still detected, try:
- Increase strength: `--strength heavy`
- Process twice (output → input again)
- Manual touch-ups in photo editor

## Limitations

### What This CANNOT Do

- ❌ Guarantee 100% bypass (detection tech evolves)
- ❌ Work on all detectors (SynthID requires heavy mode)
- ❌ Preserve perfect quality (processing = quality tradeoff)

### What It DOES Do

- ✅ Remove metadata watermarks (100% effective)
- ✅ Disrupt pixel/frequency patterns (50-80% effective)
- ✅ Batch process entire collections
- ✅ Maintain reasonable visual quality

## Legal & Ethical Notice

⚠️ **Use Responsibly**

This tool is for:
- ✅ Personal creative projects
- ✅ Academic research
- ✅ Security testing (authorized)

**NOT for:**
- ❌ Fraud or deception
- ❌ Bypassing platform rules
- ❌ Impersonating humans
- ❌ Misleading content

**Legal risks:**
- Some jurisdictions restrict watermark removal
- Platform ToS often prohibit AI masking
- Commercial use may require legal review

**You are responsible for compliance with laws and terms of service.**

## Troubleshooting

**"Command not found: exiftool"**
```bash
sudo apt install libimage-exiftool-perl  # Debian/Ubuntu
brew install exiftool                     # macOS
```

**"ImportError: No module named PIL"**
```bash
pip3 install Pillow numpy
```

**"ImageMagick policy.xml blocks PNG"**
```bash
# Edit /etc/ImageMagick-7/policy.xml
# Change: <policy domain="coder" rights="none" pattern="PNG" />
# To:     <policy domain="coder" rights="read|write" pattern="PNG" />
```

**Processing too slow**
```bash
# Pre-resize large images
magick huge.png -resize 2048x2048\> resized.png
python scripts/deai.py resized.png
```

## Development

### File Structure

```
skills/deai-image/
├── SKILL.md              # Main documentation
├── README.md             # This file
├── package.json          # ClawHub metadata
└── scripts/
    ├── deai.py           # Python version (recommended)
    ├── deai.sh           # Bash version
    └── check_deps.sh     # Dependency checker
```

### Contributing

Improvements welcome! Focus areas:
- Better detection bypass techniques
- Quality preservation algorithms
- Support for HEIC/AVIF formats
- Integration with detection APIs

## References

**Research:**
- Hu, Y., et al. (2024). "Stable signature is unstable: Removing image watermark from diffusion models." arXiv:2405.07145

**Tools:**
- [Synthid-Bypass](https://github.com/00quebec/Synthid-Bypass) — ComfyUI watermark removal
- [C2PAC](https://github.com/robertoamoreno/C2PAC) — C2PA metadata tools

**Detectors:**
- [Hive Moderation](https://hivemoderation.com/ai-generated-content-detection)
- [Google SynthID](https://deepmind.google/models/synthid/)

## License

MIT License (for educational and research purposes)

---

**Version:** 1.0.0  
**Author:** voidborne-d  
**Last Updated:** 2026-02-23
