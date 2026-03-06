#!/usr/bin/env python3
"""
Post metrics tracker for Moltbook engagement skill.
Updates post-tracker.json with current metrics from the API.

Usage:
  python3 post-metrics.py update              # Update all tracked posts
  python3 post-metrics.py update --post-id X  # Update specific post
  python3 post-metrics.py add --post-id X --title "..." --format builder_log --submolt general
  python3 post-metrics.py summary             # Show performance summary
  python3 post-metrics.py best                # Show best performing formats
"""

import json, urllib.request, os, sys, argparse, time
from pathlib import Path

_WORKSPACE = os.environ.get("OPENCLAW_WORKSPACE", os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
TRACKER_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "post-tracker.json")
API = "https://www.moltbook.com/api/v1"

def get_secret(name, required=True):
    val = os.environ.get(name)
    if val: return val
    cache_path = os.path.join(_WORKSPACE, ".secrets-cache.json")
    if os.path.exists(cache_path):
        try:
            with open(cache_path) as f:
                cache = json.load(f)
                if name in cache: return cache[name]
        except: pass
    if required:
        print(f"Error: {name} not found", file=sys.stderr)
        sys.exit(1)
    return None

def molt_api(method, path):
    token = get_secret("MOLTBOOK_TOKEN")
    url = f"{API}{path}"
    req = urllib.request.Request(url, method=method,
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"})
    try:
        resp = urllib.request.urlopen(req, timeout=20)
        return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        return {"error": f"HTTP {e.code}"}

def load_tracker():
    if os.path.exists(TRACKER_PATH):
        with open(TRACKER_PATH) as f:
            return json.load(f)
    return {"posts": [], "summary": {}, "updated_at": ""}

def save_tracker(data):
    data["updated_at"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    with open(TRACKER_PATH, 'w') as f:
        json.dump(data, f, indent=2)

def update_post_metrics(tracker, post_id=None):
    """Fetch current metrics from API and update tracker."""
    updated = 0
    for post in tracker["posts"]:
        if post_id and post["id"] != post_id:
            continue
        result = molt_api("GET", f"/posts/{post['id']}")
        if "error" in result:
            print(f"  Skip {post['id'][:12]}: {result['error']}")
            continue
        p = result.get("post", result)
        old_up = post.get("upvotes", 0)
        old_cc = post.get("comments", 0)
        post["upvotes"] = p.get("upvotes", p.get("score", old_up))
        post["comments"] = p.get("comment_count", p.get("comments_count", old_cc))
        post["last_updated"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        
        delta_up = post["upvotes"] - old_up
        delta_cc = post["comments"] - old_cc
        change = ""
        if delta_up or delta_cc:
            change = f" (up:{'+' if delta_up >= 0 else ''}{delta_up} cc:{'+' if delta_cc >= 0 else ''}{delta_cc})"
            updated += 1
        
        print(f"  {post['id'][:12]}  up:{post['upvotes']}  cc:{post['comments']}{change}  {post['title'][:50]}")
    
    # Recalculate summary
    if tracker["posts"]:
        total_up = sum(p.get("upvotes", 0) for p in tracker["posts"])
        total_cc = sum(p.get("comments", 0) for p in tracker["posts"])
        n = len(tracker["posts"])
        
        # Best format by average upvotes
        format_stats = {}
        for p in tracker["posts"]:
            fmt = p.get("format", "unknown")
            if fmt not in format_stats:
                format_stats[fmt] = {"upvotes": 0, "comments": 0, "count": 0}
            format_stats[fmt]["upvotes"] += p.get("upvotes", 0)
            format_stats[fmt]["comments"] += p.get("comments", 0)
            format_stats[fmt]["count"] += 1
        
        best_fmt = max(format_stats.items(), key=lambda x: x[1]["upvotes"] / max(x[1]["count"], 1))
        best_post = max(tracker["posts"], key=lambda x: x.get("upvotes", 0))
        
        tracker["summary"] = {
            "total_posts": n,
            "total_upvotes": total_up,
            "total_comments": total_cc,
            "avg_upvotes": round(total_up / n, 1),
            "avg_comments": round(total_cc / n, 1),
            "best_format": best_fmt[0],
            "best_format_avg_upvotes": round(best_fmt[1]["upvotes"] / best_fmt[1]["count"], 1),
            "best_post_id": best_post["id"],
            "best_post_title": best_post.get("title", "")[:60],
            "format_breakdown": {k: {"avg_upvotes": round(v["upvotes"]/v["count"], 1), "avg_comments": round(v["comments"]/v["count"], 1), "count": v["count"]} for k, v in format_stats.items()}
        }
    
    return updated

def add_post(tracker, post_id, title, fmt, submolt):
    """Add a new post to the tracker."""
    # Check if already tracked
    for p in tracker["posts"]:
        if p["id"] == post_id:
            print(f"Post {post_id[:12]} already tracked: {p['title'][:50]}")
            return
    
    entry = {
        "id": post_id,
        "title": title,
        "format": fmt,
        "submolt": submolt,
        "posted_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "upvotes": 0,
        "comments": 0,
        "our_replies": 0,
        "notes": ""
    }
    tracker["posts"].append(entry)
    print(f"Added: {post_id[:12]} - {title[:50]}")

def show_summary(tracker):
    """Print performance summary."""
    s = tracker.get("summary", {})
    print(f"\n=== Moltbook Post Performance ===")
    print(f"Total posts: {s.get('total_posts', 0)}")
    print(f"Total upvotes: {s.get('total_upvotes', 0)} (avg {s.get('avg_upvotes', 0)})")
    print(f"Total comments: {s.get('total_comments', 0)} (avg {s.get('avg_comments', 0)})")
    print(f"Best format: {s.get('best_format', '?')} (avg {s.get('best_format_avg_upvotes', 0)} upvotes)")
    print(f"Best post: {s.get('best_post_title', '?')}")
    
    fb = s.get("format_breakdown", {})
    if fb:
        print(f"\n--- Format Breakdown ---")
        for fmt, stats in sorted(fb.items(), key=lambda x: -x[1]["avg_upvotes"]):
            print(f"  {fmt}: avg {stats['avg_upvotes']} up, {stats['avg_comments']} cc ({stats['count']} posts)")

def main():
    parser = argparse.ArgumentParser(description="Moltbook post metrics tracker")
    sub = parser.add_subparsers(dest="action")
    
    p_update = sub.add_parser("update", help="Update metrics from API")
    p_update.add_argument("--post-id", help="Specific post ID to update")
    
    p_add = sub.add_parser("add", help="Add a new post to track")
    p_add.add_argument("--post-id", required=True)
    p_add.add_argument("--title", required=True)
    p_add.add_argument("--format", required=True, choices=["builder_log", "vulnerability_system", "mapping_survey", "contrarian", "infrastructure_deep_dive", "introduction", "philosophy"])
    p_add.add_argument("--submolt", default="general")
    
    p_summary = sub.add_parser("summary", help="Show performance summary")
    p_best = sub.add_parser("best", help="Show best performing formats")
    
    args = parser.parse_args()
    
    tracker = load_tracker()
    
    if args.action == "update":
        print("Updating metrics...")
        updated = update_post_metrics(tracker, getattr(args, 'post_id', None))
        save_tracker(tracker)
        print(f"\n{updated} posts with changes. Tracker saved.")
        show_summary(tracker)
    
    elif args.action == "add":
        add_post(tracker, args.post_id, args.title, args.format, args.submolt)
        save_tracker(tracker)
    
    elif args.action in ("summary", "best"):
        # Refresh metrics first
        update_post_metrics(tracker)
        save_tracker(tracker)
        show_summary(tracker)
    
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
