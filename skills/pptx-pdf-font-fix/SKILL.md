---
name: pptx-pdf-font-fix
description: Fix PowerPoint font embedding issues in PDF export by patching text transparency in PPTX files. Use when a user has a PPTX file where exported PDFs show wrong/default fonts instead of the intended downloaded/custom fonts, even with font embedding enabled. Works by applying minimal (1%) transparency to fully-opaque text runs, which forces PowerPoint to properly embed fonts during PDF export.
---

# PPT Font Fix

## Problem

PowerPoint's "Export to PDF" can fail to embed downloaded/custom fonts, substituting built-in defaults, even when:
- Fonts are properly installed and embeddable
- "Embed fonts in the file" is checked in PowerPoint options

## Workaround

Applying a tiny transparency (1%) to text with 0% transparency forces PowerPoint to correctly embed fonts in PDF output. This is visually imperceptible but changes how PowerPoint processes the font during export.

## Usage

```bash
python3 scripts/fix_font_transparency.py input.pptx [output.pptx] [--transparency 1]
```

### Options

- `output` -- Output PPTX path (default: `input_fixed.pptx`)
- `--transparency, -t` -- Transparency % to apply (default: 1)

## Behavior

- Only patches text runs that are fully opaque (0% transparency)
- Leaves text that already has any transparency untouched
- Safe to run multiple times
- Only modifies slide XML (`ppt/slides/slideN.xml`), not layouts/masters

## Workflow

1. Receive PPTX file from user
2. Run the fix script: `python3 scripts/fix_font_transparency.py input.pptx`
3. Return the patched PPTX to the user
4. User opens patched file in PowerPoint and exports to PDF -- fonts now embed correctly

## Note

PDF export must be done from PowerPoint desktop. Server-side converters (LibreOffice, Graph API) do not reproduce the same font embedding behavior.
