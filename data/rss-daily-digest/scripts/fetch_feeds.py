#!/usr/bin/env python3
"""
fetch_feeds.py — 从 feed-sources.md 中读取 RSS 源并获取最近 N 小时的文章
输出: JSON 数组到 stdout（供 Agent 或下游脚本消费）
"""


import argparse
import json
import re
import sys
from datetime import datetime, timedelta, timezone




def parse_feed_sources(filepath):
    """解析 feed-sources.md，提取分类和 URL"""
    feeds = []
    current_category = "Uncategorized"
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            # 匹配 ## Tech 格式的分类标题
            cat_match = re.match(r'^##\s+(.+)$', line)
            if cat_match:
                current_category = cat_match.group(1).strip()
                continue
            # 匹配 - URL — Description 格式的源
            feed_match = re.match(
                r'^-\s+(https?://\S+)\s+[—–-]\s+(.+)$', line
            )
            if feed_match:
                feeds.append({
                    "url": feed_match.group(1),
                    "source": feed_match.group(2).strip(),
                    "category": current_category
                })
    return feeds




def fetch_feed(url, hours=24):
    """获取单个 RSS 源的文章"""
    try:
        import feedparser
    except ImportError:
        print(
            "ERROR: feedparser not installed. Run: pip3 install feedparser",
            file=sys.stderr
        )
        sys.exit(1)


    cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)
    articles = []


    try:
        feed = feedparser.parse(url)
        if feed.bozo and not feed.entries:
            return {"error": f"Parse error: {feed.bozo_exception}", "url": url}


        for entry in feed.entries[:20]:  # 每个源最多 20 篇
            published = None
            for time_field in ['published_parsed', 'updated_parsed']:
                t = getattr(entry, time_field, None)
                if t:
                    from calendar import timegm
                    published = datetime.fromtimestamp(
                        timegm(t), tz=timezone.utc
                    )
                    break


            if published and published < cutoff:
                continue


            articles.append({
                "title": getattr(entry, 'title', 'Untitled'),
                "url": getattr(entry, 'link', ''),
                "description": getattr(entry, 'summary', '')[:300],
                "published": published.isoformat() if published else None,
            })
    except Exception as e:
        return {"error": str(e), "url": url}


    return {"articles": articles}




def main():
    parser = argparse.ArgumentParser(description='Fetch RSS feeds')
    parser.add_argument(
        '--feeds-file', required=True, help='Path to feed-sources.md'
    )
    parser.add_argument(
        '--hours', type=int, default=24, help='Lookback hours'
    )
    args = parser.parse_args()


    sources = parse_feed_sources(args.feeds_file)
    results = []
    errors = []


    for source in sources:
        result = fetch_feed(source["url"], args.hours)
        if "error" in result:
            errors.append({
                "source": source["source"], "error": result["error"]
            })
        else:
            for article in result.get("articles", []):
                article["source"] = source["source"]
                article["category"] = source["category"]
                results.append(article)


    output = {
        "articles": results,
        "errors": errors,
        "total": len(results),
        "sources_checked": len(sources),
        "sources_failed": len(errors),
        "generated_at": datetime.now(timezone.utc).isoformat()
    }


    # 同时写到临时文件（方便下游脚本读取）
    tmp_path = "/tmp/openclaw-rss-articles.json"
    with open(tmp_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)


    # 输出到 stdout（Agent 可以直接读取）
    print(json.dumps(output, ensure_ascii=False, indent=2))




if __name__ == "__main__":
    main()
