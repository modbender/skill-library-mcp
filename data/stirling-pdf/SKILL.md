---
name: stirling-pdf
description: PDF manipulation via Stirling-PDF API. Merge, split, convert, OCR, compress, sign, redact, and more. Self-hosted.
metadata:
  openclaw:
    emoji: 📄
    requires:
      bins: [node, curl]
    env: {
      STIRLING_PDF_URL: "http://localhost:8080",
      STIRLING_API_KEY: "",
    }
---

# Stirling-PDF Skill

Self-hosted PDF manipulation platform with 60+ tools via REST API.

## Configuration

Set these environment variables:
- `STIRLING_PDF_URL` — Your Stirling-PDF instance URL (default: `http://localhost:8080`)
- `STIRLING_API_KEY` — API key if authentication is enabled

## Docs

- **Official docs:** https://docs.stirlingpdf.com
- **Swagger UI:** `<your-instance>/swagger-ui/index.html` on your deployment

## Quick Commands

```bash
# Use the wrapper script
node ~/.openclaw/skills/stirling-pdf/scripts/pdf.js <operation> [options]

# Examples:
node pdf.js merge file1.pdf file2.pdf -o merged.pdf
node pdf.js split input.pdf -o ./output-dir
node pdf.js compress input.pdf -o compressed.pdf
node pdf.js ocr input.pdf -o searchable.pdf
node pdf.js convert-to-pdf document.docx -o output.pdf
node pdf.js pdf-to-word input.pdf -o output.docx
node pdf.js add-watermark input.pdf "DRAFT" -o watermarked.pdf
```

## Available Operations

### Page Operations
- `merge` - Combine multiple PDFs
- `split` - Split PDF into parts
- `rotate` - Rotate pages
- `extract-pages` - Extract specific pages
- `reorder` - Reorganize pages

### Conversion
- `convert-to-pdf` - Word, Excel, Images, HTML → PDF
- `pdf-to-word` - PDF → Word
- `pdf-to-image` - PDF → Images
- `pdf-to-text` - Extract text

### Content
- `compress` - Reduce file size
- `ocr` - Make scanned PDFs searchable
- `add-watermark` - Add text/image watermark
- `add-stamp` - Add stamp
- `redact` - Remove sensitive content
- `sign` - Add signature

### Security
- `add-password` - Password protect
- `remove-password` - Remove password
- `sanitize` - Remove metadata/scripts

## Direct API Usage

For operations not covered by the script, call the API directly:

```bash
curl -X POST "$STIRLING_PDF_URL/api/v1/general/merge-pdfs" \
  -H "X-API-KEY: $STIRLING_API_KEY" \
  -H "Content-Type: multipart/form-data" \
  -F "fileInput=@file1.pdf" \
  -F "fileInput=@file2.pdf" \
  -o merged.pdf
```

Check Swagger UI at `<your-instance>/swagger-ui/index.html` for all endpoints.

## Common Endpoints

| Operation | Endpoint |
|-----------|----------|
| Merge | `/api/v1/general/merge-pdfs` |
| Split | `/api/v1/general/split-pages` |
| Compress | `/api/v1/misc/compress-pdf` |
| OCR | `/api/v1/misc/ocr-pdf` |
| PDF to Image | `/api/v1/convert/pdf/img` |
| Image to PDF | `/api/v1/convert/img/pdf` |
| Add Watermark | `/api/v1/security/add-watermark` |
| Add Password | `/api/v1/security/add-password` |

## Notes

- Most endpoints use POST with multipart/form-data
- File input parameter is usually `fileInput`
- Response is the processed PDF file
- Check Swagger UI for exact parameters per operation
