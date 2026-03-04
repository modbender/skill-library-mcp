#!/usr/bin/env python3
"""
🐾 Ingest a URL or text into OEE's Second Brain.

Usage:
    python ingest.py "https://example.com/article"
    python ingest.py "https://x.com/user/status/123"
    python ingest.py "https://youtube.com/watch?v=abc"
    python ingest.py --text "Some plain text to remember" --title "My Note"
    echo "content" | python ingest.py --stdin --title "Piped Content"
"""

import argparse
import sys
from kb import ingest, ingest_text


def main():
    parser = argparse.ArgumentParser(description="🐾 Ingest into OEE's Second Brain")
    parser.add_argument("url", nargs="?", help="URL to ingest")
    parser.add_argument("--text", help="Plain text to ingest directly")
    parser.add_argument("--stdin", action="store_true", help="Read text from stdin")
    parser.add_argument("--title", default="Plain Text", help="Title for text ingestion")
    parser.add_argument("--tags", nargs="*", default=[], help="Tags for the content")
    args = parser.parse_args()

    if args.stdin:
        text = sys.stdin.read()
        result = ingest_text(text, title=args.title, tags=args.tags)
    elif args.text:
        result = ingest_text(args.text, title=args.title, tags=args.tags)
    elif args.url:
        result = ingest(args.url, tags=args.tags)
    else:
        parser.print_help()
        sys.exit(1)

    if result["status"] == "duplicate":
        print(f"⚡ Already exists: {result['title']} (id={result['source_id']})")
    else:
        print(f"✅ Done: {result['title']} — {result['chunks']} chunks (id={result['source_id']})")


if __name__ == "__main__":
    main()
