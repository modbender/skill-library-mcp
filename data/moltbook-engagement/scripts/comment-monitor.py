#!/usr/bin/env python3
"""
Monitor your Moltbook posts for new comments that need replies.

Usage:
  python3 comment-monitor.py check --post-id <uuid>     # Check one post for unreplied comments
  python3 comment-monitor.py check-all                    # Check all tracked posts
  python3 comment-monitor.py stats                        # Show engagement stats across all posts
"""

import json, urllib.request, os, sys, argparse, time
from pathlib import Path

_WORKSPACE = os.environ.get("OPENCLAW_WORKSPACE", os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
TRACKER_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "post-tracker.json")
API = "https://www.moltbook.com/api/v1"

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

MY_IDENTIFIERS = _load_my_identifiers()

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

def get_username(comment):
    user = comment.get("user", comment.get("author", {}))
    if isinstance(user, dict):
        return user.get("username", user.get("name", ""))
    return str(user)

def is_me(comment):
    uname = get_username(comment)
    display = ""
    user = comment.get("user", comment.get("author", {}))
    if isinstance(user, dict):
        display = user.get("display_name", "")
    return uname in MY_IDENTIFIERS or display in MY_IDENTIFIERS

def check_post(post_id, verbose=True):
    """Check a post for comments that need replies. Returns list of unreplied comments."""
    # Get post info
    post_resp = molt_api(f"/posts/{post_id}")
    if "error" in post_resp:
        if verbose:
            print(f"  Error fetching post: {post_resp['error']}")
        return []
    
    post = post_resp.get("post", post_resp)
    title = post.get("title", "")[:60]
    total_comments = post.get("comment_count", post.get("comments_count", 0))
    upvotes = post.get("upvotes", 0)
    
    # Get top-level comments (API doesn't return threaded replies)
    comments_resp = molt_api(f"/posts/{post_id}/comments?limit=100")
    comments = []
    if isinstance(comments_resp, dict) and comments_resp.get("comments"):
        comments = comments_resp["comments"]
    elif isinstance(comments_resp, list):
        comments = comments_resp
    
    # Separate our comments from others
    our_comments = [c for c in comments if is_me(c)]
    their_comments = [c for c in comments if not is_me(c)]
    
    # Filter out spam/low-quality
    substantive = []
    for c in their_comments:
        content = c.get("content", "")
        uname = get_username(c)
        # Skip obvious spam
        if len(content) < 20:
            continue
        if any(kw in content.lower() for kw in ["mint claw", "mbc-20", "🦞🦞🦞"]):
            continue
        substantive.append(c)
    
    if verbose:
        print(f"\n{'='*60}")
        print(f"Post: {title}")
        print(f"ID: {post_id[:12]}  |  up:{upvotes}  |  total comments:{total_comments}  |  API top-level:{len(comments)}")
        print(f"Our comments: {len(our_comments)}  |  Others (substantive): {len(substantive)}")
        
        if substantive:
            print(f"\nSubstantive comments from others:")
            for c in substantive:
                cid = c.get("id", "")[:12]
                uname = get_username(c)
                content = c.get("content", "")[:150]
                cup = c.get("upvotes", 0)
                print(f"  {cid}  @{uname:<20}  up:{cup}")
                print(f"    {content}")
                print()
        
        if not substantive:
            print("  No new substantive comments to reply to.")
    
    return substantive

def check_all(verbose=True):
    """Check all tracked posts for new comments."""
    if not os.path.exists(TRACKER_PATH):
        print("No post-tracker.json found. Run post-metrics.py first.")
        return
    
    with open(TRACKER_PATH) as f:
        tracker = json.load(f)
    
    posts = tracker.get("posts", [])
    
    # Only check recent posts (last 7 days worth)
    total_needing_reply = 0
    for post in posts[-10:]:  # Last 10 posts
        pid = post["id"]
        unreplied = check_post(pid, verbose)
        total_needing_reply += len(unreplied)
    
    print(f"\n{'='*60}")
    print(f"TOTAL: {total_needing_reply} substantive comments across {min(len(posts), 10)} recent posts")

def show_stats():
    """Show overall engagement stats."""
    if not os.path.exists(TRACKER_PATH):
        print("No post-tracker.json found.")
        return
    
    with open(TRACKER_PATH) as f:
        tracker = json.load(f)
    
    posts = tracker.get("posts", [])
    summary = tracker.get("summary", {})
    
    print(f"\n=== Moltbook Engagement Stats ===")
    print(f"Total posts: {len(posts)}")
    print(f"Total upvotes: {summary.get('total_upvotes', 0)}")
    print(f"Total comments: {summary.get('total_comments', 0)}")
    print(f"Avg upvotes/post: {summary.get('avg_upvotes', 0)}")
    print(f"Avg comments/post: {summary.get('avg_comments', 0)}")
    print(f"Best format: {summary.get('best_format', '?')}")
    
    fb = summary.get("format_breakdown", {})
    if fb:
        print(f"\n--- Performance by Format ---")
        for fmt, stats in sorted(fb.items(), key=lambda x: -x[1].get("avg_upvotes", 0)):
            print(f"  {fmt:<25} avg up:{stats.get('avg_upvotes',0):<6} avg cc:{stats.get('avg_comments',0):<6} ({stats.get('count',0)} posts)")
    
    print(f"\n--- Recent Posts ---")
    for p in posts[-5:]:
        print(f"  {p.get('id','')[:12]}  up:{p.get('upvotes',0):<4} cc:{p.get('comments',0):<4} {p.get('format',''):<22} {p.get('title','')[:45]}")

def main():
    parser = argparse.ArgumentParser(description="Moltbook comment monitor")
    sub = parser.add_subparsers(dest="action")
    
    p_check = sub.add_parser("check", help="Check one post for unreplied comments")
    p_check.add_argument("--post-id", required=True)
    
    sub.add_parser("check-all", help="Check all tracked posts")
    sub.add_parser("stats", help="Show engagement stats")
    
    args = parser.parse_args()
    
    if args.action == "check":
        check_post(args.post_id)
    elif args.action == "check-all":
        check_all()
    elif args.action == "stats":
        show_stats()
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
