#!/usr/bin/env python3
"""
智谱搜索工具 - 简单易用的网络搜索
"""

import sys
import os
import json
import argparse
import httpx

# 配置 - 请设置您的 API Key
API_KEY = os.getenv("ZHIPUAI_API_KEY", "")
API_URL = "https://open.bigmodel.cn/api/paas/v4/web_search"

# 搜索引擎映射
ENGINES = {
    "std": "search_std",
    "pro": "search_pro",
    "sogou": "search_pro_sogou",
    "quark": "search_pro_quark"
}

# 时间筛选映射
RECENCY = {
    "day": "oneDay",
    "week": "oneWeek",
    "month": "oneMonth",
    "year": "oneYear",
    "all": "noLimit"
}


def search(query, engine="pro", count=10, recency="all", content_size="medium", domain=None):
    """执行搜索"""
    if not API_KEY:
        raise ValueError(
            "请设置 ZHIPUAI_API_KEY 环境变量，或编辑脚本中的 API_KEY 变量\n"
            "获取 API Key: https://bigmodel.cn/usercenter/apikeys"
        )

    payload = {
        "search_query": query,
        "search_engine": ENGINES.get(engine, engine),
        "count": count,
        "search_intent": False,
        "search_recency_filter": RECENCY.get(recency, recency),
        "content_size": content_size
    }
    if domain:
        payload["search_domain_filter"] = domain

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    response = httpx.post(API_URL, json=payload, headers=headers, timeout=60)
    response.raise_for_status()
    return response.json()


def print_results(result):
    """友好打印搜索结果"""
    print(f"\n{'=' * 80}")
    print(f"搜索结果")
    print(f"{'=' * 80}\n")

    if "search_result" not in result or not result["search_result"]:
        print("未找到搜索结果")
        return

    items = result["search_result"]
    print(f"找到 {len(items)} 条结果:\n")

    for i, item in enumerate(items, 1):
        print(f"[{i}] {item.get('title', '无标题')}")
        print(f"    来源: {item.get('media', '未知')}", end="")
        if item.get('publish_date'):
            print(f" ({item['publish_date']})")
        else:
            print()
        if item.get('link'):
            print(f"    链接: {item['link']}")
        if item.get('content'):
            content = item['content']
            if len(content) > 200:
                content = content[:200] + "..."
            print(f"    摘要: {content}")
        print()


def main():
    parser = argparse.ArgumentParser(description="智谱搜索工具")
    parser.add_argument("query", help="搜索内容")
    parser.add_argument("--engine", choices=["std", "pro", "sogou", "quark"], default="pro", help="搜索引擎 (默认: pro)")
    parser.add_argument("--count", type=int, default=10, help="结果数量 (1-50, 默认: 10)")
    parser.add_argument("--recency", choices=["day", "week", "month", "year", "all"], default="all", help="时间范围 (默认: all)")
    parser.add_argument("--content-size", choices=["medium", "high"], default="medium", help="内容长度 (默认: medium)")
    parser.add_argument("--domain", help="限定域名")
    parser.add_argument("--json", action="store_true", help="输出 JSON")

    args = parser.parse_args()

    try:
        result = search(
            args.query,
            engine=args.engine,
            count=args.count,
            recency=args.recency,
            content_size=args.content_size,
            domain=args.domain
        )

        if args.json:
            print(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            print_results(result)
    except Exception as e:
        print(f"错误: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
