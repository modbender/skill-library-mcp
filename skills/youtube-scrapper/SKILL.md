# YouTube Channel Scraper

A browser-based YouTube channel discovery and scraping tool.

> Part of **[ScrapeClaw](https://www.scrapeclaw.cc/)** — a suite of production-ready, agentic social media scrapers for Instagram, YouTube, X/Twitter, and Facebook built with Python & Playwright, no API keys required.

```yaml
---
name: youtube-scrapper
description: Discover and scrape YouTube channels from your browser.
emoji: 📺
version: 1.0.2
author: influenza
tags:
  - youtube
  - scraping
  - social-media
  - channel-discovery
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

This skill provides a two-phase YouTube scraping system:

1. **Channel Discovery** — Find YouTube channels via Google Search (browser-based, no API key required)
2. **Browser Scraping** — Scrape public channel data using Playwright with anti-detection (no login required)

## Features

- 🔍  - Discover YouTube channels by location and category
- 🌐  - Full browser simulation for accurate scraping
- 🛡️  - Browser fingerprinting, human behavior simulation, and stealth scripts
- 📊  - Channel info, subscribers, views, videos, engagement data, and media
- 💾  - JSON export with downloaded thumbnails
- 🔄  - Resume interrupted scraping sessions
- ⚡  - Auto-skip unavailable channels and low-subscriber profiles
- 🌍  - Built-in residential proxy support with 4 providers
- 🗺️  - Regional configs for US, UK, Europe, India, Gulf, and East Asia

## Usage

### Agent Tool Interface

For OpenClaw agent integration, the skill provides JSON output:

```bash
# Discover YouTube channels (returns JSON queue)
python scripts/youtube_channel_discovery.py --categories tech --locations India

# Scrape from a queue file
python scripts/youtube_channel_scraper.py --queue data/queue/your_queue_file.json

# Full orchestration — discover + scrape in one go
python scripts/youtube_orchestrator.py --config resources/scraper_config_ind.json
```

## Output Data

### Channel Data Structure

```json
{
  "channel_name": "Marques Brownlee",
  "channel_url": "https://www.youtube.com/@mkbhd",
  "subscribers": 19200000,
  "total_views": 4500000000,
  "video_count": 1800,
  "description": "MKBHD: Quality Tech Videos...",
  "joined_date": "Mar 21, 2008",
  "country": "United States",
  "profile_pic_url": "https://...",
  "profile_pic_local": "thumbnails/mkbhd/profile_abc123.jpg",
  "banner_url": "https://...",
  "banner_local": "thumbnails/mkbhd/banner_def456.jpg",
  "influencer_tier": "mega",
  "category": "tech",
  "scrape_location": "New York",
  "scraped_at": "2026-02-17T12:00:00",
  "recent_videos": [
    {
      "title": "Galaxy S26 Ultra Review",
      "url": "https://www.youtube.com/watch?v=...",
      "views": 5200000,
      "published": "2 days ago",
      "duration": "14:32",
      "thumbnail_url": "https://...",
      "thumbnail_local": "thumbnails/mkbhd/video_0_ghi789.jpg"
    }
  ]
}
```

### Queue File Structure

```json
{
  "location": "India",
  "category": "tech",
  "total": 20,
  "channels": ["@channel1", "@channel2", "..."],
  "completed": ["@channel1"],
  "failed": {"@channel3": "not_found"},
  "current_index": 2,
  "created_at": "2026-02-17T12:00:00",
  "source": "google_search"
}
```

### Influencer Tiers

| Tier  | Subscribers Range   |
|-------|---------------------|
| nano  | < 1,000             |
| micro | 1,000 – 10,000      |
| mid   | 10,000 – 100,000    |
| macro | 100,000 – 1M        |
| mega  | > 1,000,000         |

### File Outputs

- **Queue files**: `data/queue/{region}/{location}_{category}_{timestamp}.json`
- **Scraped data**: `data/output_{region}/{channel_name}.json`
- **Thumbnails**: `thumbnails_{region}/{channel}/profile_*.jpg`, `thumbnails_{region}/{channel}/video_*.jpg`
- **Progress**: `data/progress/discovery_progress_{region}.json`

## Configuration

Regional config files live in `resources/`:

```
resources/scraper_config_us.json
resources/scraper_config_uk.json
resources/scraper_config_eur.json
resources/scraper_config_ind.json
resources/scraper_config_gulf.json
resources/scraper_config_east.json
```

Example config (`resources/scraper_config_ind.json`):

```json
{
  "proxy": {
    "enabled": false,
    "provider": "brightdata",
    "country": "",
    "sticky": true,
    "sticky_ttl_minutes": 10
  },
  "categories": [
    "gaming", "tech", "beauty", "fashion", "fitness",
    "food", "travel", "music", "education", "comedy",
    "lifestyle", "cooking", "diy", "art", "finance",
    "health", "entertainment"
  ],
  "locations": [
    "India", "Mumbai", "Delhi", "Bangalore", "Hyderabad",
    "Chennai", "Kolkata", "Pune", "Ahmedabad", "Jaipur"
  ],
  "max_videos_to_scrape": 6,
  "headless": false,
  "results_per_search": 20,
  "search_delay": [3, 7],
  "scrape_delay": [2, 5],
  "rate_limit_wait": 60,
  "max_retries": 3
}
```

## Filters Applied

The scraper automatically filters out:

- ❌ Unavailable or terminated channels
- ❌ Channels with < 500 subscribers (configurable)
- ❌ Non-existent channel URLs
- ❌ Already scraped entries (deduplication)
- ❌ Rate-limited requests (auto-retry with backoff)

## Anti-Detection

The scraper uses multiple anti-detection techniques:

- **Browser fingerprinting** — Rotating fingerprint profiles (viewport, user agent, timezone, WebGL, etc.)
- **Stealth JavaScript** — Hides `navigator.webdriver`, spoofs plugins/languages/hardware, canvas noise, fake `chrome` object
- **Human behavior simulation** — Random delays, mouse movements, scrolling patterns
- **Network randomization** — Variable timing between requests
- **Request interception** — Blocks known fingerprinting and tracking scripts

## Troubleshooting

### No Channels Discovered

- Try different location/category combinations
- Check if Google Search is returning CAPTCHA pages
- Run with `--headless false` to debug visually

### Rate Limiting

- Reduce scraping speed (increase delays in config)
- Run during off-peak hours
- **Use a residential proxy** (see below)

### Browser Crashes

- The orchestrator auto-restarts the browser every 50 channels
- Interrupted scrapes can be resumed — queue files track progress automatically

---

## 🌐 Residential Proxy Support

### Why Use a Residential Proxy?

Running a scraper at scale **without** a residential proxy will get your IP blocked fast. Here's why proxies are essential for long-running scrapes:

| Advantage | Description |
|-----------|-------------|
| **Avoid IP Bans** | Residential IPs look like real household users, not data-center bots. YouTube is far less likely to flag them. |
| **Automatic IP Rotation** | Each request (or session) gets a fresh IP, so rate-limits never stack up on one address. |
| **Geo-Targeting** | Route traffic through a specific country/city so scraped content matches the target audience's locale. |
| **Sticky Sessions** | Keep the same IP for a configurable window (e.g. 10 min) — critical for maintaining a consistent browsing session. |
| **Higher Success Rate** | Rotating residential IPs deliver 95%+ success rates compared to ~30% with data-center proxies on YouTube. |
| **Long-Running Scrapes** | Scrape thousands of channels over hours or days without interruption. |
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
python scripts/youtube_orchestrator.py --config resources/scraper_config_ind.json

# The log will confirm proxy is active:
# INFO - Proxy enabled: <ProxyManager provider=brightdata enabled host=brd.superproxy.io:22225>
# INFO - Browser using proxy: brightdata → brd.superproxy.io:22225
```

### Using the Proxy Manager Programmatically

```python
from proxy_manager import ProxyManager

# From config (auto-reads config from resources/)
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

1. **Use sticky sessions** — YouTube requires consistent IPs during a browsing session. Set `"sticky": true`.
2. **Target the right country** — Set `"country": "us"` (or your target region) so YouTube serves content in the expected locale.
3. **Combine with existing anti-detection** — This scraper already has fingerprinting, stealth scripts, and human behavior simulation. The proxy is the final layer.
4. **Rotate sessions between batches** — Call `pm.rotate_session()` between large batches of channels to get a fresh IP.
5. **Use delays** — Even with proxies, respect `scrape_delay` in config (default 2-5s) to avoid aggressive patterns.
6. **Monitor your proxy dashboard** — All providers have dashboards showing bandwidth usage and success rates.

## Notes

- **No login required** — Only scrapes publicly visible content
- **Checkpoint/resume** — Queue files track progress; interrupted scrapes can be resumed automatically
- **Rate limiting** — Waits 60s on rate limit, exponential backoff on consecutive failures
- **Resilient orchestration** — Auto-restarts browser, retries failed channels, graceful shutdown on SIGINT/SIGTERM
- **Regional configs** — Pre-built configs for 6 regions covering 200+ cities worldwide
