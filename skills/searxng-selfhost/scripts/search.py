#!/usr/bin/env python3
"""
Multi-backend search for agents.
Primary: local SearXNG instance (Google, Bing, Brave, Startpage, DDG, Wikipedia all in one)
Fallback: direct Wikipedia + GitHub APIs

Usage: search.py "your query" [--count N] [--json]
"""

import sys
import json
import re
import urllib.parse
import urllib.request

SEARXNG_URL = "http://127.0.0.1:8888"
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'application/json',
}

def search_searxng(query, count=10):
    """Local SearXNG instance - aggregates Google, Bing, Brave, Startpage, DDG, Wikipedia"""
    url = f"{SEARXNG_URL}/search?q={urllib.parse.quote(query)}&format=json"
    req = urllib.request.Request(url, headers=HEADERS)
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            d = json.loads(r.read())
            return [{'title': x.get('title', ''), 
                     'url': x.get('url', ''),
                     'snippet': x.get('content', '')[:200],
                     'engine': x.get('engine', '?')} for x in d.get('results', [])[:count]]
    except Exception as e:
        print(f"  [SearXNG unavailable: {e}]", file=sys.stderr)
        return None  # Signal to use fallbacks

def search_wikipedia(query, count=5):
    """Wikipedia API - always works"""
    url = f"https://en.wikipedia.org/w/api.php?action=query&list=search&srsearch={urllib.parse.quote(query)}&srlimit={count}&format=json"
    req = urllib.request.Request(url, headers=HEADERS)
    try:
        with urllib.request.urlopen(req, timeout=8) as r:
            d = json.loads(r.read())
            return [{'title': x['title'], 
                     'url': f"https://en.wikipedia.org/wiki/{urllib.parse.quote(x['title'].replace(' ', '_'))}",
                     'snippet': re.sub(r'<[^>]+>', '', x.get('snippet', '')),
                     'engine': 'wikipedia'} for x in d['query']['search'][:count]]
    except: return []

def search_github(query, count=5):
    """GitHub Search API - 10 req/min unauthenticated"""
    url = f"https://api.github.com/search/repositories?q={urllib.parse.quote(query)}&per_page={count}"
    req = urllib.request.Request(url, headers={**HEADERS, 'Accept': 'application/vnd.github.v3+json'})
    try:
        with urllib.request.urlopen(req, timeout=8) as r:
            d = json.loads(r.read())
            return [{'title': x['full_name'], 
                     'url': x['html_url'],
                     'snippet': (x.get('description') or '')[:200],
                     'engine': 'github'} for x in d.get('items', [])[:count]]
    except: return []

def search(query, count=10):
    """Search via SearXNG, fall back to direct APIs"""
    results = search_searxng(query, count)
    if results is not None:
        return results
    
    # Fallback: direct APIs
    print("  [Falling back to Wikipedia + GitHub]", file=sys.stderr)
    wp = search_wikipedia(query, count)
    gh = search_github(query, min(5, count))
    return (wp + gh)[:count]

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: search.py 'query' [--count N] [--json]")
        sys.exit(1)
    
    query = sys.argv[1]
    count = 10
    as_json = '--json' in sys.argv
    
    for i, arg in enumerate(sys.argv):
        if arg == '--count' and i + 1 < len(sys.argv):
            count = int(sys.argv[i + 1])
    
    results = search(query, count)
    
    if as_json:
        print(json.dumps(results, indent=2))
    else:
        if not results:
            print("No results found.")
        else:
            print(f"Found {len(results)} results:\n")
            for i, r in enumerate(results, 1):
                print(f"{i}. [{r['engine']}] {r['title']}")
                print(f"   {r['url']}")
                if r.get('snippet'):
                    print(f"   {r['snippet'][:150]}")
                print()
