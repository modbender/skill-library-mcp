---
name: fashion-colorize-shell
description: Convert apparel sketches into ecommerce-ready colorized shell-jacket renders. Use when users provide garment line art and ask for realistic colorized outputs (especially womens outdoor shell/hardshell), structure-preserving edits, or iterative visual refinements.
---

# Fashion Colorize Shell

## Overview

Generate "line sketch -> realistic product render" outputs for outdoor shell jackets.
This skill keeps sketch structure while applying a product-shot style (single garment, front view, white background, realistic hardshell material).

## Workflow

1. Collect inputs:
   - Required: sketch image path
   - Required: brief text (material, color, fit, key design intent)
   - Optional: style reference image path
2. Run the local script:
   - `uv run {baseDir}/scripts/run_colorize.py --sketch "<path>" --brief "<text>" --output-dir "<dir>" [--style-ref "<path>"] [--count 3]`
3. Return generated file paths.
4. For revisions, keep previous output as style input and add explicit changes in `--brief`.

## Input Guidance

- Good brief example:
  - `三层压胶硬壳材质，凯乐石薄荷绿，女性剪裁，强调胸前斜插袋和袖口调节。`
- If the user wants "technical flats", do not use this skill's default product-shot look. Ask whether they want a separate technical drawing workflow.

## Output Rules

- Default output is ecommerce-like product render:
  - Single garment
  - Front view
  - White background
  - No model, no scene, no text overlays
- Preserve key lines from sketch:
  - Hood shape
  - Center-front zipper/placket logic
  - Pocket placement direction
  - Cuff and hem adjustment zones

## Fixed Runtime Defaults

- API base URL: `https://models.kapon.cloud`
- Model preference: `gemini-3-pro-image-preview-2k` (auto-fallback to `gemini-3-pro-image-preview` if upstream fails)
- API key is never embedded in this skill. User must provide `GEMINI_API_KEY` in environment.

## Additional Reference

- See [references/prompt-structure.md](references/prompt-structure.md) for the internal prompt skeleton and revision strategy.

