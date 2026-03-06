---
name: mineru
description: "Parse PDFs, Word docs, PPTs, and images into clean Markdown using MinerU's VLM engine. Use when: (1) Converting PDF/Word/PPT/image to Markdown, (2) Extracting text/tables/formulas from documents, (3) Batch processing multiple files, (4) Saving parsed content to Obsidian or knowledge bases. Supports LaTeX formulas, tables, images, multilingual OCR, and async parallel processing."
homepage: https://mineru.net
metadata:
  openclaw:
    emoji: "📄"
    requires:
      bins: ["python3"]
      env:
        - name: MINERU_TOKEN
          description: "MinerU API key — get free token at https://mineru.net/user-center/api-token (2000 pages/day, 200MB/file)"
    install:
      - id: pip
        kind: pip
        packages: ["requests", "aiohttp"]
        label: "Install Python dependencies (pip)"
---

# MinerU Document Parser

Convert PDF, Word, PPT, and images to clean Markdown using MinerU's VLM engine — LaTeX formulas, tables, and images all preserved.

## Setup

1. Get free API token at https://mineru.net/user-center/api-token

```bash
export MINERU_TOKEN="your-token-here"
```

**Limits:** 2000 pages/day · 200 MB per file · 600 pages per file

## Supported File Types

| Type | Formats |
|------|---------|
| 📕 PDF | `.pdf` — papers, textbooks, scanned docs |
| 📝 Word | `.docx` — reports, manuscripts |
| 📊 PPT | `.pptx` — slides, presentations |
| 🖼️ Image | `.jpg`, `.jpeg`, `.png` — OCR extraction |

## Commands

### Single File

```bash
python3 scripts/mineru_v2.py --file ./document.pdf --output ./output/
```

### Batch Directory with Resume

```bash
python3 scripts/mineru_v2.py \
  --dir ./docs/ \
  --output ./output/ \
  --workers 10 \
  --resume
```

### Direct to Obsidian

```bash
python3 scripts/mineru_v2.py \
  --dir ./pdfs/ \
  --output "~/Library/Mobile Documents/com~apple~CloudDocs/Obsidian/VaultName/" \
  --resume
```

### Chinese Documents

```bash
python3 scripts/mineru_v2.py --dir ./papers/ --output ./output/ --language ch
```

### Complex Layouts (Slow but Most Accurate)

```bash
python3 scripts/mineru_v2.py --file ./paper.pdf --output ./output/ --model vlm
```

## CLI Options

```
--dir PATH          Input directory (PDF/Word/PPT/images)
--file PATH         Single file
--output PATH       Output directory (default: ./output/)
--workers N         Concurrent workers (default: 5, max: 15)
--resume            Skip already processed files
--model MODEL       Model version: pipeline | vlm | MinerU-HTML (default: vlm)
--language LANG     Document language: auto | en | ch (default: auto)
--no-formula        Disable formula recognition
--no-table          Disable table extraction
--token TOKEN       API token (overrides MINERU_TOKEN env var)
```

## Model Version Guide

| Model | Speed | Accuracy | Best For |
|-------|-------|----------|----------|
| `pipeline` | ⚡ Fast | High | Standard docs, most use cases |
| `vlm` | 🐢 Slow | Highest | Complex layouts, multi-column, mixed text+figures |
| `MinerU-HTML` | ⚡ Fast | High | Web-style output, HTML-ready content |

## Script Selection

| Script | Use When |
|--------|----------|
| `mineru_v2.py` | Default — async parallel (up to 15 workers) |
| `mineru_async.py` | Fast network, need maximum throughput |
| `mineru_stable.py` | Unstable network — sequential, max retry |

## Output Structure

```
output/
├── document-name/
│   ├── document-name.md    # Main Markdown
│   ├── images/             # Extracted images
│   └── content.json        # Metadata
```

## Performance

| Workers | Speed |
|---------|-------|
| 1 (sequential) | 1.2 files/min |
| 5 | 3.1 files/min |
| 15 | 5.6 files/min |

## Error Handling

- 5x auto-retry with exponential backoff
- Use `--resume` to continue interrupted batches
- Failed files listed at end of run

## API Reference

For detailed API documentation, see [references/api_reference.md](references/api_reference.md).
