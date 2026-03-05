---
description: Extract detailed information and metadata from PDF documents.
---
# pdfinfo

Extract detailed information and metadata from PDF documents.

## Synopsis

```
pdfinfo [options] [PDF-file]
```

## Description

Pdfinfo prints the contents of the Info dictionary (plus useful information) from a PDF file. If PDF-file is '-', it reads from stdin.

## When to Use

- When you need to know PDF metadata (title, author, creation date, etc.)
- To check if a PDF is encrypted or has permissions
- To get page count, file size, PDF version
- To check for JavaScript, forms, or embedded metadata

## Common Options

| Option | Description |
|--------|-------------|
| `-f number` | First page to examine |
| `-l number` | Last page to examine |
| `-box` | Print page box bounding boxes |
| `-meta` | Print document-level metadata |
| `-custom` | Print custom and standard metadata |
| `-js` | Print all JavaScript in the PDF |
| `-struct` | Print document structure (Tagged PDF) |
| `-struct-text` | Print textual content with document structure |
| `-url` | Print all URLs in the PDF |
| `-dests` | Print all named destinations |
| `-isodates` | Print dates in ISO-8601 format |
| `-rawdates` | Print raw (undecoded) date strings |
| `-listenc` | List available encodings |
| `-enc encoding` | Set output encoding (default: UTF-8) |
| `-opw password` | Owner password (bypasses security) |
| `-upw password` | User password |
| `-v` | Print version information |
| `-h` | Print help information |

## Output Includes

- Title, author, subject, keywords
- Creator, producer
- Creation/modification dates
- Page count, page size
- File size, PDF version
- Encryption status, permissions
- Form type (AcroForm/XFA/none)
- JavaScript presence
- Custom metadata, metadata stream
- Tagged PDF status, userproperties, suspects
- Linearized status

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
# Basic info
pdfinfo document.pdf

# Get metadata only
pdfinfo -meta document.pdf

# Check specific page range
pdfinfo -f 1 -l 5 document.pdf

# List named destinations
pdfinfo -dests document.pdf

# Read from stdin
pdfinfo - < document.pdf
```
