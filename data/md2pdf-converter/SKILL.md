---
name: md2pdf-converter
description: Offline Markdown to PDF converter with FULL Unicode support using Pandoc + WeasyPrint + local Twemoji cache (3660 colorful emojis). Converts Markdown documents to professional PDFs with Chinese fonts and colorful emojis (complete version with all variants). Use when user needs to convert Markdown reports or documents to PDF, generate PDFs with emoji support, create PDFs with proper Chinese character rendering, or work offline after initial setup.
---

# Markdown to PDF Converter (Complete Version)

## Overview

Convert Markdown documents to professional PDFs with **FULL Unicode support**, Chinese fonts, and **colorful emojis** (3660 emojis including all variants). Uses Pandoc + WeasyPrint with a local Twemoji cache to work offline after first run.

## Quick Start

Convert a Markdown file to PDF:

```bash
bash scripts/md2pdf-local.sh input.md output.pdf
```

**First run only:** Downloads ~150MB emoji resources (Twemoji 14.0.0) from GitHub. Subsequent runs work offline.

**Example:**

```bash
bash scripts/md2pdf-local.sh report.md report.pdf
```

## Features

- ✅ **Full Unicode support** (Chinese, Japanese, Korean)
- ✅ **Complete emoji support** (Twemoji 14.0.0, 3660 colorful PNGs)
- ✅ **All emoji variants** (skin tones, hair styles, regional flags, etc.)
- ✅ **Offline operation** after initial setup
- ✅ **Professional PDF layout** with page numbers
- ✅ **Code highlighting**, tables, blockquotes
- ✅ **Accurate emoji mapping** via Python pre-generated lookup table

## Technical Details

### Dependencies

- **Pandoc** - Universal document converter
- **WeasyPrint** - CSS-to-PDF renderer
- **Python 3** - For emoji mapping generation
- **wget** - For emoji download (first run only)

### How It Works

1. **First run**: Downloads Twemoji 14.0.0 to `~/.cache/md2pdf/emojis/`
2. **Python script**: Generates emoji → filename mapping table (`emoji_mapping.json`)
3. **Pandoc**: Converts Markdown to HTML with a Lua filter that replaces emoji characters with local image references
4. **WeasyPrint**: Renders HTML to PDF using:
   - AR PL UMing CN for Chinese characters
   - Local emoji images (PNG, 72x72px, colorful)
   - Professional CSS styling

### Emoji Cache Location

```
~/.cache/md2pdf/
├── emojis/                    # 3660 colorful PNG files
│   ├── 0023-fe0f-20e3.png
│   ├── 1f600.png
│   └── ...
└── emoji_mapping.json         # Emoji to filename mapping
    {
      "🙀": "1f600.png",
      "⌛": "0023-fe0f-20e3.png",
      ...
    }
```

### Emoji Mapping

The Python script `generate_emoji_mapping.py` scans all Twemoji files and creates a precise mapping from emoji characters to PNG filenames. This ensures accurate emoji replacement even for complex variants like skin tones and regional indicators.

### Fonts

**Primary Chinese font**: AR PL UMing CN

**Fallback**: Noto Sans SC, Noto Sans CJK SC, Microsoft YaHei

**Monospace**: Menlo, Monaco

## Version History

### v2.0 (Current)
- ✅ Switched to **Twemoji 14.0.0** (complete version)
- ✅ **3660 colorful emojis** (including all variants)
- ✅ **Python pre-generated mapping** for accurate emoji replacement
- ✅ Fixed black-and-white emoji display issue
- ✅ Proper support for emoji variants (skin tones, hair styles, etc.)

### v1.0 (Previous)
- Used emoji-datasource-google (~2000-3000 emojis)
- Simple hex-based filename matching (inaccurate for variants)
- Some emojis displayed as Unicode characters (black-and-white)

## Troubleshooting

### Font Issues

If Chinese characters display incorrectly, ensure AR PL UMing CN is installed:

```bash
# Ubuntu/Debian
sudo apt-get install fonts-arphic-uming

# Check if installed
fc-list | grep "AR PL UMing"
```

### Emoji Not Showing

1. Check if emoji cache exists: `ls ~/.cache/md2pdf/emojis/`
2. Check if mapping exists: `ls ~/.cache/md2pdf/emoji_mapping.json`
3. If missing, delete cache and re-run: `rm -rf ~/.cache/md2pdf`
4. Verify emoji file exists: `ls ~/.cache/md2pdf/emojis/1f600.png`

### Emoji Displaying as Black-and-White

This issue has been **FIXED** in v2.0. If you still see black-and-white emojis:

1. Verify you're using the v2.0 script:
   ```bash
   grep "TWEMOJI_VERSION" scripts/md2pdf-local.sh
   # Should show: TWEMOJI_VERSION="14.0.0"
   ```

2. Clear cache and regenerate:
   ```bash
   rm -rf ~/.cache/md2pdf
   bash scripts/md2pdf-local.sh test.md test.pdf
   ```

### WeasyPrint Errors

Install missing dependencies:

```bash
# Ubuntu/Debian
sudo apt-get install python3-weasyprint

# Or via pip
pip3 install weasyprint
```

### Python Script Errors

If `generate_emoji_mapping.py` fails:

```bash
# Check Python version
python3 --version
# Should be Python 3.6+

# Check emoji cache
ls ~/.cache/md2pdf/emojis
```

## Resources

### scripts/

**md2pdf-local.sh** - Main conversion script with automatic emoji caching and mapping

**generate_emoji_mapping.py** - Python script to generate emoji lookup table

**Usage**: Direct execution from any location (uses absolute paths):

```bash
bash /path/to/skills/md2pdf-converter/scripts/md2pdf-local.sh input.md output.pdf
```

**Key Features**:
- Automatic Twemoji download and caching
- Python pre-generated emoji mapping (accurate)
- Lua filter for emoji replacement
- CSS styling for professional output
- Temporary file cleanup (automatic)

## Comparison: v1.0 vs v2.0

| Feature | v1.0 (Old) | v2.0 (New) |
|---------|----------------|---------------|
| Emoji Source | emoji-datasource-google | Twemoji 14.0.0 |
| Emoji Count | ~2000-3000 | 3660 |
| Color Display | ❌ Unstable | ✅ Stable |
| Variants Support | ❌ Incomplete | ✅ Complete |
| Mapping Accuracy | ⚠️ Low | ✅ High |
| Offline Support | ✅ After first run | ✅ After first run |
| First Run Size | ~68MB | ~150MB |

## Performance

- **First run**: ~150MB download, 10-30 seconds (depending on network)
- **Subsequent runs**: Offline, seconds-level conversion
- **Memory usage**: ~150MB for emoji cache
- **PDF generation**: 1-5 seconds per page

## Limitations

- Missing emojis (newer than Twemoji 14.0.0) will display as Unicode characters
- First run requires internet connection (for Twemoji download)
- Emoji cache size: ~150MB (3660 PNG files at 72x72px)
