#!/usr/bin/env python3
import sys
import os
import json
import hashlib
import urllib.request
import urllib.parse
import ssl
import argparse
import concurrent.futures
import subprocess
import xml.etree.ElementTree as ET
import re

# Configuration (v3.5.1)
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GOOGLE_CSE_ID = os.getenv("GOOGLE_CSE_ID")
REDIS_HOST = os.getenv("REDIS_HOST")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
SCRAPLING_PYTHON = os.getenv("SCRAPLING_PYTHON_PATH", "python3")
# Corrected: Script is now in the same directory as this file
STEALTH_SCRIPT = os.path.join(os.path.dirname(__file__), "stealth_fetch.py")
USER_AGENT = os.getenv("SEARCH_USER_AGENT", "SearchCluster/3.5.1")

def internal_sanitize(text):
    if not text: return ""
    text = re.sub(r'ignore .*instructions|system override|you are now', '[REDACTED]', text, flags=re.I)
    text = "".join(ch for ch in text if ch.isprintable() or ch in ['\n', '\r', '\t'])
    return text.strip()

redis_client = None
if REDIS_HOST:
    try:
        import redis
        redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True, socket_connect_timeout=1)
    except: pass

def redis_set(key, value):
    if redis_client:
        try: redis_client.setex(key, 86400, value)
        except: pass

def redis_get(key):
    if redis_client:
        try: return redis_client.get(key)
        except: pass
    return None

def wiki_search(query):
    cache_key = f"search:wiki:{hashlib.md5(query.encode()).hexdigest()}"
    cached = redis_get(cache_key)
    if cached: return json.loads(cached)
    url = f"https://en.wikipedia.org/w/api.php?action=opensearch&search={urllib.parse.quote(query)}&limit=5&namespace=0&format=json"
    ctx = ssl.create_default_context()
    try:
        req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
        with urllib.request.urlopen(req, timeout=10, context=ctx) as response:
            data = json.loads(response.read().decode())
            results = []
            if isinstance(data, list) and len(data) > 3:
                for i in range(len(data[1])):
                    results.append({
                        "source": "wiki",
                        "title": internal_sanitize(data[1][i]),
                        "link": data[3][i],
                        "snippet": internal_sanitize(data[2][i])
                    })
            if results: redis_set(cache_key, json.dumps(results))
            return results
    except: return []

def reddit_search(query):
    cache_key = f"search:reddit:{hashlib.md5(query.encode()).hexdigest()}"
    cached = redis_get(cache_key)
    if cached: return json.loads(cached)
    url = f"https://www.reddit.com/search.json?q={urllib.parse.quote(query)}&limit=5"
    ctx = ssl.create_default_context()
    try:
        req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
        with urllib.request.urlopen(req, timeout=10, context=ctx) as response:
            data = json.loads(response.read().decode())
            results = []
            if "data" in data and "children" in data["data"]:
                for child in data["data"]["children"]:
                    post = child["data"]
                    results.append({
                        "source": "reddit",
                        "title": internal_sanitize(post.get("title")),
                        "link": f"https://reddit.com{post.get('permalink')}",
                        "snippet": internal_sanitize(f"r/{post.get('subreddit')} | {post.get('selftext', '')[:200]}")
                    })
            if results: redis_set(cache_key, json.dumps(results))
            return results
    except: return []

def scrapling_search(query):
    if not os.path.exists(SCRAPLING_PYTHON) or not os.path.exists(STEALTH_SCRIPT):
        return []
    try:
        result = subprocess.run([SCRAPLING_PYTHON, STEALTH_SCRIPT, query], capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            data = json.loads(result.stdout)
            for item in data:
                item["snippet"] = internal_sanitize(item.get("snippet", ""))
            return data
    except: pass
    return []

def gnews_search(query):
    url = f"https://news.google.com/rss/search?q={urllib.parse.quote(query)}&hl=en-US&gl=US&ceid=US:en"
    ctx = ssl.create_default_context()
    try:
        req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
        with urllib.request.urlopen(req, timeout=10, context=ctx) as response:
            root = ET.fromstring(response.read())
            results = []
            for item in root.findall(".//item")[:10]:
                results.append({
                    "source": "gnews",
                    "title": internal_sanitize(item.find("title").text),
                    "link": item.find("link").text,
                    "snippet": "Latest News via Google RSS"
                })
            return results
    except: return []

def google_search(query):
    if not GOOGLE_API_KEY or not GOOGLE_CSE_ID: return []
    url = f"https://www.googleapis.com/customsearch/v1?key={GOOGLE_API_KEY}&cx={GOOGLE_CSE_ID}&q={urllib.parse.quote(query)}"
    ctx = ssl.create_default_context()
    try:
        req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
        with urllib.request.urlopen(req, timeout=10, context=ctx) as response:
            data = json.loads(response.read().decode())
            results = []
            for item in data.get("items", []):
                results.append({
                    "source": "google", 
                    "title": internal_sanitize(item.get("title")), 
                    "link": item.get("link"), 
                    "snippet": internal_sanitize(item.get("snippet", ""))
                })
            return results
    except: return []

def search_all(query):
    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        futures = {
            executor.submit(google_search, query): "google",
            executor.submit(wiki_search, query): "wiki",
            executor.submit(reddit_search, query): "reddit",
            executor.submit(gnews_search, query): "gnews",
            executor.submit(scrapling_search, query): "scrapling"
        }
        for f in concurrent.futures.as_completed(futures):
            try: results.extend(f.result())
            except: pass
    return results

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Aggregated Search v3.5.1")
    parser.add_argument("source", choices=["google", "wiki", "reddit", "gnews", "scrapling", "all"])
    parser.add_argument("query")
    args = parser.parse_args()
    try:
        if args.source == "all": res = search_all(args.query)
        elif args.source == "wiki": res = wiki_search(args.query)
        elif args.source == "reddit": res = reddit_search(args.query)
        elif args.source == "scrapling": res = scrapling_search(args.query)
        elif args.source == "gnews": res = gnews_search(args.query)
        else: res = google_search(args.query)
        print(json.dumps(res, indent=2))
    except Exception as e:
        print(json.dumps({"error": str(e)}))
        sys.exit(1)
