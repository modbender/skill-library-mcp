#!/usr/bin/env python3
"""social-trends skill — 社交媒体热点分析。

支持抖音热榜抓取，可扩展微博、小红书等。
"""

from __future__ import annotations

from pathlib import Path
import sys

_SCRIPTS_DIR = Path(__file__).resolve().parents[2] / "scripts"
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))

from skill_runner.env import load_repo_dotenv

load_repo_dotenv(__file__)

import json
import sys
import urllib.error
import urllib.request


def fetch_douyin_hot(limit: int = 20) -> list[dict]:
    """Fetch Douyin hot list via public API."""
    url = "https://www.iesdouyin.com/web/api/v2/hotsearch/billboard/word/"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode())
    except (urllib.error.URLError, json.JSONDecodeError):
        return []

    items = []
    for entry in data.get("word_list", [])[:limit]:
        items.append({
            "rank": entry.get("position", 0),
            "title": entry.get("word", ""),
            "hot_value": entry.get("hot_value", 0),
            "url": f"https://www.douyin.com/search/{entry.get('word', '')}",
        })
    return items


def run(args: dict) -> dict:
    platform = args.get("platform", "all")
    limit = args.get("limit", 20)
    query = args.get("query", "").lower()

    results = {}

    if platform in ("douyin", "all"):
        items = fetch_douyin_hot(limit)
        if query:
            items = [i for i in items if query in i["title"].lower()]
        results["douyin"] = items

    return {
        "success": True,
        "platforms": results,
        "total": sum(len(v) for v in results.values()),
    }


def main() -> None:
    if len(sys.argv) > 1:
        args = json.loads(sys.argv[1])
    elif not sys.stdin.isatty():
        args = json.load(sys.stdin)
    else:
        args = {}

    result = run(args)
    json.dump(result, sys.stdout, ensure_ascii=False, indent=2)
    sys.stdout.write("\n")


if __name__ == "__main__":
    main()
