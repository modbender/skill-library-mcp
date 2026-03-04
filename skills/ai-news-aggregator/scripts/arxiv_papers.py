#!/usr/bin/env python3
"""ArXiv 论文筛选脚本 - 获取 AI/Agent/Memory/Workflow 相关论文"""

import json
import sys
import os
import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta

ARXIV_CATEGORIES = ["cs.AI", "cs.CL", "cs.LG", "cs.MA"]

SEARCH_QUERIES = [
    "LLM agent",
    "autonomous agent",
    "memory augmented language model",
    "workflow automation AI",
    "retrieval augmented generation",
    "chain of thought reasoning",
    "tool use language model",
    "multi agent system",
    "AI planning",
    "prompt engineering",
    "model context protocol",
]


def fetch_arxiv(query, max_results=20, categories=None):
    """从 ArXiv API 获取论文"""
    cat_filter = ""
    if categories:
        cat_parts = [f"cat:{c}" for c in categories]
        cat_filter = "+AND+(" + "+OR+".join(cat_parts) + ")"

    search_query = urllib.parse.quote(query)
    url = (
        f"http://export.arxiv.org/api/query?"
        f"search_query=all:{search_query}{cat_filter}"
        f"&sortBy=submittedDate&sortOrder=descending"
        f"&max_results={max_results}"
    )

    proxy = None
    http_proxy = os.environ.get("HTTP_PROXY") or os.environ.get("http_proxy")
    if http_proxy:
        proxy = urllib.request.ProxyHandler({"http": http_proxy, "https": http_proxy})

    opener = urllib.request.build_opener(proxy) if proxy else urllib.request.build_opener()
    req = urllib.request.Request(url, headers={"User-Agent": "AI-News-Aggregator/1.0"})

    try:
        resp = opener.open(req, timeout=15)
        return resp.read().decode("utf-8")
    except Exception as e:
        print(f"Error fetching arxiv: {e}", file=sys.stderr)
        return None


def parse_arxiv(xml_content):
    """解析 ArXiv Atom XML"""
    ns = {"atom": "http://www.w3.org/2005/Atom", "arxiv": "http://arxiv.org/schemas/atom"}
    papers = []

    try:
        root = ET.fromstring(xml_content)
        for entry in root.findall("atom:entry", ns):
            title = entry.findtext("atom:title", "", ns).strip().replace("\n", " ")
            summary = entry.findtext("atom:summary", "", ns).strip().replace("\n", " ")

            arxiv_id = entry.findtext("atom:id", "", ns).strip()
            published = entry.findtext("atom:published", "", ns).strip()

            authors = []
            for author in entry.findall("atom:author", ns):
                name = author.findtext("atom:name", "", ns).strip()
                if name:
                    authors.append(name)

            categories = []
            for cat in entry.findall("atom:category", ns):
                term = cat.get("term", "")
                if term:
                    categories.append(term)

            link = ""
            for l in entry.findall("atom:link", ns):
                if l.get("type") == "text/html":
                    link = l.get("href", "")
                    break
            if not link:
                link = arxiv_id

            papers.append({
                "title": title,
                "summary": summary[:300],
                "authors": authors[:5],
                "categories": categories,
                "url": link,
                "published": published[:10],
                "arxiv_id": arxiv_id.split("/")[-1] if "/" in arxiv_id else arxiv_id,
            })
    except ET.ParseError as e:
        print(f"XML parse error: {e}", file=sys.stderr)

    return papers


def score_paper(paper):
    """对论文进行相关性评分"""
    high_value_keywords = [
        "agent", "memory", "workflow", "tool use", "planning",
        "reasoning", "chain-of-thought", "rag", "retrieval",
        "autonomous", "multi-agent", "self-reflection", "mcp",
    ]
    medium_value_keywords = [
        "llm", "large language model", "transformer", "prompt",
        "instruction", "fine-tune", "alignment", "evaluation",
        "benchmark", "context window", "long context",
    ]

    text = (paper["title"] + " " + paper["summary"]).lower()
    score = 0
    for kw in high_value_keywords:
        if kw in text:
            score += 3
    for kw in medium_value_keywords:
        if kw in text:
            score += 1
    return score


def main():
    import argparse
    parser = argparse.ArgumentParser(description="ArXiv AI 论文筛选")
    parser.add_argument("--query", default=None, help="自定义搜索词")
    parser.add_argument("--limit", type=int, default=10, help="每个查询的最大结果数")
    parser.add_argument("--top", type=int, default=10, help="最终显示前 N 篇")
    parser.add_argument("--json", action="store_true", help="JSON 格式输出")
    args = parser.parse_args()

    all_papers = {}
    queries = [args.query] if args.query else SEARCH_QUERIES

    for q in queries:
        print(f"  搜索: {q}...", file=sys.stderr)
        content = fetch_arxiv(q, max_results=args.limit, categories=ARXIV_CATEGORIES)
        if content:
            papers = parse_arxiv(content)
            for p in papers:
                key = p["arxiv_id"]
                if key not in all_papers:
                    all_papers[key] = p
                    all_papers[key]["score"] = score_paper(p)
            print(f"  ✓ {q}: {len(papers)} 篇", file=sys.stderr)
        else:
            print(f"  ✗ {q}: 获取失败", file=sys.stderr)

    ranked = sorted(all_papers.values(), key=lambda x: x["score"], reverse=True)
    top_papers = ranked[:args.top]

    if args.json:
        print(json.dumps(top_papers, ensure_ascii=False, indent=2))
    else:
        print(f"\n📄 ArXiv AI 论文精选 - 从 {len(all_papers)} 篇中选出 Top {len(top_papers)}")
        print("=" * 60)
        for i, p in enumerate(top_papers, 1):
            stars = "⭐" * min(p["score"] // 3, 5)
            print(f"\n{i}. **{p['title']}** {stars}")
            print(f"   作者: {', '.join(p['authors'][:3])}")
            print(f"   分类: {', '.join(p['categories'][:3])}")
            print(f"   日期: {p['published']}")
            print(f"   摘要: {p['summary'][:150]}...")
            print(f"   链接: {p['url']}")


if __name__ == "__main__":
    main()
