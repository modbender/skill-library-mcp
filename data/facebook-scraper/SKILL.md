---
name: Facebook Page & Group Scraper
description: A browser-based Facebook page and group discovery and scraping tool.
---


# Facebook Page & Group Scraper

> Part of **[ScrapeClaw](https://www.scrapeclaw.cc/)** — a suite of production-ready, agentic social media scrapers for Instagram, YouTube, X/Twitter, and Facebook built with Python & Playwright, no API keys required.

A browser-based Facebook page and group discovery and scraping tool.

```yaml
---
name: facebook-scraper
description: Discover and scrape Facebook pages and public groups from your browser.
emoji: 📘
version: 1.0.0
author: influenza
tags:
  - facebook
  - scraping
  - social-media
  - page-discovery
  - group-discovery
  - business-pages
metadata:
  clawdbot:
    requires:
      bins:
        - python3
        - chromium

    config:
      stateDirs:
        - data/output
        - data/queue
        - thumbnails
      outputFormats:
        - json
        - csv
---
```

## Overview

This skill provides a two-phase Facebook scraping system:

1. **Page/Group Discovery**  
2. **Browser Scraping** 

## Features

- 🔍  - Discover Facebook pages and groups by location and category
- 🌐  - Full browser simulation for accurate scraping
- 🛡️  - Browser fingerprinting, human behavior simulation, and stealth scripts
- 📊  - Page/group info, stats, images, and engagement data
- 💾  - JSON/CSV export with downloaded thumbnails
- 🔄  - Resume interrupted scraping sessions
- ⚡  - Auto-skip private groups, low-like pages, empty profiles
- 📂  - Supports pages, groups, and public profiles via --type flag

#### Getting Google API Credentials (Optional)

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing
3. Enable "Custom Search API"
4. Create API credentials → API Key
5. Go to [Programmable Search Engine](https://programmablesearchengine.google.com/)
6. Create a search engine with `facebook.com` as the site to search
7. Copy the Search Engine ID

## Usage

### Agent Tool Interface

For OpenClaw agent integration, the skill provides JSON output:

```bash
# Discover Facebook pages (returns JSON)
discover --location "Miami" --category "restaurant" --type page --output json

# Discover Facebook groups (returns JSON)
discover --location "New York" --category "fitness" --type group --output json

# Scrape single page (returns JSON)
scrape --page-name examplebusiness --output json

# Scrape single group (returns JSON)
scrape --page-name examplegroup --type group --output json
```

## Output Data

### Page/Group Data Structure

```json
{
  "page_name": "example_business",
  "display_name": "Example Business",
  "entity_type": "page",
  "category": "Restaurant",
  "subcategory": "Italian Restaurant",
  "about": "Family-owned Italian restaurant since 1985",
  "followers": 45000,
  "page_likes": 42000,
  "location": "Miami, FL",
  "address": "123 Main St, Miami, FL 33101",
  "phone": "+1-555-0123",
  "email": "info@example.com",
  "website": "https://example.com",
  "hours": "Mon-Sat 11AM-10PM",
  "is_verified": false,
  "page_tier": "mid",
  "profile_pic_local": "thumbnails/example_business/profile_abc123.jpg",
  "cover_photo_local": "thumbnails/example_business/cover_def456.jpg",
  "recent_posts": [
    {"post_url": "https://facebook.com/example_business/posts/123", "reactions": 320, "comments": 45, "shares": 12}
  ],
  "scrape_timestamp": "2026-02-20T14:30:00"
}
```

### Group Data Structure

```json
{
  "page_name": "example_group",
  "display_name": "Miami Fitness Community",
  "entity_type": "group",
  "about": "A community for fitness enthusiasts in Miami",
  "members": 15000,
  "privacy": "Public",
  "posts_per_day": 25,
  "location": "Miami",
  "page_tier": "mid",
  "profile_pic_local": "thumbnails/example_group/profile_abc123.jpg",
  "cover_photo_local": "thumbnails/example_group/cover_def456.jpg",
  "scrape_timestamp": "2026-02-20T14:30:00"
}
```

### Page Tiers

| Tier  | Likes/Members Range |
|-------|---------------------|
| nano  | < 1,000             |
| micro | 1,000 - 10,000      |
| mid   | 10,000 - 100,000    |
| macro | 100,000 - 1M        |
| mega  | > 1,000,000         |

### File Outputs

- **Queue files**: `data/queue/{location}_{category}_{type}_{timestamp}.json`
- **Scraped data**: `data/output/{page_name}.json`
- **Thumbnails**: `thumbnails/{page_name}/profile_*.jpg`, `thumbnails/{page_name}/cover_*.jpg`
- **Export files**: `data/export_{timestamp}.json`, `data/export_{timestamp}.csv`

## Configuration

Edit `config/scraper_config.json`:

```json
{
  "google_search": {
    "enabled": true,
    "api_key": "",
    "search_engine_id": "",
    "queries_per_location": 3
  },
  "scraper": {
    "headless": false,
    "min_likes": 1000,
    "download_thumbnails": true,
    "max_thumbnails": 6
  },
  "cities": ["New York", "Los Angeles", "Miami", "Chicago"],
  "categories": ["restaurant", "retail", "fitness", "real-estate", "healthcare", "beauty"]
}
```

## Filters Applied

The scraper automatically filters out:

- ❌ Private groups
- ❌ Pages with < 1,000 likes (configurable)
- ❌ Deactivated or removed pages
- ❌ Non-existent pages/groups
- ❌ Already scraped entries (deduplication)

## Troubleshooting

### Login Issues

- Ensure credentials are correct
- Handle verification codes when prompted
- Wait if rate limited (the script will auto-retry)

### No Pages Discovered

- Check Google API key and quota
- Verify Search Engine ID is configured for facebook.com
- Try different location/category combinations

### Rate Limiting

- Reduce scraping speed (increase delays)
- Use multiple Facebook accounts
- Run during off-peak hours
- **Use a residential proxy** (see below)

---

## 🌐 Residential Proxy Support

### Why Use a Residential Proxy?

Running a scraper at scale **without** a residential proxy will get your IP blocked fast. Here's why proxies are essential for long-running scrapes:

| Advantage | Description |
|-----------|-------------|
| **Avoid IP Bans** | Residential IPs look like real household users, not data-center bots. Facebook is far less likely to flag them. |
| **Automatic IP Rotation** | Each request (or session) gets a fresh IP, so rate-limits never stack up on one address. |
| **Geo-Targeting** | Route traffic through a specific country/city so scraped content matches the target audience's locale. |
| **Sticky Sessions** | Keep the same IP for a configurable window (e.g. 10 min) — critical for maintaining a Facebook login session. |
| **Higher Success Rate** | Rotating residential IPs deliver 95%+ success rates compared to ~30% with data-center proxies on Facebook. |
| **Long-Running Scrapes** | Scrape thousands of pages/groups over hours or days without interruption. |
| **Concurrent Scraping** | Run multiple browser instances across different IPs simultaneously. |

### Recommended Proxy Providers

We have affiliate partnerships with top residential proxy providers. Using these links supports continued development of this skill:

| Provider | Best For | Sign Up |
|----------|----------|---------|
| **Bright Data** | World's largest residential network, 72M+ IPs, enterprise-grade | 👉 [**Sign Up for Bright Data**](https://get.brightdata.com/o1kpd2da8iv4) |
| **IProyal** | Premium residential pool, pay-as-you-go, 195+ countries | 👉 [**Sign Up for IProyal**](https://iproyal.com/?r=ScrapeClaw) |
| **Storm Proxies** | Fast & reliable residential IPs, developer-friendly API | 👉 [**Sign Up for Storm Proxies**](https://stormproxies.com/clients/aff/go/scrapeclaw) |
| **NetNut** | ISP-grade residential network, 52M+ IPs, direct connectivity | 👉 [**Sign Up for NetNut**](https://netnut.io?ref=mwrlzwv) |


### Setup Steps

#### 1. Get Your Proxy Credentials

Sign up with any provider above, then grab:
- **Username** (from your provider dashboard)
- **Password** (from your provider dashboard)
- **Host** and **Port** are pre-configured per provider (or use custom)

#### 2. Configure Entirely via Environment Variables

```bash
export PROXY_ENABLED=true
export PROXY_PROVIDER=netnut       # brightdata | iproyal | stormproxies | netnut | custom
export PROXY_USERNAME=your_user
export PROXY_PASSWORD=your_pass
export PROXY_COUNTRY=us            # optional: two-letter country code
export PROXY_STICKY=true           # optional: keep same IP per session
```

#### 3. Provider-Specific Host/Port Defaults

These are auto-configured when you set the `provider` name:

| Provider | Host | Port |
|----------|------|------|
| Bright Data | `brd.superproxy.io` | `22225` |
| IProyal | `proxy.iproyal.com` | `12321` |
| Storm Proxies | `rotating.stormproxies.com` | `9999` |
| NetNut | `gw-resi.netnut.io` | `5959` |

Override with `"host"` and `"port"` in config or `PROXY_HOST` / `PROXY_PORT` env vars if your plan uses a different gateway.

#### 4. Custom Proxy Provider

For any other proxy service, set provider to `custom` and supply host/port manually:

```json
{
  "proxy": {
    "enabled": true,
    "provider": "custom",
    "host": "your.proxy.host",
    "port": 8080,
    "username": "user",
    "password": "pass"
  }
}
```

### Running the Scraper with Proxy

Once configured, the scraper picks up the proxy automatically — no extra flags needed:

```bash
# Discover and scrape as usual — proxy is applied automatically
python main.py discover --location "Miami" --category "restaurant" --type page
python main.py scrape --page-name examplebusiness

# The log will confirm proxy is active:
# INFO - Proxy enabled: <ProxyManager provider=netnut enabled host=gw-resi.netnut.io:5959>
# INFO - Browser using proxy: netnut → gw-resi.netnut.io:5959
```

### Using the Proxy Manager Programmatically

```python
from proxy_manager import ProxyManager

# From config (auto-reads config/scraper_config.json)
pm = ProxyManager.from_config()

# From environment variables
pm = ProxyManager.from_env()

# Manual construction
pm = ProxyManager(
    provider="netnut",
    username="your_user",
    password="your_pass",
    country="us",
    sticky=True
)

# For Playwright browser context
proxy = pm.get_playwright_proxy()
# → {"server": "http://gw-resi.netnut.io:5959", "username": "user-country-us-session-abc123", "password": "pass"}

# For requests / aiohttp
proxies = pm.get_requests_proxy()
# → {"http": "http://user:pass@host:port", "https": "http://user:pass@host:port"}

# Force new IP (rotates session ID)
pm.rotate_session()

# Debug info
print(pm.info())
```

### Best Practices for Long-Running Scrapes

1. **Always use sticky sessions** — Facebook requires consistent IPs during a login session. Set `"sticky": true`.
2. **Target the right country** — Set `"country": "us"` (or your target region) so Facebook serves content in the expected locale.
3. **Combine with existing anti-detection** — This scraper already has fingerprinting, stealth scripts, and human behavior simulation. The proxy is the final layer.
4. **Rotate sessions between accounts** — Call `pm.rotate_session()` when switching Facebook accounts to get a fresh IP.
5. **Use delays** — Even with proxies, respect `delay_between_profiles` in config (default 5-10s) to avoid aggressive patterns.
6. **Monitor your proxy dashboard** — All providers (Bright Data, IProyal, Storm Proxies, NetNut) have dashboards showing bandwidth usage and success rates.
