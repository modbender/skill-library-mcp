---
name: md-table-image
description: Render markdown tables as PNG images. Use whenever you need to send a table in chat — render it as an image instead of raw markdown text.
metadata: {"clawdbot":{"emoji":"📊","requires":{"bins":["node"]}}}
---

# MD Table Image

Renders markdown (especially tables) into a styled PNG image.

## Usage

```bash
node {baseDir}/scripts/render.mjs "markdown content" -o /path/to/output.png
```

Or pipe markdown in:

```bash
echo "| A | B |\n|---|---|\n| 1 | 2 |" | node {baseDir}/scripts/render.mjs -o /path/to/output.png
```

## Options

- `-o <path>`: Output PNG path (default: `/tmp/table.png`)
- `--title <text>`: Optional title above the table
- `--width <px>`: Viewport width (default: 800)
- `--dark`: Dark theme

## When to Use

**Always** use this skill when sending tables to chat. Render the table as an image and send the image instead of raw markdown.
