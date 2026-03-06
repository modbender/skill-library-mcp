---
name: markdown-canvas
description: Convert markdown files to beautiful HTML pages suitable for Canvas display or browser viewing. Use when user asks to render, visualize, display, or share markdown files (.md) in a visual format. Triggers include phrases like "render xxx.md", "canvas display xxx.md", "visualize markdown", "make xxx.md pretty", "share xxx.md as HTML".
homepage: https://github.com/jingyu525/markdown-canvas
metadata: { "openclaw": { "emoji": "📝", "requires": { "bins": ["python3"] } } }
---

# Markdown Canvas Renderer

Convert markdown files into beautiful, shareable HTML pages with zero external dependencies.

## Quick Start

When a user wants to render a markdown file:

1. **Run the conversion script**:
   ```bash
   python3 scripts/convert.py <path/to/file.md>
   ```

2. **Open in browser** (if no Canvas node available):
   ```bash
   open <output.html>
   ```

3. **Or push to Canvas** (if node paired):
   ```bash
   canvas present file://<output.html>
   ```

## Usage Examples

### Basic conversion
```bash
# Converts ai-landscape-2026.md → ai-landscape-2026.html
python3 scripts/convert.py ai-landscape-2026.md
```

### Custom output path
```bash
python3 scripts/convert.py input.md -o /path/to/output.html
```

### Custom page title
```bash
python3 scripts/convert.py notes.md -t "My Research Notes"
```

## Supported Markdown Features

The converter handles:
- **Headers** (# through ######)
- **Bold** (`**text**` or `__text__`)
- **Italic** (`*text*` or `_text_`)
- **Code blocks** (```language ... ```)
- **Inline code** (`code`)
- **Links** (`[text](url)`)
- **Lists** (unordered: `- `, `* `, `+ `)
- **Horizontal rules** (`---`, `***`, `___`)

## Design Philosophy

**Token efficiency**: Template is pre-built; only markdown content flows through the context window.

**Zero dependencies**: Pure Python + self-contained HTML template with embedded CSS.

**Progressive enhancement**: Works offline, no CDN required, renders instantly.

## Workflow

1. User requests markdown rendering
2. Run `scripts/convert.py` on their file
3. Script reads `assets/template.html`
4. Script converts markdown → HTML
5. Script injects HTML into template
6. Output saved alongside source (or custom path)
7. Open in browser OR push to Canvas

## Token Cost Analysis

Per conversion:
- Read SKILL.md: ~500 tokens (first time only)
- Execute script: ~100 tokens
- Report result: ~50 tokens

**Total: ~650 tokens** vs ~8000 tokens for generating full HTML each time.

## Output Location

By default, output is saved next to the input file:
- `notes.md` → `notes.html`
- `/path/to/doc.md` → `/path/to/doc.html`

Use `-o` flag to specify custom location.
