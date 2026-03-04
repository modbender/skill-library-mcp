---
name: docling
description: Extract and parse content from web pages, PDFs, documents (docx, pptx), and images using the docling CLI with GPU acceleration. Use INSTEAD of web_fetch for extracting content from specific URLs when you need clean, structured text. Use Brave (web_search) for searching/discovering pages. Use docling when you HAVE a URL and need its content parsed.
version: 1.0.2
metadata:
  requires:
    bins: ["docling"]
---

# Docling - Document & Web Content Extraction

CLI tool for parsing documents and web pages into clean, structured text. Uses GPU acceleration for OCR and ML models.

## Prerequisites

- `docling` CLI must be installed (e.g., via `pipx install docling`)
- For GPU support: NVIDIA GPU with CUDA drivers

## When to Use

- **Extract content from a URL** → Use docling (not web_fetch)
- **Search for information** → Use web_search (Brave)
- **Parse PDFs, DOCX, PPTX** → Use docling
- **OCR on images** → Use docling

## Quick Commands

### Web Page → Markdown (default)
```bash
docling "<URL>" --from html --to md
```
Output: creates a `.md` file in current directory (or use `--output`)

### Web Page → Plain Text
```bash
docling "<URL>" --from html --to text --output /tmp/docling_out
```

### PDF with OCR
```bash
docling "/path/to/file.pdf" --ocr --device cuda --output /tmp/docling_out
```

## Key Options

| Option | Values | Description |
|--------|--------|-------------|
| `--from` | html, pdf, docx, pptx, image, md, csv, xlsx | Input format |
| `--to` | md, text, json, yaml, html | Output format |
| `--device` | auto, cuda, cpu | Accelerator (default: auto) |
| `--output` | path | Output directory (recommended: use controlled temp dir) |
| `--ocr` | flag | Enable OCR for images/scanned PDFs |
| `--tables` | flag | Extract tables (default: on) |

## Security Notes

⚠️ **Avoid these flags unless you trust the source:**
- `--enable-remote-services` - can send data to remote endpoints
- `--allow-external-plugins` - loads third-party code
- Custom `--headers` with untrusted values - can redirect requests

## Workflow

1. **For web content extraction**: Use `docling "<URL>" --from html --to text --output /tmp/docling_out`
2. **Read the output file** from the specified output directory
3. **Clean up** the output directory after reading

## GPU Support

Docling supports GPU acceleration via CUDA (NVIDIA). Verify CUDA is available:
```bash
python -c "import torch; print(torch.cuda.is_available())"
```

## Full CLI Reference

See [references/cli-reference.md](references/cli-reference.md) for complete option list.
