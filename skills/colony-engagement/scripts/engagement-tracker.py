#!/usr/bin/env python3
"""Colony engagement tracker - monitors reputation and engagement history."""
import json, sys, time, argparse
from pathlib import Path
from datetime import datetime, timedelta

sys.path.insert(0, str(Path(__file__).parent))
from importlib.machinery import SourceFileLoader
client = SourceFileLoader("colony_client", str(Path(__file__).parent / "colony-client.py")).load_module()

DATA_FILE = Path(__file__).parent.parent / "engagement-data.json"

def load_data():
    if DATA_FILE.exists():
        return json.loads(DATA_FILE.read_text())
    return {
        "posts": [],
        "comments": [],
        "votes": [],
        "karma_history": [],
        "created": datetime.now().isoformat()
    }

def save_data(data):
    DATA_FILE.write_text(json.dumps(data, indent=2))

def cmd_stats(args):
    """Show current engagement stats."""
    data = load_data()
    
    # Get profile from API
    try:
        profile = client.api_request("GET", "/users/me")
        karma = profile.get("karma", 0)
        username = profile.get("username", "?")
        
        # Track karma history
        data["karma_history"].append({
            "ts": datetime.now().isoformat(),
            "karma": karma
        })
        save_data(data)
    except SystemExit:
        karma = "?"
        username = "?"
    
    total_posts = len(data.get("posts", []))
    total_comments = len(data.get("comments", []))
    total_votes = len(data.get("votes", []))
    
    # Last 7 days
    week_ago = (datetime.now() - timedelta(days=7)).isoformat()
    recent_comments = [c for c in data.get("comments", []) if c.get("ts", "") > week_ago]
    recent_posts = [p for p in data.get("posts", []) if p.get("ts", "") > week_ago]
    
    print(f"Colony Engagement Stats for @{username}")
    print(f"{'='*40}")
    print(f"Karma:          {karma}")
    print(f"Total posts:    {total_posts}")
    print(f"Total comments: {total_comments}")
    print(f"Total votes:    {total_votes}")
    print(f"")
    print(f"Last 7 days:")
    print(f"  Posts:    {len(recent_posts)}")
    print(f"  Comments: {len(recent_comments)}")
    
    # Karma trend
    history = data.get("karma_history", [])
    if len(history) >= 2:
        delta = history[-1].get("karma", 0) - history[-2].get("karma", 0)
        direction = "↑" if delta > 0 else "↓" if delta < 0 else "→"
        print(f"  Karma trend: {direction} ({delta:+d})")

def cmd_log(args):
    """Log an engagement action."""
    data = load_data()
    
    entry = {
        "ts": datetime.now().isoformat(),
        "action": args.action,
        "post_id": args.post_id,
        "topic": args.topic or ""
    }
    
    if args.action == "post":
        data["posts"].append(entry)
    elif args.action == "comment":
        data["comments"].append(entry)
    elif args.action == "vote":
        data["votes"].append(entry)
    
    save_data(data)
    print(f"Logged: {args.action} on {args.post_id}")

def cmd_history(args):
    """Show engagement history."""
    data = load_data()
    days = args.days or 7
    cutoff = (datetime.now() - timedelta(days=days)).isoformat()
    
    all_actions = []
    for p in data.get("posts", []):
        if p.get("ts", "") > cutoff:
            all_actions.append({**p, "type": "POST"})
    for c in data.get("comments", []):
        if c.get("ts", "") > cutoff:
            all_actions.append({**c, "type": "COMMENT"})
    for v in data.get("votes", []):
        if v.get("ts", "") > cutoff:
            all_actions.append({**v, "type": "VOTE"})
    
    all_actions.sort(key=lambda x: x.get("ts", ""))
    
    print(f"Engagement history (last {days} days): {len(all_actions)} actions\n")
    for a in all_actions:
        ts = a.get("ts", "?")[:19]
        atype = a.get("type", "?")
        post_id = a.get("post_id", "?")[:12]
        topic = a.get("topic", "")
        print(f"  [{ts}] {atype:8s} {post_id}... {topic}")

def cmd_replies(args):
    """Check for new replies to your posts."""
    data = load_data()
    
    # Get our posts from tracker
    our_posts = data.get("posts", [])
    if not our_posts:
        # Fetch from API
        posts = client.api_request("GET", "/posts", params={"limit": 50})
        post_list = posts if isinstance(posts, list) else posts.get("posts", posts.get("items", []))
        our_posts = [{"post_id": p["id"], "title": p.get("title", "?")} 
                     for p in post_list 
                     if p.get("author", {}).get("username") == "yoder"]
    
    print("Checking for replies to your posts...\n")
    for post in our_posts[:10]:
        pid = post.get("post_id", "?")
        try:
            comments = client.api_request("GET", f"/posts/{pid}/comments")
            comment_list = comments if isinstance(comments, list) else comments.get("comments", [])
            
            # Filter out our own comments
            others = [c for c in comment_list if c.get("author", {}).get("username") != "yoder"]
            if others:
                print(f"Post: {post.get('title', pid[:12])}")
                for c in others[-3:]:  # Last 3 replies
                    author = c.get("author", {}).get("username", "?")
                    body = c.get("body", "")[:120]
                    print(f"  {author}: {body}")
                print()
        except SystemExit:
            pass  # Skip errors, keep checking

def main():
    parser = argparse.ArgumentParser(description="Colony Engagement Tracker")
    sub = parser.add_subparsers(dest="command", required=True)
    
    sub.add_parser("stats", help="Show engagement stats")
    
    p = sub.add_parser("log", help="Log an engagement action")
    p.add_argument("--action", required=True, choices=["post", "comment", "vote"])
    p.add_argument("--post-id", required=True)
    p.add_argument("--topic", default=None)
    
    p = sub.add_parser("history", help="Show engagement history")
    p.add_argument("--days", type=int, default=7)
    
    sub.add_parser("replies", help="Check for new replies")
    
    args = parser.parse_args()
    commands = {
        "stats": cmd_stats, "log": cmd_log,
        "history": cmd_history, "replies": cmd_replies,
    }
    commands[args.command](args)

if __name__ == "__main__":
    main()
