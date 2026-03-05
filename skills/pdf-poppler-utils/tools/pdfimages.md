---
description: Extract images embedded in PDF documents.
---
# pdfimages

Extract images embedded in PDF documents.

## Synopsis

```
pdfimages [options] PDF-file [image-prefix]
```

## Description

Pdfimages extracts images from PDF files. If PDF-file is '-', it reads from stdin. Images are saved as PPM, PBM, or JPEG files.

## When to Use

- To extract all images from a PDF
- To save embedded graphics for reuse
- To extract thumbnails or icons from PDF files

## Common Options

| Option | Description |
|--------|-------------|
| `-f number` | First page to scan |
| `-l number` | Last page to scan |
| `-png` | Change default output format to PNG |
| `-tiff` | Change default output format to TIFF |
| `-j` | Write JPEG format as JPEG files |
| `-jp2` | Write JPEG2000 format as JP2 files |
| `-jbig2` | Write JBIG2 format as JBIG2 files |
| `-ccitt` | Write CCITT format as CCITT files |
| `-all` | Write all image formats in native format |
| `-list` | List images without extracting |
| `-p` | Include page numbers in output file names |
| `-print-filenames` | Print image filenames to stdout |
| `-q` | Don't print any messages or errors |
| `-opw password` | Owner password |
| `-upw password` | User password |
| `-v` | Print version information |
| `-h` | Print help information |

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
# Extract all images as PPM
pdfimages document.pdf extracted_

# Extract as PNG
pdfimages -png document.pdf extracted_

# List images without extracting
pdfimages -list document.pdf

# Extract from specific pages
pdfimages -f 1 -l 10 -png document.pdf page_images_
```
