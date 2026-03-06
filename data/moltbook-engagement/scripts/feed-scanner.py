#!/usr/bin/env python3
"""
Moltbook feed scanner - finds engagement opportunities.

Usage:
  python3 feed-scanner.py scan                    # Scan hot feed for opportunities
  python3 feed-scanner.py scan --sort new          # Scan new feed
  python3 feed-scanner.py scan --min-upvotes 10    # Only show posts with 10+ upvotes
  python3 feed-scanner.py scan --unengaged         # Only show posts we haven't commented on
  python3 feed-scanner.py profile <username>       # Show a user's recent posts
  python3 feed-scanner.py search <query>           # Search posts
  python3 feed-scanner.py trending                 # Show top trending posts
"""

import json, urllib.request, os, sys, argparse, time
from pathlib import Path

_WORKSPACE = os.environ.get("OPENCLAW_WORKSPACE", os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
API = "https://www.moltbook.com/api/v1"
PERMANENT_DEDUP_PATH = os.path.join(_WORKSPACE, "memory", "moltbook-permanent-dedup.json")

# Spam filters
SPAM_KEYWORDS = {"mint claw", "mbc-20", "minting claw", "$mdt", "$shipyard"}
SPAM_AUTHORS = {"donaldtrump", "KingMolt", "crabkarmabot"}

def get_secret(name, required=True):
    val = os.environ.get(name)
    if val: return val
    cache_path = os.path.join(_WORKSPACE, ".secrets-cache.json")
    if os.path.exists(cache_path):
        try:
            with open(cache_path) as f:
                return json.load(f).get(name)
        except: pass
    if required:
        print(f"Error: {name} not found", file=sys.stderr)
        sys.exit(1)
    return None

def molt_api(path):
    token = get_secret("MOLTBOOK_TOKEN")
    url = f"{API}{path}"
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"})
    try:
        resp = urllib.request.urlopen(req, timeout=20)
        return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        return {"error": f"HTTP {e.code}"}

def load_dedup():
    if os.path.exists(PERMANENT_DEDUP_PATH):
        try:
            with open(PERMANENT_DEDUP_PATH) as f:
                return set(json.load(f).get("commented_posts", []))
        except: pass
    return set()

def is_spam(post):
    title = post.get("title", "").lower()
    content = post.get("content", "").lower()[:200]
    user = post.get("user", post.get("author", {}))
    uname = user.get("username", user.get("name", "")) if isinstance(user, dict) else str(user)
    
    if uname in SPAM_AUTHORS:
        return True
    for kw in SPAM_KEYWORDS:
        if kw in title or kw in content:
            return True
    if len(title) < 15 and "claw" in title.lower():
        return True
    return False

def _load_my_identifiers():
    """Load identity set from env, config file, or defaults."""
    identifiers = set()
    env_user = os.environ.get("MOLTBOOK_USERNAME")
    if env_user:
        identifiers.add(env_user)
    for path in [
        os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "moltbook-identity.json"),
        os.path.join(_WORKSPACE, "moltbook-identity.json"),
    ]:
        if os.path.exists(path):
            try:
                with open(path) as f:
                    for name in json.load(f).get("identifiers", []):
                        identifiers.add(name)
            except: pass
    return identifiers or {"real-yoder-og-bot", "Yoder", "yoder"}

_MY_IDS = _load_my_identifiers()

def is_our_post(post):
    user = post.get("user", post.get("author", {}))
    uname = user.get("username", user.get("name", "")) if isinstance(user, dict) else str(user)
    return uname in _MY_IDS

def format_post(post, dedup_set, show_content=False):
    user = post.get("user", post.get("author", {}))
    uname = user.get("username", user.get("name", "")) if isinstance(user, dict) else str(user)
    pid = post["id"]
    title = post.get("title", "")[:65]
    up = post.get("upvotes", 0)
    cc = post.get("comment_count", post.get("comments_count", 0))
    submolt = post.get("submolt", {})
    sub_name = submolt.get("name", "?") if isinstance(submolt, dict) else "?"
    
    # Check engagement status
    engaged = pid in dedup_set
    # Also check if any post_id:parent_id combos exist
    if not engaged:
        for key in dedup_set:
            if key.startswith(pid):
                engaged = True
                break
    
    status = "[DONE]" if engaged else "[NEW] "
    
    line = f"{status} {pid[:12]}  @{uname[:18]:<18}  up:{up:<5} cc:{cc:<5} m/{sub_name:<15}  {title}"
    
    if show_content:
        content = post.get("content", "")[:300]
        line += f"\n    {content}\n"
    
    return line

def scan_feed(sort="hot", limit=50, min_upvotes=0, unengaged_only=False, show_content=False):
    dedup = load_dedup()
    
    results = []
    for offset in range(0, min(limit, 200), 50):
        batch_size = min(50, limit - offset)
        resp = molt_api(f"/posts?sort={sort}&limit={batch_size}&offset={offset}")
        posts = resp.get("posts", resp) if isinstance(resp, dict) else resp
        if not posts:
            break
        results.extend(posts)
    
    print(f"=== Moltbook Feed ({sort}) - {len(results)} posts scanned ===\n")
    
    shown = 0
    for p in results:
        if is_spam(p) or is_our_post(p):
            continue
        up = p.get("upvotes", 0)
        if up < min_upvotes:
            continue
        
        pid = p["id"]
        engaged = pid in dedup or any(k.startswith(pid) for k in dedup)
        if unengaged_only and engaged:
            continue
        
        print(format_post(p, dedup, show_content))
        shown += 1
    
    print(f"\n{shown} posts shown (filtered spam + own posts)")
    if unengaged_only:
        print("Showing unengaged only")

def search_posts(query, limit=20):
    dedup = load_dedup()
    resp = molt_api(f"/search?q={urllib.request.quote(query)}&type=post&limit={limit}")
    results = resp.get("results", [])
    
    print(f"=== Search: '{query}' - {len(results)} results ===\n")
    for r in results:
        pid = r.get("id", "?")
        author = r.get("author", {})
        aname = author.get("name", "?") if isinstance(author, dict) else "?"
        title = r.get("title", "")[:65]
        up = r.get("upvotes", 0)
        rel = r.get("relevance", 0)
        
        engaged = pid in dedup or any(k.startswith(pid) for k in dedup)
        status = "[DONE]" if engaged else "[NEW] "
        
        print(f"{status} {pid[:12]}  @{aname[:18]:<18}  up:{up:<5} rel:{rel:.2f}  {title}")

def trending(limit=20):
    """Show top posts by upvotes."""
    dedup = load_dedup()
    resp = molt_api(f"/posts?sort=top&limit={limit}")
    posts = resp.get("posts", resp) if isinstance(resp, dict) else resp
    
    print(f"=== Trending (Top {limit}) ===\n")
    for p in posts:
        if is_spam(p):
            continue
        print(format_post(p, dedup))

def main():
    parser = argparse.ArgumentParser(description="Moltbook feed scanner")
    sub = parser.add_subparsers(dest="action")
    
    p_scan = sub.add_parser("scan", help="Scan feed for opportunities")
    p_scan.add_argument("--sort", default="hot", choices=["hot", "new", "top"])
    p_scan.add_argument("--limit", type=int, default=50)
    p_scan.add_argument("--min-upvotes", type=int, default=0)
    p_scan.add_argument("--unengaged", action="store_true")
    p_scan.add_argument("--content", action="store_true", help="Show post content preview")
    
    p_search = sub.add_parser("search", help="Search posts")
    p_search.add_argument("query")
    p_search.add_argument("--limit", type=int, default=20)
    
    p_trending = sub.add_parser("trending", help="Show trending posts")
    p_trending.add_argument("--limit", type=int, default=20)
    
    args = parser.parse_args()
    
    if args.action == "scan":
        scan_feed(args.sort, args.limit, args.min_upvotes, args.unengaged, args.content)
    elif args.action == "search":
        search_posts(args.query, args.limit)
    elif args.action == "trending":
        trending(args.limit)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
