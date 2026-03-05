#!/usr/bin/env python3
"""
ddgs-search-wrapper: Drop-in replacement for web-search-plus.
Translates ddgs CLI output to the JSON format topic-monitor expects.

Output format: {"provider": "ddgs", "results": [{"title", "url", "snippet", "published_date"}]}
"""
import argparse
import json
import subprocess
import tempfile
import os
from datetime import datetime


def search(query: str, max_results: int = 5, backend: str = "google") -> dict:
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False, mode="w") as f:
        tmp = f.name

    try:
        result = subprocess.run(
            ["ddgs", "text", "-q", query, "-m", str(max_results), "-b", backend, "-o", tmp],
            capture_output=True, text=True, timeout=30,
            env={k: v for k, v in os.environ.items() if k in ("PATH", "HOME", "LANG", "TERM")}
        )

        if os.path.exists(tmp) and os.path.getsize(tmp) > 0:
            with open(tmp) as f:
                raw = json.load(f)
        else:
            return {"provider": "ddgs", "results": [], "error": result.stderr.strip()}

        results = []
        for item in raw:
            results.append({
                "title": item.get("title", ""),
                "url": item.get("href", ""),
                "snippet": item.get("body", ""),
                "published_date": datetime.now().isoformat()
            })

        return {"provider": "ddgs", "results": results}

    except subprocess.TimeoutExpired:
        return {"provider": "ddgs", "results": [], "error": "Search timed out"}
    except Exception as e:
        return {"provider": "ddgs", "results": [], "error": str(e)}
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)


def main():
    parser = argparse.ArgumentParser(description="ddgs search wrapper (web-search-plus compatible)")
    parser.add_argument("--query", "-q", required=True, help="Search query")
    parser.add_argument("--max-results", "-m", type=int, default=5, help="Max results")
    parser.add_argument("--backend", "-b", default="google", help="Search backend")
    args = parser.parse_args()

    output = search(args.query, args.max_results, args.backend)
    print(json.dumps(output))


if __name__ == "__main__":
    main()
