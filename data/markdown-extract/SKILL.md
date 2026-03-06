---
name: markdown-extract Skill
description: Extract clean markdown from any URL using the markdown.new API.
---

# markdown-extract Skill

Extract clean markdown from any URL using the markdown.new API.

## Description

This skill converts web pages to clean markdown format using the markdown.new API. It supports multiple extraction methods and handles errors gracefully.

## Usage

```
!markdown-extract <url> [method]
```

### Arguments

- `url` (required): The URL to extract markdown from
- `method` (optional): Extraction method - `auto`, `ai`, or `browser`. Default: `auto`

### Examples

```bash
# Extract using default method (auto)
!markdown-extract https://example.com

# Extract using AI method
!markdown-extract https://example.com ai

# Extract using browser method
!markdown-extract https://example.com browser
```

## API

- GET `https://markdown.new/<url>` - Returns clean markdown (auto method)
- POST with JSON body `{url: "...", method: "browser|ai"}` - Specific extraction method

## Methods

- **auto**: Content negotiation with `Accept: text/markdown` header (fastest, default)
- **ai**: Cloudflare Workers AI `toMarkdown()` conversion
- **browser**: Headless browser rendering for JS-heavy pages (slowest but most complete)

## Error Handling

- Invalid URL: Returns error message
- Network failure: Returns retryable error
- API error: Returns error details
- Cloudflare block detection and fallback handling
