# Marp CLI Examples

Detailed examples for Markdown to presentation conversion.

## Complete Presentation Workflow

### From Markdown to Distribution

```bash
# Step 1: Create presentation.md
cat > presentation.md << 'EOF'
---
marp: true
theme: gaia
paginate: true
---

# Product Launch

## Features
- Feature A
- Feature B
- Feature C

## Pricing
Tier 1: Free
Tier 2: $10/mo

---
# Thank You!
EOF

# Step 2: Watch and preview during editing
marp -w -p presentation.md

# Step 3: Export when ready
marp --pdf presentation.md
marp --pptx presentation.md
marp --images png presentation.md
```

## Format-Specific Examples

### PDF Generation

```bash
# Basic PDF
marp --pdf deck.md

# PDF with outlines
marp --pdf --pdf-outlines deck.md

# PDF with notes annotations
marp --pdf --pdf-notes deck.md

# PDF with browser selection
marp --pdf --browser firefox deck.md

# High-resolution effect (via image scale)
marp --pdf --image-scale 2 deck.md

# Multiple PDFs
marp --pdf presentation-1.md presentation-2.md presentation-3.md
```

### PowerPoint Generation

```bash
# Standard PPTX
marp --pptx deck.md

# Editable PPTX (experimental)
marp --pptx --pptx-editable deck.md

# PPTX with custom scale
marp --pptx --image-scale 3 deck.md

# PPTX with Edge browser
marp --pptx --browser edge deck.md
```

### Image Generation

```bash
# All slides as PNG
marp --images png deck.md

# All slides as JPEG
marp --images jpeg deck.md

# Title slide only
marp --image png deck.md -o title.png

# High-res title slide
marp deck.md -o og-image.png --image-scale 3

# 2x scale for all images
marp --images png deck.md --image-scale 2

# Square thumbnail
marp deck.md -o thumbnail.png --image png --image-scale 1
```

## Watch and Preview Examples

### Development Session

```bash
# Start watch with preview
marp -w -p deck.md

# In another terminal or the markdown file
echo "## New Section" >> deck.md
# Preview window auto-refreshes
```

### Multi-Format Watch

```bash
# Watch and generate multiple formats
marp -w --pdf deck.md &
marp -w --pptx deck.md &
marp -w --images png deck.md &

# Edit deck.md
# All formats regenerate automatically
```

### Preview with Specific Format

```bash
# Preview PDF output
marp -p --pdf deck.md

# Preview PPTX conversion
marp -p --pptx deck.md

# Preview images
marp -p --images png deck.md
```

## Server Mode Examples

### Presentation Server

```bash
# Start server
marp -s ./presentations/

# Client can access:
# http://localhost:8080/
# http://localhost:8080/deck.md
# http://localhost:8080/deck.md?pdf
# http://localhost:8080/deck.md?pptx
# http://localhost:8080/deck.md?images=png
```

### Custom Port

```bash
# Port 3000
PORT=3000 marp -s ./slides

# Port 8080 on specific interface
HOST=0.0.0.0 PORT=8080 marp -s ./slides
```

### Server with Watch

```bash
# Server that auto-updates on file changes
marp -s -w ./presentations

# Development server
marp -s -w -p ./presentations
```

### Default Deck

```bash
# Create index.md as default
cat > ./presentations/index.md << 'EOF'
---
marp: true
---

# Default Presentation
EOF

# Serve directory
marp -s ./presentations

# http://localhost:8080/ automatically shows index.md
```

## Batch Processing

### Convert All Markdown

```bash
# All to HTML
marp *.md

# All to PDF
marp --pdf *.md

# All to PPTX
marp --pptx *.md

# All to PNG
marp --images png *.md
```

### Directory Processing

```bash
# Process entire directory
marp ./presentations/*.md

# With parallelism
marp -P 10 ./presentations/*.md

# Non-parallel (safer for limited resources)
marp --no-parallel ./presentations/*.md
```

### Organized Output

```bash
# Create organized exports
mkdir -p exports/{pdf,pptx,images}

# All formats
marp --pdf deck.md -o exports/pdf/
marp --pptx deck.md -o exports/pptx/
marp --images png deck.md -o exports/images/
```

## Advanced Browser Options

### Browser Selection

```bash
# Use Firefox specifically
marp --browser firefox deck.md -o deck.pdf

# Try Firefox first, fall back to Chrome
marp --browser firefox,chrome deck.md -o deck.pdf

# Edge specifically
marp --browser edge deck.md -o deck.pdf
```

### Custom Browser Path

```bash
# Brave browser
marp --browser-path /usr/bin/brave-browser deck.md -o deck.pdf

# Chromium specific install
marp --browser-path /opt/chromium/chrome deck.md -o deck.pdf

# Firefox Nightly
marp --browser-path /Applications/Firefox\ Nightly.app/Contents/MacOS/firefox deck.md -o deck.png
```

### Browser Timeout

```bash
# Allow 60 seconds for browser operations
marp --browser-timeout 60 deck.md -o deck.pdf

# Quick conversions (may timeout)
marp --browser-timeout 15 deck.md -o deck.png
```

## Theme and Style Examples

### Using Themes

```markdown
---
marp: true
theme: gaia
---

# Gaia Theme

Content styled with Gaia.
```

```bash
marp gaia-theme.md
```

### Custom CSS

```markdown
---
marp: true
theme: default
style: |
  section {
    font-family: 'Arial', sans-serif;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
  }
  h1 {
    color: #fbbf24;
  }
---

# Custom Styled

This slide has custom CSS.
```

### Inline Themes

```bash
# Override theme
marp -t gaia deck.md

# Use specific template
marp --template bespoke deck.md
```

## Automation Examples

### CI/CD Pipeline

```bash
#!/bin/bash
# build-presentations.sh

# Generate all output formats
marp --pdf presentation.md -o dist/presentation.pdf
marp --pptx presentation.md -o dist/presentation.pptx
marp --images png presentation.md -o dist/images/

# Generate social images
marp presentation.md -o og-image.png --image-scale 3
marp presentation.md -o thumb.jpg --image jpeg

echo "Build complete"
```

### Cron Job

```bash
# Generate daily report
0 9 * * * marp --pdf /path/to/daily-report.md -o /output/report-$(date +\%Y\%m\%d).pdf
```

### Git Hook

```bash
#!/bin/bash
# pre-commit hook

# Check if any .md files changed
if git diff --name-only | grep -q '\.md$'; then
    echo "Converting presentations..."
    git diff --name-only | grep '\.md$' | while read file; do
        marp --pdf "$file"
    done
fi
```

## Presenter Notes Workflow

```markdown
---
marp: true
---

# Slide with Notes

Content for audience.

<!-- Note: This is what I tell the audience about this content -->

---

# Next Slide

More content.

<!-- Note: Don't forget to mention the key point here -->
```

```bash
# Export notes
marp --notes presentation.md -o speaker-notes.txt

# PDF with notes
marp --pdf --pdf-notes presentation.md -o with-notes.pdf
```

## Image Optimization Examples

### Social Media

```bash
# Twitter/X (high res square)
marp talk.md -o twitter.png --image --image-scale 3

# LinkedIn (professional)
marp talk.md -o linkedin.png --image --image-scale 2

# Instagram (square)
marp talk.md -o instagram.png --image --image-scale 2
```

### Documentation Images

```bash
# Documentation thumbnails
for file in docs/*.md; do
    name=$(basename "$file" .md)
    marp "$file" -o "docs/images/$name.png" --image --image-scale 2
done
```

### Website Assets

```bash
# Generate hero images
marp --image hero-content.md -o assets/hero.png --image-scale 3
marp --image about-slide.md -o assets/about.jpg --image jpeg --image-scale 3
```

## Multi-Platform Distribution

```bash
#!/bin/bash
# distribute.sh

PRESENTATION="deck.md"

# Generate all formats
marp --pdf "$PRESENTATION" -o dist/deck.pdf
marp --pptx "$PRESENTATION" -o dist/deck.pptx
marp --images png "$PRESENTATION" -o dist/images/

# Create zip
cd dist
zip -r deck.zip *.pdf *.pptx *.png

echo "Ready for distribution!"
```

## Troubleshooting Examples

### Browser Detection Issues

```bash
# Check which browsers are detected
# Try explicit browser selection
marp --pdf deck.md --browser chrome

# If auto fails, specify path
marp --pdf deck.md --browser-path /usr/bin/google-chrome
```

### Timeout Adjustments

```bash
# Increase timeout for large presentations
marp --pdf --browser-timeout 60 large-deck.md

# Decrease for fast, small decks
marp --pdf --browser-timeout 20 small-deck.md
```

### Local File Issues

```bash
# If local images are blocked
marp deck.md -o output.html --allow-local-files

# For PDF conversion
marp --pdf deck.md --allow-local-files
```

### Memory Issues

```bash
# Reduce parallelism
marp --pdf *.md -P 2

# Disable parallelism completely
marp --pdf *.md --no-parallel
```

## Integration Examples

### With Pandoc

```bash
# Convert from other formats to Marp
pandoc presentation.docx -t markdown -o deck.md
marp --pdf deck.md
```

### With Static Site Generators

```bash
# Generate slides from Jekyll posts
marp _posts/*.md -o static/slides/

# Hugo example
marp content/presentations/*.md -o static/presentations/
```

### With Makefiles

```makefile
.PHONY: all pdf pptx images clean

PRESENTATION = deck.md

all: pdf pptx images

pdf:
	marp --pdf $(PRESENTATION) -o dist/deck.pdf

pptx:
	marp --pptx $(PRESENTATION) -o dist/deck.pptx

images:
	marp --images png $(PRESENTATION) -o dist/images/

clean:
	rm -rf dist/
```

## Performance Tips

```bash
# Use parallelism for multiple files
marp --pdf *.md -P 8

# Cache browser instance with watch mode
marp -w --pdf deck.md

# Pre-warm conversion with test run
marp deck.md -o /dev/null
marp --pdf deck.md

# Batch process after edits
# Edit all files first, then convert once
marp --pdf *.md
```

---

**For more examples:**
- [SKILL.md](SKILL.md) - Core CLI usage
- [QUICKSTART.md](QUICKSTART.md) - Quick patterns
- Official docs: https://github.com/marp-team/marp-cli
