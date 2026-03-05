#!/usr/bin/env python3
"""News fetcher using RSS feeds - fast and reliable."""

import sys
import json
import re
from urllib.request import urlopen
from urllib.error import URLError
from html import unescape
import xml.etree.ElementTree as ET

# RSS Feed sources
SOURCES = {
    "general": [
        {"name": "Tagesschau", "url": "https://www.tagesschau.de/infocomments/extern/feed10344~_all-_all.json"},
        {"name": "FAZ", "url": "https://www.faz.net/rss/aktuell/"},
        {"name": "Spiegel", "url": "https://www.spiegel.de/schlagzeilen/tops/atom.xml"},
        {"name": "Süddeutsche", "url": "https://www.sueddeutsche.de/list/panorama feed"},
    ],
    "it": [
        {"name": "Heise", "url": "https://www.heise.de/rss/heise-topnews.rss"},
        {"name": "Golem", "url": "https://www.golem.de/rss.php"},
        {"name": "Slashdot", "url": "https://slashdot.org/slashdot.rss"},
    ],
    "cybersecurity": [
        {"name": "The Hacker News", "url": "https://feeds.feedburner.com/TheHackersNews"},
        {"name": "BleepingComputer", "url": "https://www.bleepingcomputer.com/feed/"},
        {"name": "Logbuch Netzpolitik", "url": "https://logbuch-netzpolitik.de/layer/feed mp3"},
    ]
}

# Words to filter (case-insensitive)
BLACKLIST = {
    "sport", "trump", "usa", "iran", "ukraine", "putin", "epstein",
    "bürgergeld", "mietreform", "jobs", "stellenmarkt", "karriere",
    "bilder des tages", "streik", "ivanti", "fortinet", "solarwinds", "spd"
}

def clean_text(text):
    """Clean text."""
    if not text:
        return ""
    text = unescape(text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def is_filtered(title):
    """Check if headline contains blacklisted words."""
    if not title:
        return True
    title_lower = title.lower()
    for word in BLACKLIST:
        if word in title_lower:
            return True
    return False

def extract_rss_headlines(url, source_name):
    """Extract headlines from RSS feed."""
    try:
        with urlopen(url, timeout=15) as response:
            content = response.read()
        
        # Try XML parsing
        try:
            root = ET.fromstring(content)
            headlines = []
            
            # Handle different RSS formats
            for item in root.findall('.//item') or root.findall('.//entry'):
                title_elem = item.find('title') or item.find('title')
                link_elem = item.find('link') or item.find('link')
                
                if title_elem is not None and title_elem.text:
                    title = clean_text(title_elem.text)
                    link = ""
                    if link_elem is not None:
                        link = clean_text(link_elem.text) or clean_text(link_elem.get('href', '')) or clean_text(link_elem.get('url', ''))
                    
                    if title and link and not is_filtered(title):
                        headlines.append({"title": title, "url": link, "source": source_name})
            
            return headlines[:15]
            
        except ET.ParseError:
            # Fallback: try JSON (Tagesschau uses JSON)
            import json
            data = json.loads(content)
            headlines = []
            for item in data[:15]:
                title = clean_text(item.get('title', ''))
                link = item.get('link', '')
                if title and link and not is_filtered(title):
                    headlines.append({"title": title, "url": link, "source": source_name})
            return headlines
        
    except (URLError, Exception) as e:
        print(f"  [Error: {source_name} - {e}]", file=sys.stderr)
        return []

def display_category(category, sources):
    """Display news for a category."""
    print(f"\n{'='*50}")
    print(f"  📰 {category.upper()} NEWS")
    print(f"{'='*50}\n")
    
    all_headlines = []
    
    for source in sources:
        headlines = extract_rss_headlines(source["url"], source["name"])
        all_headlines.extend(headlines)
    
    if not all_headlines:
        print("  [No headlines found]")
        return
    
    # Remove duplicates based on title
    seen = set()
    unique_headlines = []
    for h in all_headlines:
        key = h["title"].lower()[:50]
        if key not in seen:
            seen.add(key)
            unique_headlines.append(h)
    
    for i, h in enumerate(unique_headlines[:10], 1):
        print(f"  {i}. {h['title']}")
        print(f"  {h['url']}\n")

def main():
    category = None
    if len(sys.argv) > 1:
        category = sys.argv[1].lower()
    
    if category and category not in SOURCES:
        print(f"Unknown category: {category}")
        print(f"Available: {', '.join(SOURCES.keys())} (or no category for all)")
        sys.exit(1)
    
    categories_to_fetch = [category] if category else list(SOURCES.keys())
    
    for cat in categories_to_fetch:
        display_category(cat, SOURCES[cat])

if __name__ == "__main__":
    main()
