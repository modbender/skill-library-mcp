# Instagram Profile Scraper

A browser-based Instagram profile discovery and scraping tool.

> Part of **[ScrapeClaw](https://www.scrapeclaw.cc/)** — a suite of production-ready, agentic social media scrapers for Instagram, YouTube, X/Twitter, and Facebook built with Python & Playwright, no API keys required.

```yaml
---
name: instagram-scraper
description: Discover and scrape Instagram profiles from your browser.
emoji: 📸
version: 1.0.3
author: influenza
tags:
  - instagram
  - scraping
  - social-media
  - influencer-discovery
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

This skill provides a two-phase Instagram scraping system:

1. **Profile Discovery**  
2. **Browser Scraping** 

## Features

- 🔍  - Discover Instagram profiles by location and category
- 🌐  - Full browser simulation for accurate scraping
- 🛡️  - Browser fingerprinting, human behavior simulation, and stealth scripts
- 📊  - Profile info, stats, images, and engagement data
- 💾  - JSON/CSV export with downloaded thumbnails
- 🔄  - Resume interrupted scraping sessions
- ⚡  - Auto-skip private accounts, low followers, empty profiles
- 🌍  - Built-in residential proxy support with 4 providers



#### Getting Google API Credentials (Optional)

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing
3. Enable "Custom Search API"
4. Create API credentials → API Key
5. Go to [Programmable Search Engine](https://programmablesearchengine.google.com/)
6. Create a search engine with `instagram.com` as the site to search
7. Copy the Search Engine ID

## Usage

### Agent Tool Interface

For OpenClaw agent integration, the skill provides JSON output:

```bash
# Discover profiles (returns JSON)
discover --location "Miami" --category "fitness" --output json

# Scrape single profile (returns JSON)
scrape --username influencer123 --output json
```

## Output Data

### Profile Data Structure

```json
{
  "username": "example_user",
  "full_name": "Example User",
  "bio": "Fashion blogger | NYC",
  "followers": 125000,
  "following": 1500,
  "posts_count": 450,
  "is_verified": false,
  "is_private": false,
  "influencer_tier": "mid",
  "category": "fashion",
  "location": "New York",
  "profile_pic_local": "thumbnails/example_user/profile_abc123.jpg",
  "content_thumbnails": [
    "thumbnails/example_user/content_1_def456.jpg",
    "thumbnails/example_user/content_2_ghi789.jpg"
  ],
  "post_engagement": [
    {"post_url": "https://instagram.com/p/ABC123/", "likes": 5420, "comments": 89}
  ],
  "scrape_timestamp": "2025-02-09T14:30:00"
}
```

### Influencer Tiers

| Tier  | Follower Range    |
|-------|-------------------|
| nano  | < 1,000           |
| micro | 1,000 - 10,000    |
| mid   | 10,000 - 100,000  |
| macro | 100,000 - 1M      |
| mega  | > 1,000,000       |

### File Outputs

- **Queue files**: `data/queue/{location}_{category}_{timestamp}.json`
- **Scraped data**: `data/output/{username}.json`
- **Thumbnails**: `thumbnails/{username}/profile_*.jpg`, `thumbnails/{username}/content_*.jpg`
- **Export files**: `data/export_{timestamp}.json`, `data/export_{timestamp}.csv`

## Configuration

Edit `config/scraper_config.json`:

```json
{
  "proxy": {
    "enabled": false,
    "provider": "brightdata",
    "country": "",
    "sticky": true,
    "sticky_ttl_minutes": 10
  },
  "google_search": {
    "enabled": true,
    "api_key": "",
    "search_engine_id": "",
    "queries_per_location": 3
  },
  "scraper": {
    "headless": false,
    "min_followers": 1000,
    "download_thumbnails": true,
    "max_thumbnails": 6
  },
  "cities": ["New York", "Los Angeles", "Miami", "Chicago"],
  "categories": ["fashion", "beauty", "fitness", "food", "travel", "tech"]
}
```



## Filters Applied

The scraper automatically filters out:

- ❌ Private accounts
- ❌ Accounts with < 1,000 followers (configurable)
- ❌ Accounts with no posts
- ❌ Non-existent/removed accounts
- ❌ Already scraped accounts (deduplication)

## Troubleshooting

### Login Issues

- Ensure credentials are correct
- Handle verification codes when prompted
- Wait if rate limited (the script will auto-retry)

### No Profiles Discovered

- Check Google API key and quota
- Verify Search Engine ID is configured for instagram.com
- Try different location/category combinations

### Rate Limiting

- Reduce scraping speed (increase delays in config)
- Run during off-peak hours
- **Use a residential proxy** (see below)

---

## 🌐 Residential Proxy Support

### Why Use a Residential Proxy?

Running a scraper at scale **without** a residential proxy will get your IP blocked fast. Here's why proxies are essential for long-running scrapes:

| Advantage | Description |
|-----------|-------------|
| **Avoid IP Bans** | Residential IPs look like real household users, not data-center bots. Instagram is far less likely to flag them. |
| **Automatic IP Rotation** | Each request (or session) gets a fresh IP, so rate-limits never stack up on one address. |
| **Geo-Targeting** | Route traffic through a specific country/city so scraped content matches the target audience's locale. |
| **Sticky Sessions** | Keep the same IP for a configurable window (e.g. 10 min) — critical for maintaining a consistent browsing session. |
| **Higher Success Rate** | Rotating residential IPs deliver 95%+ success rates compared to ~30% with data-center proxies on Instagram. |
| **Long-Running Scrapes** | Scrape thousands of profiles over hours or days without interruption. |
| **Concurrent Scraping** | Run multiple browser instances across different IPs simultaneously. |

### Recommended Proxy Providers

We have affiliate partnerships with top residential proxy providers. Using these links supports continued development of this skill:

| Provider | Best For | Sign Up |
|----------|----------|---------|
| **Bright Data** | World's largest network, 72M+ IPs, enterprise-grade | 👉 [**Get Bright Data**](https://get.brightdata.com/o1kpd2da8iv4) |
| **IProyal** | Pay-as-you-go, 195+ countries, no traffic expiry | 👉 [**Get IProyal**](https://iproyal.com/?r=ScrapeClaw) |
| **Storm Proxies** | Fast & reliable, developer-friendly API, competitive pricing | 👉 [**Get Storm Proxies**](https://stormproxies.com/clients/aff/go/scrapeclaw) |
| **NetNut** | ISP-grade network, 52M+ IPs, direct connectivity | 👉 [**Get NetNut**](https://netnut.io?ref=mwrlzwv) |



### Setup Steps

#### 1. Get Your Proxy Credentials

Sign up with any provider above, then grab:
- **Username** (from your provider dashboard)
- **Password** (from your provider dashboard)
- **Host** and **Port** are pre-configured per provider (or use custom)

#### 2. Configure via Environment Variables

```bash
export PROXY_ENABLED=true
export PROXY_PROVIDER=brightdata    # brightdata | iproyal | stormproxies | netnut | custom
export PROXY_USERNAME=your_user
export PROXY_PASSWORD=your_pass
export PROXY_COUNTRY=us             # optional: two-letter country code
export PROXY_STICKY=true            # optional: keep same IP per session
```

#### 3. Provider-Specific Host/Port Defaults

These are auto-configured when you set the `provider` name:

| Provider | Host | Port |
|----------|------|------|
| Bright Data | `brd.superproxy.io` | `22225` |
| IProyal | `proxy.iproyal.com` | `12321` |
| Storm Proxies | `rotating.stormproxies.com` | `9999` |
| NetNut | `gw-resi.netnut.io` | `5959` |

Override with `PROXY_HOST` / `PROXY_PORT` env vars if your plan uses a different gateway.

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
python main.py discover --location "Miami" --category "fitness"
python main.py scrape --username influencer123

# The log will confirm proxy is active:
# INFO - Proxy enabled: <ProxyManager provider=brightdata enabled host=brd.superproxy.io:22225>
# INFO - Browser using proxy: brightdata → brd.superproxy.io:22225
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
    provider="brightdata",
    username="your_user",
    password="your_pass",
    country="us",
    sticky=True
)

# For Playwright browser context
proxy = pm.get_playwright_proxy()
# → {"server": "http://brd.superproxy.io:22225", "username": "user-country-us-session-abc123", "password": "pass"}

# For requests / aiohttp
proxies = pm.get_requests_proxy()
# → {"http": "http://user:pass@host:port", "https": "http://user:pass@host:port"}

# Force new IP (rotates session ID)
pm.rotate_session()

# Debug info
print(pm.info())
```

### Best Practices for Long-Running Scrapes

1. **Use sticky sessions** — Instagram requires consistent IPs during a browsing session. Set `"sticky": true`.
2. **Target the right country** — Set `"country": "us"` (or your target region) so Instagram serves content in the expected locale.
3. **Combine with existing anti-detection** — This scraper already has fingerprinting, stealth scripts, and human behavior simulation. The proxy is the final layer.
4. **Rotate sessions between batches** — Call `pm.rotate_session()` between large batches of profiles to get a fresh IP.
5. **Use delays** — Even with proxies, respect `delay_between_profiles` in config to avoid aggressive patterns.
6. **Monitor your proxy dashboard** — All providers have dashboards showing bandwidth usage and success rates.

