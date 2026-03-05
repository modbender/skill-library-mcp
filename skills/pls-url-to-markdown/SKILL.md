---
name: url-to-markdown
description: Fetch URLs and convert web pages to clean Markdown for AI processing or knowledge bases. Use when: (1) Researching web content, (2) Building knowledge bases, (3) Extracting articles, (4) Converting pages for docs.
---

# URL to Markdown Converter

Fetches URLs and converts web pages to clean Markdown.

## Quick Start

### Python Method (`markdownify`)
```bash
pip install requests beautifulsoup4 markdownify

python3 -c "... fetching and converting URL ..."
```

### CLI Tools (`html2text`, `pandoc`)
```bash
curl -s URL | html2text
wget -q -O - URL | pandoc -f html -t markdown
```

## Full Extraction Script
```python
import requests
from bs4 import BeautifulSoup
from markdownify import markdownify as md

def url_to_markdown(url, output_file=None):
    # ... fetch, parse, convert logic ...
    pass
```

## Content Extraction Patterns

### Extract Article Body
```python
def extract_article(html):
    soup = BeautifulSoup(html, 'html.parser')
    article = soup.find('article') or soup.find('main')
    return md(str(article)) if article else None
```

### Preserve Code Blocks
```python
def preserve_code(html):
    # ... logic to wrap code in ``` ...
    pass
```

## CLI Usage

```bash
python url_to_markdown.py URL -o output.md
```

## Error Handling

```python
def safe_fetch(url, retries=3):
    # ... retry logic ...
    pass
```
