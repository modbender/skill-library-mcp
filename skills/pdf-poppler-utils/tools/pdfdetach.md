---
description: Extract attachments from PDF documents.
---
# pdfdetach

Extract attachments from PDF documents.

## Synopsis

```
pdfdetach [options] [PDF-file]
```

## Description

Pdfdetach lists or extracts embedded files from PDF documents.

## When to Use

- To list all embedded file attachments
- To extract embedded files from a PDF
- To check if a PDF has hidden attachments

## Common Options

| Option | Description |
|--------|-------------|
| `-list` | List all embedded files (with details) |
| `-save number` | Save embedded file by index number |
| `-savefile filename` | Save embedded file by exact filename |
| `-saveall` | Extract all embedded files |
| `-o path` | Output file (for -save) or directory (for -saveall) |
| `-enc encoding-name` | Text encoding for output (default: UTF-8) |
| `-opw password` | Owner password (bypasses all security) |
| `-upw password` | User password |
| `-v` | Print version information |
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
# List all attachments
pdfdetach -list document.pdf

# Extract all attachments to ./output/
pdfdetach -saveall -o output/ document.pdf

# Extract specific file by index
pdfdetach -save 1 document.pdf

# Extract file by filename
pdfdetach -savefile myattachment.pdf document.pdf

# Extract with password
pdfdetach -saveall -opw myownerpass document.pdf
```
