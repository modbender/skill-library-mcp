#!/usr/bin/env python3
"""markdown-to-html: Convert Markdown to styled HTML."""

import sys
import argparse
import re
import html as html_mod

LIGHT_CSS = """
body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif; max-width: 800px; margin: 2rem auto; padding: 0 1rem; line-height: 1.6; color: #24292e; background: #fff; }
h1,h2,h3,h4,h5,h6 { margin-top: 1.5em; margin-bottom: 0.5em; border-bottom: 1px solid #eaecef; padding-bottom: 0.3em; }
code { background: #f6f8fa; padding: 0.2em 0.4em; border-radius: 3px; font-size: 85%; }
pre { background: #f6f8fa; padding: 1em; border-radius: 6px; overflow-x: auto; }
pre code { background: none; padding: 0; }
blockquote { border-left: 4px solid #dfe2e5; margin: 0; padding: 0.5em 1em; color: #6a737d; }
table { border-collapse: collapse; width: 100%; }
th, td { border: 1px solid #dfe2e5; padding: 6px 13px; }
th { background: #f6f8fa; }
img { max-width: 100%; }
a { color: #0366d6; text-decoration: none; }
hr { border: none; border-top: 2px solid #eaecef; }
ul, ol { padding-left: 2em; }
"""

DARK_CSS = """
body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif; max-width: 800px; margin: 2rem auto; padding: 0 1rem; line-height: 1.6; color: #c9d1d9; background: #0d1117; }
h1,h2,h3,h4,h5,h6 { margin-top: 1.5em; margin-bottom: 0.5em; border-bottom: 1px solid #21262d; padding-bottom: 0.3em; }
code { background: #161b22; padding: 0.2em 0.4em; border-radius: 3px; font-size: 85%; }
pre { background: #161b22; padding: 1em; border-radius: 6px; overflow-x: auto; }
pre code { background: none; padding: 0; }
blockquote { border-left: 4px solid #30363d; margin: 0; padding: 0.5em 1em; color: #8b949e; }
table { border-collapse: collapse; width: 100%; }
th, td { border: 1px solid #30363d; padding: 6px 13px; }
th { background: #161b22; }
img { max-width: 100%; }
a { color: #58a6ff; text-decoration: none; }
hr { border: none; border-top: 2px solid #21262d; }
ul, ol { padding-left: 2em; }
"""


def md_to_html(md_text):
    """Simple but solid Markdown to HTML converter using only stdlib."""
    lines = md_text.split('\n')
    html_lines = []
    in_code_block = False
    in_list = None  # 'ul' or 'ol'
    in_paragraph = False

    def close_list():
        nonlocal in_list
        if in_list:
            html_lines.append(f'</{in_list}>')
            in_list = None

    def close_para():
        nonlocal in_paragraph
        if in_paragraph:
            html_lines.append('</p>')
            in_paragraph = False

    def inline(text):
        # Images
        text = re.sub(r'!\[([^\]]*)\]\(([^)]+)\)', r'<img src="\2" alt="\1">', text)
        # Links
        text = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2">\1</a>', text)
        # Bold+italic
        text = re.sub(r'\*\*\*(.+?)\*\*\*', r'<strong><em>\1</em></strong>', text)
        # Bold
        text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
        # Italic
        text = re.sub(r'\*(.+?)\*', r'<em>\1</em>', text)
        # Inline code
        text = re.sub(r'`([^`]+)`', r'<code>\1</code>', text)
        # Strikethrough
        text = re.sub(r'~~(.+?)~~', r'<del>\1</del>', text)
        return text

    for line in lines:
        # Code blocks
        if line.strip().startswith('```'):
            if in_code_block:
                html_lines.append('</code></pre>')
                in_code_block = False
            else:
                close_para()
                close_list()
                lang = line.strip()[3:].strip()
                cls = f' class="language-{html_mod.escape(lang)}"' if lang else ''
                html_lines.append(f'<pre><code{cls}>')
                in_code_block = True
            continue

        if in_code_block:
            html_lines.append(html_mod.escape(line))
            continue

        stripped = line.strip()

        # Empty line
        if not stripped:
            close_para()
            close_list()
            continue

        # Headings
        m = re.match(r'^(#{1,6})\s+(.+)$', stripped)
        if m:
            close_para()
            close_list()
            level = len(m.group(1))
            html_lines.append(f'<h{level}>{inline(m.group(2))}</h{level}>')
            continue

        # HR
        if re.match(r'^[-*_]{3,}\s*$', stripped):
            close_para()
            close_list()
            html_lines.append('<hr>')
            continue

        # Blockquote
        if stripped.startswith('>'):
            close_para()
            close_list()
            text = stripped.lstrip('>').strip()
            html_lines.append(f'<blockquote><p>{inline(text)}</p></blockquote>')
            continue

        # Unordered list
        m = re.match(r'^[-*+]\s+(.+)$', stripped)
        if m:
            close_para()
            if in_list != 'ul':
                close_list()
                html_lines.append('<ul>')
                in_list = 'ul'
            html_lines.append(f'<li>{inline(m.group(1))}</li>')
            continue

        # Ordered list
        m = re.match(r'^\d+\.\s+(.+)$', stripped)
        if m:
            close_para()
            if in_list != 'ol':
                close_list()
                html_lines.append('<ol>')
                in_list = 'ol'
            html_lines.append(f'<li>{inline(m.group(1))}</li>')
            continue

        # Paragraph
        if not in_paragraph:
            close_list()
            html_lines.append('<p>')
            in_paragraph = True
        html_lines.append(inline(stripped))

    close_para()
    close_list()
    if in_code_block:
        html_lines.append('</code></pre>')

    return '\n'.join(html_lines)


def main():
    parser = argparse.ArgumentParser(description='Convert Markdown to styled HTML')
    parser.add_argument('input', help='Input markdown file (use - for stdin)')
    parser.add_argument('-o', '--output', help='Output HTML file (default: stdout)')
    parser.add_argument('--theme', choices=['light', 'dark'], default='light')
    parser.add_argument('--title', default='Document')
    args = parser.parse_args()

    if args.input == '-':
        md_text = sys.stdin.read()
    else:
        with open(args.input, 'r') as f:
            md_text = f.read()

    css = LIGHT_CSS if args.theme == 'light' else DARK_CSS
    body = md_to_html(md_text)
    title = html_mod.escape(args.title)

    result = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<style>{css}</style>
</head>
<body>
{body}
</body>
</html>"""

    if args.output:
        with open(args.output, 'w') as f:
            f.write(result)
        print(f"Written to {args.output}", file=sys.stderr)
    else:
        print(result)


if __name__ == '__main__':
    main()
