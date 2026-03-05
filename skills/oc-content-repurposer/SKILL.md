---
name: content-repurposer
description: Repurpose any blog post or article into multiple social media formats. Input a URL or text, get X/Twitter thread, LinkedIn post, Instagram caption, email snippet, and summary. Use when asked to repurpose content, create social posts from an article, turn a blog into tweets, or generate multi-platform content.
---

# Content Repurposer

Turn any article or blog post into ready-to-post content for multiple platforms.

## Quick Start

```bash
# Repurpose from URL — generates all formats
uv run --with beautifulsoup4 python scripts/repurpose.py url "https://example.com/blog-post"

# Repurpose from text file
python scripts/repurpose.py file article.txt

# Generate only specific formats
uv run --with beautifulsoup4 python scripts/repurpose.py url "https://example.com/post" --formats twitter,linkedin

# Output as JSON (for automation)
uv run --with beautifulsoup4 python scripts/repurpose.py url "https://example.com/post" -f json

# Save all outputs to files
uv run --with beautifulsoup4 python scripts/repurpose.py url "https://example.com/post" -o output/

# Repurpose from clipboard/stdin
echo "Your article text here..." | python scripts/repurpose.py stdin
```

## Commands

| Command | Args | Description |
|---------|------|-------------|
| `url` | `<url> [--formats LIST] [-f FORMAT] [-o DIR]` | Extract article from URL and repurpose |
| `file` | `<path> [--formats LIST] [-f FORMAT] [-o DIR]` | Repurpose from text/markdown file |
| `stdin` | `[--formats LIST] [-f FORMAT]` | Repurpose from piped input |

## Output Formats

| Platform | What You Get |
|----------|-------------|
| **Twitter/X** | Thread of 5-8 tweets, each ≤280 chars, with hooks and hashtags |
| **LinkedIn** | Professional post (1300 chars), insight-driven, with CTA |
| **Instagram** | Caption (2200 chars max), storytelling style, 20-30 hashtags |
| **Email** | Newsletter snippet with subject line, preview text, and body |
| **Summary** | 3-sentence TL;DR for quick sharing |

## Examples

### From URL
```bash
uv run --with beautifulsoup4 python scripts/repurpose.py url "https://blog.example.com/ai-trends-2026"
```

### Only Twitter + LinkedIn
```bash
uv run --with beautifulsoup4 python scripts/repurpose.py url "https://example.com/post" --formats twitter,linkedin
```

### Save to directory
```bash
uv run --with beautifulsoup4 python scripts/repurpose.py url "https://example.com/post" -o ./social-posts/
# Creates: twitter.txt, linkedin.txt, instagram.txt, email.txt, summary.txt
```

## Notes

- Uses beautifulsoup4 for URL extraction (optional for file/stdin input)
- Content extraction focuses on article body (removes nav, sidebar, footer)
- All generated content is original repurposing, not copy-paste
- Character limits are enforced per platform
