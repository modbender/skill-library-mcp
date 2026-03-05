#!/usr/bin/env python3
"""
Farnam Street Blog Fetcher
Fetches articles from Farnam Street RSS and returns structured data.
"""
import sys
import json
import argparse
from datetime import datetime, timezone, timedelta
from pathlib import Path

try:
    import feedparser
    import requests
except ImportError:
    print("Error: Required packages not installed.")
    print("Run: pip install feedparser requests")
    sys.exit(1)

# RSS URL
RSS_URL = "https://fs.blog/feed/"
REQUEST_TIMEOUT = 30


def fetch_rss():
    """Download and parse RSS from Farnam Street"""
    try:
        response = requests.get(RSS_URL, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        return feedparser.parse(response.content)
    except requests.RequestException as e:
        print(json.dumps({"error": f"Failed to fetch RSS: {e}"}))
        sys.exit(1)


def get_date_range(feed):
    """Get available date range from RSS entries

    Returns:
        tuple: (min_date, max_date) in YYYY-MM-DD format, or (None, None)
    """
    dates = []
    for entry in feed.entries:
        # Parse from pubDate
        if hasattr(entry, 'published_parsed') and entry.published_parsed:
            dt = datetime(*entry.published_parsed[:6], tzinfo=timezone.utc)
            dates.append(dt.strftime("%Y-%m-%d"))

    if not dates:
        return None, None

    return min(dates), max(dates)


def extract_date_from_link(link):
    """Extract date from URL (FS Blog doesn't use dates in links)

    Args:
        link: URL string

    Returns:
        None (FS Blog doesn't encode dates in URLs)
    """
    # FS Blog doesn't encode dates in article URLs
    return None


def get_content_by_date(feed, target_date):
    """Extract content for a specific date

    Args:
        feed: Feedparser parsed feed
        target_date: Date string in YYYY-MM-DD format

    Returns:
        dict with keys: title, link, content, pubDate, or None if not found
    """
    target_dt = datetime.strptime(target_date, "%Y-%m-%d")

    for entry in feed.entries:
        # Check by pubDate
        if hasattr(entry, 'published_parsed') and entry.published_parsed:
            dt = datetime(*entry.published_parsed[:6], tzinfo=timezone.utc)
            entry_date = dt.strftime("%Y-%m-%d")

            if entry_date == target_date:
                return extract_entry_content(entry)

    return None


def extract_entry_content(entry):
    """Extract content from an RSS entry

    Returns:
        dict with keys: title, link, content, pubDate, is_members_only
    """
    # Check if members only
    title = entry.get("title", "")
    is_members_only = "[FS Members]" in title

    # Get full content
    if hasattr(entry, 'content') and entry.content:
        content = entry.content[0].get('value', '')
    elif hasattr(entry, 'summary'):
        content = entry.summary
    else:
        content = title

    # Check for members only in content
    if "Members Only content" in content or "Not a member? Join Us" in content:
        is_members_only = True

    return {
        "title": title,
        "link": entry.get("link", ""),
        "pubDate": entry.get("published"),
        "content": content,
        "is_members_only": is_members_only
    }


def search_by_keyword(feed, keyword):
    """Search articles by keyword in title

    Args:
        feed: Feedparser parsed feed
        keyword: Search keyword

    Returns:
        List of matching articles
    """
    results = []
    keyword_lower = keyword.lower()

    for entry in feed.entries:
        title = entry.get("title", "")
        if keyword_lower in title.lower():
            results.append({
                "title": title,
                "link": entry.get("link", ""),
                "pubDate": entry.get("published"),
                "summary": entry.get("summary", "")
            })

    return results


def main():
    parser = argparse.ArgumentParser(description='Fetch Farnam Street articles')
    parser.add_argument('--date-range', action='store_true', help='Show available date range')
    parser.add_argument('--date', type=str, help='Get content for specific date (YYYY-MM-DD)')
    parser.add_argument('--relative', type=str, choices=['yesterday', 'today', 'day-before'],
                       help='Relative date: yesterday, today, day-before')
    parser.add_argument('--search', type=str, help='Search articles by keyword')

    args = parser.parse_args()

    # Fetch RSS
    feed = fetch_rss()

    # Date range mode
    if args.date_range:
        min_date, max_date = get_date_range(feed)
        print(json.dumps({
            "min_date": min_date,
            "max_date": max_date,
            "total_entries": len(feed.entries)
        }, indent=2))
        return

    # Search mode
    if args.search:
        results = search_by_keyword(feed, args.search)
        print(json.dumps({
            "keyword": args.search,
            "count": len(results),
            "results": results[:10]  # Limit to 10 results
        }, indent=2, ensure_ascii=False))
        return

    # Calculate target date
    if args.relative:
        if args.relative == 'yesterday':
            target_date = (datetime.now(timezone.utc) - timedelta(days=1)).strftime("%Y-%m-%d")
        elif args.relative == 'day-before':
            target_date = (datetime.now(timezone.utc) - timedelta(days=2)).strftime("%Y-%m-%d")
        else:  # today
            target_date = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        date_arg = target_date
    elif args.date:
        target_date = args.date
        date_arg = target_date
    else:
        # Default: yesterday
        target_date = (datetime.now(timezone.utc) - timedelta(days=1)).strftime("%Y-%m-%d")
        date_arg = target_date

    # Get content
    content = get_content_by_date(feed, target_date)

    if content:
        # Clean HTML entities
        content["content"] = content["content"].replace('&lt;', '<').replace('&gt;', '>').replace('&amp;', '&')

        print(json.dumps(content, indent=2, ensure_ascii=False))
    else:
        # Return empty result with available range
        min_date, max_date = get_date_range(feed)
        print(json.dumps({
            "error": "not_found",
            "message": f"No content found for {target_date}",
            "target_date": target_date,
            "available_range": {
                "min": min_date,
                "max": max_date
            }
        }, indent=2))


if __name__ == "__main__":
    main()
