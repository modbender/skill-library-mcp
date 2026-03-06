---
name: tavily-extract
description: Extract content from specific URLs using Tavily's extraction API. Returns clean markdown/text from web pages.
homepage: https://tavily.com
metadata: {"openclaw":{"emoji":"📄","requires":{"bins":["node"],"env":["TAVILY_API_KEY"]},"primaryEnv":"TAVILY_API_KEY"}}
---

# Tavily Extract

Extract clean content from specific URLs. Ideal when you know which pages you want content from.

## Authentication

Get your API key at https://tavily.com and add to your OpenClaw config:

```json
{
  "skills": {
    "entries": {
      "tavily-extract": {
        "enabled": true,
        "apiKey": "tvly-YOUR_API_KEY_HERE"
      }
    }
  }
}
```

Or set in environment variable:
```bash
export TAVILY_API_KEY="tvly-YOUR_API_KEY_HERE"
```

## Quick Start

### Using the Script

```bash
node {baseDir}/scripts/extract.mjs "https://example.com/article"
node {baseDir}/scripts/extract.mjs "url1,url2,url3"
node {baseDir}/scripts/extract.mjs "url" --query "authentication API"
```

### Examples

```bash
# Single URL
node {baseDir}/scripts/extract.mjs "https://docs.python.org/3/tutorial/classes.html"

# Multiple URLs
node {baseDir}/scripts/extract.mjs "https://example.com/page1,https://example.com/page2"

# With query focus
node {baseDir}/scripts/extract.mjs "https://example.com/docs" --query "authentication API"

# Advanced extraction for JS pages
node {baseDir}/scripts/extract.mjs "https://app.example.com" --depth advanced --timeout 60
```

## Options

| Option| Description | Default |
|--------|-------------|---------|
| `--query <text>` | Rerank chunks by relevance | - |
| `--chunks <n>` | Chunks per URL (1-5, requires query) | 3 |
| `--depth <mode>` | Extract depth: `basic` or `advanced` | `basic` |
| `--format <fmt>` | Output format: `markdown` or `text` | `markdown` |
| `--timeout <sec>` | Max wait time (1-60 seconds) | varies |
| `--json` | Output raw JSON | false |

## Extract Depth

| Depth | When to Use |
|-------|-------------|
| `basic` | Simple text extraction, faster |
| `advanced` | Dynamic/JS-rendered pages, tables, structured data |

## Tips

- **Max 20 URLs per request** - batch larger lists
- **Use `--query` + `--chunks`** to get only relevant content
- **Try `basic` first**, fall back to `advanced` if content is missing
- **Set longer `--timeout`** for slow pages (up to 60s)
- **Check `failed_results`** in JSON output for URLs that couldn't be extracted