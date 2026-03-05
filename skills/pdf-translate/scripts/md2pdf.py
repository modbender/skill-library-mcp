#!/usr/bin/env python3
"""
md2pdf.py — Markdown to PDF converter with professional Chinese typography.

Usage:
    python3 scripts/md2pdf.py input.md output.pdf

Dependencies:
    pip3 install markdown weasyprint
"""

import sys
import os
import platform

if platform.system() == "Darwin":
    brew_lib = "/opt/homebrew/lib"
    if os.path.isdir(brew_lib):
        os.environ.setdefault("DYLD_FALLBACK_LIBRARY_PATH", brew_lib)

import markdown
from weasyprint import HTML

CSS_STYLESHEET = """
@page {
    size: A4;
    margin: 2.2cm 2cm 2.5cm 2cm;

    @bottom-center {
        content: counter(page);
        font-size: 9pt;
        color: #999;
        font-family: "Helvetica Neue", Arial, sans-serif;
    }
}

@page :first {
    @bottom-center { content: none; }
}

:root {
    --text-primary: #1a1a1a;
    --text-secondary: #374151;
    --text-muted: #6b7280;
    --accent: #2563eb;
    --accent-dark: #1e40af;
    --bg-code: #f3f4f6;
    --bg-blockquote: #f8fafc;
    --border-light: #e5e7eb;
    --border-code: #d1d5db;
}

body {
    font-family: "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei",
                 "WenQuanYi Micro Hei", "Noto Sans CJK SC",
                 "Helvetica Neue", Arial, sans-serif;
    font-size: 10.5pt;
    line-height: 1.8;
    color: var(--text-primary);
    text-align: justify;
    word-break: break-word;
    orphans: 3;
    widows: 3;
}

/* ---- Headings ---- */
h1 {
    font-size: 22pt;
    font-weight: 700;
    color: var(--text-primary);
    margin: 0 0 0.8em 0;
    padding-bottom: 0.4em;
    border-bottom: 2px solid var(--accent);
    line-height: 1.3;
    page-break-after: avoid;
}

h2 {
    font-size: 16pt;
    font-weight: 700;
    color: var(--accent-dark);
    margin: 1.8em 0 0.6em 0;
    padding-bottom: 0.3em;
    border-bottom: 1px solid var(--border-light);
    line-height: 1.4;
    page-break-after: avoid;
}

h3 {
    font-size: 13pt;
    font-weight: 600;
    color: var(--text-primary);
    margin: 1.4em 0 0.5em 0;
    line-height: 1.4;
    page-break-after: avoid;
}

h4 {
    font-size: 11.5pt;
    font-weight: 600;
    color: var(--text-secondary);
    margin: 1.2em 0 0.4em 0;
    line-height: 1.4;
    page-break-after: avoid;
}

/* ---- Paragraphs ---- */
p {
    margin: 0 0 0.8em 0;
    text-align: justify;
}

/* ---- Links ---- */
a {
    color: var(--accent);
    text-decoration: none;
}

/* ---- Bold / Italic ---- */
strong { font-weight: 700; }
em { font-style: italic; }

/* ---- Horizontal Rule ---- */
hr {
    border: none;
    border-top: 1px solid var(--border-light);
    margin: 1.5em 0;
}

/* ---- Lists ---- */
ul, ol {
    margin: 0.4em 0 0.8em 0;
    padding-left: 1.8em;
}

li {
    margin-bottom: 0.3em;
    line-height: 1.7;
}

li > ul, li > ol {
    margin-top: 0.2em;
    margin-bottom: 0.2em;
}

/* Checkbox-style lists */
li > p { margin-bottom: 0.2em; }

/* ---- Code (inline) ---- */
code {
    font-family: "SF Mono", "Fira Code", "Source Code Pro",
                 "Menlo", monospace,
                 "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei",
                 "Noto Sans CJK SC", sans-serif;
    font-size: 0.88em;
    background: var(--bg-code);
    border: 1px solid var(--border-code);
    border-radius: 3px;
    padding: 0.15em 0.35em;
    color: #c7254e;
    word-break: break-all;
}

/* ---- Code blocks ---- */
pre {
    background: #1e293b;
    color: #e2e8f0;
    border-radius: 6px;
    padding: 1em 1.2em;
    margin: 0.6em 0 1em 0;
    overflow-x: auto;
    line-height: 1.6;
    page-break-inside: avoid;
}

pre code {
    font-family: "SF Mono", "Fira Code", "Source Code Pro",
                 "Menlo", monospace,
                 "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei",
                 "Noto Sans CJK SC", sans-serif;
    background: none;
    border: none;
    padding: 0;
    color: #e2e8f0;
    font-size: 9pt;
    white-space: pre-wrap;
    word-wrap: break-word;
}

/* ---- Blockquotes ---- */
blockquote {
    background: var(--bg-blockquote);
    border-left: 4px solid var(--accent);
    margin: 0.6em 0 1em 0;
    padding: 0.8em 1.2em;
    color: var(--text-secondary);
    border-radius: 0 4px 4px 0;
    page-break-inside: avoid;
}

blockquote p {
    margin-bottom: 0.3em;
}

blockquote p:last-child {
    margin-bottom: 0;
}

/* ---- Tables ---- */
table {
    width: 100%;
    border-collapse: collapse;
    margin: 0.8em 0 1.2em 0;
    font-size: 9.5pt;
    page-break-inside: avoid;
}

thead {
    background: #f1f5f9;
}

th {
    font-weight: 600;
    text-align: left;
    padding: 0.6em 0.8em;
    border: 1px solid var(--border-light);
    color: var(--text-primary);
}

td {
    padding: 0.5em 0.8em;
    border: 1px solid var(--border-light);
    vertical-align: top;
    line-height: 1.6;
}

tr:nth-child(even) {
    background: #fafbfc;
}

/* ---- Images ---- */
img {
    max-width: 100%;
    height: auto;
    margin: 0.5em 0;
}

/* ---- Cover page helper ---- */
.cover-title {
    font-size: 28pt;
    text-align: center;
    margin-top: 35%;
}

/* ---- Utility: page break ---- */
.page-break {
    page-break-after: always;
}
"""


def convert_md_to_pdf(md_path: str, pdf_path: str) -> None:
    with open(md_path, "r", encoding="utf-8") as f:
        md_text = f.read()

    extensions = [
        "extra",       # tables, fenced_code, footnotes, etc.
        "codehilite",  # syntax highlighting hints
        "toc",         # table of contents
        "sane_lists",  # better list handling
        "smarty",      # smart quotes
    ]

    extension_configs = {
        "codehilite": {
            "css_class": "highlight",
            "guess_lang": False,
        },
    }

    html_body = markdown.markdown(
        md_text,
        extensions=extensions,
        extension_configs=extension_configs,
        output_format="html5",
    )

    full_html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="utf-8">
    <style>{CSS_STYLESHEET}</style>
</head>
<body>
{html_body}
</body>
</html>"""

    HTML(string=full_html).write_pdf(pdf_path)
    file_size = os.path.getsize(pdf_path)
    print(f"PDF generated: {pdf_path} ({file_size / 1024:.0f} KB)")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python3 md2pdf.py <input.md> <output.pdf>")
        sys.exit(1)

    md_path = sys.argv[1]
    pdf_path = sys.argv[2]

    if not os.path.exists(md_path):
        print(f"Error: {md_path} not found")
        sys.exit(1)

    convert_md_to_pdf(md_path, pdf_path)
