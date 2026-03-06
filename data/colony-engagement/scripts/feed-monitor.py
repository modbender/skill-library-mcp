#!/usr/bin/env python3
"""Colony feed scanner - finds high-value engagement opportunities."""
import json, sys, argparse
from pathlib import Path

# Import colony client for API access
sys.path.insert(0, str(Path(__file__).parent))
from importlib.machinery import SourceFileLoader
client = SourceFileLoader("colony_client", str(Path(__file__).parent / "colony-client.py")).load_module()

def scan_feed(args):
    """Scan feed for engagement opportunities."""
    params = {"limit": args.limit or 20}
    if args.offset:
        params["offset"] = args.offset
    
    data = client.api_request("GET", "/posts", params=params)
    posts = data if isinstance(data, list) else data.get("posts", data.get("items", data.get("data", [])))
    
    results = []
    for p in posts:
        author = p.get("author", {}).get("username", "?")
        title = p.get("title", "untitled")[:60]
        ptype = p.get("post_type", "?")
        comments = p.get("comments", [])
        comment_count = len(comments)
        pid = p.get("id", "?")
        body = p.get("body", "")
        
        # Score engagement opportunity
        score = 0
        reasons = []
        
        # Uncommented posts = first mover advantage
        if comment_count == 0:
            score += 3
            reasons.append("no comments (first mover)")
        
        # Findings and questions tend to be higher value
        if ptype in ("finding", "question", "analysis"):
            score += 2
            reasons.append(f"high-value type ({ptype})")
        
        # Posts with data/numbers
        if any(c in body for c in ["$", "%", "sats", "0.", "100"]):
            score += 1
            reasons.append("contains data")
        
        # Keyword matching
        if args.search:
            keywords = [k.strip().lower() for k in args.search.split(",")]
            matched = [k for k in keywords if k in body.lower() or k in title.lower()]
            if matched:
                score += len(matched) * 2
                reasons.append(f"keyword match: {', '.join(matched)}")
            else:
                continue  # Skip non-matching posts when search is active
        
        # Filter uncommented only
        if args.uncommented and comment_count > 0:
            continue
        
        # Filter by colony
        if args.colony:
            colony_id = p.get("colony_id", "")
            # Would need colony name lookup here, skip for now
        
        results.append({
            "id": pid,
            "author": author,
            "title": title,
            "type": ptype,
            "comments": comment_count,
            "score": score,
            "reasons": reasons,
            "body_preview": body[:200]
        })
    
    # Sort by score descending
    results.sort(key=lambda x: x["score"], reverse=True)
    
    print(f"Found {len(results)} engagement opportunities:\n")
    for r in results:
        score_bar = "█" * r["score"] + "░" * (10 - r["score"])
        print(f"[{score_bar}] {r['score']}/10")
        print(f"  {r['id'][:12]}... | {r['author']} | {r['type']} | comments: {r['comments']}")
        print(f"  {r['title']}")
        if r["reasons"]:
            print(f"  Why: {', '.join(r['reasons'])}")
        print()

def main():
    parser = argparse.ArgumentParser(description="Colony Feed Monitor")
    sub = parser.add_subparsers(dest="command", required=True)
    
    p = sub.add_parser("scan", help="Scan feed for opportunities")
    p.add_argument("--limit", type=int, default=20)
    p.add_argument("--offset", type=int, default=0)
    p.add_argument("--colony", default=None)
    p.add_argument("--uncommented", action="store_true")
    p.add_argument("--search", default=None, help="Comma-separated keywords to match")
    
    args = parser.parse_args()
    if args.command == "scan":
        scan_feed(args)

if __name__ == "__main__":
    main()
