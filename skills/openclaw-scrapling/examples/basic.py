#!/usr/bin/env python3
"""
Basic scraping example - Fast HTTP requests
Use for: Static HTML sites without JavaScript or bot protection
"""
from scrapling.fetchers import Fetcher

# Fetch a simple page
url = "https://quotes.toscrape.com"
print(f"Fetching: {url}")

page = Fetcher.get(url)

# Extract quotes
quotes = page.css('.quote')
print(f"\nFound {len(quotes)} quotes:\n")

for i, quote in enumerate(quotes[:5], 1):  # Show first 5
    text = quote.css('.text::text').get()
    author = quote.css('.author::text').get()
    print(f"{i}. \"{text}\"")
    print(f"   — {author}\n")
