---
name: md-to-pdf
description: Use this skill to convert Markdown to PDF with consistent styles.
---

# md-to-pdf

**version:** 1.0.0  
**author:** 大总管  
**description:** Convert Markdown (.md) files to styled PDF documents with pandoc + wkhtmltopdf

Use this skill to convert Markdown to PDF with consistent styles.

## Quick Start

1. Ensure dependencies exist:

```bash
pandoc --version
wkhtmltopdf --version
```

2. Run conversion:

```bash
bash {baseDir}/scripts/md2pdf.sh /abs/path/doc.md
```

## Style Options

Use built-in styles:

- `clean` (default): simple business style
- `modern`: blue, presentation-friendly
- `paper`: serif, reading-friendly

Examples:

```bash
bash {baseDir}/scripts/md2pdf.sh /abs/path/doc.md --style clean
bash {baseDir}/scripts/md2pdf.sh /abs/path/doc.md /abs/path/out.pdf --style modern
bash {baseDir}/scripts/md2pdf.sh /abs/path/doc.md --style paper
```

## Custom CSS

Pass an absolute CSS path:

```bash
bash {baseDir}/scripts/md2pdf.sh /abs/path/doc.md /abs/path/doc.pdf --style /abs/path/custom.css
```

## Notes

- Script enables local CSS loading via `--enable-local-file-access`.
- If output title warning appears, set Markdown metadata `title:`.
- For detailed usage and troubleshooting, read `{baseDir}/references/usage.md`.
