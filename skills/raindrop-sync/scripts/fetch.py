#!/usr/bin/env python3
"""
Fetch bookmarks from Raindrop.io API.

Usage:
    python3 fetch.py [--since 24h] [--collection ID] [--output FILE]

Environment:
    RAINDROP_TOKEN - API token from raindrop.io
"""

import argparse
import json
import os
import sys
from datetime import datetime, timedelta
from urllib.request import Request, urlopen
from urllib.error import HTTPError

API_BASE = "https://api.raindrop.io/rest/v1"

def parse_duration(s: str) -> timedelta:
    """Parse duration string like '24h', '7d', '1w'."""
    if s.endswith('h'):
        return timedelta(hours=int(s[:-1]))
    elif s.endswith('d'):
        return timedelta(days=int(s[:-1]))
    elif s.endswith('w'):
        return timedelta(weeks=int(s[:-1]))
    else:
        return timedelta(hours=int(s))

def fetch_raindrops(token: str, collection_id: int = 0, since: datetime = None) -> list:
    """Fetch raindrops from API."""
    url = f"{API_BASE}/raindrops/{collection_id}?perpage=50&sort=-created"
    
    req = Request(url)
    req.add_header("Authorization", f"Bearer {token}")
    
    try:
        with urlopen(req) as resp:
            data = json.loads(resp.read().decode())
    except HTTPError as e:
        print(f"API error: {e.code} {e.reason}", file=sys.stderr)
        sys.exit(1)
    
    items = data.get("items", [])
    
    if since:
        filtered = []
        for item in items:
            created = datetime.fromisoformat(item["created"].replace("Z", "+00:00"))
            if created.replace(tzinfo=None) >= since:
                filtered.append(item)
        return filtered
    
    return items

def main():
    parser = argparse.ArgumentParser(description="Fetch Raindrop.io bookmarks")
    parser.add_argument("--since", help="Fetch items newer than (e.g., 24h, 7d)")
    parser.add_argument("--collection", type=int, default=0, help="Collection ID (0 = all)")
    parser.add_argument("--output", "-o", help="Output file (default: stdout)")
    args = parser.parse_args()
    
    token = os.environ.get("RAINDROP_TOKEN")
    if not token:
        print("Error: RAINDROP_TOKEN not set", file=sys.stderr)
        sys.exit(1)
    
    since = None
    if args.since:
        since = datetime.utcnow() - parse_duration(args.since)
    
    items = fetch_raindrops(token, args.collection, since)
    
    output = []
    for item in items:
        output.append({
            "id": item["_id"],
            "title": item.get("title", ""),
            "url": item.get("link", ""),
            "excerpt": item.get("excerpt", ""),
            "tags": item.get("tags", []),
            "created": item.get("created", ""),
            "collection_id": item.get("collection", {}).get("$id")
        })
    
    result = json.dumps(output, indent=2, ensure_ascii=False)
    
    if args.output:
        with open(args.output, "w") as f:
            f.write(result)
        print(f"Wrote {len(output)} items to {args.output}", file=sys.stderr)
    else:
        print(result)

if __name__ == "__main__":
    main()
