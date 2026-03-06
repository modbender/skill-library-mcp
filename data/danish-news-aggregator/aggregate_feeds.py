#!/usr/bin/env python3
"""
Danish News RSS Aggregator
Fetches multiple Danish RSS feeds and combines them into a single RSS feed.
"""

import json
import os
import sys
from datetime import datetime
from xml.etree import ElementTree
from xml.dom import minidom
import urllib.request
import urllib.error
import ssl

# Configuration
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
FEEDS_FILE = os.path.join(SCRIPT_DIR, "feeds.json")
OUTPUT_FILE = os.path.join(SCRIPT_DIR, "combined_danish_news.xml")
MAX_ITEMS_PER_FEED = 20
USER_AGENT = "DanishNewsAggregator/1.0"

# Default feeds if feeds.json doesn't exist
DEFAULT_FEEDS = [
    {"name": "berlingske", "url": "https://www.berlingske.dk/next-api/feeds/alle", "language": "da"},
    {"name": "politiken", "url": "https://politiken.dk/rss", "language": "da"},
    {"name": "thelocal", "url": "https://feeds.thelocal.com/rss/dk", "language": "en"},
    {"name": "nordjyske", "url": "https://nordjyske.dk/rss/nyheder", "language": "da"},
    {"name": "information", "url": "https://www.information.dk/feed", "language": "da"},
]


def load_feeds():
    """Load feeds from JSON configuration file."""
    if os.path.exists(FEEDS_FILE):
        try:
            with open(FEEDS_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data.get("feeds", DEFAULT_FEEDS)
        except Exception as e:
            print(f"Error loading feeds.json: {e}", file=sys.stderr)
    return DEFAULT_FEEDS


def fetch_feed(feed_info):
    """Fetch and parse a single RSS feed."""
    name = feed_info.get("name", "unknown")
    url = feed_info.get("url", "")
    
    if not url:
        print(f"No URL for feed: {name}", file=sys.stderr)
        return []
    
    print(f"Fetching: {name}...")
    
    try:
        # Create SSL context that doesn't verify certificates (for testing)
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        
        req = urllib.request.Request(
            url,
            headers={"User-Agent": USER_AGENT}
        )
        
        with urllib.request.urlopen(req, timeout=30, context=ctx) as response:
            content = response.read().decode("utf-8")
            
        # Parse RSS/Atom feed
        try:
            root = ElementTree.fromstring(content)
        except ElementTree.ParseError:
            # Try as Atom
            root = ElementTree.fromstring(content)
        
        items = []
        
        # Check if it's RSS or Atom
        if root.tag == "rss":
            channel = root.find("channel")
            if channel is not None:
                for item in channel.findall("item")[:MAX_ITEMS_PER_FEED]:
                    title = _get_text(item, "title")
                    link = _get_text(item, "link")
                    description = _get_text(item, "description")
                    pub_date = _get_text(item, "pubDate") or _get_text(item, "dc:date")
                    
                    if title and link:
                        items.append({
                            "title": title,
                            "link": link,
                            "description": _strip_html(description) if description else "",
                            "pub_date": pub_date,
                            "source": name,
                            "language": feed_info.get("language", "da")
                        })
                        
        elif root.tag == "{http://www.w3.org/2005/Atom}feed" or root.tag == "feed":
            # Atom feed
            for entry in root.findall("entry")[:MAX_ITEMS_PER_FEED]:
                title = _get_text(entry, "title")
                link = _get_atom_link(entry)
                summary = _get_text(entry, "summary") or _get_text(entry, "content")
                pub_date = _get_text(entry, "published") or _get_text(entry, "updated")
                
                if title and link:
                    items.append({
                        "title": title,
                        "link": link,
                        "description": _strip_html(summary) if summary else "",
                        "pub_date": pub_date,
                        "source": name,
                        "language": feed_info.get("language", "da")
                    })
        
        print(f"  -> Got {len(items)} items from {name}")
        return items
        
    except urllib.error.URLError as e:
        print(f"  -> Error fetching {name}: {e}", file=sys.stderr)
        return []
    except Exception as e:
        print(f"  -> Error parsing {name}: {e}", file=sys.stderr)
        return []


def _get_text(element, tag):
    """Get text from an XML element, handling namespaces."""
    if element is None:
        return ""
    
    # Try direct tag
    found = element.find(tag)
    if found is not None and found.text:
        return found.text
    
    # Try with namespace
    for ns in ["", "http://purl.org/dc/elements/1.1/", "http://search.yahoo.com/mrss/"]:
        found = element.find(f"{{{ns}}}{tag}")
        if found is not None and found.text:
            return found.text
    
    return ""


def _get_atom_link(entry):
    """Get link from Atom entry."""
    # Try link with rel="alternate" or no rel
    for link in entry.findall("link"):
        rel = link.get("rel", "alternate")
        if rel == "alternate" or rel is None:
            href = link.get("href")
            if href:
                return href
    return ""


def _strip_html(text):
    """Remove HTML tags from text."""
    if not text:
        return ""
    import re
    # Remove HTML tags
    clean = re.sub(r"<[^>]+>", "", text)
    # Decode HTML entities
    clean = clean.replace("&nbsp;", " ")
    clean = clean.replace("&amp;", "&")
    clean = clean.replace("&lt;", "<")
    clean = clean.replace("&gt;", ">")
    clean = clean.replace("&quot;", '"')
    return clean.strip()


def parse_date(date_str):
    """Parse various date formats to datetime."""
    if not date_str:
        return datetime(1970, 1, 1)  # Return epoch for empty dates
    
    # Try to detect and handle timezone
    date_str = date_str.strip()
    has_timezone = any(tz in date_str for tz in ["GMT", "UTC", "+", "-"])
    
    formats = [
        "%a, %d %b %Y %H:%M:%S %z",  # RFC 822 with timezone
        "%a, %d %b %Y %H:%M:%S GMT",  # RFC 822 (GMT) - treat as UTC
        "%Y-%m-%dT%H:%M:%S%z",        # ISO 8601 with timezone
        "%Y-%m-%dT%H:%M:%S",          # ISO 8601 (no timezone)
        "%Y-%m-%d %H:%M:%S",          # Simple format
    ]
    
    for fmt in formats:
        try:
            dt = datetime.strptime(date_str, fmt)
            # Convert to naive datetime (remove timezone info for comparison)
            if dt.tzinfo is not None:
                dt = dt.replace(tzinfo=None)
            return dt
        except ValueError:
            continue
    
    return datetime(1970, 1, 1)  # Return epoch for unparseable dates


def generate_rss(articles, output_path):
    """Generate combined RSS feed."""
    rss = ElementTree.Element("rss", version="2.0")
    rss.set("xmlns:atom", "http://www.w3.org/2005/Atom")
    
    channel = ElementTree.SubElement(rss, "channel")
    
    # Channel metadata
    ElementTree.SubElement(channel, "title").text = "Danish News Aggregator"
    ElementTree.SubElement(channel, "link").text = "https://example.com/danish-news"
    ElementTree.SubElement(channel, "description").text = "Combined Danish news from multiple sources"
    ElementTree.SubElement(channel, "language").text = "da"
    ElementTree.SubElement(channel, "lastBuildDate").text = datetime.utcnow().strftime("%a, %d %b %Y %H:%M:%S GMT")
    ElementTree.SubElement(channel, "generator").text = "DanishNewsAggregator/1.0"
    
    # Atom link
    atom_link = ElementTree.SubElement(channel, "atom:link")
    atom_link.set("href", "https://example.com/danish-news/combined.xml")
    atom_link.set("rel", "self")
    atom_link.set("type", "application/rss+xml")
    
    # Add articles
    for article in articles:
        item = ElementTree.SubElement(channel, "item")
        
        ElementTree.SubElement(item, "title").text = article.get("title", "")
        ElementTree.SubElement(item, "link").text = article.get("link", "")
        
        desc = article.get("description", "")
        if desc:
            ElementTree.SubElement(item, "description").text = desc
        
        pub_date = article.get("pub_date", "")
        if pub_date:
            ElementTree.SubElement(item, "pubDate").text = pub_date
        
        # Source and language as categories
        source = article.get("source", "")
        if source:
            ElementTree.SubElement(item, "category").text = source
    
    # Pretty print
    rough_string = ElementTree.tostring(rss, encoding="unicode")
    reparsed = minidom.parseString(rough_string)
    pretty_xml = reparsed.toprettyxml(indent="  ", encoding="UTF-8")
    
    with open(output_path, "wb") as f:
        f.write(pretty_xml)
    
    print(f"\nCombined RSS feed written to: {output_path}")
    print(f"Total articles: {len(articles)}")


def main():
    """Main function."""
    print("=" * 50)
    print("Danish News RSS Aggregator")
    print("=" * 50)
    
    # Load feeds
    feeds = load_feeds()
    print(f"\nLoaded {len(feeds)} feeds\n")
    
    # Fetch all feeds
    all_articles = []
    for feed in feeds:
        articles = fetch_feed(feed)
        all_articles.extend(articles)
    
    print(f"\nTotal articles fetched: {len(all_articles)}")
    
    # Sort by date (newest first)
    # First, try to parse dates for proper sorting
    for article in all_articles:
        article["_parsed_date"] = parse_date(article.get("pub_date", ""))
    
    all_articles.sort(key=lambda x: x["_parsed_date"], reverse=True)
    
    # Remove date parsing helper
    for article in all_articles:
        del article["_parsed_date"]
    
    # Generate combined RSS
    generate_rss(all_articles, OUTPUT_FILE)
    
    print("\nDone!")


if __name__ == "__main__":
    main()
