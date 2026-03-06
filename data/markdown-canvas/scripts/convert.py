#!/usr/bin/env python3
"""
Markdown to Canvas HTML Converter
Converts markdown files to beautiful HTML pages suitable for Canvas display.
"""

import sys
import argparse
from pathlib import Path
import re

def read_template():
    """Read the HTML template from assets"""
    template_path = Path(__file__).parent.parent / "assets" / "template.html"
    with open(template_path, 'r', encoding='utf-8') as f:
        return f.read()

def escape_html(text):
    """Escape HTML special characters"""
    return (text
        .replace('&', '&amp;')
        .replace('<', '&lt;')
        .replace('>', '&gt;')
        .replace('"', '&quot;')
        .replace("'", '&#39;'))

def convert_markdown_to_html(md_content):
    """
    Simple markdown to HTML converter.
    Supports: headers, bold, italic, code blocks, inline code, links, lists.
    """
    html = []
    in_code_block = False
    code_block_content = []
    code_language = ''
    in_list = False
    list_items = []
    
    lines = md_content.split('\n')
    i = 0
    
    while i < len(lines):
        line = lines[i]
        
        # Code blocks
        if line.startswith('```'):
            if not in_code_block:
                in_code_block = True
                code_language = line[3:].strip()
                code_block_content = []
            else:
                in_code_block = False
                code_html = escape_html('\n'.join(code_block_content))
                html.append(f'<pre><code class="language-{code_language}">{code_html}</code></pre>')
            i += 1
            continue
        
        if in_code_block:
            code_block_content.append(line)
            i += 1
            continue
        
        # Headers
        if line.startswith('#'):
            level = len(line) - len(line.lstrip('#'))
            text = line.lstrip('#').strip()
            text = process_inline_formatting(text)
            html.append(f'<h{level}>{text}</h{level}>')
            i += 1
            continue
        
        # Unordered lists
        if line.strip().startswith(('- ', '* ', '+ ')):
            if not in_list:
                in_list = True
                list_items = []
            item_text = re.sub(r'^[\s\-\*\+]+', '', line).strip()
            item_text = process_inline_formatting(item_text)
            list_items.append(f'<li>{item_text}</li>')
            i += 1
            continue
        
        # End of list
        if in_list and not line.strip().startswith(('- ', '* ', '+ ')):
            html.append('<ul>' + ''.join(list_items) + '</ul>')
            in_list = False
            list_items = []
        
        # Horizontal rule
        if line.strip() in ('---', '***', '___'):
            html.append('<hr>')
            i += 1
            continue
        
        # Empty line
        if not line.strip():
            html.append('<br>')
            i += 1
            continue
        
        # Normal paragraph
        text = process_inline_formatting(line)
        html.append(f'<p>{text}</p>')
        i += 1
    
    # Close any open list
    if in_list:
        html.append('<ul>' + ''.join(list_items) + '</ul>')
    
    return '\n'.join(html)

def process_inline_formatting(text):
    """Process inline markdown formatting"""
    # Bold
    text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
    text = re.sub(r'__(.+?)__', r'<strong>\1</strong>', text)
    
    # Italic
    text = re.sub(r'\*(.+?)\*', r'<em>\1</em>', text)
    text = re.sub(r'_(.+?)_', r'<em>\1</em>', text)
    
    # Inline code
    text = re.sub(r'`(.+?)`', r'<code>\1</code>', text)
    
    # Links
    text = re.sub(r'\[(.+?)\]\((.+?)\)', r'<a href="\2" target="_blank">\1</a>', text)
    
    return text

def main():
    parser = argparse.ArgumentParser(description='Convert markdown to Canvas HTML')
    parser.add_argument('input', help='Input markdown file path')
    parser.add_argument('-o', '--output', help='Output HTML file path (optional)')
    parser.add_argument('-t', '--title', help='Page title (defaults to filename)')
    
    args = parser.parse_args()
    
    # Read input markdown
    input_path = Path(args.input)
    if not input_path.exists():
        print(f"Error: File not found: {args.input}", file=sys.stderr)
        sys.exit(1)
    
    with open(input_path, 'r', encoding='utf-8') as f:
        md_content = f.read()
    
    # Determine title
    title = args.title or input_path.stem
    
    # Convert markdown to HTML
    content_html = convert_markdown_to_html(md_content)
    
    # Read template and inject content
    template = read_template()
    final_html = template.replace('{{TITLE}}', escape_html(title))
    final_html = final_html.replace('{{CONTENT}}', content_html)
    
    # Determine output path
    if args.output:
        output_path = Path(args.output)
    else:
        output_path = input_path.with_suffix('.html')
    
    # Write output
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(final_html)
    
    print(f"✓ Converted: {input_path}")
    print(f"✓ Output: {output_path}")
    print(f"✓ Size: {len(final_html)} bytes")
    
    return str(output_path)

if __name__ == '__main__':
    main()
