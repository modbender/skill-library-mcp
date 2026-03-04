#!/usr/bin/env python3
"""
Adaptive scraping example - Survives website redesigns
Use for: Sites that frequently change their HTML structure
"""
from scrapling.fetchers import Fetcher

url = "https://quotes.toscrape.com"
print(f"Adaptive scraping: {url}\n")

# First run - save the selector pattern
print("First run: Saving adaptive pattern...")
page = Fetcher.get(url)

# Use auto_save to remember element patterns
products = page.css('.quote', auto_save=True)
print(f"Found {len(products)} elements, pattern saved\n")

# Later, if website changes, use adaptive=True to relocate elements
# This will find similar elements even if CSS classes changed
print("Later run: Using adaptive matching...")
page = Fetcher.get(url)
relocated = page.css('.quote', adaptive=True)
print(f"Found {len(relocated)} elements using adaptive matching\n")

# Show some data
for quote in relocated[:3]:
    text = quote.css('.text::text').get()
    author = quote.css('.author::text').get()
    print(f"\"{text[:60]}...\" — {author}")
