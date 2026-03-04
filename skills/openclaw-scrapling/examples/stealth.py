#!/usr/bin/env python3
"""
Stealth scraping example - Bypass anti-bot protection
Use for: Sites with Cloudflare, bot detection, or fingerprinting
"""
from scrapling.fetchers import StealthyFetcher

# Target a protected site
url = "https://nopecha.com/demo/cloudflare"
print(f"Fetching (stealth mode): {url}")

# Stealth mode with headless browser
page = StealthyFetcher.fetch(
    url,
    headless=True,           # Run invisible browser
    solve_cloudflare=True,   # Auto-solve Cloudflare challenges
    network_idle=True        # Wait for page to fully load
)

# Extract content
content = page.css('#padded_content a')
print(f"\nFound {len(content)} links:")

for link in content[:5]:
    text = link.css('::text').get()
    href = link.attrib.get('href', '')
    print(f"  - {text}: {href}")
