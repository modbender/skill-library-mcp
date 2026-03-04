---
description: Merge multiple PDF files into a single PDF.
---
# pdfunite

Merge multiple PDF files into a single PDF.

## Synopsis

```
pdfunite [options] PDF-sourcefile1..PDF-sourcefilen PDF-destfile
```

## Description

Pdfunite merges several PDF files in order of their occurrence on command line to one PDF result file.

## Important Notes

- **None of the source PDFs should be encrypted.**

## When to Use

- To combine multiple PDFs into one
- To merge scanned pages into a single document
- To concatenate PDF chapters or sections

## Options

| Option | Description |
|--------|-------------|
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
# Merge three PDFs
pdfunite chapter1.pdf chapter2.pdf chapter3.pdf combined.pdf

# Merge all PDFs in current directory
pdfunite *.pdf merged.pdf

# Merge with specific order
pdfunite intro.pdf main.pdf appendix.pdf full_document.pdf
```
