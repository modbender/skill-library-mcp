#!/usr/bin/env python3
"""GitHub Trending 抓取脚本 - 获取每日趋势项目"""

import json
import sys
import urllib.request
import urllib.error
import re
from html.parser import HTMLParser


class TrendingParser(HTMLParser):
    """解析 GitHub Trending 页面"""
    def __init__(self):
        super().__init__()
        self.repos = []
        self.current = {}
        self.in_repo = False
        self.in_desc = False
        self.in_stars = False
        self.capture_text = False
        self.text_buf = ""

    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)
        cls = attrs_dict.get("class", "")

        if tag == "article" and "Box-row" in cls:
            self.in_repo = True
            self.current = {"name": "", "desc": "", "stars": "", "lang": "", "url": ""}

        if self.in_repo:
            if tag == "a" and "color-fg-default" in cls:
                href = attrs_dict.get("href", "")
                self.current["url"] = f"https://github.com{href}"
                self.current["name"] = href.strip("/")
                self.capture_text = True
                self.text_buf = ""

            if tag == "p" and "color-fg-muted" in cls:
                self.in_desc = True
                self.text_buf = ""

            if tag == "span" and "repo-language-color" in cls:
                pass
            if tag == "span" and "d-inline-block" in cls and "float-sm-right" not in cls:
                pass

    def handle_data(self, data):
        if self.in_desc:
            self.text_buf += data
        if self.capture_text:
            self.text_buf += data

    def handle_endtag(self, tag):
        if tag == "a" and self.capture_text:
            self.capture_text = False

        if tag == "p" and self.in_desc:
            self.in_desc = False
            self.current["desc"] = self.text_buf.strip()

        if tag == "article" and self.in_repo:
            self.in_repo = False
            if self.current.get("name"):
                self.repos.append(self.current)


def fetch_trending(language="", since="daily"):
    """从 GitHub Trending 页面抓取趋势项目"""
    url = f"https://github.com/trending/{language}?since={since}"

    proxy = None
    import os
    http_proxy = os.environ.get("HTTP_PROXY") or os.environ.get("http_proxy")
    if http_proxy:
        proxy = urllib.request.ProxyHandler({"http": http_proxy, "https": http_proxy})

    opener = urllib.request.build_opener(proxy) if proxy else urllib.request.build_opener()
    req = urllib.request.Request(url, headers={
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
        "Accept": "text/html",
        "Accept-Language": "en-US,en;q=0.9",
    })

    try:
        resp = opener.open(req, timeout=15)
        html = resp.read().decode("utf-8")
    except Exception as e:
        print(f"Error fetching trending: {e}", file=sys.stderr)
        return []

    parser = TrendingParser()
    parser.feed(html)

    # 用正则补充 stars 信息
    star_pattern = re.compile(r'(\d[\d,]*)\s+stars\s+today')
    star_matches = star_pattern.findall(html)
    for i, repo in enumerate(parser.repos):
        if i < len(star_matches):
            repo["stars"] = star_matches[i]

    return parser.repos


def filter_ai_repos(repos):
    """筛选 AI/ML 相关的项目"""
    ai_keywords = [
        "ai", "ml", "llm", "gpt", "agent", "transformer", "diffusion",
        "neural", "deep-learning", "machine-learning", "nlp", "cv",
        "rag", "embedding", "vector", "langchain", "autogen", "crewai",
        "openai", "anthropic", "gemini", "claude", "ollama", "llama",
        "stable-diffusion", "midjourney", "workflow", "memory", "mcp",
        "copilot", "cursor", "agentic", "reasoning", "cot", "chain-of-thought",
    ]
    filtered = []
    for repo in repos:
        text = (repo["name"] + " " + repo["desc"]).lower()
        if any(kw in text for kw in ai_keywords):
            filtered.append(repo)
    return filtered


def main():
    import argparse
    parser = argparse.ArgumentParser(description="GitHub Trending 抓取")
    parser.add_argument("--language", default="", help="编程语言筛选")
    parser.add_argument("--since", default="daily", choices=["daily", "weekly", "monthly"])
    parser.add_argument("--ai-only", action="store_true", help="仅显示 AI 相关项目")
    parser.add_argument("--limit", type=int, default=15, help="最多显示数量")
    parser.add_argument("--json", action="store_true", help="JSON 格式输出")
    args = parser.parse_args()

    repos = fetch_trending(args.language, args.since)

    if args.ai_only:
        repos = filter_ai_repos(repos)

    repos = repos[:args.limit]

    if args.json:
        print(json.dumps(repos, ensure_ascii=False, indent=2))
    else:
        if not repos:
            print("未获取到趋势项目（可能是网络问题或页面结构变化）")
            return

        print(f"🔥 GitHub Trending ({args.since}) - {'AI/ML 相关' if args.ai_only else '全部'}")
        print("=" * 60)
        for i, repo in enumerate(repos, 1):
            stars_str = f" ⭐ {repo['stars']} today" if repo.get("stars") else ""
            print(f"\n{i}. **{repo['name']}**{stars_str}")
            if repo["desc"]:
                print(f"   {repo['desc']}")
            print(f"   {repo['url']}")


if __name__ == "__main__":
    main()
