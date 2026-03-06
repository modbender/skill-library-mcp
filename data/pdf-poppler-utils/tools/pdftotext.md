---
description: Convert PDF documents to plain text.
---
# pdftotext

Convert PDF documents to plain text.

## Synopsis

```
pdftotext [options] PDF-file [text-file]
```

## Description

Pdftotext converts PDF files to plain text. If text-file is not specified, converts file.pdf to file.txt. If text-file is '-', outputs to stdout. If PDF-file is '-', reads from stdin.

## When to Use

- To extract readable text from a PDF
- To process PDF content for analysis or NLP
- To create text versions of documents for accessibility

## Common Options

| Option | Description |
|--------|-------------|
| `-f number` | First page to convert |
| `-l number` | Last page to convert |
| `-r number` | Resolution in DPI (default: 72) |
| `-x number` | x-coordinate of crop area top-left corner |
| `-y number` | y-coordinate of crop area top-left corner |
| `-W number` | Width of crop area in pixels (default: 0) |
| `-H number` | Height of crop area in pixels (default: 0) |
| `-layout` | Maintain original physical layout |
| `-raw` | Keep text in content stream order |
| `-fixed number` | Fixed-pitch/tabular text with specified character width |
| `-nodiag` | Discard diagonal text (useful for watermarks) |
| `-htmlmeta` | Generate simple HTML with meta info |
| `-bbox` | Generate XHTML with bounding boxes |
| `-bbox-layout` | Bounding boxes for blocks, lines, words |
| `-tsv` | TSV format with bounding box info |
| `-cropbox` | Use crop box instead of media box |
| `-colspacing number` | Spacing after word as fraction of font size (default: 0.7) |
| `-nopgbrk` | Don't insert page breaks between pages |
| `-enc encoding` | Output encoding (default: UTF-8) |
| `-listenc` | List available encodings |
| `-eol unix\|dos\|mac` | End-of-line convention |
| `-opw password` | Owner password |
| `-upw password` | User password |
| `-q` | Quiet mode - don't print messages |
| `-v` | Print version information |

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
# Basic conversion
pdftotext document.pdf output.txt

# Use stdout
pdftotext document.pdf - | less

# Maintain layout
pdftotext -layout document.pdf output.txt

# Convert specific pages
pdftotext -f 1 -l 5 document.pdf output.txt

# Generate HTML with metadata
pdftotext -htmlmeta document.pdf output.html
```
