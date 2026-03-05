---
name: scrapling
description: Advanced web scraping with anti-bot bypass, JavaScript support, and adaptive selectors. Use when scraping websites with Cloudflare protection, dynamic content, or frequent UI changes.
homepage: https://github.com/D4Vinci/Scrapling
version: 1.0.0
metadata:
  clawdbot:
    emoji: 🕷️
    requires:
      bins: [python3, pip]
      python_packages: [scrapling]
    category: web-scraping
    author: OpenClaw Community
---

# Scrapling Web Scraping Skill

Use Scrapling to scrape modern websites, including those with anti-bot protection, JavaScript-rendered content, and adaptive element tracking.

## When to Use This Skill

- User asks to scrape a website or extract data from a URL
- Need to bypass Cloudflare, bot detection, or anti-scraping measures
- Need to handle JavaScript-rendered/dynamic content (React, Vue, etc.)
- Website requires login or session management
- Website structure changes frequently (adaptive selectors)
- Need to scrape multiple pages with rate limiting

## Commands

All commands use the `scrape.py` script in this skill's directory.

### Basic HTTP Scraping (Fast)

```bash
python scrape.py \
  --url "https://example.com" \
  --selector ".product" \
  --output products.json
```

**Use when:** Static HTML, no JavaScript, no bot protection

### Stealth Mode (Bypass Anti-Bot)

```bash
python scrape.py \
  --url "https://nopecha.com/demo/cloudflare" \
  --stealth \
  --selector "#content" \
  --output data.json
```

**Use when:** Cloudflare protection, bot detection, fingerprinting

**Features:**
- Bypasses Cloudflare Turnstile automatically
- Browser fingerprint spoofing
- Headless browser mode

### Dynamic/JavaScript Content

```bash
python scrape.py \
  --url "https://spa-website.com" \
  --dynamic \
  --selector ".loaded-content" \
  --wait-for ".loaded-content" \
  --output data.json
```

**Use when:** React/Vue/Angular apps, lazy-loaded content, AJAX

**Features:**
- Full Playwright browser automation
- Wait for elements to load
- Network idle detection

### Adaptive Selectors (Survives Website Changes)

```bash
# First time - save the selector pattern
python scrape.py \
  --url "https://example.com" \
  --selector ".product-card" \
  --adaptive-save \
  --output products.json

# Later, if website structure changes
python scrape.py \
  --url "https://example.com" \
  --adaptive \
  --output products.json
```

**Use when:** Website frequently redesigns, need robust scraping

**How it works:**
- First run: Saves element patterns/structure
- Later runs: Uses similarity algorithms to relocate moved elements
- Auto-updates selector cache

### Session Management (Login Required)

```bash
# Login and save session
python scrape.py \
  --url "https://example.com/dashboard" \
  --stealth \
  --login \
  --username "user@example.com" \
  --password "password123" \
  --session-name "my-session" \
  --selector ".protected-data" \
  --output data.json

# Reuse saved session (no login needed)
python scrape.py \
  --url "https://example.com/another-page" \
  --stealth \
  --session-name "my-session" \
  --selector ".more-data" \
  --output more_data.json
```

**Use when:** Content requires authentication, multi-step scraping

### Extract Specific Data Types

**Text only:**
```bash
python scrape.py \
  --url "https://example.com" \
  --selector ".content" \
  --extract text \
  --output content.txt
```

**Markdown:**
```bash
python scrape.py \
  --url "https://docs.example.com" \
  --selector "article" \
  --extract markdown \
  --output article.md
```

**Attributes:**
```bash
# Extract href links
python scrape.py \
  --url "https://example.com" \
  --selector "a.product-link" \
  --extract attr:href \
  --output links.json
```

**Multiple fields:**
```bash
python scrape.py \
  --url "https://example.com/products" \
  --selector ".product" \
  --fields "title:.title::text,price:.price::text,link:a::attr(href)" \
  --output products.json
```

### Advanced Options

**Proxy support:**
```bash
python scrape.py \
  --url "https://example.com" \
  --proxy "http://user:pass@proxy.com:8080" \
  --selector ".content"
```

**Rate limiting:**
```bash
python scrape.py \
  --url "https://example.com" \
  --selector ".content" \
  --delay 2  # 2 seconds between requests
```

**Custom headers:**
```bash
python scrape.py \
  --url "https://api.example.com" \
  --headers '{"Authorization": "Bearer token123"}' \
  --selector "body"
```

**Screenshot (for debugging):**
```bash
python scrape.py \
  --url "https://example.com" \
  --stealth \
  --screenshot debug.png
```

## Python API (For Custom Scripts)

You can also use Scrapling directly in Python scripts:

```python
from scrapling.fetchers import Fetcher, StealthyFetcher, DynamicFetcher

# Basic HTTP request
page = Fetcher.get('https://example.com')
products = page.css('.product')
for product in products:
    title = product.css('.title::text').get()
    price = product.css('.price::text').get()
    print(f"{title}: {price}")

# Stealth mode (bypass anti-bot)
page = StealthyFetcher.fetch('https://protected-site.com', headless=True)
data = page.css('.content').getall()

# Dynamic content (full browser)
page = DynamicFetcher.fetch('https://spa-app.com', network_idle=True)
items = page.css('.loaded-item').getall()

# Sessions (login)
from scrapling.fetchers import StealthySession

with StealthySession(headless=True) as session:
    # Login
    login_page = session.fetch('https://example.com/login')
    login_page.fill('#username', 'user@example.com')
    login_page.fill('#password', 'password123')
    login_page.click('#submit')
    
    # Access protected content
    protected_page = session.fetch('https://example.com/dashboard')
    data = protected_page.css('.private-data').getall()
```

## Output Formats

- **JSON** (default): `--output data.json`
- **JSONL** (streaming): `--output data.jsonl`
- **CSV**: `--output data.csv`
- **TXT** (text only): `--output data.txt`
- **MD** (markdown): `--output data.md`
- **HTML** (raw): `--output data.html`

## Selector Types

Scrapling supports multiple selector formats:

**CSS selectors:**
```bash
--selector ".product"
--selector "div.container > p.text"
--selector "a[href*='product']"
```

**XPath selectors:**
```bash
--selector "//div[@class='product']"
--selector "//a[contains(@href, 'product')]"
```

**Pseudo-elements (like Scrapy):**
```bash
--selector ".product::text"          # Text content
--selector "a::attr(href)"           # Attribute value
--selector ".price::text::strip"     # Text with whitespace removed
```

**Combined selectors:**
```bash
--selector ".product .title::text"   # Nested elements
```

## Troubleshooting

**Issue: "Element not found"**
- Try `--dynamic` if content is JavaScript-loaded
- Use `--wait-for SELECTOR` to wait for element
- Use `--screenshot` to debug what's visible

**Issue: "Cloudflare blocking"**
- Use `--stealth` mode
- Add `--solve-cloudflare` flag (enabled by default in stealth)
- Try `--delay 2` to slow down requests

**Issue: "Login not working"**
- Use `--headless false` to see browser interaction
- Check credentials are correct
- Website might use CAPTCHA (manual intervention needed)

**Issue: "Selector broke after website update"**
- Use `--adaptive` mode to auto-relocate elements
- Re-run with `--adaptive-save` to update saved patterns

## Examples

### Scrape Hacker News Front Page
```bash
python scrape.py \
  --url "https://news.ycombinator.com" \
  --selector ".athing" \
  --fields "title:.titleline>a::text,link:.titleline>a::attr(href)" \
  --output hn_stories.json
```

### Scrape Protected Site with Login
```bash
python scrape.py \
  --url "https://example.com/data" \
  --stealth \
  --login \
  --username "user@example.com" \
  --password "secret" \
  --session-name "example-session" \
  --selector ".data-table tr" \
  --output protected_data.json
```

### Monitor Price Changes
```bash
# Save initial selector pattern
python scrape.py \
  --url "https://store.com/product/123" \
  --selector ".price" \
  --adaptive-save \
  --output price.txt

# Later, check price (even if page redesigned)
python scrape.py \
  --url "https://store.com/product/123" \
  --adaptive \
  --output price_new.txt
```

### Scrape Dynamic JavaScript App
```bash
python scrape.py \
  --url "https://react-app.com/data" \
  --dynamic \
  --wait-for ".loaded-content" \
  --selector ".item" \
  --fields "name:.name::text,value:.value::text" \
  --output app_data.json
```

## Notes

- **First run**: Scrapling downloads browsers (~500MB). This is automatic.
- **Sessions**: Saved in `sessions/` directory, reusable across runs
- **Adaptive cache**: Saved in `selector_cache.json`, auto-updated
- **Rate limiting**: Always respect `robots.txt` and add delays for ethical scraping
- **Legal**: Use only on sites you have permission to scrape

## Dependencies

Installed automatically when skill is installed:
- scrapling[all] - Main library with all features
- pyyaml - For config file support

## Skill Structure

```
scrapling/
├── SKILL.md           # This file
├── scrape.py          # Main CLI script
├── requirements.txt   # Python dependencies
├── sessions/          # Saved browser sessions
├── selector_cache.json # Adaptive selector patterns
└── examples/          # Example scripts
    ├── basic.py
    ├── stealth.py
    ├── dynamic.py
    └── adaptive.py
```

## Advanced: Custom Python Scripts

For complex scraping tasks, you can create custom Python scripts in this directory:

```python
# custom_scraper.py
from scrapling.fetchers import StealthyFetcher
from scrapling.spiders import Spider, Response
import json

class MySpider(Spider):
    name = "custom"
    start_urls = ["https://example.com/page1"]
    
    async def parse(self, response: Response):
        for item in response.css('.product'):
            yield {
                "title": item.css('.title::text').get(),
                "price": item.css('.price::text').get()
            }
        
        # Follow pagination
        next_page = response.css('.next-page::attr(href)').get()
        if next_page:
            yield response.follow(next_page)

# Run spider
result = MySpider().start()
with open('output.json', 'w') as f:
    json.dump(result.items, f, indent=2)
```

Run with:
```bash
python custom_scraper.py
```

---

**Questions?** Check Scrapling docs: https://scrapling.readthedocs.io
