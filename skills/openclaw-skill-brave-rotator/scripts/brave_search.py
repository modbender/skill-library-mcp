#!/usr/bin/env python3
"""
Brave Search with automatic API key rotation.
Rotates through multiple keys to maximize free tier limits (2000 req/month per key).

Usage:
    python3 brave_search.py "your query" [--count 5] [--type web|news|image]
    
Environment:
    BRAVE_API_KEYS=key1,key2,key3   (comma-separated list)
    BRAVE_KEY_STATE_FILE            (optional, path to state JSON, default: ~/.brave_key_state.json)
"""

import os
import sys
import json
import time
import argparse
import urllib.request
import urllib.parse
import urllib.error
import gzip
from pathlib import Path


STATE_FILE = Path(os.environ.get("BRAVE_KEY_STATE_FILE", Path.home() / ".brave_key_state.json"))
BRAVE_API_BASE = "https://api.search.brave.com/res/v1"


def load_state():
    if STATE_FILE.exists():
        try:
            return json.loads(STATE_FILE.read_text())
        except Exception:
            pass
    return {"keys": {}, "current_index": 0}


def save_state(state):
    STATE_FILE.write_text(json.dumps(state, indent=2))


def get_keys():
    raw = os.environ.get("BRAVE_API_KEYS", "")
    keys = [k.strip() for k in raw.split(",") if k.strip()]
    if not keys:
        print("ERROR: BRAVE_API_KEYS not set. Export as: export BRAVE_API_KEYS=key1,key2,key3", file=sys.stderr)
        sys.exit(1)
    return keys


def pick_key(keys, state):
    """Pick next usable key using round-robin. Skip exhausted keys (rate error in last 60s)."""
    n = len(keys)
    start = state.get("current_index", 0) % n
    now = time.time()
    
    for i in range(n):
        idx = (start + i) % n
        key = keys[idx]
        key_state = state["keys"].get(key, {})
        blocked_until = key_state.get("blocked_until", 0)
        if now >= blocked_until:
            state["current_index"] = (idx + 1) % n
            return key, idx
    
    # All blocked — use least recently blocked
    idx = start
    state["current_index"] = (idx + 1) % n
    return keys[idx], idx


def search(query, count=5, search_type="web", country="us", lang="en"):
    keys = get_keys()
    state = load_state()
    
    key, idx = pick_key(keys, state)
    
    endpoint_map = {
        "web": f"{BRAVE_API_BASE}/web/search",
        "news": f"{BRAVE_API_BASE}/news/search",
        "image": f"{BRAVE_API_BASE}/images/search",
    }
    endpoint = endpoint_map.get(search_type, endpoint_map["web"])
    
    params = urllib.parse.urlencode({
        "q": query,
        "count": count,
        "country": country,
        "search_lang": lang,
    })
    url = f"{endpoint}?{params}"
    
    req = urllib.request.Request(url, headers={
        "Accept": "application/json",
        "Accept-Encoding": "gzip",
        "X-Subscription-Token": key,
    })
    
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            raw = resp.read()
            if resp.headers.get("Content-Encoding") == "gzip":
                raw = gzip.decompress(raw)
            data = json.loads(raw)
            state["keys"].setdefault(key, {})["last_success"] = time.time()
            state["keys"][key]["requests"] = state["keys"][key].get("requests", 0) + 1
            save_state(state)
            return data, key, idx
            
    except urllib.error.HTTPError as e:
        if e.code in (429, 403):
            state["keys"].setdefault(key, {})["blocked_until"] = time.time() + 60
            save_state(state)
            print(f"[brave-rotator] Key #{idx} rate limited, rotating...", file=sys.stderr)
            key, idx = pick_key(keys, state)
            req.add_header("X-Subscription-Token", key)
            with urllib.request.urlopen(req, timeout=10) as resp:
                raw = resp.read()
                if resp.headers.get("Content-Encoding") == "gzip":
                    raw = gzip.decompress(raw)
                data = json.loads(raw)
                save_state(state)
                return data, key, idx
        raise


def format_results(data, search_type="web"):
    results = []
    if search_type == "web":
        items = data.get("web", {}).get("results", [])
        for item in items:
            results.append({
                "title": item.get("title"),
                "url": item.get("url"),
                "snippet": item.get("description"),
            })
    elif search_type == "news":
        items = data.get("results", [])
        for item in items:
            results.append({
                "title": item.get("title"),
                "url": item.get("url"),
                "snippet": item.get("description"),
                "age": item.get("age"),
            })
    elif search_type == "image":
        items = data.get("results", [])
        for item in items:
            results.append({
                "title": item.get("title"),
                "url": item.get("url"),
                "thumbnail": item.get("thumbnail", {}).get("src"),
            })
    return results


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Brave Search with key rotation")
    parser.add_argument("query", help="Search query")
    parser.add_argument("--count", type=int, default=5, help="Number of results (default: 5)")
    parser.add_argument("--type", choices=["web", "news", "image"], default="web", dest="search_type")
    parser.add_argument("--country", default="us")
    parser.add_argument("--lang", default="en")
    parser.add_argument("--json", action="store_true", help="Output raw JSON")
    args = parser.parse_args()
    
    data, used_key, used_idx = search(args.query, args.count, args.search_type, args.country, args.lang)
    
    print(f"[brave-rotator] Used key #{used_idx} ({used_key[:8]}...)", file=sys.stderr)
    
    if args.json:
        print(json.dumps(data, indent=2, ensure_ascii=False))
    else:
        results = format_results(data, args.search_type)
        for i, r in enumerate(results, 1):
            print(f"\n{i}. {r['title']}")
            print(f"   {r['url']}")
            if r.get("snippet"):
                print(f"   {r['snippet'][:150]}")
