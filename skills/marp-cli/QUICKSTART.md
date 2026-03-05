# Marp CLI Quickstart

Quick start guide for converting Markdown to presentations with Marp CLI.

## Installation

**Note:** Installation via npm/standalone binary is not covered in these examples. Assumes `marp` command is available.

```bash
# Verify installation
marp --version

# Quick test
echo "# Hello World" | marp -
```

## Basic Markdown Syntax

```markdown
---
marp: true
theme: gaia
paginate: true
---

# Presentation Title

## First Section

- Bullet point
- Another point

### Subsection

Content goes here.

---
# Slide 2

Bold and *italic* text.
```

## Core Commands

### Convert to HTML (default)

```bash
# Single file
marp presentation.md

# Specify output filename
marp presentation.md -o export.html

# Multiple files
marp slide1.md slide2.md slide3.md

# Directory
marp ./slides/
```

### Convert to PDF 🌐

**Requires:** Chrome, Edge, or Firefox installed.

```bash
# Convert to PDF
marp --pdf presentation.md

# Specify output
marp presentation.md -o deck.pdf

# Auto-detect from extension
marp presentation.md -o output.pdf

# With outlines/bookmarks
marp --pdf --pdf-outlines presentation.md

# Disable headings in outlines
marp --pdf --pdf-outlines.headings=false presentation.md
```

### Convert to PowerPoint 🌐

```bash
# Convert to PPTX
marp --pptx presentation.md

# Specify output
marp presentation.md -o deck.pptx

# Auto-detect
marp presentation.md -o output.pptx
```

**Editable PPTX (experimental):**
```bash
# Generate editable PPTX (requires LibreOffice Impress)
marp --pptx --pptx-editable presentation.md

# Note: Lower reproducibility, no presenter notes
```

### Convert to Images 🌐

```bash
# Multiple PNG images
marp --images png presentation.md
# Output: presentation.001.png, presentation.002.png, ...

# Multiple JPEG images
marp --images jpeg presentation.md

# Title slide only
marp --image png presentation.md
# Output: presentation.001.png

# High resolution
marp --image png presentation.md --image-scale 2
marp --image png presentation.md -o title@3x.png --image-scale 3
```

### Export Presenter Notes

```bash
# Export notes to text file
marp --notes presentation.md

# Auto-detect from extension
marp presentation.md -o notes.txt

# With PDF conversion
marp --pdf --pdf-notes presentation.md
```

## Watch Mode

```bash
# Watch single file
marp -w presentation.md

# Watch with preview
marp -w -p presentation.md

# Watch multiple files
marp -w *.md

# Watch directory
marp -w ./slides/
```

## Server Mode

```bash
# Serve directory
marp -s ./slides

# Server with watch
marp -s -w ./slides

# Custom port
PORT=5000 marp -s ./slides

# Access via web browser
# http://localhost:8080/

# Request specific formats
# http://localhost:8080/deck.md?pdf
# http://localhost:8080/deck.md?pptx
# http://localhost:8080/deck.md?images=png
# http://localhost:8080/deck.md?image=jpeg
```

## Preview Window

```bash
# Open preview window
marp -p presentation.md

# Preview with specific output
marp -p --pdf presentation.md
marp -p --images png presentation.md
```

**Note:** Preview mode automatically enables watch mode.

## Multiple File Processing

```bash
# Convert all markdown files
marp *.md

# Parallel conversion (default: 5 concurrent)
marp -P 10 presentation*.md

# Disable parallelism
marp --no-parallel *.md

# Convert directory structure
marp -I ./input --output-dir ./output
```

## Browser Options

```bash
# Choose browser
marp --browser chrome deck.md -o deck.pdf
marp --browser edge deck.md -o deck.pdf
marp --browser firefox deck.md -o deck.png

# Try multiple browsers in order
marp --browser firefox,chrome deck.md -o deck.pdf

# Specify custom browser path
marp --browser-path /path/to/chrome deck.md -o deck.pdf

# Use Brave browser
marp --browser-path /usr/bin/brave-browser deck.md -o deck.png
```

## Template Options

```bash
# Use specific template
marp --template bespoke deck.md

# Common template: bespoke (default)
marp -t bespoke deck.md
```

**Template features:**
- Keyboard navigation
- Fullscreen toggle
- On-screen controller
- Presenter view
- Fragmented lists
- Progress bar (with `--bespoke.progress`)

## Output Options

```bash
# Output to specific directory
marp deck.md -o ./exports/deck.html

# Output with custom extension
marp deck.md -o custom-name.pdf

# Pipe markdown input
echo "# Title\n\nContent" | marp - -o output.html

# Read from stdin
cat presentation.md | marp - -o deck.pdf
```

## Advanced Options

### Security and Local Files

```bash
# Allow local files (use with caution)
marp --pdf --allow-local-files deck.md

# Note: Default blocks local file access for security
```

### PDF Advanced

```bash
# Outlines options
marp --pdf --pdf-outlines deck.md
marp --pdf --pdf-outlines.pages=false deck.md
marp --pdf --pdf-outlines.headings=false deck.md

# Presenter notes as PDF annotations
marp --pdf --pdf-notes deck.md
```

### Image Scaling

```bash
# High resolution images
marp deck.md -o deck.png --image-scale 3

# 2x scale (default for PPTX)
marp deck.md -o deck.pptx --image-scale 2
```

## Typical Workflows

### Development Workflow

```bash
# Start watch mode with preview
marp -w -p deck.md

# Edit markdown in your editor
# Browser auto-refreshes on save

# When ready, export
marp --pdf deck.md
```

### Batch Conversion

```bash
# Convert all to PDF
for file in *.md; do
    marp --pdf "$file"
done

# Or use marp's parallel processing
marp --pdf *.md
```

### Presentation Deployment

```bash
# Serve and present
marp -s ./presentations

# Share URL with team
# Format-specific outputs via query strings
```

### Social Media Images

```bash
# Create high-res OG image
marp deck.md -o og-image.png --image-scale 3

# Square format from first slide
marp deck.md -o thumbnail.jpeg --image jpeg
```

## Configuration File

Marp CLI can use `.marprc` (JSON) or `marp.config.js`:

```json
{
  "allowLocalFiles": true,
  "engine": "@marp-team/marp-core",
  "html": true,
  "options": {
    "allow-local-files": true
  },
  "pdf": {
    "notes": true,
    "outlines": true
  }
}
```

## Tips

1. **Auto-detection:** Marp detects output format from file extension
2. **Parallel processing:** Default 5 concurrent conversions for multiple files
3. **Browser caching:** First conversion may be slower
4. **Preview mode:** Best for development, auto-refreshes
5. **Server mode:** Best for collaborative work and testing
6. **Image scale:** Use higher scale for quality, but larger files

## Markdown Frontmatter

Add frontmatter to control presentation:

```markdown
---
marp: true
theme: gaia
paginate: true
style: |
  /* Custom CSS */
  section {
    font-size: 24px;
  }
---

# Title

Content...
```

Common themes: `default`, `gaia`, `uncover`, `invert`

## Presenter Notes

Add notes for each slide:

```markdown
---

# Slide Title

Slide content.

<!-- Presenter note: Remember to mention X -->
```

Export notes:
```bash
marp --notes deck.md
```

---

**Next Steps:**
- [EXAMPLES.md](EXAMPLES.md) - Detailed examples
- [README.md](README.md) - Full overview
- Official docs: https://github.com/marp-team/marp-cli
