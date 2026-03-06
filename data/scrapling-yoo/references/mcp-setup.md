# MCP Server Setup

## Installation

```bash
# Base MCP support
pip install scrapling[mcp]

# With browser automation
pip install scrapling[mcp,playwright]
python -m playwright install chromium
```

## OpenClaw Configuration

Add to your OpenClaw MCP config:

```json
{
  "mcpServers": {
    "scrapling": {
      "command": "python",
      "args": ["-m", "scrapling.mcp"]
    }
  }
}
```

Or with environment variables:

```json
{
  "mcpServers": {
    "scrapling": {
      "command": "python",
      "args": ["-m", "scrapling.mcp"],
      "env": {
        "PYTHONPATH": "/path/to/venv/lib/python3.x/site-packages"
      }
    }
  }
}
```

## Available Tools

### fetch_page
Fast HTTP fetch for static pages.

```json
{
  "url": "https://example.com",
  "headers": {"User-Agent": "..."},
  "timeout": 30,
  "impersonate": "chrome"
}
```

### fetch_dynamic
Browser-based fetch for JS-rendered content.

```json
{
  "url": "https://spa.example.com",
  "headless": true,
  "network_idle": true,
  "wait_for": "selector",
  "timeout": 30000
}
```

### fetch_stealthy
Anti-bot fetch with Cloudflare bypass.

```json
{
  "url": "https://protected.example.com",
  "headless": true,
  "solve_cloudflare": true,
  "google_search": false
}
```

### css_select
Extract data using CSS selectors.

```json
{
  "html": "<html>...</html>",
  "selector": ".product .title::text",
  "first_only": false,
  "adaptive": false,
  "auto_save": false
}
```

### xpath_select
Extract data using XPath.

```json
{
  "html": "<html>...</html>",
  "xpath": "//div[@class='product']/h2/text()",
  "first_only": false
}
```

### start_spider
Run a spider crawl.

```json
{
  "name": "my_spider",
  "start_urls": ["https://example.com/products"],
  "concurrent_requests": 10,
  "download_delay": 1.0,
  "crawldir": "./crawl_data"
}
```

## Usage via mcporter

```bash
# Fetch a page
mcporter call scrapling fetch_page --url "https://example.com"

# Extract with CSS
mcporter call scrapling css_select \\
  --html "$(cat page.html)" \\
  --selector ".title::text"

# Stealth fetch
mcporter call scrapling fetch_stealthy \\
  --url "https://protected.com" \\
  --solve-cloudflare true
```

## Benefits of MCP Mode

1. **Reduced Token Usage** — Scrapling extracts data BEFORE passing to AI
2. **Faster Operations** — Direct function calls vs text generation
3. **Structured Output** — JSON responses, not parsed text
4. **Error Handling** — Proper exceptions and status codes

## Demo Video

See Scrapling MCP in action: https://www.youtube.com/watch?v=qyFk3ZNwOxE
