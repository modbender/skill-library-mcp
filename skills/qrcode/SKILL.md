---
name: qrcode
description: "Generate styled QR codes (SVG/PNG/JPG) with custom colors, shapes,
  and error correction. Agent should display generated files. Secure: all
  outputs saved to workspace root."
---


# QRCode Generator

Generate customizable QR codes from text or URLs. Supports multiple formats (SVG/PNG/JPG) with styling options.

## Agent Instructions

**After generating QR codes, you MUST:**

1. Display the generated file using appropriate markdown syntax:
   - For images (PNG/JPG): `![QR Code](sandbox:/path/to/file.png)`
   - For SVG: Display as image or provide download link
2. Confirm the file path and format to the user
3. Offer to regenerate with different styling if needed

## Quick Start

```bash
# Basic usage (auto-generated filename)
node {baseDir}/scripts/generate.mjs "Hello World"

# Custom styled QR code
node {baseDir}/scripts/generate.mjs "https://example.com" -o myqr.svg --dot circle --eye rounded --color "#2563eb"

# High-resolution transparent PNG
node {baseDir}/scripts/generate.mjs "Contact Info" --format png --size 2048 --transparent

# Print-quality JPEG
node {baseDir}/scripts/generate.mjs "https://example.com" --format jpg -o qr.jpg --size 2048 --quality 95
```

## Options

### Output

- `-o, --out <filename>` - Output filename (workspace root only). Default: `qrcode_<text>_<timestamp>.<ext>`
- `--format <svg|png|jpg>` - Output format (default: `svg`)

### Dimensions

- `--size <px>` - Base pixel size (default: `1024`, max: `10000`)
- `--scale <n>` - Resolution multiplier (default: `1`, max: `10`)
- `--margin <modules>` - Quiet zone size (default: `4`, max: `100`)

### Styling

- `--dot <square|circle>` - Data module shape (default: `square`)
- `--eye <square|circle|rounded>` - Finder pattern style (default: `square`)
- `--color <#RRGGBB>` - Foreground color (default: `#000000`)
- `--background <#RRGGBB>` - Background color (default: `#ffffff`)
- `--transparent` - Transparent background (PNG only, ignored for SVG/JPG)

### Quality

- `--ec <L|M|Q|H>` - Error correction: Low/Medium/Quality/High (default: `M`)
  - **L (~7%)**: Clean environments, maximum data capacity
  - **M (~15%)**: General use, balanced capacity/reliability
  - **Q (~25%)**: Styled QR codes, moderate damage tolerance
  - **H (~30%)**: Logo embedding, heavy styling, outdoor use
- `--quality <1-100>` - JPEG compression quality (default: `80`)

## File Handling

**Security-enforced workspace root output:**

- All files saved to workspace root directory only
- Path components stripped: `-o ../path/file.svg` → `workspace/file.svg`
- Auto-generated filenames include sanitized text and timestamp
- Maximum text length: 4096 characters

## Installation

```bash
cd {baseDir}
npm install
```

**Dependencies:** `qrcode` (matrix generation), `sharp` (image conversion)

**Platform notes:** macOS requires Xcode Command Line Tools. See [sharp docs](https://sharp.pixelplumbing.com/install) for other platforms.

## Examples

### WiFi QR Code

```bash
node {baseDir}/scripts/generate.mjs "WIFI:S:MyNetwork;T:WPA;P:password123;;" --format png -o wifi.png --size 1024
```

### Styled Business Card

```bash
node {baseDir}/scripts/generate.mjs "BEGIN:VCARD
VERSION:3.0
FN:John Doe
TEL:+1234567890
EMAIL:john@example.com
END:VCARD" --dot circle --eye rounded --color "#1e40af" --background "#eff6ff" -o contact.svg
```

### High-Resolution Print

```bash
node {baseDir}/scripts/generate.mjs "https://example.com" --format jpg --size 4096 --quality 95 --ec H -o print.jpg
```

### Transparent Logo Overlay

```bash
node {baseDir}/scripts/generate.mjs "https://example.com" --format png --size 2048 --transparent --margin 2 -o overlay.png
```

### Logo Embedding (Requires High Error Correction)

```bash
# Use --ec H when QR code will have logo overlay (covers ~20-30% of center)
node {baseDir}/scripts/generate.mjs "https://example.com" --format png --size 2048 --ec H -o logo-base.png
```

## Security Features

- ✅ **Path traversal protection** - All outputs forced to workspace root
- ✅ **Symlink attack prevention** - Atomic writes with verification
- ✅ **Input validation** - Length limits (4096 chars), character whitelisting
- ✅ **Filename sanitization** - Dangerous characters stripped from filenames
- ✅ **Resource limits** - Max size/scale to prevent DoS attacks

## Troubleshooting

| Issue               | Solution                                                                                                                   |
| ------------------- | -------------------------------------------------------------------------------------------------------------------------- |
| `npm install` fails | Install build tools:`xcode-select --install` (macOS) or see [sharp install guide](https://sharp.pixelplumbing.com/install) |
| QR code won't scan  | Increase `--size`, use higher error correction (`--ec H`), or simplify styling                                             |
| Colors not working  | Use hex format `#RRGGBB` (e.g., `#FF5733`), not RGB or color names                                                         |
| File too large      | Reduce `--size`, `--scale`, or increase `--quality` for JPG                                                                |
| Permission denied   | Check workspace directory write permissions                                                                                |

## Error Correction Levels Explained

Error correction allows QR codes to remain scannable even when partially damaged or obscured:

| Level | Recovery Capacity | Data Capacity | Use Case                                                   |
| ----- | ----------------- | ------------- | ---------------------------------------------------------- |
| `L`   | ~7% damage        | Maximum       | Clean environments, screen display, maximum data           |
| `M`   | ~15% damage       | High          | **General use (default)**, standard printing               |
| `Q`   | ~25% damage       | Medium        | Styled designs (circles/rounded), possible minor damage    |
| `H`   | ~30% damage       | Minimum       | Logo embedding, outdoor use, heavy styling, print-on-print |

**Key principle:** Higher error correction = more damage tolerance but less data capacity.

**When to use H level:**

- Embedding logos (covers 20-30% of center)
- Circular dots or rounded eyes
- Outdoor/weathered environments
- Low-quality printing
- Stickers that may peel/scratch

## Format Comparison

| Format | Transparency | Quality  | File Size  | Use Case                   |
| ------ | ------------ | -------- | ---------- | -------------------------- |
| SVG    | ✅           | Infinite | Smallest   | Web, scalable graphics     |
| PNG    | ✅           | Lossless | Medium     | Digital displays, overlays |
| JPG    | ❌           | Lossy    | Smallest\* | Print, photos, email       |

\*With compression

## Tips

- **Scanning distance**: Use `--size 1024` for mobile (1-2m), `--size 2048+` for print/posters
- **Styling vs. reliability**: Higher `--ec` levels compensate for `--dot circle` or `--eye rounded`
- **Transparent backgrounds**: Use PNG format with `--transparent`; JPG always uses white/specified background
- **File size optimization**: SVG for web, JPG with `--quality 80-85` for print
- **Data capacity**: L/M/Q/H levels affect max alphanumeric capacity: ~4296/3391/2420/1852 chars (Version 40)
- **Logo placement**: Use `--ec H` and leave center area clear (approximately 30% of QR code)

## Common Use Cases

| Scenario                  | Recommended Settings                                             |
| ------------------------- | ---------------------------------------------------------------- |
| Website URL               | `--format png --size 1024 --ec M`                                |
| WiFi credentials          | `--format png --size 1024 --ec M`                                |
| Business card (vCard)     | `--format svg --dot circle --eye rounded --ec Q`                 |
| Print poster              | `--format jpg --size 4096 --quality 95 --ec H`                   |
| Logo overlay base         | `--format png --size 2048 --ec H --transparent`                  |
| Email signature           | `--format png --size 512 --ec M`                                 |
| Product packaging         | `--format svg --ec H` (scalable for any print size)              |
| Outdoor signage           | `--format jpg --size 2048+ --ec H --quality 90`                  |
| Social media profile      | `--format png --size 1024 --transparent --dot circle --ec Q`     |
| Payment QR (high density) | `--format png --size 2048 --ec L --margin 2` (maximize capacity) |
