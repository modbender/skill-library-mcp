#!/usr/bin/env python3
"""
V2EX 产品/工具话题搜索

从 V2EX 的产品相关节点（分享创造、分享发现等）获取话题，
并通过关键词过滤筛选出与工具、产品、独立开发相关的内容。

无需认证，无需 Token。

Usage:
    python3 v2ex_topics.py
    python3 v2ex_topics.py --nodes create share
    python3 v2ex_topics.py --filter "AI工具"
    python3 v2ex_topics.py --no-filter
"""

import argparse
import json
import os
import sys
import urllib.request
import urllib.error
from datetime import datetime

TMP_DIR = os.path.join(os.getcwd(), "tmp")
RESULT_FILE = os.path.join(TMP_DIR, "v2ex_results.txt")

# 产品/工具相关的核心节点
PRODUCT_NODES = {
    "create": "分享创造",
    "share": "分享发现",
}

# 所有可选节点（用 --nodes 指定）
ALL_NODES = {
    "create": "分享创造",
    "share": "分享发现",
    "macos": "macOS",
    "chrome": "Chrome",
    "programmer": "程序员",
    "app": "App 推荐",
}

# 产品/工具相关关键词（用于从话题中筛选出有价值的内容）
TOOL_KEYWORDS = [
    "工具", "tool", "app", "开源", "独立开发", "side project",
    "上线", "发布", "launch", "分享", "推荐", "效率",
    "插件", "extension", "cli", "bot", "自动化", "脚本",
    "做了", "写了", "开发了", "搞了", "造了", "新项目",
    "产品", "saas", "开箱", "体验", "测评", "神器",
    "github", "chrome", "vscode", "浏览器", "桌面",
    "免费", "付费", "订阅", "买断",
]


def _ensure_tmp_dir():
    os.makedirs(TMP_DIR, exist_ok=True)


def fetch_node_topics(node_name, page=1):
    """通过节点名获取该节点下的话题列表。"""
    url = f"https://www.v2ex.com/api/topics/show.json?node_name={node_name}&p={page}"
    headers = {"User-Agent": "idea2mvp-skill/1.0"}
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        print(f"⚠️ V2EX API error {e.code} for node '{node_name}'", file=sys.stderr)
        return []
    except urllib.error.URLError as e:
        print(f"⚠️ Network error for node '{node_name}': {e.reason}", file=sys.stderr)
        return []


def is_tool_related(topic):
    """判断话题是否与工具/产品/独立开发相关。"""
    text = f"{topic.get('title', '')} {topic.get('content', '')}".lower()
    return any(kw.lower() in text for kw in TOOL_KEYWORDS)


def matches_filter(topic, filter_keyword):
    """自定义关键词过滤。"""
    if not filter_keyword:
        return True
    text = f"{topic.get('title', '')} {topic.get('content', '')}".lower()
    return filter_keyword.lower() in text


def format_as_text(topics, nodes_used):
    nodes_label = ", ".join(f"{ALL_NODES.get(n, n)}({n})" for n in nodes_used)
    lines = [f"V2EX 产品/工具话题 — 节点: {nodes_label}", "=" * 60, ""]

    for i, t in enumerate(topics, 1):
        title = t.get("title", "(no title)")
        url = t.get("url", "")
        node = t.get("node", {}).get("title", "N/A")
        author = t.get("member", {}).get("username", "N/A")
        replies = t.get("replies", 0)
        created = t.get("created", "")

        date_str = ""
        if created:
            try:
                date_str = datetime.fromtimestamp(created).strftime("%Y-%m-%d %H:%M")
            except (OSError, ValueError):
                date_str = str(created)

        content_raw = t.get("content", "") or ""
        content_preview = content_raw[:200]
        if len(content_raw) > 200:
            content_preview += "..."

        lines.append(f"#{i} {title}")
        lines.append(f"  节点: {node}  作者: {author}  回复: {replies}  日期: {date_str}")
        if content_preview:
            lines.append(f"  {content_preview}")
        lines.append(f"  {url}")
        lines.append("")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="V2EX 产品/工具话题搜索")
    parser.add_argument(
        "--nodes", nargs="+", default=None,
        help=f"指定节点（默认: create share）。可选: {', '.join(ALL_NODES.keys())}"
    )
    parser.add_argument("--filter", type=str, default=None, help="自定义关键词过滤")
    parser.add_argument(
        "--no-filter", action="store_true",
        help="不做关键词过滤，返回节点下所有话题"
    )
    parser.add_argument(
        "--pages", type=int, default=1,
        help="每个节点获取的页数（默认 1，每页约 20 条）"
    )
    args = parser.parse_args()

    nodes = args.nodes or list(PRODUCT_NODES.keys())
    # 验证节点名
    for n in nodes:
        if n not in ALL_NODES:
            print(f"⚠️ 未知节点 '{n}'，可选: {', '.join(ALL_NODES.keys())}", file=sys.stderr)
            sys.exit(1)

    all_topics = []
    for node in nodes:
        node_label = ALL_NODES.get(node, node)
        print(f"🔍 获取 V2EX [{node_label}] 节点话题...", file=sys.stderr, flush=True)
        for page in range(1, args.pages + 1):
            topics = fetch_node_topics(node, page=page)
            if not topics:
                break
            all_topics.extend(topics)

    if not all_topics:
        print("❌ 未获取到任何话题", file=sys.stderr)
        sys.exit(1)

    print(f"📦 共获取 {len(all_topics)} 条话题", file=sys.stderr, flush=True)

    # 过滤
    if args.filter:
        filtered = [t for t in all_topics if matches_filter(t, args.filter)]
        print(f"🔎 关键词 '{args.filter}' 过滤后: {len(filtered)} 条", file=sys.stderr, flush=True)
    elif not args.no_filter:
        filtered = [t for t in all_topics if is_tool_related(t)]
        print(f"🔎 工具/产品关键词过滤后: {len(filtered)} 条", file=sys.stderr, flush=True)
    else:
        filtered = all_topics

    if not filtered:
        print("💡 过滤后无结果，尝试 --no-filter 或更换 --filter 关键词", file=sys.stderr)
        # 仍然输出未过滤的结果作为备选
        print("📋 输出未过滤的原始结果作为参考", file=sys.stderr)
        filtered = all_topics

    # 按回复数降序排列（热度指标）
    filtered.sort(key=lambda t: t.get("replies", 0), reverse=True)

    text = format_as_text(filtered, nodes)
    _ensure_tmp_dir()
    with open(RESULT_FILE, "w", encoding="utf-8") as f:
        f.write(text)
    print(text)
    print(f"\n📄 结果已保存到 {RESULT_FILE}", file=sys.stderr)


if __name__ == "__main__":
    main()
