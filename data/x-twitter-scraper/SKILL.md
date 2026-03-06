---
name: Twitter/X Profile Scraper
description: A browser-based Twitter/X profile discovery and scraping tool.
---

# Twitter/X Profile Scraper


A browser-based Twitter/X profile discovery and scraping tool.

> Part of **[ScrapeClaw](https://www.scrapeclaw.cc/)** — a suite of production-ready, agentic social media scrapers for Instagram, YouTube, X/Twitter, and Facebook built with Python & Playwright, no API keys required.

```yaml
---
name: twitter-scraper
description: Discover and scrape Twitter/X public profiles from your browser.
emoji: 🐦
version: 1.0.2
author: influenza
tags:
  - twitter
  - x
  - scraping
  - social-media
  - profile-discovery
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

This skill provides a two-phase Twitter/X scraping system:

1. **Profile Discovery** — Find Twitter accounts via Google Custom Search API or DuckDuckGo
2. **Browser Scraping** — Scrape public profiles using Playwright with anti-detection (no login required)

## Features

- 🔍  - Discover Twitter/X profiles by location and category
- 🌐  - Full browser simulation for accurate scraping
- 🛡️  - Browser fingerprinting, human behavior simulation, and stealth scripts
- 📊  - Profile info, followers, tweets, engagement data, and media
- 💾  - JSON/CSV export with downloaded thumbnails
- 🔄  - Resume interrupted scraping sessions
- ⚡  - Auto-skip private accounts, low-follower profiles, suspended users
- 🌍  - Built-in residential proxy support with 4 providers

#### Getting Google API Credentials (Optional)

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing
3. Enable "Custom Search API"
4. Create API credentials → API Key
5. Go to [Programmable Search Engine](https://programmablesearchengine.google.com/)
6. Create a search engine with `x.com` and `twitter.com` as the sites to search
7. Copy the Search Engine ID

If not configured, discovery falls back to DuckDuckGo (no API key needed).

## Usage

### Agent Tool Interface

For OpenClaw agent integration, the skill provides JSON output:

```bash
# Discover Twitter profiles (returns JSON)
discover --location "Miami" --category "tech" --output json

# Discover profiles in a specific category (returns JSON)
discover --location "New York" --category "crypto" --output json

# Scrape single profile (returns JSON)
scrape --username elonmusk --output json

# Scrape from a queue file
scrape data/queue/Miami_tech_20260220_120000.json
```

## Output Data

### Profile Data Structure

```json
{
  "username": "elonmusk",
  "display_name": "Elon Musk",
  "bio": "...",
  "followers": 180000000,
  "following": 800,
  "tweets_count": 45000,
  "is_verified": true,
  "profile_pic_url": "https://...",
  "profile_pic_local": "thumbnails/elonmusk/profile_abc123.jpg",
  "user_location": "Mars & Earth",
  "join_date": "June 2009",
  "website": "https://x.ai",
  "influencer_tier": "mega",
  "category": "tech",
  "scrape_location": "New York",
  "scraped_at": "2026-02-17T12:00:00",
  "recent_tweets": [
    {
      "id": "1234567890",
      "text": "Tweet content...",
      "timestamp": "2026-02-17T10:30:00.000Z",
      "likes": 50000,
      "retweets": 12000,
      "replies": 3000,
      "views": "5.2M",
      "media_urls": ["https://..."],
      "media_local": ["thumbnails/elonmusk/tweet_media_0_def456.jpg"],
      "is_retweet": false,
      "is_reply": false,
      "url": "https://x.com/elonmusk/status/1234567890"
    }
  ]
}
```

### Queue File Structure

```json
{
  "location": "New York",
  "category": "tech",
  "total": 15,
  "usernames": ["user1", "user2", "..."],
  "completed": ["user1"],
  "failed": {"user3": "not_found"},
  "current_index": 2,
  "created_at": "2026-02-17T12:00:00",
  "source": "google_api"
}
```

### Influencer Tiers

| Tier  | Followers Range     |
|-------|---------------------|
| nano  | < 1,000             |
| micro | 1,000 - 10,000      |
| mid   | 10,000 - 100,000    |
| macro | 100,000 - 1M        |
| mega  | > 1,000,000         |

### File Outputs

- **Queue files**: `data/queue/{location}_{category}_{timestamp}.json`
- **Scraped data**: `data/output/{username}.json`
- **Thumbnails**: `thumbnails/{username}/profile_*.jpg`, `thumbnails/{username}/tweet_media_*.jpg`
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
    "min_followers": 500,
    "max_tweets": 20,
    "download_thumbnails": true,
    "max_thumbnails": 6,
    "delay_between_profiles": [4, 8],
    "timeout": 60000
  },
  "cities": ["New York", "Los Angeles", "Miami", "Chicago"],
  "categories": ["tech", "politics", "sports", "entertainment", "news", "crypto"]
}
```

## Filters Applied

The scraper automatically filters out:

- ❌ Suspended or deactivated accounts
- ❌ Protected (private) accounts
- ❌ Profiles with < 500 followers (configurable)
- ❌ Non-existent usernames
- ❌ Already scraped entries (deduplication)

## Anti-Detection

The scraper uses multiple anti-detection techniques:

- **Browser fingerprinting** — 4 rotating fingerprint profiles (viewport, user agent, timezone, WebGL, etc.)
- **Stealth JavaScript** — Hides `navigator.webdriver`, spoofs plugins/languages/hardware, canvas noise, fake `chrome` object
- **Human behavior simulation** — Random delays, mouse movements, scrolling patterns
- **Network randomization** — Variable timing between requests
- **Login wall handling** — Automatically dismisses Twitter's login prompts and overlays

## Troubleshooting

### No Profiles Discovered

- Check Google API key and quota
- Verify Search Engine ID is configured for x.com and twitter.com
- Try different location/category combinations
- If Google fails, DuckDuckGo fallback is used automatically

### Rate Limiting

- Reduce scraping speed (increase delays in config)
- Run during off-peak hours
- **Use a residential proxy** (see below)

### Login Wall Issues

- The scraper automatically dismisses login prompts
- If content is blocked, try running with `--headless` disabled to debug visually

---

## 🌐 Residential Proxy Support

### Why Use a Residential Proxy?

Running a scraper at scale **without** a residential proxy will get your IP blocked fast. Here's why proxies are essential for long-running scrapes:

| Advantage | Description |
|-----------|-------------|
| **Avoid IP Bans** | Residential IPs look like real household users, not data-center bots. Twitter/X is far less likely to flag them. |
| **Automatic IP Rotation** | Each request (or session) gets a fresh IP, so rate-limits never stack up on one address. |
| **Geo-Targeting** | Route traffic through a specific country/city so scraped content matches the target audience's locale. |
| **Sticky Sessions** | Keep the same IP for a configurable window (e.g. 10 min) — critical for maintaining a consistent browsing session. |
| **Higher Success Rate** | Rotating residential IPs deliver 95%+ success rates compared to ~30% with data-center proxies on Twitter/X. |
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
python main.py discover --location "Miami" --category "tech"
python main.py scrape --username elonmusk

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

1. **Use sticky sessions** — Twitter requires consistent IPs during a browsing session. Set `"sticky": true`.
2. **Target the right country** — Set `"country": "us"` (or your target region) so Twitter serves content in the expected locale.
3. **Combine with existing anti-detection** — This scraper already has fingerprinting, stealth scripts, and human behavior simulation. The proxy is the final layer.
4. **Rotate sessions between batches** — Call `pm.rotate_session()` between large batches of profiles to get a fresh IP.
5. **Use delays** — Even with proxies, respect `delay_between_profiles` in config (default 4-8s) to avoid aggressive patterns.
6. **Monitor your proxy dashboard** — All providers have dashboards showing bandwidth usage and success rates.

## Notes

- **No login required** — Only scrapes publicly visible content
- **Checkpoint/resume** — Queue files track progress; interrupted scrapes can be resumed with `--resume`
- **Rate limiting** — Waits 60s on rate limit, stops on daily limit detection
- **Twitter selectors** — Uses `data-testid` attributes (stable across UI changes) with fallbacks to `aria-label` and structural selectors
