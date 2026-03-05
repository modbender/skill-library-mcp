#!/usr/bin/env python3
"""search_and_download.py — Search SkillNet and optionally download the top result.

Usage:
  python search_and_download.py "query" [--mode vector] [--threshold 0.7] \
        [--download] [--target-dir ~/.openclaw/workspace/skills] [--no-fallback]

Requires: pip install skillnet-ai
"""
import argparse
import os
import sys

def main():
    parser = argparse.ArgumentParser(description="Search SkillNet skills and optionally download.")
    parser.add_argument("query", help="Search query (keywords or natural language)")
    parser.add_argument("--mode", default="keyword", choices=["keyword", "vector"],
                        help="Search mode: keyword (exact) or vector (semantic)")
    parser.add_argument("--category", default=None, help="Filter by category")
    parser.add_argument("--limit", type=int, default=10, help="Max results")
    parser.add_argument("--threshold", type=float, default=0.75, help="Similarity threshold (vector mode)")
    parser.add_argument("--min-stars", type=int, default=0, help="Minimum star rating")
    parser.add_argument("--download", action="store_true", help="Auto-download the top result")
    parser.add_argument("--target-dir", default=os.path.expanduser("~/.openclaw/workspace/skills"),
                        help="Directory to install downloaded skills into")
    parser.add_argument("--no-fallback", action="store_true",
                        help="Disable automatic retry with vector mode when keyword returns 0 results")
    args = parser.parse_args()

    # Determine effective fallback flag
    fallback = not args.no_fallback

    try:
        from skillnet_ai import SkillNetClient
    except ImportError:
        print("ERROR: skillnet-ai not installed. Run: pip install skillnet-ai", file=sys.stderr)
        sys.exit(1)

    client = SkillNetClient()

    # --- Search ---
    print(f"🔍 Searching SkillNet ({args.mode} mode): \"{args.query}\"")
    results = client.search(
        q=args.query,
        mode=args.mode,
        category=args.category,
        limit=args.limit,
        min_stars=args.min_stars,
        threshold=args.threshold,
    )

    # Fallback: keyword → vector
    if not results and args.mode == "keyword" and fallback:
        print("   No keyword results. Retrying with vector mode (threshold=0.65)...")
        results = client.search(
            q=args.query,
            mode="vector",
            limit=args.limit,
            threshold=0.65,
        )

    if not results:
        print("❌ No skills found.")
        sys.exit(0)

    # --- Display ---
    print(f"\n📋 Found {len(results)} skills:\n")
    for i, s in enumerate(results, 1):
        name = getattr(s, "skill_name", "N/A")
        desc = getattr(s, "skill_description", "")[:120]
        stars = getattr(s, "stars", 0)
        url = getattr(s, "skill_url", "")
        cat = getattr(s, "category", "")
        print(f"  {i}. [{name}]  ⭐ {stars}  ({cat})")
        print(f"     {desc}")
        if url:
            print(f"     {url}")
        print()

    # --- Download top result ---
    if args.download:
        top = results[0]
        url = getattr(top, "skill_url", None)
        if not url:
            print("⚠️  Top result has no URL. Skipping download.")
            sys.exit(0)

        os.makedirs(args.target_dir, exist_ok=True)
        print(f"⬇️  Downloading top result into {args.target_dir}...")
        try:
            installed = client.download(url=url, target_dir=args.target_dir)
            print(f"✅ Installed at: {installed}")
        except Exception as e:
            print(f"❌ Download failed: {e}", file=sys.stderr)
            sys.exit(1)


if __name__ == "__main__":
    main()
