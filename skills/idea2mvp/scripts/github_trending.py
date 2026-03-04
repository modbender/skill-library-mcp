#!/usr/bin/env python3
"""
GitHub Trending Tool Finder - 一步获取近期热门工具类项目

流程全自动：搜索 → 过滤 → 生成纯文本摘要 → 保存到 tmp/github_results.txt

无需 GitHub Token（未认证限 10 次/分钟，认证后 30 次/分钟）。
如需更高速率，可设置环境变量 GITHUB_TOKEN。

Usage:
    python3 github_trending.py
    python3 github_trending.py --days 7 --min-stars 100
    python3 github_trending.py --lang python --topic cli
    python3 github_trending.py --days 90 --lang typescript --min-stars 200
"""

import argparse
import json
import os
import sys
import urllib.parse
import urllib.request
import urllib.error
from datetime import datetime, timedelta


API_URL = "https://api.github.com/search/repositories"

TMP_DIR = os.path.join(os.getcwd(), "tmp")
RESULT_FILE = os.path.join(TMP_DIR, "github_results.txt")

EXCLUDE_KEYWORDS = [
    "framework", "library", "database", "cloud", "infrastructure",
    "kubernetes", "docker", "terraform", "ansible",
]


def _ensure_tmp_dir():
    os.makedirs(TMP_DIR, exist_ok=True)


def search_github(query, sort="stars", order="desc", per_page=30, page=1, token=None):
    params = f"q={urllib.parse.quote(query)}&sort={sort}&order={order}&per_page={per_page}&page={page}"
    url = f"{API_URL}?{params}"

    headers = {
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "idea2mvp-skill",
    }
    if token:
        headers["Authorization"] = f"token {token}"

    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        print(f"❌ GitHub API error {e.code}: {body}", file=sys.stderr)
        sys.exit(1)
    except urllib.error.URLError as e:
        print(f"❌ Network error: {e.reason}", file=sys.stderr)
        sys.exit(1)


def build_query(days=30, min_stars=50, language=None, topic=None, keywords=None):
    since_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
    parts = []
    if keywords:
        parts.append(keywords)
    else:
        parts.append("tool OR utility OR CLI OR app OR productivity")
    parts.append(f"created:>{since_date}")
    parts.append(f"stars:>={min_stars}")
    if language:
        parts.append(f"language:{language}")
    if topic:
        parts.append(f"topic:{topic}")
    return " ".join(parts)


def is_tool_project(repo):
    name = repo.get("name", "").lower()
    desc = (repo.get("description") or "").lower()
    topics = [t.lower() for t in repo.get("topics", [])]
    text = f"{name} {desc} {' '.join(topics)}"
    return not any(kw in text for kw in EXCLUDE_KEYWORDS)


def format_as_text(repos, query):
    lines = [f"GitHub Trending Tools", f"Search: {query}", "=" * 50, ""]

    for i, repo in enumerate(repos, 1):
        desc = repo.get("description") or "(no description)"
        if len(desc) > 150:
            desc = desc[:150] + "..."
        topics = ", ".join(repo.get("topics", [])[:5]) or ""

        lines.append(f"#{i} ⭐{repo['stargazers_count']}  {repo['full_name']}")
        lines.append(f"  {desc}")
        lines.append(f"  Language: {repo.get('language') or 'N/A'}  Created: {repo['created_at'][:10]}")
        if topics:
            lines.append(f"  Topics: {topics}")
        lines.append(f"  {repo['html_url']}")
        lines.append("")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="GitHub 热门工具项目搜索（一步到位）")
    parser.add_argument("--days", type=int, default=30, help="最近 N 天 (default: 30)")
    parser.add_argument("--min-stars", type=int, default=50, help="最低 star 数 (default: 50)")
    parser.add_argument("--lang", type=str, default=None, help="语言过滤，如 python, typescript, rust")
    parser.add_argument("--topic", type=str, default=None, help="topic 过滤，如 cli, tool")
    parser.add_argument("--keywords", type=str, default=None, help="自定义搜索关键词")
    parser.add_argument("--limit", type=int, default=20, help="最多展示数量 (default: 20)")
    args = parser.parse_args()

    token = os.environ.get("GITHUB_TOKEN")
    query = build_query(days=args.days, min_stars=args.min_stars, language=args.lang,
                        topic=args.topic, keywords=args.keywords)

    print(f"🔍 搜索: {query}", file=sys.stderr)

    data = search_github(query, per_page=min(args.limit + 10, 100), token=token)
    items = data.get("items", [])
    tools = [r for r in items if is_tool_project(r)][:args.limit]

    if not tools:
        print("💡 没有找到匹配的工具项目，尝试增大 --days 或降低 --min-stars", file=sys.stderr)
        sys.exit(1)

    text = format_as_text(tools, query)
    _ensure_tmp_dir()
    with open(RESULT_FILE, "w", encoding="utf-8") as f:
        f.write(text)
    print(text)
    print(f"\n📄 结果已保存到 {RESULT_FILE}", file=sys.stderr)


if __name__ == "__main__":
    main()
