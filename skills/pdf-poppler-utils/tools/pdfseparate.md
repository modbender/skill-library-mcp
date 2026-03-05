---
description: Split a multi-page PDF into individual page files.
---
# pdfseparate

Split a multi-page PDF into individual page files.

## Synopsis

```
pdfseparate [options] PDF-file PDF-page-pattern
```

## Description

Pdfseparate extracts pages from a PDF file into separate PDF files.

## When to Use

- To extract specific pages from a PDF
- To split a PDF into individual pages
- To create single-page PDFs from a multi-page document

## Important Notes

- The PDF file must not be encrypted.

## Page Pattern

The page pattern should contain `%d` (printf-style) which will be replaced with the page number.

Examples:
- `page_%03d.pdf` → page_001.pdf, page_002.pdf, etc.
- `page_%d.pdf` → page_1.pdf, page_2.pdf, etc.

## Options

| Option | Description |
|--------|-------------|
| `-f number` | First page to extract (default: 1) |
| `-l number` | Last page to extract (default: last page) |
| `-v` | Print copyright and version information |
| `-h`, `--help` | Print usage information |

## Exit Codes

| Code | Description |
|------|-------------|
| 0 | No error |
| 1 | Error opening PDF file |
| 2 | Error opening output file |
| 3 | PDF permissions error |
| 99 | Other error |

## Examples

```bash
# Split into individual pages
pdfseparate document.pdf page_%03d.pdf

# Extract specific range (pages 1-5)
pdfseparate -f 1 -l 5 document.pdf first_five_%03d.pdf
```

- pdfinfo - PDF information
- pdftotext - Extract text from PDF
