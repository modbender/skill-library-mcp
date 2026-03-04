#!/usr/bin/env python3
"""
Dynamic scraping example - JavaScript-rendered content
Use for: React/Vue/Angular apps, lazy-loaded content, SPAs
"""
from scrapling.fetchers import DynamicFetcher

# Target a JavaScript-heavy site
url = "https://quotes.toscrape.com/js/"  # JavaScript version
print(f"Fetching (dynamic mode): {url}")

# Full browser automation
page = DynamicFetcher.fetch(
    url,
    headless=True,
    network_idle=True,      # Wait for all network requests to finish
    disable_resources=False  # Load CSS/JS (needed for React/Vue)
)

# Extract dynamically loaded content
quotes = page.css('.quote')
print(f"\nFound {len(quotes)} quotes (loaded via JavaScript):\n")

for quote in quotes[:3]:
    text = quote.css('.text::text').get()
    author = quote.css('.author::text').get()
    tags = quote.css('.tag::text').getall()
    print(f"\"{text}\"")
    print(f"  — {author}")
    print(f"  Tags: {', '.join(tags)}\n")
