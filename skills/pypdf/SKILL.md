---
name: pypdf
description: Extract text, metadata, and pages from PDF files using pypdf. Use for tasks such as reading PDF content, extracting specific pages, splitting or merging PDFs, reading document metadata, and rotating or transforming pages.
metadata:
  openclaw:
    requires:
      bins:
        - python3
---

# pypdf

Use `scripts/pypdf_cli.py` for deterministic PDF operations instead of ad-hoc pypdf snippets.

## Workflow

1. Confirm the PDF file path is accessible locally.
2. Run the desired command (inspect, extract-text, extract-pages, merge, split, rotate).
3. Inspect text output or the resulting PDF file.

## Command Guide

- Inspect metadata and page count:
  - `python scripts/pypdf_cli.py info --input <file.pdf>`
- Extract all text:
  - `python scripts/pypdf_cli.py extract-text --input <file.pdf>`
- Extract text from specific pages (0-indexed):
  - `python scripts/pypdf_cli.py extract-text --input <file.pdf> --pages 0 1 2`
- Split PDF into individual pages:
  - `python scripts/pypdf_cli.py split --input <file.pdf> --output-dir <dir/>`
- Extract a page range into a new PDF:
  - `python scripts/pypdf_cli.py extract-pages --input <file.pdf> --pages 0 1 2 --output <out.pdf>`
- Merge multiple PDFs:
  - `python scripts/pypdf_cli.py merge --inputs <a.pdf> <b.pdf> <c.pdf> --output <merged.pdf>`
- Rotate pages:
  - `python scripts/pypdf_cli.py rotate --input <file.pdf> --angle 90 --output <rotated.pdf>`
  - `--angle` must be 90, 180, or 270.
  - Optionally restrict to specific pages with `--pages 0 2`.

## Operational Rules

- Pages are always 0-indexed in all commands.
- For `extract-text`, output goes to stdout; redirect to a file when needed.
- Require explicit `--output` for commands that write a new PDF.
- Install dependency if missing: `pip install pypdf`.
