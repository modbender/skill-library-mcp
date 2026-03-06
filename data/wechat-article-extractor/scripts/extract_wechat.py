#!/usr/bin/env python3
"""
Extract WeChat article content from mirror HTML to clean Markdown.

Supports mirror sites: 53ai.com, ofweek.com, juejin.cn, woshipm.com, 36kr.com,
and raw WeChat HTML (js_content / rich_media_content).

Usage:
    python3 extract_wechat.py <html_file> [output.md]
    python3 extract_wechat.py --test  # run self-tests

Exit codes:
    0 = success
    1 = usage error
    2 = file not found or unreadable
    3 = extraction failed (no content found)
"""

import sys
import re
import os
import json

# Noise patterns for image filtering
IMG_NOISE = [
    'static.53ai', 'avatar', 'qrcode', 'icon', 'logo',
    'tab1', 'edit-icon', 'banner-ad', 'promotion', 'wxpay',
    'reward', 'donate', 'mp_profile', 'default_head',
]

# Content block selectors, ordered by specificity
CONTENT_SELECTORS = [
    '<div class="detail-content">',          # 53ai.com
    '<div id="js_content"',                   # WeChat original
    '<div class="rich_media_content"',        # WeChat original (alt)
    '<div class="article-content"',           # juejin, generic
    '<div class="Post-RichTextContainer"',    # zhihu
    '<article',                               # semantic HTML
    '<div class="content"',                   # generic fallback
]

# Footer markers to cut off
FOOTER_MARKERS = [
    '<div class="tags">', '<div class="share">',
    'class="related"', 'class="footer"',
    '53AI，企业落地', '<div class="recommend-footer"',
    'class="comment"', '点击"阅读原文"',
    'class="reward"', '赞赏', '喜欢此内容',
]


def decode_html_entities(text):
    """Decode common HTML entities."""
    entities = {
        '&nbsp;': ' ', '&amp;': '&', '&lt;': '<', '&gt;': '>',
        '&quot;': '"', '&#39;': "'", '&apos;': "'",
        '&mdash;': '—', '&ndash;': '–', '&hellip;': '…',
        '&lsquo;': '\u2018', '&rsquo;': '\u2019',
        '&ldquo;': '\u201c', '&rdquo;': '\u201d',
        '&bull;': '•', '&middot;': '·',
    }
    for entity, char in entities.items():
        text = text.replace(entity, char)
    # Numeric entities
    text = re.sub(r'&#(\d+);', lambda m: chr(int(m.group(1))), text)
    text = re.sub(r'&#x([0-9a-fA-F]+);', lambda m: chr(int(m.group(1), 16)), text)
    return text


def extract_img_url(tag):
    """Extract the best image URL from an <img> tag."""
    # Prefer data-src (WeChat lazy-load), then src
    for attr in ['data-src', 'src']:
        match = re.search(rf'{attr}=["\']([^"\']+)["\']', tag)
        if match:
            url = match.group(1)
            # Skip noise images
            if any(n in url.lower() for n in IMG_NOISE):
                return None
            # Skip tiny tracking pixels
            width = re.search(r'width=["\']?(\d+)', tag)
            if width and int(width.group(1)) < 10:
                return None
            # Skip data: URIs (inline SVGs, etc.)
            if url.startswith('data:'):
                return None
            return url
    return None


def extract_alt_text(tag):
    """Extract alt text from an <img> tag."""
    match = re.search(r'alt=["\']([^"\']*)["\']', tag)
    return match.group(1).strip() if match else ''


def html_to_md(html_str):
    """Convert HTML content to Markdown."""
    # Remove scripts and styles first
    html_str = re.sub(r'<script[^>]*>.*?</script>', '', html_str, flags=re.S)
    html_str = re.sub(r'<style[^>]*>.*?</style>', '', html_str, flags=re.S)
    html_str = re.sub(r'<!--.*?-->', '', html_str, flags=re.S)

    # Headings
    for level, tag in [(2, 'h2'), (3, 'h3'), (4, 'h4'), (5, 'h5')]:
        prefix = '#' * level
        html_str = re.sub(
            rf'<{tag}[^>]*>(.*?)</{tag}>',
            rf'\n\n{prefix} \1\n\n', html_str, flags=re.S
        )

    # Bold and italic
    html_str = re.sub(r'<(?:strong|b)[^>]*>(.*?)</(?:strong|b)>', r'**\1**', html_str, flags=re.S)
    html_str = re.sub(r'<(?:em|i)[^>]*>(.*?)</(?:em|i)>', r'*\1*', html_str, flags=re.S)

    # Links
    def link_replace(m):
        href = re.search(r'href=["\']([^"\']+)["\']', m.group(0))
        text = re.sub(r'<[^>]+>', '', m.group(1))
        if href and text.strip():
            return f'[{text.strip()}]({href.group(1)})'
        return text

    html_str = re.sub(r'<a[^>]*>(.*?)</a>', link_replace, html_str, flags=re.S)

    # Line breaks
    html_str = re.sub(r'<br\s*/?>', '\n', html_str)

    # Paragraphs
    html_str = re.sub(r'<p[^>]*>(.*?)</p>', r'\n\n\1\n\n', html_str, flags=re.S)

    # Blockquotes
    def blockquote_replace(m):
        content = re.sub(r'<[^>]+>', '', m.group(1)).strip()
        lines = content.split('\n')
        return '\n\n' + '\n'.join(f'> {line}' for line in lines) + '\n\n'

    html_str = re.sub(r'<blockquote[^>]*>(.*?)</blockquote>', blockquote_replace, html_str, flags=re.S)

    # List items
    html_str = re.sub(r'<li[^>]*>(.*?)</li>', r'\n- \1', html_str, flags=re.S)
    html_str = re.sub(r'</?[uo]l[^>]*>', '\n', html_str)

    # Code blocks
    html_str = re.sub(
        r'<pre[^>]*><code[^>]*>(.*?)</code></pre>',
        r'\n\n```\n\1\n```\n\n', html_str, flags=re.S
    )
    html_str = re.sub(r'<code[^>]*>(.*?)</code>', r'`\1`', html_str, flags=re.S)

    # Horizontal rules
    html_str = re.sub(r'<hr[^>]*/?>',  '\n\n---\n\n', html_str)

    # Images
    def img_replace(m):
        url = extract_img_url(m.group(0))
        if url:
            alt = extract_alt_text(m.group(0))
            return f'\n\n![{alt}]({url})\n\n'
        return ''

    html_str = re.sub(r'<img[^>]*/?>',  img_replace, html_str)

    # Remove remaining HTML tags
    html_str = re.sub(r'<[^>]+>', '', html_str)

    # Decode entities
    html_str = decode_html_entities(html_str)

    # Clean up whitespace
    html_str = re.sub(r'[ \t]+', ' ', html_str)
    html_str = re.sub(r' *\n *', '\n', html_str)
    html_str = re.sub(r'\n{3,}', '\n\n', html_str)

    return html_str.strip()


def find_content_block(html):
    """Find the main content block in the HTML."""
    for selector in CONTENT_SELECTORS:
        idx = html.find(selector)
        if idx >= 0:
            # Find a reasonable end — take up to 500KB from start
            content = html[idx:idx + 500000]

            # Cut at footer markers
            min_end = len(content)
            for marker in FOOTER_MARKERS:
                pos = content.find(marker)
                if 0 < pos < min_end:
                    min_end = pos
            return content[:min_end]
    return None


def extract_metadata(html):
    """Extract title, author, date, and account name from HTML."""
    metadata = {}

    # Title — try multiple patterns
    title_patterns = [
        r'<h1[^>]*class="[^"]*detail-title[^"]*"[^>]*>\s*(.*?)\s*</h1>',
        r'<h1[^>]*id="activity-name"[^>]*>\s*(.*?)\s*</h1>',
        r'<meta\s+property="og:title"\s+content="([^"]+)"',
        r'<title>([^<]+)</title>',
        r'<h1[^>]*>(.*?)</h1>',
    ]
    for pattern in title_patterns:
        m = re.search(pattern, html, re.S)
        if m:
            title = re.sub(r'<[^>]+>', '', m.group(1)).strip()
            if title and len(title) > 2:
                metadata['title'] = title
                break

    # Author
    author_patterns = [
        r'<meta\s+name="author"\s+content="([^"]+)"',
        r'作者[：:]\s*([^\s<\n,，]+)',
        r'<span[^>]*class="[^"]*author[^"]*"[^>]*>\s*(.*?)\s*</span>',
    ]
    for pattern in author_patterns:
        m = re.search(pattern, html, re.S)
        if m:
            author = re.sub(r'<[^>]+>', '', m.group(1)).strip()
            if author:
                metadata['author'] = author
                break

    # Account name (WeChat-specific)
    account_patterns = [
        r'<span[^>]*class="[^"]*profile_nickname[^"]*"[^>]*>\s*(.*?)\s*</span>',
        r'来源[：:]\s*([^\s<\n,，]+)',
        r'公众号[：:]\s*([^\s<\n,，]+)',
    ]
    for pattern in account_patterns:
        m = re.search(pattern, html, re.S)
        if m:
            name = re.sub(r'<[^>]+>', '', m.group(1)).strip()
            if name:
                metadata['account'] = name
                break

    # Date
    date_patterns = [
        r'发布日期[：:]\s*([\d\-/: ]+)',
        r'(\d{4}[-/]\d{1,2}[-/]\d{1,2})',
        r'<meta[^>]*pubdate[^>]*content="([^"]+)"',
    ]
    for pattern in date_patterns:
        m = re.search(pattern, html)
        if m:
            metadata['date'] = m.group(1).strip()
            break

    return metadata


def build_markdown(metadata, body, source_url=None):
    """Assemble final Markdown with header."""
    title = metadata.get('title', 'WeChat Article')
    lines = [f'# {title}', '']

    if metadata.get('author'):
        lines.append(f'**作者：** {metadata["author"]}  ')
    if metadata.get('account'):
        lines.append(f'**来源：** 微信公众号「{metadata["account"]}」  ')
    if metadata.get('date'):
        lines.append(f'**日期：** {metadata["date"]}  ')
    if source_url:
        lines.append(f'**原文：** {source_url}  ')

    lines += ['', '---', '', body]

    return '\n'.join(lines)


def count_images(md_text):
    """Count markdown image references."""
    return len(re.findall(r'!\[.*?\]\(.*?\)', md_text))


def extract(html_path, output_path=None, source_url=None):
    """Main extraction pipeline."""
    # Read HTML
    if not os.path.isfile(html_path):
        print(f"ERROR: File not found: {html_path}", file=sys.stderr)
        return 2

    try:
        with open(html_path, 'r', encoding='utf-8') as f:
            html = f.read()
    except UnicodeDecodeError:
        # Try with fallback encoding
        with open(html_path, 'r', encoding='gb18030', errors='replace') as f:
            html = f.read()

    if len(html) < 100:
        print(f"ERROR: File too small ({len(html)} bytes), likely not a valid HTML page", file=sys.stderr)
        return 3

    # Extract metadata
    metadata = extract_metadata(html)

    # Find and convert content
    content_html = find_content_block(html)
    if not content_html:
        print("WARNING: Could not find main content block, using full HTML", file=sys.stderr)
        content_html = html

    body = html_to_md(content_html)

    if len(body) < 50:
        print(f"ERROR: Extracted content too short ({len(body)} chars), extraction likely failed", file=sys.stderr)
        return 3

    # Build final markdown
    md = build_markdown(metadata, body, source_url)

    # Output
    if output_path:
        os.makedirs(os.path.dirname(output_path) or '.', exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(md)

        # Print summary as JSON for machine parsing
        summary = {
            'status': 'ok',
            'output': output_path,
            'title': metadata.get('title', 'WeChat Article'),
            'chars': len(md),
            'images': count_images(md),
        }
        print(json.dumps(summary, ensure_ascii=False))
    else:
        print(md)

    return 0


def run_tests():
    """Basic self-tests."""
    print("Running self-tests...")

    # Test HTML entity decoding
    assert decode_html_entities('&amp; &lt; &gt;') == '& < >'
    assert decode_html_entities('&#65;') == 'A'
    print("  ✓ HTML entity decoding")

    # Test image URL extraction
    assert extract_img_url('<img src="https://example.com/photo.jpg">') == 'https://example.com/photo.jpg'
    assert extract_img_url('<img data-src="https://example.com/photo.jpg" src="">') == 'https://example.com/photo.jpg'
    assert extract_img_url('<img src="https://example.com/qrcode.png">') is None
    assert extract_img_url('<img src="https://example.com/logo.svg">') is None
    assert extract_img_url('<img src="data:image/svg+xml;base64,abc">') is None
    print("  ✓ Image URL extraction")

    # Test content block finder
    html = '<html><body><div id="js_content"><p>Hello world</p></div></body></html>'
    block = find_content_block(html)
    assert block is not None
    assert 'Hello world' in block
    print("  ✓ Content block detection")

    # Test metadata extraction
    html = '<html><h1 class="detail-title">Test Title</h1><span>作者：张三</span></html>'
    meta = extract_metadata(html)
    assert meta.get('title') == 'Test Title'
    assert meta.get('author') == '张三'
    print("  ✓ Metadata extraction")

    # Test full html_to_md
    html = '<p>Hello <strong>world</strong></p><p>Second paragraph</p>'
    md = html_to_md(html)
    assert '**world**' in md
    assert 'Second paragraph' in md
    print("  ✓ HTML to Markdown conversion")

    # Test markdown assembly
    md = build_markdown({'title': 'Test', 'author': 'Author'}, 'Body text', 'https://example.com')
    assert '# Test' in md
    assert '**作者：** Author' in md
    assert 'https://example.com' in md
    print("  ✓ Markdown assembly")

    print("\nAll tests passed ✓")
    return 0


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <html_file> [output.md]")
        print(f"       {sys.argv[0]} --test")
        sys.exit(1)

    if sys.argv[1] == '--test':
        sys.exit(run_tests())

    source_url = None
    if '--source' in sys.argv:
        idx = sys.argv.index('--source')
        if idx + 1 < len(sys.argv):
            source_url = sys.argv[idx + 1]

    output = sys.argv[2] if len(sys.argv) > 2 and not sys.argv[2].startswith('--') else None
    sys.exit(extract(sys.argv[1], output, source_url))
