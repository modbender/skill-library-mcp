---
name: data-scraper
description: Web page data collection and structured text extraction
version: 1.0.0
author: 무펭이 🐧
---

# data-scraper

**Web Data Scraper** — Extract structured data from web pages using curl + parsing. Lightweight, no browser required. Supports HTML-to-text, table extraction, price monitoring, and batch scraping.

## When to Use

- Extract text content from web pages (articles, blogs, docs)
- Scrape product prices, reviews, or listings
- Monitor pages for changes (price drops, new content)
- Batch-collect data from multiple URLs
- Convert HTML tables to structured formats (JSON/CSV)

## Quick Start

```bash
# Extract readable text from URL
data-scraper fetch "https://example.com/article"

# Extract specific elements
data-scraper extract "https://example.com" --selector "h2, .price"

# Monitor for changes
data-scraper watch "https://example.com/product" --interval 3600
```

## Extraction Modes

### Text Mode (default)
Fetches page and extracts readable content, stripping HTML tags, scripts, and styles. Similar to reader mode.

```bash
data-scraper fetch URL
# Output: clean markdown text
```

### Selector Mode
Target specific CSS selectors for precise extraction.

```bash
data-scraper extract URL --selector ".product-title, .price, .rating"
# Output: matched elements as structured data
```

### Table Mode
Extract HTML tables into structured formats.

```bash
data-scraper table URL --index 0
# Output: JSON array of row objects (header → value mapping)
```

### Link Mode
Extract all links from a page with optional filtering.

```bash
data-scraper links URL --filter "*.pdf"
# Output: filtered list of absolute URLs
```

## Batch Scraping

```bash
# Scrape multiple URLs
data-scraper batch urls.txt --output results/

# With rate limiting
data-scraper batch urls.txt --delay 2000 --output results/
```

`urls.txt` format:
```
https://site1.com/page
https://site2.com/page
https://site3.com/page
```

## Change Monitoring

```bash
# Watch for changes, alert on diff
data-scraper watch URL --selector ".price" --interval 3600

# Compare with previous snapshot
data-scraper diff URL
```

Stores snapshots in `data-scraper/snapshots/` with timestamps. Alerts via notification-hub when changes detected.

## Output Formats

| Format | Flag | Use Case |
|--------|------|----------|
| Text | `--format text` | Reading, summarization |
| JSON | `--format json` | Data processing |
| CSV | `--format csv` | Spreadsheets |
| Markdown | `--format md` | Documentation |

## Headers & Auth

```bash
# Custom headers
data-scraper fetch URL --header "Authorization: Bearer TOKEN"

# Cookie-based auth
data-scraper fetch URL --cookie "session=abc123"

# User-Agent override
data-scraper fetch URL --ua "Mozilla/5.0..."
```

## Rate Limiting & Ethics

- Default: 1 request per second per domain
- Respects `robots.txt` when `--polite` flag is set
- Configurable delay between requests
- Stops on 429 (Too Many Requests) and backs off

## Error Handling

| Error | Behavior |
|-------|----------|
| 404 | Log and skip |
| 403/401 | Warn about auth requirement |
| 429 | Exponential backoff (max 3 retries) |
| Timeout | Retry once with longer timeout |
| SSL error | Warn, option to proceed with `--insecure` |

## Integration

- **web-claude**: Use as fallback when web_fetch isn't enough
- **competitor-watch**: Feed scraped data into competitor analysis
- **seo-audit**: Scrape competitor pages for SEO comparison
- **performance-tracker**: Collect social metrics from public profiles
