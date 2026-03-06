#!/usr/bin/env python3
"""
jina-reader.py — Read any URL via Jina Reader API.

SECURITY MANIFEST:
    Environment variables accessed: JINA_API_KEY (only)
    External endpoints called: https://r.jina.ai/ (only)
    Local files read: none
    Local files written: none
    Data sent: URL provided as argument + JINA_API_KEY via Authorization header
    Data received: Markdown/JSON content via stdout

Usage:
    python3 jina-reader.py <url> [--json]

Requires JINA_API_KEY environment variable.
No external dependencies (uses urllib from stdlib).
"""

import json
import os
import sys
import urllib.request
import urllib.error


def main():
    if len(sys.argv) < 2 or sys.argv[1] in ("-h", "--help"):
        print("Usage: python3 jina-reader.py <url> [--json]")
        print()
        print("Read any URL (web page or PDF) and return clean markdown.")
        print()
        print("Options:")
        print("  --json    Return JSON output (includes url, title, content)")
        print("  -h        Show this help")
        sys.exit(0)

    api_key = os.environ.get("JINA_API_KEY")
    if not api_key:
        print("Error: JINA_API_KEY environment variable is not set.", file=sys.stderr)
        print("Get your key at https://jina.ai/", file=sys.stderr)
        sys.exit(1)

    url = sys.argv[1]
    use_json = "--json" in sys.argv[2:]
    accept = "application/json" if use_json else "text/plain"

    req = urllib.request.Request(
        f"https://r.jina.ai/{url}",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Accept": accept,
            "User-Agent": "Mozilla/5.0 (compatible; JinaReader/1.0)",
        },
    )

    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            content = resp.read().decode("utf-8")
            print(content)
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        print(f"Error: HTTP {e.code}", file=sys.stderr)
        print(body, file=sys.stderr)
        sys.exit(1)
    except urllib.error.URLError as e:
        print(f"Error: {e.reason}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
