#!/usr/bin/env python3
"""
convert_to_html.py — Convert a markdown manuscript to HTML.

Preferred: pandoc (handles Mermaid blocks, tables, nested lists, inline HTML correctly)
Fallback:  markdown2 (pip install markdown2)

Usage:
  python3 scripts/convert_to_html.py [--input book/final-manuscript.md] [--output book/book.html]
    [--title "Book Title"] [--metadata book/metadata.json] [--css styles.css]

Requirements (choose one):
  - pandoc installed (brew install pandoc  /  apt install pandoc)
  - OR: pip install markdown2
"""

import os
import re
import sys
import json
import shutil
import argparse
import datetime
import subprocess

CSS = """
body { font-family: Georgia, serif; max-width: 820px; margin: 60px auto; padding: 0 24px;
       line-height: 1.8; color: #222; background: #fafafa; }
h1 { font-size: 2em; margin-top: 2em; border-bottom: 2px solid #ddd; padding-bottom: 0.3em; }
h2 { font-size: 1.45em; margin-top: 1.8em; color: #333; }
h3 { font-size: 1.15em; color: #444; }
pre { background: #f4f4f4; border: 1px solid #ddd; padding: 1em; overflow-x: auto;
      border-radius: 4px; font-size: 0.88em; }
code { background: #f0f0f0; padding: 2px 5px; border-radius: 3px; font-size: 0.88em; }
blockquote { border-left: 4px solid #aaa; margin: 1em 0; padding: 0.5em 1.2em; color: #555; }
table { border-collapse: collapse; width: 100%; margin: 1em 0; }
th, td { border: 1px solid #ddd; padding: 8px 12px; text-align: left; }
th { background: #f2f2f2; font-weight: bold; }
hr { border: none; border-top: 1px solid #ddd; margin: 2.5em 0; }
.meta { color: #888; font-size: 0.88em; margin-bottom: 2em; }
a { color: #0066cc; }
.mermaid { background: #f9f9f9; border: 1px solid #eee; padding: 1em; border-radius: 4px;
           font-family: monospace; white-space: pre; font-size: 0.85em; }
"""

def load_metadata(metadata_path, args):
    meta = {}
    if metadata_path and os.path.exists(metadata_path):
        with open(metadata_path) as f:
            meta = json.load(f)
    title = getattr(args, 'title', None) or meta.get("title", "Book")
    author = meta.get("author", "Author")
    year = meta.get("year", datetime.date.today().year)
    word_count = meta.get("word_count", "")
    chapter_count = meta.get("chapter_count", "")
    return title, author, year, word_count, chapter_count

def convert_with_pandoc(input_path, output_path, title, css_path=None):
    """Use pandoc for reliable conversion."""
    cmd = [
        "pandoc", input_path,
        "--standalone",
        "--output", output_path,
        f"--metadata=title:{title}",
        "--toc",
        "--toc-depth=2",
    ]
    if css_path and os.path.exists(css_path):
        cmd += [f"--css={css_path}"]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"pandoc error: {result.stderr}", file=sys.stderr)
        return False
    return True

def convert_with_markdown2(input_path, output_path, title, author, year, word_count, chapter_count):
    """Fallback: markdown2 library."""
    try:
        import markdown2
    except ImportError:
        print("ERROR: Neither pandoc nor markdown2 is available.")
        print("  Install pandoc: brew install pandoc  OR  apt install pandoc")
        print("  OR: pip install markdown2")
        sys.exit(1)

    with open(input_path) as f:
        md = f.read()

    body = markdown2.markdown(md, extras=["tables", "fenced-code-blocks", "toc", "header-ids"])

    meta_parts = [f"by {author}", str(year)]
    if word_count:
        meta_parts.append(f"{word_count:,} words" if isinstance(word_count, int) else f"{word_count} words")
    if chapter_count:
        meta_parts.append(f"{chapter_count} chapters")
    meta_line = " · ".join(meta_parts)

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{title}</title>
  <style>{CSS}</style>
</head>
<body>
<div class="meta">{meta_line}</div>
{body}
</body>
</html>"""

    with open(output_path, "w") as f:
        f.write(html)
    return True

def write_css(css_path):
    with open(css_path, "w") as f:
        f.write(CSS)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default="book/final-manuscript.md")
    parser.add_argument("--output", default="book/book.html")
    parser.add_argument("--title", default=None)
    parser.add_argument("--metadata", default="book/metadata.json")
    parser.add_argument("--css", default=None, help="Path to CSS file (pandoc mode only)")
    args = parser.parse_args()

    if not os.path.exists(args.input):
        print(f"ERROR: Input not found: {args.input}")
        sys.exit(1)

    os.makedirs(os.path.dirname(args.output) or ".", exist_ok=True)
    title, author, year, word_count, chapter_count = load_metadata(args.metadata, args)

    if shutil.which("pandoc"):
        print("Using pandoc for conversion...")
        css_path = args.css
        if not css_path:
            css_path = os.path.join(os.path.dirname(args.output), "styles.css")
            write_css(css_path)
        ok = convert_with_pandoc(args.input, args.output, title, css_path)
        if ok:
            print(f"Written: {args.output}")
            return

    print("pandoc not found or failed — falling back to markdown2...")
    convert_with_markdown2(args.input, args.output, title, author, year, word_count, chapter_count)
    print(f"Written: {args.output}")

if __name__ == "__main__":
    main()
