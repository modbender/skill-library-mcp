---
description: Analyze fonts used in PDF documents.
---
# pdffonts

Analyze fonts used in PDF documents.

## Synopsis

```
pdffonts [options] [PDF-file]
```

## Description

Pdffonts lists the fonts used in a PDF file along with various information for each font. If PDF-file is '-', it reads from stdin.

## When to Use

- To check which fonts are embedded in a PDF
- To verify if all fonts are embedded (important for portability)
- To identify font types (Type 1, TrueType, CID, etc.)
- To detect subset fonts

## Output Information

For each font, shows:
- **name**: Font name (may include subset prefix)
- **type**: Font type (Type 1, Type 1C/CFF, Type 3, TrueType, CID Type 0, CID Type 0C, CID TrueType)
- **encoding**: Font encoding
- **emb**: "yes" if font is embedded
- **sub**: "yes" if it's a subset
- **uni**: "yes" if ToUnicode map exists
- **object ID**: Font dictionary object ID (number and generation)

## Common Options

| Option | Description |
|--------|-------------|
| `-f number` | First page to analyze |
| `-l number` | Last page to analyze |
| `-subst` | List substitute fonts for non-embedded fonts |
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
# Analyze all fonts
pdffonts document.pdf

# Check specific pages
pdffonts -f 1 -l 5 document.pdf

# Show substitute fonts
pdffonts -subst document.pdf
```

