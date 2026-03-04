---
name: md2pdf
description: Convert Markdown files to PDF with full LaTeX math formula rendering and CJK (Chinese/Japanese/Korean) support. Use when the user asks to convert markdown to PDF, render a report as PDF, export notes to PDF, or generate a printable document from markdown. Handles $...$ inline and $$...$$ display math, code blocks, tables, and mixed CJK/Latin text. Requires pandoc + texlive-xetex.
---

# md2pdf

Convert Markdown → PDF via Pandoc + XeLaTeX. Full LaTeX math + CJK support.

## Prerequisites

System packages (apt):

```
pandoc texlive-xetex texlive-fonts-recommended texlive-fonts-extra texlive-latex-extra texlive-lang-chinese
```

## Quick Convert

```bash
bash <skill_dir>/scripts/md2pdf.sh input.md output.pdf
```

The script auto-detects CJK content, picks suitable fonts, sanitizes emoji, adds TOC, and configures XeLaTeX.

## Manual Pandoc Command

For fine-grained control, run pandoc directly:

```bash
pandoc input.md -o output.pdf \
  --pdf-engine=xelatex \
  -f markdown-smart \
  -H header.tex \
  -V mainfont="DejaVu Sans" \
  -V monofont="DejaVu Sans Mono" \
  -V geometry:margin=20mm \
  -V fontsize=10pt \
  -V colorlinks=true \
  --highlight-style=tango \
  --toc -V toc-title="Table of Contents"
```

Where `header.tex` contains:

```latex
\usepackage{xeCJK}
\setCJKmainfont{<CJK font name>}
```

## Key Details

- **Math**: Pandoc natively converts `$...$` (inline) and `$$...$$` (display) to LaTeX math. No MathJax/KaTeX needed.
- **CJK fonts**: Script auto-detects from: Noto Sans CJK SC > WenQuanYi Micro Hei > Droid Sans Fallback > AR PL UMing CN.
- **Emoji**: Replaced with text equivalents (`✅` → `[Y]`, `❌` → `[N]`, `⭐` → `*`) since most LaTeX fonts lack emoji glyphs.
- **Smart quotes**: Use `-f markdown-smart` to avoid curly quote rendering issues.
- **Long tables**: Pandoc may struggle with complex tables; keep tables simple or use `longtable` LaTeX package.

## Troubleshooting

| Problem | Fix |
|---------|-----|
| Missing character warnings | Check `fc-list :lang=zh` for available CJK fonts; install `fonts-noto-cjk` if needed |
| `xelatex not found` | Install `texlive-xetex` |
| PDF has no math rendering | Ensure markdown uses `$...$` / `$$...$$` (not HTML math tags) |
| Broken table layout | Simplify table or add `-V geometry:margin=15mm` for more width |
