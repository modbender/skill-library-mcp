#!/usr/bin/env python3
"""
News module for daily briefing.
Fetches top headlines from various sources using web search.
"""

import sys
import json
import urllib.request
import urllib.parse
import re
from html.parser import HTMLParser


class MLStripper(HTMLParser):
    """Strip HTML tags from text."""
    def __init__(self):
        super().__init__()
        self.reset()
        self.fed = []
    
    def handle_data(self, d):
        self.fed.append(d)
    
    def get_data(self):
        return ''.join(self.fed)


def strip_tags(html):
    """Remove HTML tags from string."""
    s = MLStripper()
    try:
        s.feed(html)
        return s.get_data()
    except:
        return re.sub(r'<[^>]+>', '', html)


def fetch_hackernews(limit=5):
    """Fetch top stories from Hacker News."""
    try:
        # Get top story IDs
        top_url = "https://hacker-news.firebaseio.com/v0/topstories.json"
        req = urllib.request.Request(top_url)
        with urllib.request.urlopen(req, timeout=10) as response:
            story_ids = json.loads(response.read().decode('utf-8'))[:limit]
        
        stories = []
        for story_id in story_ids:
            story_url = f"https://hacker-news.firebaseio.com/v0/item/{story_id}.json"
            req = urllib.request.Request(story_url)
            with urllib.request.urlopen(req, timeout=5) as response:
                story = json.loads(response.read().decode('utf-8'))
                if story and 'title' in story:
                    stories.append({
                        'title': story['title'],
                        'source': 'Hacker News',
                        'url': story.get('url', f"https://news.ycombinator.com/item?id={story_id}")
                    })
        return stories
    except Exception as e:
        return []


def fetch_rss_feed(url, source_name, limit=5):
    """Generic RSS feed fetcher with basic parsing."""
    try:
        req = urllib.request.Request(
            url,
            headers={'User-Agent': 'Mozilla/5.0 (compatible; DailyBriefing/1.0)'}
        )
        with urllib.request.urlopen(req, timeout=10) as response:
            content = response.read().decode('utf-8', errors='ignore')
        
        # Extract titles using regex (simple approach)
        titles = []
        # Look for <title> tags in items
        items = content.split('<item>')[1:]
        for item in items[:limit]:
            title_match = re.search(r'<title[^>]*>([^<]+)</title>', item)
            if title_match:
                title = strip_tags(title_match.group(1))
                # Clean up CDATA if present
                title = title.replace('<![CDATA[', '').replace(']]>', '').strip()
                if title and len(title) > 10:
                    titles.append({
                        'title': title,
                        'source': source_name,
                        'url': ''
                    })
        return titles
    except Exception as e:
        return []


def fetch_news_fallback(sources=None, limit=5):
    """
    Fallback news aggregation using multiple RSS feeds.
    Returns list of news items.
    """
    if sources is None:
        sources = ['bbc', 'guardian', 'techcrunch']
    
    all_news = []
    
    # RSS feed URLs
    feeds = {
        'bbc': ('http://feeds.bbci.co.uk/news/rss.xml', 'BBC'),
        'guardian': ('http://www.theguardian.com/uk/rss', 'The Guardian'),
        'techcrunch': ('https://techcrunch.com/feed/', 'TechCrunch'),
        'verge': ('https://www.theverge.com/rss/index.xml', 'The Verge'),
        'wired': ('https://www.wired.com/feed/rss', 'Wired'),
    }
    
    for source in sources:
        if source in feeds:
            url, name = feeds[source]
            items = fetch_rss_feed(url, name, limit=limit)
            all_news.extend(items)
    
    # If we didn't get enough from RSS, add Hacker News
    if len(all_news) < limit:
        hn_items = fetch_hackernews(limit=limit - len(all_news))
        all_news.extend(hn_items)
    
    # Return unique items, limited to requested count
    seen = set()
    unique_news = []
    for item in all_news:
        # Simple deduplication by title similarity
        title_lower = item['title'].lower()[:50]
        if title_lower not in seen and len(unique_news) < limit:
            seen.add(title_lower)
            unique_news.append(item)
    
    return unique_news[:limit]


def format_news(news_items):
    """Format news items for output."""
    if not news_items:
        return "⚠️ Unable to fetch news headlines"
    
    output = []
    for item in news_items:
        title = item.get('title', 'Unknown')
        # Truncate long titles
        if len(title) > 100:
            title = title[:97] + '...'
        output.append(f"   • {title}")
    
    return '\n'.join(output)


def get_news(limit=5, sources=None):
    """Get news headlines."""
    news_items = fetch_news_fallback(sources=sources, limit=limit)
    return format_news(news_items)


if __name__ == "__main__":
    limit = int(sys.argv[1]) if len(sys.argv) > 1 else 5
    print(get_news(limit=limit))
