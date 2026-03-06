---
name: Web Scraping & Data Extraction Engine
description: Complete web scraping methodology — legal compliance, architecture design, anti-detection, data pipelines, and production operations. Use when building scrapers, extracting web data, monitoring competitors, or automating data collection at scale.
---

# Web Scraping & Data Extraction Engine

## Quick Health Check (Run First)

Score your scraping operation (2 points each):

| Signal | Healthy | Unhealthy |
|--------|---------|-----------|
| Legal compliance | robots.txt checked, ToS reviewed | Scraping blindly |
| Architecture | Tool matches site complexity | Using Puppeteer for static HTML |
| Anti-detection | Rotation, delays, fingerprint diversity | Single IP, no delays |
| Data quality | Validation + dedup pipeline | Raw dumps, no cleaning |
| Error handling | Retry logic, circuit breakers | Crashes on first 403 |
| Monitoring | Success rates tracked, alerts set | No visibility |
| Storage | Structured, deduplicated, versioned | Flat files, duplicates |
| Scheduling | Appropriate frequency, off-peak | Hammering during business hours |

**Score: /16** → 12+: Production-ready | 8-11: Needs work | <8: Stop and redesign

---

## Phase 1: Legal & Ethical Foundation

### Pre-Scrape Compliance Checklist

```yaml
compliance_brief:
  target_domain: ""
  date_assessed: ""
  
  robots_txt:
    checked: false
    target_paths_allowed: false
    crawl_delay_specified: ""
    ai_bot_rules: ""  # Many sites now block AI crawlers specifically
    
  terms_of_service:
    reviewed: false
    scraping_mentioned: false
    scraping_prohibited: false
    api_available: false
    api_sufficient: false
    
  data_classification:
    type: ""  # public-factual | public-personal | behind-auth | copyrighted
    contains_pii: false
    pii_types: []  # name, email, phone, address, photo
    gdpr_applies: false  # EU residents' data
    ccpa_applies: false  # California residents' data
    
  legal_risk: ""  # low | medium | high | do-not-scrape
  decision: ""  # proceed | use-api | request-permission | abandon
  justification: ""
```

### Legal Landscape Quick Reference

| Scenario | Risk Level | Key Case Law |
|----------|-----------|--------------|
| Public data, no login, robots.txt allows | LOW | hiQ v. LinkedIn (2022) |
| Public data, robots.txt disallows | MEDIUM | Meta v. Bright Data (2024) |
| Behind authentication | HIGH | Van Buren v. US (2021), CFAA |
| Personal data without consent | HIGH | GDPR Art. 6, CCPA §1798.100 |
| Republishing copyrighted content | HIGH | Copyright Act §106 |
| Price/product comparison | LOW | eBay v. Bidder's Edge (fair use) |
| Academic/research use | LOW-MEDIUM | Varies by jurisdiction |
| Bypassing anti-bot measures | HIGH | CFAA "exceeds authorized access" |

### Decision Rules

1. **API exists and covers your needs?** → Use the API. Always.
2. **robots.txt disallows your target?** → Respect it unless you have written permission.
3. **Data behind login?** → Do not scrape without explicit authorization.
4. **Contains PII?** → GDPR/CCPA compliance required before collection.
5. **Copyrighted content?** → Extract facts/data points only, never full content.
6. **Site explicitly prohibits scraping?** → Request permission or find alternative source.

### AI Crawler Considerations (2025+)

Many sites now specifically block AI-related crawlers:

```
# Common AI bot blocks in robots.txt
User-agent: GPTBot
User-agent: ChatGPT-User
User-agent: Google-Extended
User-agent: CCBot
User-agent: anthropic-ai
User-agent: ClaudeBot
User-agent: Bytespider
User-agent: PerplexityBot
```

**Rule**: If collecting data for AI training, check for these specific blocks.

---

## Phase 2: Architecture Decision

### Tool Selection Matrix

| Tool/Approach | Best For | Speed | JS Support | Complexity | Cost |
|---------------|----------|-------|------------|------------|------|
| HTTP client (requests/axios) | Static HTML, APIs | ⚡⚡⚡ | ❌ | Low | Free |
| Beautiful Soup / Cheerio | Static HTML parsing | ⚡⚡⚡ | ❌ | Low | Free |
| Scrapy | Large-scale structured crawling | ⚡⚡⚡ | Plugin | Medium | Free |
| Playwright / Puppeteer | JS-rendered, SPAs, interactions | ⚡ | ✅ | Medium | Free |
| Selenium | Legacy, browser automation | ⚡ | ✅ | High | Free |
| Crawlee | Hybrid (HTTP + browser fallback) | ⚡⚡ | ✅ | Medium | Free |
| Firecrawl / ScrapingBee | Managed, anti-bot bypass | ⚡⚡ | ✅ | Low | Paid |
| Bright Data / Oxylabs | Enterprise, proxy + browser | ⚡⚡ | ✅ | Low | Paid |

### Decision Tree

```
Is the content in the initial HTML source?
├── YES → Is the site structure consistent?
│   ├── YES → Static scraper (requests + BeautifulSoup/Cheerio)
│   └── NO → Scrapy with custom parsers
└── NO → Does the page require user interaction?
    ├── YES → Playwright/Puppeteer with interaction scripts
    └── NO → Playwright in non-interactive mode
        └── At scale (>10K pages)? → Crawlee (hybrid mode)
            └── Heavy anti-bot? → Managed service (Firecrawl/ScrapingBee)
```

### Architecture Brief YAML

```yaml
scraping_project:
  name: ""
  objective: ""  # What data, why, how often
  
  targets:
    - domain: ""
      pages_estimated: 0
      rendering: "static" | "javascript" | "spa"
      anti_bot: "none" | "basic" | "cloudflare" | "advanced"
      rate_limit: ""  # requests per second safe limit
      
  tool_selected: ""
  justification: ""
  
  data_schema:
    fields: []
    output_format: ""  # json | csv | database
    
  schedule:
    frequency: ""  # once | hourly | daily | weekly
    preferred_time: ""  # off-peak for target timezone
    
  infrastructure:
    proxy_needed: false
    proxy_type: ""  # residential | datacenter | mobile
    storage: ""
    monitoring: ""
```

---

## Phase 3: Request Engineering

### HTTP Request Best Practices

```python
# Python example — production request pattern
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

session = requests.Session()

# Retry strategy
retry = Retry(
    total=3,
    backoff_factor=1,      # 1s, 2s, 4s
    status_forcelist=[429, 500, 502, 503, 504],
    respect_retry_after_header=True
)
session.mount("https://", HTTPAdapter(max_retries=retry))

# Realistic headers
session.headers.update({
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Cache-Control": "no-cache",
})
```

### Header Rotation Strategy

Rotate these to avoid fingerprinting:

| Header | Rotation Pool Size | Notes |
|--------|-------------------|-------|
| User-Agent | 20-50 real browser UAs | Match OS distribution |
| Accept-Language | 5-10 locale combos | Match proxy geo |
| Sec-Ch-Ua | Match User-Agent | Chrome/Edge/Brave |
| Referer | Vary per request | Previous page or search engine |

### Rate Limiting Rules

| Site Type | Safe Delay | Aggressive (risky) |
|-----------|-----------|-------------------|
| Small business site | 5-10 seconds | 2-3 seconds |
| Medium site | 2-5 seconds | 1-2 seconds |
| Large platform (Amazon, etc.) | 3-5 seconds | 1 second |
| API endpoint | Per API docs | Never exceed |
| robots.txt crawl-delay | Respect exactly | Never below |

**Rules:**
1. Always respect `Crawl-delay` in robots.txt
2. Add random jitter (±30%) to avoid pattern detection
3. Slow down during business hours for smaller sites
4. Respect `Retry-After` headers — they mean it
5. Watch for 429s — back off exponentially (2x each time)

---

## Phase 4: Parsing & Extraction

### CSS Selector Strategy (Priority Order)

1. **Data attributes** → `[data-product-id]`, `[data-price]` (most stable)
2. **Semantic IDs** → `#product-title`, `#price` (stable but can change)
3. **ARIA attributes** → `[aria-label="Price"]` (accessibility, fairly stable)
4. **Semantic HTML** → `article`, `main`, `nav` (structural, stable)
5. **Class names** → `.product-card` (can change with redesigns)
6. **XPath position** → `//div[3]/span[2]` (FRAGILE — last resort)

### Extraction Patterns

**Structured data first** — Check before writing CSS selectors:

```python
# 1. Check JSON-LD (best source — structured, clean)
import json
from bs4 import BeautifulSoup

soup = BeautifulSoup(html, 'html.parser')
for script in soup.find_all('script', type='application/ld+json'):
    data = json.loads(script.string)
    # Often contains: Product, Article, Organization, etc.

# 2. Check Open Graph meta tags
og_title = soup.find('meta', property='og:title')
og_price = soup.find('meta', property='product:price:amount')

# 3. Check microdata
items = soup.find_all(itemtype=True)

# 4. Fall back to CSS selectors only if above are empty
```

**Table extraction pattern:**

```python
import pandas as pd

# Quick table extraction
tables = pd.read_html(html)  # Returns list of DataFrames

# For complex tables with merged cells
def extract_table(soup, selector):
    table = soup.select_one(selector)
    headers = [th.get_text(strip=True) for th in table.select('thead th')]
    rows = []
    for tr in table.select('tbody tr'):
        cells = [td.get_text(strip=True) for td in tr.select('td')]
        rows.append(dict(zip(headers, cells)))
    return rows
```

**Pagination handling:**

```python
# Pattern 1: Next button
while True:
    # ... scrape current page ...
    next_link = soup.select_one('a.next-page, [rel="next"], .pagination .next a')
    if not next_link or not next_link.get('href'):
        break
    url = urljoin(base_url, next_link['href'])
    
# Pattern 2: API pagination (infinite scroll sites)
page = 1
while True:
    resp = session.get(f"{api_url}?page={page}&limit=50")
    data = resp.json()
    if not data.get('results'):
        break
    # ... process results ...
    page += 1

# Pattern 3: Cursor-based
cursor = None
while True:
    params = {"limit": 50}
    if cursor:
        params["cursor"] = cursor
    resp = session.get(api_url, params=params)
    data = resp.json()
    # ... process ...
    cursor = data.get('next_cursor')
    if not cursor:
        break
```

### JavaScript-Rendered Content

```python
# Playwright pattern for JS-rendered pages
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    context = browser.new_context(
        viewport={"width": 1920, "height": 1080},
        user_agent="Mozilla/5.0 ...",
    )
    page = context.new_page()
    
    # Block unnecessary resources (speed + stealth)
    page.route("**/*.{png,jpg,jpeg,gif,svg,woff,woff2}", 
               lambda route: route.abort())
    
    page.goto(url, wait_until="networkidle")
    
    # Wait for specific content (better than arbitrary sleep)
    page.wait_for_selector('[data-product-id]', timeout=10000)
    
    # Extract after JS rendering
    content = page.content()
    # ... parse with BeautifulSoup/Cheerio ...
    
    browser.close()
```

---

## Phase 5: Anti-Detection & Stealth

### Detection Signals (What Sites Check)

| Signal | Detection Method | Mitigation |
|--------|-----------------|------------|
| IP reputation | IP blacklists, datacenter ranges | Residential proxies |
| Request rate | Requests/min from same IP | Rate limiting + jitter |
| TLS fingerprint | JA3/JA4 hash matching | Use real browser or curl-impersonate |
| Browser fingerprint | Canvas, WebGL, fonts | Playwright with stealth plugin |
| JavaScript challenges | Cloudflare Turnstile, hCaptcha | Managed browser services |
| Cookie/session behavior | Missing cookies, no history | Full session management |
| Navigation pattern | Direct URL hits, no referrer | Simulate natural browsing |
| Mouse/keyboard events | No interaction telemetry | Event simulation (Playwright) |
| Header consistency | Mismatched headers vs UA | Header sets that match |

### Proxy Strategy

```yaml
proxy_strategy:
  # Tier 1: Free/Datacenter (for non-protected sites)
  basic:
    type: "datacenter"
    cost: "$1-5/GB"
    success_rate: "60-80%"
    use_for: "APIs, small sites, no anti-bot"
    
  # Tier 2: Residential (for most protected sites)
  standard:
    type: "residential"
    cost: "$5-15/GB"
    success_rate: "90-95%"
    use_for: "Cloudflare, major platforms"
    rotation: "per-request or sticky 10min"
    
  # Tier 3: Mobile/ISP (for maximum stealth)
  premium:
    type: "mobile"
    cost: "$15-30/GB"
    success_rate: "95-99%"
    use_for: "Aggressive anti-bot, social media"
    
  rules:
    - Start with cheapest tier, escalate only on blocks
    - Match proxy geo to target audience geo
    - Rotate on 403/429, not every request
    - Use sticky sessions for multi-page scrapes
    - Monitor proxy health — remove slow/blocked IPs
```

### Playwright Stealth Configuration

```python
# Essential stealth for Playwright
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(
        headless=True,
        args=[
            '--disable-blink-features=AutomationControlled',
            '--disable-features=IsolateOrigins,site-per-process',
        ]
    )
    context = browser.new_context(
        viewport={"width": 1920, "height": 1080},
        locale="en-US",
        timezone_id="America/New_York",
        geolocation={"latitude": 40.7128, "longitude": -74.0060},
        permissions=["geolocation"],
    )
    
    # Remove automation indicators
    page = context.new_page()
    page.add_init_script("""
        Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
        Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3]});
    """)
```

### Cloudflare Bypass Decision

```
Cloudflare detected?
├── JS Challenge only → Playwright with stealth + residential proxy
├── Turnstile CAPTCHA → Managed service (ScrapingBee/Bright Data)
├── Under Attack Mode → Wait, try later, or managed service
└── WAF blocking → Different approach needed
    ├── Check for API endpoints (network tab)
    ├── Check for mobile app API
    └── Consider if data is available elsewhere
```

---

## Phase 6: Data Pipeline & Quality

### Data Validation Rules

```python
# Validation pattern — validate BEFORE storing
from dataclasses import dataclass, field
from typing import Optional
import re
from datetime import datetime

@dataclass
class ScrapedProduct:
    url: str
    title: str
    price: Optional[float]
    currency: str = "USD"
    scraped_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    
    def validate(self) -> list[str]:
        errors = []
        if not self.url.startswith('http'):
            errors.append("Invalid URL")
        if not self.title or len(self.title) < 3:
            errors.append("Title too short or missing")
        if self.price is not None and self.price < 0:
            errors.append("Negative price")
        if self.price is not None and self.price > 1_000_000:
            errors.append("Price suspiciously high — verify")
        if self.currency not in ("USD", "EUR", "GBP", "BTC"):
            errors.append(f"Unknown currency: {self.currency}")
        return errors
```

### Deduplication Strategy

| Method | When to Use | Implementation |
|--------|------------|----------------|
| URL-based | Pages with unique URLs | Hash the canonical URL |
| Content hash | Same URL, changing content | MD5/SHA256 of key fields |
| Fuzzy matching | Near-duplicate detection | Jaccard similarity > 0.85 |
| Composite key | Multi-field uniqueness | Hash(domain + product_id + variant) |

```python
import hashlib

def dedup_key(item: dict, fields: list[str]) -> str:
    """Generate dedup key from selected fields."""
    values = "|".join(str(item.get(f, "")) for f in fields)
    return hashlib.sha256(values.encode()).hexdigest()

# Usage
seen = set()
for item in scraped_items:
    key = dedup_key(item, ["url", "product_id"])
    if key not in seen:
        seen.add(key)
        clean_items.append(item)
```

### Data Cleaning Pipeline

```
Raw HTML → Parse → Extract → Validate → Clean → Deduplicate → Store
                                ↓
                          Quarantine (failed validation)
```

**Common cleaning operations:**

| Problem | Solution |
|---------|----------|
| HTML entities (`&amp;`) | `html.unescape()` |
| Extra whitespace | `" ".join(text.split())` |
| Unicode issues | `unicodedata.normalize('NFKD', text)` |
| Price in text ("$49.99") | Regex: `r'[\$£€]?([\d,]+\.?\d*)'` |
| Date formats vary | `dateutil.parser.parse()` with `dayfirst` flag |
| Relative URLs | `urllib.parse.urljoin(base, relative)` |
| Encoding issues | `chardet.detect()` then decode |

---

## Phase 7: Storage & Export

### Storage Decision Guide

| Volume | Frequency | Query Needs | Recommendation |
|--------|-----------|-------------|----------------|
| <10K records | One-time | None | JSON/CSV files |
| <10K records | Recurring | Simple lookups | SQLite |
| 10K-1M records | Recurring | Complex queries | PostgreSQL |
| 1M+ records | Continuous | Analytics | PostgreSQL + partitioning |
| Append-only logs | Continuous | Time-series | ClickHouse / TimescaleDB |

### SQLite Pattern (Most Common)

```python
import sqlite3
import json
from datetime import datetime

def init_db(path="scraper_data.db"):
    conn = sqlite3.connect(path)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS items (
            id INTEGER PRIMARY KEY,
            url TEXT UNIQUE,
            data JSON NOT NULL,
            scraped_at TEXT DEFAULT (datetime('now')),
            updated_at TEXT,
            checksum TEXT
        )
    """)
    conn.execute("CREATE INDEX IF NOT EXISTS idx_url ON items(url)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_scraped ON items(scraped_at)")
    return conn

def upsert(conn, url, data, checksum):
    conn.execute("""
        INSERT INTO items (url, data, checksum) VALUES (?, ?, ?)
        ON CONFLICT(url) DO UPDATE SET
            data = excluded.data,
            updated_at = datetime('now'),
            checksum = excluded.checksum
        WHERE items.checksum != excluded.checksum
    """, (url, json.dumps(data), checksum))
    conn.commit()
```

### Export Formats

```python
# CSV export
import csv
def to_csv(items, path, fields):
    with open(path, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(items)

# JSON Lines (best for large datasets — streaming)
def to_jsonl(items, path):
    with open(path, 'w') as f:
        for item in items:
            f.write(json.dumps(item) + '\n')

# Incremental export (only new/changed since last export)
def export_since(conn, last_export_time):
    cursor = conn.execute(
        "SELECT data FROM items WHERE scraped_at > ? OR updated_at > ?",
        (last_export_time, last_export_time)
    )
    return [json.loads(row[0]) for row in cursor]
```

---

## Phase 8: Error Handling & Resilience

### Error Classification

| HTTP Code | Meaning | Action |
|-----------|---------|--------|
| 200 | Success | Process normally |
| 301/302 | Redirect | Follow (max 5 hops) |
| 403 | Forbidden/blocked | Rotate proxy, slow down |
| 404 | Not found | Log, skip, mark URL dead |
| 429 | Rate limited | Respect Retry-After, back off 2x |
| 500-504 | Server error | Retry 3x with backoff |
| Connection timeout | Network issue | Retry with different proxy |
| SSL error | Certificate issue | Log, investigate, skip |

### Circuit Breaker Pattern

```python
class CircuitBreaker:
    def __init__(self, failure_threshold=5, reset_timeout=300):
        self.failures = 0
        self.threshold = failure_threshold
        self.reset_timeout = reset_timeout
        self.last_failure = 0
        self.state = "closed"  # closed | open | half-open
    
    def record_failure(self):
        self.failures += 1
        self.last_failure = time.time()
        if self.failures >= self.threshold:
            self.state = "open"
            # Alert: "Circuit open — too many failures"
    
    def record_success(self):
        self.failures = 0
        self.state = "closed"
    
    def can_proceed(self):
        if self.state == "closed":
            return True
        if self.state == "open":
            if time.time() - self.last_failure > self.reset_timeout:
                self.state = "half-open"
                return True  # Try one request
            return False
        return True  # half-open: allow attempt
```

### Checkpoint & Resume

```python
import json
from pathlib import Path

class Checkpointer:
    def __init__(self, path="checkpoint.json"):
        self.path = Path(path)
        self.state = self._load()
    
    def _load(self):
        if self.path.exists():
            return json.loads(self.path.read_text())
        return {"completed_urls": [], "last_page": 0, "cursor": None}
    
    def save(self):
        self.path.write_text(json.dumps(self.state))
    
    def is_done(self, url):
        return url in self.state["completed_urls"]
    
    def mark_done(self, url):
        self.state["completed_urls"].append(url)
        if len(self.state["completed_urls"]) % 50 == 0:
            self.save()  # Periodic save
```

---

## Phase 9: Monitoring & Operations

### Scraper Health Dashboard

```yaml
dashboard:
  real_time:
    - metric: "requests_per_minute"
      alert_if: "> 60 for small sites"
    - metric: "success_rate"
      alert_if: "< 90%"
    - metric: "avg_response_time_ms"
      alert_if: "> 5000"
    - metric: "blocked_rate"
      alert_if: "> 10%"
      
  per_run:
    - metric: "pages_scraped"
    - metric: "items_extracted"
    - metric: "items_validated"
    - metric: "items_deduplicated"
    - metric: "new_items"
    - metric: "updated_items"
    - metric: "errors_by_type"
    - metric: "run_duration"
    - metric: "proxy_cost"
    
  weekly:
    - metric: "data_freshness"
      description: "% of records updated in last 7 days"
    - metric: "site_structure_changes"
      description: "Selectors that stopped matching"
    - metric: "total_cost"
      description: "Proxy + compute + storage"
```

### Breakage Detection

Sites redesign. Selectors break. Detect it early:

```python
def health_check(results: list[dict], expected_fields: list[str]) -> dict:
    """Check if scraper is still extracting correctly."""
    total = len(results)
    if total == 0:
        return {"status": "CRITICAL", "message": "Zero results — likely broken"}
    
    field_coverage = {}
    for field in expected_fields:
        filled = sum(1 for r in results if r.get(field))
        coverage = filled / total
        field_coverage[field] = coverage
        
    issues = []
    for field, coverage in field_coverage.items():
        if coverage < 0.5:
            issues.append(f"{field}: {coverage:.0%} fill rate (expected >50%)")
    
    if issues:
        return {"status": "WARNING", "issues": issues}
    return {"status": "OK", "field_coverage": field_coverage}
```

### Operational Runbook

**Daily:**
- Check success rate per target domain
- Review error logs for new patterns
- Verify data freshness

**Weekly:**
- Compare extraction counts vs baseline (>20% drop = investigate)
- Review proxy spend
- Spot-check 10 random records for accuracy

**Monthly:**
- Full selector validation against live pages
- Review legal compliance (robots.txt changes, ToS updates)
- Cost optimization review
- Prune dead URLs from queue

---

## Phase 10: Common Scraping Patterns

### Pattern 1: E-commerce Price Monitor

```yaml
use_case: "Track competitor prices daily"
tool: "requests + BeautifulSoup"
schedule: "Daily at 03:00 UTC (off-peak)"
targets: ["competitor-a.com/products", "competitor-b.com/api"]
data:
  - product_id
  - product_name
  - price
  - currency
  - in_stock
  - scraped_at
storage: "SQLite with price history"
alerts: "Price change > 10% → notify"
```

### Pattern 2: Job Board Aggregator

```yaml
use_case: "Aggregate job listings from multiple boards"
tool: "Scrapy with per-site spiders"
schedule: "Every 6 hours"
targets: ["board-a.com", "board-b.com", "board-c.com"]
data:
  - title
  - company
  - location
  - salary_range
  - posted_date
  - url
  - source
dedup: "Hash(title + company + location)"
storage: "PostgreSQL"
```

### Pattern 3: News & Content Monitor

```yaml
use_case: "Monitor industry news mentions"
tool: "requests + RSS feeds (preferred) + web fallback"
schedule: "Every 30 minutes"
approach:
  1: "RSS/Atom feeds (fastest, cleanest)"
  2: "Google News RSS for topic"
  3: "Direct scraping if no feed"
data:
  - headline
  - source
  - url
  - published_at
  - snippet
  - sentiment
alerts: "Keyword match → immediate notification"
```

### Pattern 4: Social Media Intelligence

```yaml
use_case: "Track brand mentions and sentiment"
tool: "Official APIs (always) + web search fallback"
rules:
  - NEVER scrape social platforms directly — use APIs
  - Twitter/X: Official API ($100/mo basic)
  - Reddit: Official API (free tier available)
  - LinkedIn: No scraping (aggressive legal action)
  - Instagram: Official API only (Meta Business)
fallback: "Brave/Google search for public mentions"
```

### Pattern 5: Real Estate Listings

```yaml
use_case: "Track property listings and prices"
tool: "Playwright (most listing sites are JS-heavy)"
schedule: "Daily"
challenges:
  - Heavy JavaScript rendering
  - Anti-bot measures (Cloudflare common)
  - Frequent layout changes
  - Map-based results
approach: "API endpoint discovery via network tab first"
```

---

## Phase 11: Scaling Strategies

### Concurrency Architecture

```
Single machine (small scale):
├── asyncio + aiohttp (Python) → 50-200 concurrent requests
├── Worker pool (ThreadPoolExecutor) → 10-50 threads
└── Scrapy reactor → Built-in concurrency

Multi-machine (large scale):
├── URL queue: Redis / RabbitMQ / SQS
├── Workers: Multiple Scrapy/custom workers
├── Results: Shared PostgreSQL / S3
└── Coordinator: Celery / custom scheduler
```

### Cost Optimization

| Lever | Impact | How |
|-------|--------|-----|
| Static > Browser | 10-50x cheaper | Always try HTTP first |
| Block images/CSS/fonts | 60-80% bandwidth saved | Route filtering |
| Cache DNS | Minor but cumulative | Local DNS cache |
| Compress responses | 50-70% bandwidth | Accept-Encoding: gzip, br |
| Smart scheduling | Avoid redundant scrapes | Change detection before full re-scrape |
| Proxy tier matching | 3-10x cost difference | Don't use residential for easy sites |

---

## Phase 12: Advanced Patterns

### API Discovery (Network Tab Mining)

Before building a scraper, check if the site has hidden API endpoints:

1. Open DevTools → Network tab
2. Filter by XHR/Fetch
3. Navigate the site, click load-more, filter/sort
4. Look for JSON responses — these are your goldmine
5. Most SPAs load data via REST/GraphQL APIs

**Common hidden API patterns:**
- `/api/v1/products?page=1&limit=20`
- `/graphql` with query parameters
- `/_next/data/...` (Next.js data routes)
- `/wp-json/wp/v2/posts` (WordPress)

### Headless Browser Optimization

```python
# Minimize browser resource usage
context = browser.new_context(
    viewport={"width": 1280, "height": 720},
    java_script_enabled=True,  # Only if needed
    has_touch=False,
    is_mobile=False,
)

# Block resource types you don't need
page.route("**/*", lambda route: (
    route.abort() if route.request.resource_type in 
    ["image", "stylesheet", "font", "media"] 
    else route.continue_()
))
```

### Scraping Behind Authentication

```python
# When authorized to scrape behind login
# ALWAYS use session-based auth, never store passwords in code

# Pattern: Login once, reuse session
session = requests.Session()
login_resp = session.post("https://example.com/login", data={
    "username": os.environ["SCRAPE_USER"],
    "password": os.environ["SCRAPE_PASS"],
})
assert login_resp.ok, "Login failed"

# Session cookies are now stored — use for subsequent requests
data_resp = session.get("https://example.com/api/data")
```

### Change Detection (Avoid Redundant Scrapes)

```python
import hashlib

def has_changed(url, session, last_etag=None, last_modified=None):
    """Check if page changed without downloading full content."""
    headers = {}
    if last_etag:
        headers["If-None-Match"] = last_etag
    if last_modified:
        headers["If-Modified-Since"] = last_modified
    
    resp = session.head(url, headers=headers)
    
    if resp.status_code == 304:
        return False, resp.headers.get("ETag"), resp.headers.get("Last-Modified")
    
    return True, resp.headers.get("ETag"), resp.headers.get("Last-Modified")
```

---

## Quality Scoring Rubric (0-100)

| Dimension | Weight | What to Assess |
|-----------|--------|---------------|
| Legal compliance | 20% | robots.txt, ToS, PII handling, audit trail |
| Data quality | 20% | Validation, accuracy, completeness, freshness |
| Resilience | 15% | Error handling, retries, circuit breakers, checkpointing |
| Anti-detection | 15% | Proxy rotation, fingerprint diversity, rate limiting |
| Architecture | 10% | Right tool selection, clean code, modularity |
| Monitoring | 10% | Success rates, breakage detection, alerting |
| Performance | 5% | Speed, cost efficiency, resource usage |
| Documentation | 5% | Runbook, schema docs, legal assessment |

**Grading:** 90+ Excellent | 75-89 Good | 60-74 Needs work | <60 Redesign

---

## 10 Common Mistakes

| # | Mistake | Fix |
|---|---------|-----|
| 1 | No robots.txt check | Always check first — it's your legal defense |
| 2 | Fixed delays (no jitter) | Add ±30% random jitter to all delays |
| 3 | No data validation | Validate every field before storing |
| 4 | Using browser for static HTML | HTTP client is 10-50x faster and cheaper |
| 5 | Single IP, no rotation | Proxy rotation for any serious scraping |
| 6 | No breakage detection | Monitor extraction counts and field fill rates |
| 7 | Storing raw HTML only | Extract + structure immediately |
| 8 | No checkpoint/resume | Long scrapes must be resumable |
| 9 | Ignoring structured data | JSON-LD/microdata is cleaner than CSS selectors |
| 10 | Scraping when API exists | Always check for API first |

---

## 5 Edge Cases

1. **Single-page apps (React/Vue/Angular)**: Must use browser rendering OR find the underlying API (network tab). Prefer API discovery — it's faster and more reliable.

2. **Infinite scroll**: Intercept the XHR/fetch calls that load more content. Simulate scrolling only as last resort. The API endpoint usually accepts `page` or `offset` params.

3. **CAPTCHAs**: If you're hitting CAPTCHAs, you're scraping too aggressively. Slow down first. If CAPTCHAs persist: managed services (2Captcha, Anti-Captcha) or rethink approach.

4. **Dynamic class names** (CSS modules, Tailwind): Use data attributes, ARIA labels, or text content selectors instead. `[data-testid="price"]` survives redesigns. `.sc-bdVTJa` does not.

5. **Multi-language sites**: Detect language via `html[lang]` attribute. Set `Accept-Language` header to get desired locale. Watch for different URL structures (`/en/`, `/de/`, subdomains).

---

## Natural Language Commands

1. **"Check if I can scrape [URL]"** → Run compliance checklist (robots.txt, ToS, data type)
2. **"What tool should I use for [site]?"** → Analyze site rendering, anti-bot, recommend tool
3. **"Build a scraper for [description]"** → Full architecture brief + code pattern
4. **"My scraper is getting blocked"** → Anti-detection diagnostic + proxy/stealth recommendations
5. **"Extract [data] from [URL]"** → Check structured data first, then CSS selectors
6. **"Monitor [site] for changes"** → Change detection + scheduling + alerting setup
7. **"How do I handle pagination on [site]?"** → Identify pagination type + code pattern
8. **"Scrape at scale ([N] pages)"** → Concurrency architecture + cost estimate
9. **"Clean and store this scraped data"** → Validation + dedup + storage recommendation
10. **"Is my scraper healthy?"** → Run health check + breakage detection
11. **"Find the API behind [site]"** → Network tab mining guide + common patterns
12. **"Set up price monitoring for [competitors]"** → Full e-commerce monitor pattern
