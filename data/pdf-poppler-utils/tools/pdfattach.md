---
description: Attach files to a PDF document.
---
# pdfattach

Attach files to a PDF document.

## Synopsis

```
pdfattach [options] PDF-file attachment-file [output-pdf]
```

## Description

Pdfattach embeds files into a PDF document as attachments.

## When to Use

- To embed files in a PDF
- To attach supporting documents to a PDF
- To bundle related files together

## Common Options

| Option | Description |
|--------|-------------|
| `-replace` | Replace embedded file with same name (if it exists) |
| `-embed` | Embed the file (default) |
| `-noembed` | Don't embed, just reference |
| `-name name` | Set attachment name in PDF |
| `-description desc` | Set attachment description |
| `-mime mime` | Set MIME type (auto-detected if not specified) |
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
# Attach a file
pdfattach document.pdf spreadsheet.xlsx output.pdf

# Attach with custom name
pdfattach -name "Supporting Data" document.pdf data.csv output.pdf

# Attach with description
pdfattach -description "Source code" document.pdf source.zip output.pdf

# Attach with MIME type
pdfattach -mime application/json document.pdf config.json output.pdf
```
