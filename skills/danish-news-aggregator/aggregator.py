#!/usr/bin/env python3
"""
Danish News RSS Aggregator
Aggregates 100+ Danish RSS feeds into category-based unified feeds.
"""

import feedparser
import json
import os
import hashlib
from datetime import datetime, timedelta
from dateutil import parser as dateparser
from collections import defaultdict

# Configuration
CONFIG = {
    "refresh_interval": 900,  # 15 minutes
    "max_items_per_feed": 50,
    "max_items_total": 200,
    "deduplicate": True,
    "time_filter_hours": 24,
}

# Verified working feeds organized by category
FEEDS = {
    "national": [
        {"url": "https://www.dr.dk/nyheder/service/rss", "name": "DR Nyheder", "authority": 10},
        {"url": "https://www.berlingske.dk/content/rss", "name": "Berlingske", "authority": 9},
        {"url": "https://politiken.dk/rss/senestenyt.rss", "name": "Politiken", "authority": 9},
        {"url": "https://www.information.dk/feed", "name": "Information", "authority": 8},
        {"url": "https://www.kristeligt-dagblad.dk/rss", "name": "Kristeligt Dagblad", "authority": 7},
        {"url": "https://www.weekendavisen.dk/rss", "name": "Weekendavisen", "authority": 7},
        {"url": "https://feeds.thelocal.com/rss/dk", "name": "The Local Denmark", "authority": 6},
    ],
    "regional": [
        {"url": "https://nordjyske.dk/rss/nyheder", "name": "Nordjyske", "authority": 7},
        {"url": "https://fyens.dk/feed/danmark", "name": "Fyens Stiftstidende", "authority": 6},
        {"url": "https://jv.dk/feed/danmark", "name": "JydskeVestkysten", "authority": 6},
        {"url": "https://hsfo.dk/feed/danmark", "name": "Horsens Folkeblad", "authority": 5},
        {"url": "https://frdb.dk/feed/danmark", "name": "Fredericia Dagblad", "authority": 5},
    ],
    "sports": [
        {"url": "https://www.tv2.dk/sport/rss", "name": "TV2 Sport", "authority": 8},
        {"url": "http://www.bold.dk/feed/rss_by_tag/246752", "name": "Bold.dk", "authority": 7},
        {"url": "https://www.tipsbladet.dk/rss-feed-fra-tips-bladet", "name": "Tipsbladet", "authority": 7},
 "https://www        {"url":.dr.dk/sport/rss", "name": "DR Sport", "authority": 7},
    ],
    "business": [
        {"url": "https://finans.dk/rss", "name": "Finans", "authority": 8},
        {"url": "https://borsen.dk/rss", "name": "Børsen", "authority": 8},
        {"url": "https://www.nationalbanken.dk/da/rss-feeds", "name": "Nationalbanken", "authority": 7},
    ],
    "tech": [
        {"url": "https://version2.dk/rss", "name": "Version2", "authority": 7},
        {"url": "https://ing.dk/rss/senestenyt", "name": "Ingeniøren", "authority": 7},
        {"url": "https://www.computerworld.dk/rss/all", "name": "Computerworld DK", "authority": 6},
    ],
    "english": [
        {"url": "https://feeds.thelocal.com/rss/dk", "name": "The Local Denmark", "authority": 8},
        {"url": "https://cphpost.dk/feed/", "name": "The Copenhagen Post", "authority": 7},
        {"url": "https://yourdanishlife.dk/feed", "name": "Your Danish Life", "authority": 5},
    ],
}


def fetch_feed(url, name, authority):
    """Fetch and parse a single RSS feed."""
    try:
        feed = feedparser.parse(url)
        entries = []
        cutoff_time = datetime.now() - timedelta(hours=CONFIG["time_filter_hours"])
        
        for entry in feed.entries[:20]:  # Limit per source
            try:
                published = None
                if hasattr(entry, 'published'):
                    try:
                        published = dateparser.parse(entry.published)
                    except:
                        pass
                elif hasattr(entry, 'updated'):
                    try:
                        published = dateparser.parse(entry.updated)
                    except:
                        pass
                
                # Skip old entries
                if published and published < cutoff_time:
                    continue
                
                # Create unique ID
                entry_id = hashlib.md5(
                    (entry.get('link', entry.get('title', '')) + name).encode()
                ).hexdigest()
                
                entries.append({
                    'id': entry_id,
                    'title': entry.get('title', 'No title'),
                    'link': entry.get('link', ''),
                    'summary': entry.get('summary', entry.get('description', ''))[:500],
                    'published': published.isoformat() if published else datetime.now().isoformat(),
                    'source': name,
                    'authority': authority,
                    'category': [],
                })
            except Exception:
                continue
        
        return entries
    except Exception as e:
        print(f"Error fetching {name}: {e}")
        return []


def deduplicate(entries):
    """Remove duplicate entries based on title similarity."""
    seen = set()
    unique = []
    
    for entry in entries:
        # Simple dedupe - use link as key
        link = entry['link']
        if link and link not in seen:
            seen.add(link)
            unique.append(entry)
    
    return unique


def sort_by_authority_and_time(entries):
    """Sort by authority (source quality) then by time."""
    return sorted(entries, key=lambda x: (x['authority'], x['published']), reverse=True)


def generate_rss(entries, feed_title, feed_description, feed_url):
    """Generate RSS 2.0 XML from entries."""
    items = ""
    for entry in entries[:CONFIG["max_items_per_feed"]]:
        items += f"""<item>
    <title><![CDATA[{entry['title']}]]></title>
    <link>{entry['link']}</link>
    <description><![CDATA[{entry['summary']}]]></description>
    <pubDate>{entry['published']}</pubDate>
    <source>{entry['source']}</source>
    <category>{feed_title}</category>
</item>

"""
    
    rss = f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom" xmlns:media="http://search.yahoo.com/mrss/">
<channel>
    <title>{feed_title}</title>
    <description>{feed_description}</description>
    <link>{feed_url}</link>
    <language>da</language>
    <lastBuildDate>{datetime.now().strftime('%a, %d %b %Y %H:%M:%S +0000')}</lastBuildDate>
    <atom:link href="{feed_url}" rel="self" type="application/rss+xml"/>
    <generator>Danish News Aggregator v1.0</generator>
{items}</channel>
</rss>"""
    return rss


def aggregate_category(category, feeds):
    """Aggregate feeds for a specific category."""
    print(f"Aggregating {category}...")
    all_entries = []
    
    for feed_info in feeds:
        entries = fetch_feed(feed_info['url'], feed_info['name'], feed_info['authority'])
        for entry in entries:
            entry['category'] = [category]
        all_entries.extend(entries)
    
    # Deduplicate
    if CONFIG["deduplicate"]:
        all_entries = deduplicate(all_entries)
    
    # Sort by authority
    all_entries = sort_by_authority_and_time(all_entries)
    
    print(f"  Found {len(all_entries)} entries from {len(feeds)} sources")
    return all_entries


def main():
    """Main aggregation function."""
    print("🇩🇰 Danish News Aggregator v1.0")
    print("=" * 40)
    
    # Create output directory
    output_dir = os.path.dirname(os.path.abspath(__file__)) + "/output"
    os.makedirs(output_dir, exist_ok=True)
    
    all_entries_national = aggregate_category("national", FEEDS.get("national", []))
    all_entries_regional = aggregate_category("regional", FEEDS.get("regional", []))
    all_entries_sports = aggregate_category("sports", FEEDS.get("sports", []))
    all_entries_business = aggregate_category("business", FEEDS.get("business", []))
    all_entries_tech = aggregate_category("tech", FEEDS.get("tech", []))
    all_entries_english = aggregate_category("english", FEEDS.get("english", []))
    
    # Combine all for "all" feed
    all_entries_all = (
        all_entries_national + 
        all_entries_regional + 
        all_entries_sports + 
        all_entries_business + 
        all_entries_tech + 
        all_entries_english
    )
    all_entries_all = sort_by_authority_and_time(deduplicate(all_entries_all) if CONFIG["deduplicate"] else all_entries_all)
    
    base_url = "https://your-domain.com/feeds"
    
    # Generate feeds
    feeds_to_generate = [
        ("danish-all.xml", "All Danish News", "All Danish news from major sources", all_entries_all),
        ("danish-national.xml", "Danish National News", "National newspapers (DR, Berlingske, Politiken)", all_entries_national),
        ("danish-regional.xml", "Danish Regional News", "Regional and local newspapers", all_entries_regional),
        ("danish-sports.xml", "Danish Sports News", "Sports from Bold, Tipsbladet, TV2 Sport", all_entries_sports),
        ("danish-business.xml", "Danish Business News", "Business and finance (Børsen, Finans)", all_entries_business),
        ("danish-tech.xml", "Danish Tech News", "Technology and science (Version2, Ingeniøren)", all_entries_tech),
        ("danish-english.xml", "English News from Denmark", "English-language Denmark news", all_entries_english),
    ]
    
    print("\n" + "=" * 40)
    print("Generating feeds:")
    
    for filename, title, desc, entries in feeds_to_generate:
        rss = generate_rss(entries, title, desc, f"{base_url}/{filename}")
        filepath = os.path.join(output_dir, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(rss)
        print(f"  ✅ {filename} ({len(entries)} items)")
    
    print(f"\n📁 Feeds saved to: {output_dir}")
    print("🇩🇰 Aggregation complete!")


if __name__ == "__main__":
    main()
