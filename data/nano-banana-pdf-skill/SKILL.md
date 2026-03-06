---
name: nano-pdf-edit
description: Edit PDF files visually using natural language with the nano-pdf CLI tool, powered by Google's Gemini 3 Pro Image (Nano Banana). Use this skill whenever the user wants to edit, modify, or update PDF slides or pages using AI — including fixing typos, updating charts/graphs, changing colors or branding, adding new slides, modifying text, or making any visual change to a PDF deck or report. Also trigger when the user mentions "nano-pdf", "nano pdf", "edit my pdf", "update my slides", "fix my deck", or wants AI-powered changes to PDF content. Even if the user just says "change the title on page 3" or "fix the typo on slide 5" for a PDF file, this skill applies. Do NOT use for extracting text, merging/splitting PDFs, filling forms, or other non-visual PDF operations.
version: 1.0.1
metadata:
   openclaw:
      requires:
         env:
            - GEMINI_API_KEY
         bins:
            - python3
      primaryEnv: GEMINI_API_KEY
      emoji: "📄"
      homepage: https://github.com/ps06756/nano-banana-pdf-skill
---

# Nano PDF Editing Skill

Edit PDF files with natural language prompts using the **nano-pdf** CLI tool.

Nano-PDF converts PDF pages to images, sends them to Google's Gemini 3 Pro Image with your edit instructions, then stitches the AI-edited pages back into the PDF — preserving searchable text via OCR re-hydration.

**Source**: https://github.com/gavrielc/Nano-PDF

## Prerequisites

Before running any nano-pdf command, ensure the following dependencies are installed. If any are missing, install them before proceeding:

1. **nano-pdf** — `pip install nano-pdf` (or use `uvx nano-pdf` to run without installing)
2. **poppler** — PDF-to-image rendering (`brew install poppler` on macOS / `sudo apt-get install poppler-utils` on Linux)
3. **tesseract** — OCR for text layer restoration (`brew install tesseract` on macOS / `sudo apt-get install tesseract-ocr` on Linux)
4. **GEMINI_API_KEY** — A **paid** Google Gemini API key (free tier does not support image generation). Get one at https://aistudio.google.com/api-keys — then `export GEMINI_API_KEY="your_key"`

## Two Commands

### `nano-pdf edit` — Modify existing pages

```bash
nano-pdf edit <file.pdf> <page> "<prompt>" [<page> "<prompt>" ...] [options]
```

Pages are 1-indexed. Multiple page+prompt pairs can be provided and are processed in parallel.

### `nano-pdf add` — Insert new AI-generated slides

```bash
nano-pdf add <file.pdf> <position> "<prompt>" [options]
```

Position 0 inserts at the beginning. The new slide automatically matches the visual style of the existing deck. Document context is enabled by default for `add`.

## Options Reference

For full details on all available flags, read `references/options.md` in this skill directory.

Key flags:
- `--output "new.pdf"` — Output filename (default: `edited_<original>.pdf`)
- `--resolution "4K"` — `4K` (default), `2K`, or `1K`
- `--style-refs "1,5"` — Pages to use as style references
- `--use-context` / `--no-use-context` — Include full PDF text as model context
- `--disable-google-search` — Prevent model from using Google Search

## Workflow

When a user asks to edit a PDF:

1. **Check dependencies** — Ensure nano-pdf, poppler, tesseract, and GEMINI_API_KEY are available. If any are missing, tell the user what to install and stop.
2. **Identify the edit** — Determine which page(s) need changes and what the prompt should be
3. **Choose the right command** — `edit` for modifying existing pages, `add` for inserting new ones
4. **Pick appropriate options**:
   - Use `--style-refs` if the user wants a specific visual style from certain pages
   - Use `--use-context` when editing multiple pages that need to be consistent
   - Use `--resolution "2K"` if speed matters more than quality
5. **Run nano-pdf** and present the output PDF to the user

## Prompt Writing Tips

The quality of the edit depends heavily on the prompt. Follow these guidelines:

- **Be specific**: "Change the title from 'Overview' to 'Q3 Summary'" beats "update the title"
- **Reference visible elements**: "The bar chart on the left side" helps the model locate what to change
- **One focused change per prompt**: For complex edits, use multiple page+prompt pairs
- **Mention what to preserve**: "Keep the layout the same but change the header color to blue"
- **Use style refs for consistency**: When updating branding across pages, point at a reference page

## Examples

For a comprehensive set of examples covering common use cases (typos, charts, branding, adding slides, batch edits), read `references/examples.md` in this skill directory.

Quick reference:

```bash
# Fix a typo on page 3
nano-pdf edit report.pdf 3 "Fix 'recieve' to 'receive'"

# Update chart data
nano-pdf edit deck.pdf 12 "Update the revenue chart to show Q3 at $2.5M"

# Multi-page branding update
nano-pdf edit slides.pdf \
  1 "Change header background to dark blue, text to white" \
  2 "Update the logo to show 'NewCorp' instead of 'OldCorp'" \
  --style-refs "1" --output branded.pdf

# Add a new title slide at the beginning
nano-pdf add deck.pdf 0 "Title slide: 'Annual Review 2025' with subtitle 'Building the Future'"

# Add a summary slide after page 5 using document context
nano-pdf add deck.pdf 5 "Summary slide with key takeaways as bullet points"
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| `Missing system dependencies` | Install missing deps (see Prerequisites above), restart terminal |
| `GEMINI_API_KEY not found` | `export GEMINI_API_KEY="your_key"` |
| `PAID API key required` | Enable billing at https://aistudio.google.com/api-keys |
| Style mismatch | Use `--style-refs "1,3"` pointing at pages with desired style |
| Slow processing | Use `--resolution "2K"` or `"1K"` |
| Bad OCR / text layer | Use `--resolution "4K"` for better OCR accuracy |
| Model ignores part of prompt | Break into smaller, focused edits across multiple runs |
