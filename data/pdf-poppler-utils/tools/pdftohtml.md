---
description: Convert PDF documents to HTML format.
---
# pdftohtml

Convert PDF documents to HTML format.

## Synopsis

```
pdftohtml [options] <PDF-file> [<HTML-file> <XML-file>]
```

## Description

Pdftohtml converts PDF files to HTML format for viewing in web browsers.

## When to Use

- To view PDF in a web browser
- To make PDF content searchable on the web
- To extract layout and formatting to HTML

## Common Options

| Option | Description |
|--------|-------------|
| `-stdout` | Output to stdout |
| `-noframes` | Generate single HTML file (no frames). Not supported in complex output mode. |
| `-c` | Generate complex output |
| `-s` | Generate single HTML that includes all pages |
| `-q` | Do not print any messages or errors |
| `-p` | Exchange .pdf links with .html |
| `-dataurls` | Use data URLs instead of external images |
| `-i` | Ignore images |
| `-xml` | Output for XML post-processing |
| `-noroundcoord` | Do not round coordinates (with XML output only) |
| `-enc encoding` | Output text encoding name (default: UTF-8) |
| `-fmt` | Image file format for Splash output (png or jpg) |
| `-nomerge` | Do not merge paragraphs |
| `-nodrm` | Override document DRM settings |
| `-hidden` | Force hidden text extraction |
| `-wbt percent` | Word break threshold (default: 10) |
| `-fontfullname` | Output font name without substitutions |
| `-zoom number` | Zoom PDF document (default: 1.5, 1 = 72 DPI) |
| `-wbt` | Adjust word break threshold percent (default: 10) |
| `-fontfullname` | Output font name without substitutions |
| `-hidden` | Extract hidden text |
| `-zoom number` | Zoom factor (default: 1.5). -zoom 1 = 72 DPI |
| `-f number` | First page to convert |
| `-l number` | Last page to convert |
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
# Basic conversion
pdftohtml document.pdf output.html

# No frames (single file)
pdftohtml -noframes document.pdf output.html

# Extract hidden text
pdftohtml -hidden document.pdf output.html

# Complex output
pdftohtml -c document.pdf output.html

# XML output for processing
pdftohtml -xml document.pdf output.html
```
