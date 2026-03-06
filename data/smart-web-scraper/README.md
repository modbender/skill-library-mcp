# Smart Web Scraper

Extract structured data from any web page into JSON, CSV, or Markdown.

## Features

- **CSS Selectors** — Target specific elements (products, prices, articles, contacts)
- **Auto Table Detection** — Find and extract HTML tables automatically
- **Link Extraction** — Get all links with text, filterable by internal/external
- **Page Structure** — Extract title, meta tags, headings, and page outline
- **Multi-Page Crawl** — Follow pagination and scrape across multiple pages
- **Multiple Formats** — Output as JSON, CSV, Markdown, or plain text
- **Respectful Crawling** — Built-in rate limiting, robots.txt compliance
- **No API Keys** — Works out of the box, no external services needed

## Installation

### As an OpenClaw/ClawHub skill

```bash
clawhub install smart-web-scraper
```

### Standalone

```bash
git clone https://github.com/YOUR_USERNAME/smart-web-scraper.git
cd smart-web-scraper
pip install beautifulsoup4 lxml  # Required dependencies
```

## Usage

```bash
# Extract text from a page
python scripts/scraper.py extract "https://example.com"

# Extract specific elements
python scripts/scraper.py extract "https://example.com/products" -s ".product-card" -f json

# Extract all tables as CSV
python scripts/scraper.py tables "https://example.com/pricing" -f csv -o pricing.csv

# Get all links
python scripts/scraper.py links "https://example.com" --external

# Page structure overview
python scripts/scraper.py structure "https://example.com"

# Multi-page crawl
python scripts/scraper.py crawl "https://example.com/blog/page/1" --pages 5 -s ".post" -f json
```

## Use Cases

- **Price monitoring** — Scrape product pages for pricing data
- **Lead generation** — Extract contact info from business directories
- **Content aggregation** — Collect articles, blog posts, job listings
- **Competitive analysis** — Gather competitor product/feature data
- **Research** — Extract data from academic or government websites
- **SEO auditing** — Analyze page structure, headings, and link profiles

## Output Examples

### JSON format (`-f json`)
```json
[
  {
    "text": "Premium Plan - $49/month",
    "tag": "div",
    "class": "pricing-card",
    "attributes": {"data-plan": "premium"}
  }
]
```

### CSV format (`-f csv`)
```
text,tag,class
"Premium Plan - $49/month",div,pricing-card
"Basic Plan - $19/month",div,pricing-card
```

## Limitations

- Static HTML only (no JavaScript rendering)
- Respects rate limits and robots.txt by default
- Some sites may block automated access

## License

MIT

## Author

Built by OpenClaw Setup Services — Professional AI agent configuration and custom skill development.

**Need custom scraping solutions?** Contact us for tailored data extraction pipelines.
