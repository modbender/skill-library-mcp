---
name: desearch-crawl
description: Crawl/scrape and extract content from any webpage URL. Returns the page content as clean text or raw HTML. Use this when you need to read the full contents of a specific web page.
metadata: {"clawdbot":{"emoji":"🕷️","homepage":"https://desearch.ai","requires":{"env":["DESEARCH_API_KEY"]}}}
---

# Crawl Webpage By Desearch

Extract content from any webpage URL. Returns clean text or raw HTML.

## Quick Start

1. Get an API key from https://console.desearch.ai
2. Set environment variable: `export DESEARCH_API_KEY='your-key-here'`

## Usage

```bash
# Crawl a webpage (returns clean text by default)
scripts/desearch.py crawl "https://en.wikipedia.org/wiki/Artificial_intelligence"

# Get raw HTML
scripts/desearch.py crawl "https://example.com" --crawl-format html
```


## Options

| Option | Description |
|--------|-------------|
| `--crawl-format` | Output content format: `text` (default) or `html` |

## Examples

### Read a documentation page
```bash
scripts/desearch.py crawl "https://docs.python.org/3/tutorial/index.html"
```

### Get raw HTML for analysis
```bash
scripts/desearch.py crawl "https://example.com/page" --crawl-format html
```

## Response

### Example (`format=text`, truncated, default)
```
Artificial intelligence (AI) is the capability of computational systems to perform tasks that typically require human intelligence, such as learning, reasoning, problem-solving, perception, and decision-making...
```

### Example (`format=html`, truncated)
```html
<!DOCTYPE html>
<html>
  <head><title>Artificial intelligence - Wikipedia</title></head>
  <body>
    <p>Artificial intelligence (AI) is the capability of computational systems...</p>
  </body>
</html>
```

### Notes
- Response is plain text or raw HTML — not JSON.
- Default format is `text`. Use `--crawl-format html` only when you need to inspect page structure.
- Prefer `text` format to avoid bloating the agent context with markup.

### Errors
Status 401, Unauthorized (e.g., missing/invalid API key)
```json
{
  "detail": "Invalid or missing API key"
}
```

Status 402, Payment Required (e.g., balance depleted)
```json
{
  "detail": "Insufficient balance, please add funds to your account to continue using the service."
}
```

## Resources
- [API Reference](https://desearch.ai/docs/api-reference/get-web-crawl)
- [Desearch Console](https://console.desearch.ai)
