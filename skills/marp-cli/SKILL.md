---
name: marp-cli
description: Convert Markdown to presentations via CLI. Output HTML, PDF, PowerPoint (PPTX), and images (PNG/JPEG).
homepage: https://github.com/marp-team/marp-cli
metadata:
  {
    "openclaw":
      {
        "emoji": "📽️",
        "requires": { "anyBins": ["marp"] },
      },
  }
---

# Marp CLI

Convert Markdown to presentations via CLI. Output HTML, PDF, PowerPoint (PPTX), and images (PNG/JPEG).

**Browser requirement:** Conversions marked with 🌐 require a compatible browser (Chrome, Edge, or Firefox) installed on your system.

## Quick Start

```bash
# Convert to HTML
marp slide-deck.md

# Convert to PDF (requires browser)
marp --pdf slide-deck.md

# Convert to PowerPoint
marp --pptx slide-deck.md

# Convert to images
marp --images png slide-deck.md
```

📖 **Detailed guide:** [QUICKSTART.md](QUICKSTART.md)

## Format conversion

### HTML
```bash
marp slide-deck.md
marp slide-deck.md -o output.html
```

### PDF 🌐
```bash
marp --pdf slide-deck.md
marp slide-deck.md -o output.pdf

# With PDF outlines
marp --pdf --pdf-outlines slide-deck.md

# Includes presenter notes as annotations on lower-left
marp --pdf --pdf-notes slide-deck.md
```

### PowerPoint (PPTX) 🌐
```bash
marp --pptx slide-deck.md
marp slide-deck.md -o output.pptx

# Editable PPTX (experimental, requires LibreOffice Impress)
marp --pptx --pptx-editable slide-deck.md
```

### Images 🌐
```bash
# Multiple images
marp --images png slide-deck.md
marp --images jpeg slide-deck.md

# Title slide image only
marp --image png slide-deck.md
marp slide-deck.md -o output.png

# High resolution (scale factor)
marp slide-deck.md -o title.png --image-scale 2
```

### Presenter notes
```bash
marp --notes slide-deck.md
marp slide-deck.md -o output.txt
```

## Watch mode

```bash
# Watch file and auto-convert on changes
marp -w slide-deck.md

# Watch with browser preview
marp -w -p slide-deck.md
```

## Server mode

```bash
# Serve directory with on-demand conversion
marp -s ./slides

# Specify port via environment
PORT=5000 marp -s ./slides

# Access converted formats via query strings
# http://localhost:8080/deck.md?pdf
# http://localhost:8080/deck.md?pptx
```

## Preview window

```bash
# Open preview window (automatically enables watch mode)
marp -p slide-deck.md

# Preview with PDF output
marp -p --pdf slide-deck.md
```

## Multiple files

```bash
# Convert multiple files
marp slide1.md slide2.md slide3.md

# Convert directory
marp ./slides/

# Use glob patterns
marp **/*.md

# Convert with parallelism (default: 5 concurrent)
marp -P 10 ./*.md

# Disable parallelism
marp --no-parallel ./*.md
```

## Options

| Option | Description |
|--------|-------------|
| `-o, --output <path>` | Output file path |
| `-w, --watch` | Watch mode - auto-convert on changes |
| `-s, --server <dir>` | Server mode - serve directory |
| `-p, --preview` | Open preview window |
| `--pdf` | Convert to PDF (requires Chrome/Edge/Firefox) |
| `--pptx` | Convert to PowerPoint PPTX (requires browser) |
| `--pptx-editable` | Generate editable PPTX (experimental) |
| `--images [png\|jpeg]` | Convert to multiple images |
| `--image` | Convert title slide to single image |
| `--image-scale <factor>` | Scale factor for images |
| `--notes` | Export presenter notes to TXT |
| `--pdf-notes` | Add PDF note annotations |
| `--pdf-outlines` | Add PDF outlines/bookmarks |
| `--allow-local-files` | Allow accessing local files (security note) |
| `--browser <chrome\|edge\|firefox>` | Choose browser for conversion |
| `--browser-path <path>` | Specify browser executable path |
| `-P, --parallel <num>` | Parallel conversion count |
| `--no-parallel` | Disable parallel conversion |
| `--template <name>` | HTML template (default: bespoke) |

## Common patterns

```bash
# Watch and preview while editing
marp -w -p deck.md

# Serve slides directory
marp -s ./presentations

# Convert all slides to PDF
marp --pdf *.md

# Create OG image from title
marp deck.md -o og.png --image-scale 3

# Export presenter notes
marp --notes deck.md
```

## Documentation

| Document | Description |
|----------|-------------|
| [QUICKSTART.md](QUICKSTART.md) | Quick start guide |
| [EXAMPLES.md](EXAMPLES.md) | Detailed examples |
| [README.md](README.md) | Project overview |
| Official docs | https://github.com/marp-team/marp-cli |
