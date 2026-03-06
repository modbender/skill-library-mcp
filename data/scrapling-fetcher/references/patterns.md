# Scrapling Patterns Reference

## Fetcher Selection Guide

| Scenario | Fetcher | Notes |
|---|---|---|
| Regular sites, APIs | `Fetcher` | Fastest, HTTP-only |
| Cloudflare, anti-bot | `StealthyFetcher` | Headless Chrome, fingerprint spoofing |
| Heavy JS rendering | `DynamicFetcher` | Full Playwright browser |
| Async pipeline | `AsyncFetcher` | Async equivalent of Fetcher |

## Python Quick Patterns

### Basic HTTP fetch
```python
from scrapling.fetchers import Fetcher
page = Fetcher.get('https://example.com')
print(page.status)  # 200
text = page.get_all_text(ignore_tags=('script', 'style'))
```

### Stealth fetch (bypass Cloudflare)
```python
from scrapling.fetchers import StealthyFetcher
page = StealthyFetcher.fetch('https://protected-site.com', headless=True, network_idle=True)
```

### Dynamic fetch (JS-rendered content)
```python
from scrapling.fetchers import DynamicFetcher
page = DynamicFetcher.fetch('https://spa-site.com', headless=True, network_idle=True)
```

### CSS selector extraction
```python
titles = page.css('h2.title')
for t in titles:
    print(t.text)

# Get attribute
links = page.css('a.product-link')
for a in links:
    print(a.attrib['href'])
```

### XPath extraction
```python
items = page.xpath('//div[@class="item"]/span/text()')
```

### Adaptive scraping (survives site redesigns)
```python
# First run: auto_save=True saves element fingerprints
products = page.css('.product-card', auto_save=True)
# Later runs: adaptive=True finds them even if CSS changed
products = page.css('.product-card', adaptive=True)
```

### Find similar elements
```python
first = page.css('.price')[0]
all_prices = first.find_similar()
```

### Session with cookies
```python
from scrapling.fetchers import FetcherSession
session = FetcherSession()
session.get('https://example.com/login', data={'user': 'x', 'pass': 'y'})
page = session.get('https://example.com/dashboard')
```

### Async usage
```python
import asyncio
from scrapling.fetchers import AsyncFetcher

async def scrape():
    page = await AsyncFetcher.get('https://example.com')
    return page.css('h1')[0].text

asyncio.run(scrape())
```

## CLI Usage

```bash
# Simple text extraction
python3 scrape.py https://example.com

# CSS selector extraction
python3 scrape.py https://example.com --selector "h2.title"

# Extract attribute value
python3 scrape.py https://example.com --selector "a.product" --attr href

# Stealth mode for protected sites
python3 scrape.py https://cloudflare-site.com --mode stealth

# JSON output
python3 scrape.py https://example.com --selector ".price" --json

# Quiet mode (no INFO logs)
python3 scrape.py https://example.com -q
```

## MCP Server Setup

> ⚠️ The MCP server starts a local HTTP service. Only use in trusted environments.

```bash
scrapling mcp
# or
python3 -m scrapling.mcp
```

Add to OpenClaw MCP config (mcporter) to get scraping as a native tool. Confirm with user before starting.
