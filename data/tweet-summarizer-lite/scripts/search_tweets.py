#!/usr/bin/env python3
"""
Search stored tweets by text, source, or date.

Usage:
    search_tweets.py --text "search query"
    search_tweets.py --source username
    search_tweets.py --since 2026-02-01
    search_tweets.py --list-sources
    search_tweets.py --stats
"""

import sys
import json
from pathlib import Path
from datetime import datetime

def load_tweets():
    """Load all stored tweets."""
    data_dir = Path.home() / '.openclaw' / 'workspace' / 'data' / 'tweets-lite'
    tweet_file = data_dir / 'index.json'
    
    if not tweet_file.exists():
        return {}
    
    with open(tweet_file, 'r') as f:
        return json.load(f)

def search_by_text(query):
    """Search tweets by text content."""
    tweets = load_tweets()
    query_lower = query.lower()
    
    results = {}
    for tweet_id, data in tweets.items():
        if query_lower in data['text'].lower():
            results[tweet_id] = data
    
    return results

def list_sources():
    """List all sources (tweet authors)."""
    tweets = load_tweets()
    sources = set()
    
    for data in tweets.values():
        # Extract author from text if possible
        if '@' in data['text']:
            match = data['text'].split('@')[1].split(' ')[0]
            sources.add('@' + match)
    
    return sorted(sources)

def get_stats():
    """Show storage statistics."""
    tweets = load_tweets()
    data_dir = Path.home() / '.openclaw' / 'workspace' / 'data' / 'tweets-lite'
    
    return {
        'total_tweets': len(tweets),
        'data_directory': str(data_dir),
        'tweets_file': str(data_dir / 'index.json')
    }

def main():
    if len(sys.argv) < 2:
        print("Usage:")
        print("  search_tweets.py --text 'search query'")
        print("  search_tweets.py --source @username")
        print("  search_tweets.py --list-sources")
        print("  search_tweets.py --stats")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == '--text' and len(sys.argv) > 2:
        query = ' '.join(sys.argv[2:])
        results = search_by_text(query)
        
        print(f"🔍 Found {len(results)} matching tweets:\n")
        for tweet_id, data in results.items():
            print(f"📌 ID: {tweet_id}")
            print(f"   {data['text'][:100]}...")
            print(f"   Stored: {data['timestamp']}\n")
    
    elif command == '--list-sources':
        sources = list_sources()
        print("📍 Tweet sources:")
        for source in sources:
            print(f"  {source}")
    
    elif command == '--stats':
        stats = get_stats()
        print("📊 Storage statistics:")
        print(f"  Total tweets: {stats['total_tweets']}")
        print(f"  Data dir: {stats['data_directory']}")
    
    else:
        print(f"❌ Unknown command: {command}")
        sys.exit(1)

if __name__ == '__main__':
    main()
