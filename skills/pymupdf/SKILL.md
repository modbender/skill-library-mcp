---
name: pymupdf
description: Render PDF pages to images, extract embedded images, annotate PDFs, and perform advanced PDF inspection using pymupdf (fitz). Use for tasks such as exporting pages as PNG/JPG, extracting images embedded in a PDF, drawing annotations, redacting content, or when high-fidelity rendering is required. For text extraction, splitting, merging, or rotating PDFs, use the pypdf skill instead.
metadata:
  openclaw:
    requires:
      bins:
        - python3
---

# pymupdf

Use `scripts/pymupdf_cli.py` for deterministic pymupdf operations instead of ad-hoc fitz snippets.

## Workflow

1. Confirm the PDF file path is accessible locally.
2. Run the desired command (export-images, extract-images, info).
3. Inspect the output directory or stdout.

## Command Guide

- Export pages as images:
  - `python scripts/pymupdf_cli.py export-images --input <file.pdf> --output-dir <dir/>`
  - Override format: `--format png` (default), `jpg`, or `ppm`.
  - Override resolution: `--dpi 300` (default: 150).
  - Restrict to specific pages: `--pages 0 1 2`.
- Extract images embedded inside a PDF:
  - `python scripts/pymupdf_cli.py extract-images --input <file.pdf> --output-dir <dir/>`
  - Optionally restrict to specific pages: `--pages 0 1 2`.
- Inspect page dimensions and basic document info:
  - `python scripts/pymupdf_cli.py info --input <file.pdf>`

## Operational Rules

- Pages are always 0-indexed in all commands.
- `export-images` renders each page as a raster image at the specified DPI.
- `extract-images` saves raw image streams embedded in the PDF (e.g. photos, logos); output filenames include page index and image index.
- Install dependency if missing: `pip install pymupdf`.
- For text extraction, splitting, merging, or rotating PDFs, use the pypdf skill instead.
