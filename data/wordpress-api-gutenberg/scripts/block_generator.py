#!/usr/bin/env python3
"""
Gutenberg Block Generator

Convert markdown or plain text to WordPress Gutenberg block format.
Supports common blocks: paragraphs, headings, lists, code blocks, images.

Usage:
    python block_generator.py input.md --output blocks.html
    python block_generator.py --text "Hello world" --format html
"""

import argparse
import re
import json
from typing import List, Dict, Any, Optional


class BlockGenerator:
    def __init__(self, add_paragraph_spacing: bool = True):
        """
        Initialize block generator.
        
        Args:
            add_paragraph_spacing: Add double newlines between blocks
        """
        self.add_spacing = add_paragraph_spacing
        
    def markdown_to_blocks(self, markdown: str) -> str:
        """
        Convert markdown text to Gutenberg blocks.
        
        Args:
            markdown: Markdown text
            
        Returns:
            Gutenberg block HTML
        """
        lines = markdown.split('\n')
        blocks = []
        i = 0
        
        while i < len(lines):
            line = lines[i].strip()
            
            # Empty line
            if not line:
                i += 1
                continue
            
            # Heading
            if line.startswith('#'):
                level = len(line.split(' ')[0])
                if level > 6:
                    level = 6
                text = line[level:].strip()
                blocks.append(self.heading_block(text, level))
                i += 1
                continue
            
            # List items
            if line.startswith('- ') or line.startswith('* ') or re.match(r'^\d+\. ', line):
                list_items = []
                list_type = 'unordered' if line.startswith(('- ', '* ')) else 'ordered'
                
                while i < len(lines) and (lines[i].startswith('- ') or 
                                         lines[i].startswith('* ') or 
                                         re.match(r'^\d+\. ', lines[i])):
                    item = lines[i].strip()
                    # Remove bullet/number
                    if list_type == 'unordered':
                        item = re.sub(r'^[-*]\s+', '', item)
                    else:
                        item = re.sub(r'^\d+\.\s+', '', item)
                    list_items.append(item)
                    i += 1
                
                blocks.append(self.list_block(list_items, list_type))
                continue
            
            # Code block (triple backticks)
            if line.startswith('```'):
                language = line[3:].strip() or 'plaintext'
                code_lines = []
                i += 1
                
                while i < len(lines) and not lines[i].strip().startswith('```'):
                    code_lines.append(lines[i])
                    i += 1
                
                if i < len(lines) and lines[i].strip().startswith('```'):
                    i += 1
                
                code = '\n'.join(code_lines)
                blocks.append(self.code_block(code, language))
                continue
            
            # Blockquote
            if line.startswith('> '):
                quote_lines = []
                while i < len(lines) and lines[i].startswith('> '):
                    quote_lines.append(lines[i][2:].strip())
                    i += 1
                quote_text = ' '.join(quote_lines)
                blocks.append(self.quote_block(quote_text))
                continue
            
            # Image (markdown format)
            img_match = re.match(r'^!\[([^\]]*)\]\(([^)]+)\)$', line)
            if img_match:
                alt_text = img_match.group(1)
                image_url = img_match.group(2)
                blocks.append(self.image_block(image_url, alt_text))
                i += 1
                continue
            
            # Link (markdown format)
            link_match = re.match(r'^\[([^\]]+)\]\(([^)]+)\)$', line)
            if link_match:
                # Convert to paragraph with link
                link_text = link_match.group(1)
                link_url = link_match.group(2)
                paragraph = f'<p><a href="{link_url}">{link_text}</a></p>'
                blocks.append(self.custom_block('core/paragraph', {}, paragraph))
                i += 1
                continue
            
            # Horizontal rule
            if line.strip() in ('---', '***', '___'):
                blocks.append(self.separator_block())
                i += 1
                continue
            
            # Regular paragraph (collect consecutive non-empty lines)
            paragraph_lines = []
            while i < len(lines) and lines[i].strip() and not self.is_special_markdown(lines[i]):
                paragraph_lines.append(lines[i].strip())
                i += 1
            
            if paragraph_lines:
                paragraph = ' '.join(paragraph_lines)
                # Convert inline markdown
                paragraph = self.convert_inline_markdown(paragraph)
                blocks.append(self.paragraph_block(paragraph))
                continue
            
            i += 1
        
        # Join blocks
        separator = '\n\n' if self.add_spacing else '\n'
        return separator.join(blocks)
    
    def is_special_markdown(self, line: str) -> bool:
        """Check if line starts with special markdown syntax."""
        line = line.strip()
        return (line.startswith('#') or
                line.startswith('- ') or
                line.startswith('* ') or
                re.match(r'^\d+\. ', line) or
                line.startswith('```') or
                line.startswith('> ') or
                re.match(r'^!\[.*\]\(.*\)$', line) or
                re.match(r'^\[.*\]\(.*\)$', line) or
                line in ('---', '***', '___'))
    
    def convert_inline_markdown(self, text: str) -> str:
        """Convert inline markdown to HTML."""
        # Bold: **text** or __text__
        text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
        text = re.sub(r'__(.+?)__', r'<strong>\1</strong>', text)
        
        # Italic: *text* or _text_
        text = re.sub(r'\*(.+?)\*', r'<em>\1</em>', text)
        text = re.sub(r'_(.+?)_', r'<em>\1</em>', text)
        
        # Code: `text`
        text = re.sub(r'`(.+?)`', r'<code>\1</code>', text)
        
        # Links: [text](url)
        text = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2">\1</a>', text)
        
        return text
    
    def paragraph_block(self, text: str, align: str = None, 
                       text_color: str = None, 
                       background_color: str = None) -> str:
        """Create paragraph block."""
        attrs = {}
        class_names = []
        
        if align:
            attrs['align'] = align
            class_names.append(f'has-text-align-{align}')
        
        if text_color:
            attrs['textColor'] = text_color
            class_names.append(f'has-{text_color}-color')
        
        if background_color:
            attrs['backgroundColor'] = background_color
            class_names.append(f'has-{background_color}-background-color')
        
        # Build paragraph HTML
        class_attr = f' class="{" ".join(class_names)}"' if class_names else ''
        paragraph_html = f'<p{class_attr}>{text}</p>'
        
        return self.custom_block('core/paragraph', attrs, paragraph_html)
    
    def heading_block(self, text: str, level: int = 2, 
                     anchor: str = None) -> str:
        """Create heading block."""
        if level < 2:
            level = 2
        if level > 6:
            level = 6
        
        attrs = {'level': level}
        if anchor:
            attrs['anchor'] = anchor
        
        heading_html = f'<h{level}>{text}</h{level}>'
        if anchor:
            heading_html = f'<h{level} id="{anchor}">{text}</h{level}>'
        
        return self.custom_block('core/heading', attrs, heading_html)
    
    def list_block(self, items: List[str], list_type: str = 'unordered') -> str:
        """Create list block."""
        attrs = {'ordered': list_type == 'ordered'}
        
        list_tag = 'ol' if list_type == 'ordered' else 'ul'
        list_html = f'<{list_tag}>\n'
        for item in items:
            list_html += f'  <li>{item}</li>\n'
        list_html += f'</{list_tag}>'
        
        return self.custom_block('core/list', attrs, list_html)
    
    def code_block(self, code: str, language: str = 'plaintext') -> str:
        """Create code block."""
        attrs = {'language': language} if language != 'plaintext' else {}
        
        code_html = f'<pre class="wp-block-code"><code>{code}</code></pre>'
        if language != 'plaintext':
            code_html = f'<pre class="wp-block-code language-{language}"><code>{code}</code></pre>'
        
        return self.custom_block('core/code', attrs, code_html)
    
    def quote_block(self, text: str, citation: str = None) -> str:
        """Create quote block."""
        attrs = {}
        quote_html = f'<blockquote class="wp-block-quote"><p>{text}</p>'
        
        if citation:
            quote_html += f'<cite>{citation}</cite>'
            attrs['citation'] = citation
        
        quote_html += '</blockquote>'
        return self.custom_block('core/quote', attrs, quote_html)
    
    def image_block(self, url: str, alt_text: str = '', 
                   align: str = None, caption: str = None) -> str:
        """Create image block."""
        attrs = {}
        class_names = ['wp-block-image']
        
        if align:
            attrs['align'] = align
            class_names.append(f'align{align}')
        
        image_html = f'<figure class="{" ".join(class_names)}">'
        image_html += f'<img src="{url}" alt="{alt_text}"/>'
        
        if caption:
            image_html += f'<figcaption class="wp-element-caption">{caption}</figcaption>'
            attrs['caption'] = caption
        
        image_html += '</figure>'
        return self.custom_block('core/image', attrs, image_html)
    
    def separator_block(self, style: str = 'default') -> str:
        """Create separator block."""
        attrs = {}
        class_names = ['wp-block-separator', 'has-alpha-channel-opacity']
        
        if style != 'default':
            attrs['className'] = f'is-style-{style}'
            class_names.append(f'is-style-{style}')
        
        separator_html = f'<hr class="{" ".join(class_names)}"/>'
        return self.custom_block('core/separator', attrs, separator_html)
    
    def custom_block(self, block_name: str, attrs: Dict[str, Any], 
                    inner_html: str) -> str:
        """
        Create custom block with given attributes.
        
        Args:
            block_name: Block namespace (e.g., 'core/paragraph')
            attrs: Block attributes as dictionary
            inner_html: Inner HTML content
            
        Returns:
            Complete block HTML
        """
        # Format attributes JSON
        if attrs:
            # Convert to JSON, remove whitespace
            attrs_json = json.dumps(attrs, separators=(',', ':'))
            block_comment = f'<!-- wp:{block_name} {attrs_json} -->'
        else:
            block_comment = f'<!-- wp:{block_name} -->'
        
        closing_comment = f'<!-- /wp:{block_name} -->'
        
        return f'{block_comment}{inner_html}{closing_comment}'
    
    def wrap_in_group(self, blocks_html: str, 
                     background_color: str = None,
                     align: str = None) -> str:
        """
        Wrap blocks in a group block.
        
        Args:
            blocks_html: HTML of inner blocks
            background_color: Background color class
            align: Alignment
            
        Returns:
            Group block HTML
        """
        attrs = {}
        class_names = ['wp-block-group']
        
        if background_color:
            attrs['backgroundColor'] = background_color
            class_names.append(f'has-{background_color}-background-color')
            class_names.append('has-background')
        
        if align:
            attrs['align'] = align
        
        group_html = f'<div class="{" ".join(class_names)}">'
        group_html += blocks_html
        group_html += '</div>'
        
        return self.custom_block('core/group', attrs, group_html)
    
    def wrap_in_columns(self, columns_html: List[str], 
                       widths: List[str] = None) -> str:
        """
        Wrap content in columns block.
        
        Args:
            columns_html: List of column HTML strings
            widths: Optional list of width percentages (e.g., ["50%", "50%"])
            
        Returns:
            Columns block HTML
        """
        columns_block = []
        
        for i, column_html in enumerate(columns_html):
            attrs = {}
            if widths and i < len(widths):
                attrs['width'] = widths[i]
            
            column_inner = f'<div class="wp-block-column">'
            column_inner += column_html
            column_inner += '</div>'
            
            columns_block.append(self.custom_block('core/column', attrs, column_inner))
        
        columns_inner = '\n'.join(columns_block)
        columns_wrapper = f'<div class="wp-block-columns">{columns_inner}</div>'
        
        return self.custom_block('core/columns', {}, columns_wrapper)


def main():
    parser = argparse.ArgumentParser(description='Generate Gutenberg blocks from markdown/text')
    parser.add_argument('input', nargs='?', help='Input file (markdown)')
    parser.add_argument('--text', help='Input text')
    parser.add_argument('--output', '-o', help='Output file')
    parser.add_argument('--format', choices=['html', 'json'], default='html',
                       help='Output format')
    parser.add_argument('--spacing', action='store_true', default=True,
                       help='Add spacing between blocks (default: true)')
    parser.add_argument('--no-spacing', action='store_false', dest='spacing',
                       help='Remove spacing between blocks')
    
    args = parser.parse_args()
    
    # Read input
    input_text = ''
    if args.input:
        with open(args.input, 'r', encoding='utf-8') as f:
            input_text = f.read()
    elif args.text:
        input_text = args.text
    else:
        print("Error: No input provided. Use --text or provide input file.")
        sys.exit(1)
    
    # Generate blocks
    generator = BlockGenerator(add_paragraph_spacing=args.spacing)
    blocks_html = generator.markdown_to_blocks(input_text)
    
    # Output
    if args.format == 'json':
        output_data = {
            'content': blocks_html,
            'block_count': blocks_html.count('<!-- wp:'),
            'format': 'gutenberg'
        }
        output = json.dumps(output_data, indent=2)
    else:
        output = blocks_html
    
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(output)
        print(f"✓ Generated {blocks_html.count('<!-- wp:')} blocks to {args.output}")
    else:
        print(output)


if __name__ == "__main__":
    import sys
    main()