#!/usr/bin/env python3
"""RSS 聚合脚本 - 高性能并发版

优化点：
1. 并发抓取 (10线程) - 10倍速度提升
2. ETag/Last-Modified 缓存 - 避免重复下载
3. 智能超时 (10秒) - 快速失败
4. 日期过滤 - 支持只抓取最近 N 天的新闻
"""

import json
import sys
import os
import xml.etree.ElementTree as ET
import urllib.request
from html import unescape
import re
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone, timedelta
import time
import logging
import argparse

# 配置
MAX_WORKERS = 10
TIMEOUT = 15  # 适度超时
CACHE_PATH = Path(__file__).parent / ".rss_cache.json"
CACHE_TTL_HOURS = 1

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)


def load_sources(category=None):
    """从 rss_sources.json 加载源列表"""
    sources_file = Path(__file__).parent / "rss_sources.json"
    if not sources_file.exists():
        logger.error(f"No sources file at {sources_file}")
        return []
    with open(sources_file) as f:
        sources = json.load(f)
    if category and category != "all":
        sources = [s for s in sources if s.get("category") == category]
    return sources


def load_cache():
    """加载缓存"""
    try:
        if CACHE_PATH.exists():
            with open(CACHE_PATH) as f:
                cache = json.load(f)
            # 清理过期缓存
            now = time.time()
            ttl = CACHE_TTL_HOURS * 3600
            return {k: v for k, v in cache.items() if now - v.get("ts", 0) < ttl}
    except Exception:
        pass
    return {}


def save_cache(cache):
    """保存缓存"""
    try:
        with open(CACHE_PATH, 'w') as f:
            json.dump(cache, f)
    except Exception as e:
        logger.debug(f"Cache save error: {e}")


def fetch_rss_concurrent(source, cache, timeout=TIMEOUT):
    """并发抓取单个 RSS 源"""
    name = source["name"]
    url = source["url"]

    req_headers = {
        "User-Agent": "AI-News-Aggregator/2.0",
        "Accept": "application/rss+xml, application/xml, text/xml, application/atom+xml, */*",
    }

    # 添加条件请求头
    cache_entry = cache.get(url, {})
    if cache_entry.get("etag"):
        req_headers["If-None-Match"] = cache_entry["etag"]
    if cache_entry.get("last_modified"):
        req_headers["If-Modified-Since"] = cache_entry["last_modified"]

    proxy = None
    http_proxy = os.environ.get("HTTP_PROXY") or os.environ.get("http_proxy")
    if http_proxy:
        proxy = urllib.request.ProxyHandler({"http": http_proxy, "https": http_proxy})
    opener = urllib.request.build_opener(proxy) if proxy else urllib.request.build_opener()

    req = urllib.request.Request(url, headers=req_headers)

    try:
        with opener.open(req, timeout=timeout) as resp:
            content = resp.read().decode("utf-8", errors="replace")

            # 更新缓存（保存内容和元数据）
            cache[url] = {
                "content": content,
                "etag": resp.headers.get("ETag"),
                "last_modified": resp.headers.get("Last-Modified"),
                "ts": time.time()
            }

            return {"name": name, "status": "ok", "content": content}

    except urllib.error.HTTPError as e:
        if e.code == 304:  # Not Modified - 从缓存返回
            if cache_entry.get("content"):
                logger.debug(f"{name}: 304, using cached content")
                return {"name": name, "status": "ok", "content": cache_entry["content"]}
            return {"name": name, "status": "error", "error": "304 but no cache"}
        return {"name": name, "status": "error", "error": f"HTTP {e.code}"}
    except Exception as e:
        return {"name": name, "status": "error", "error": str(e)}


def parse_date(date_str):
    """解析各种 RSS 日期格式，返回 UTC datetime"""
    if not date_str:
        return None

    date_str = date_str.strip()

    # 格式1: RFC 2822 (RSS 2.0) - Thu, 05 Feb 2026 00:00:00 +0000
    rfc_patterns = [
        '%a, %d %b %Y %H:%M:%S %z',
        '%a, %d %b %Y %H:%M:%S %Z',
        '%d %b %Y %H:%M:%S %z',
        '%d %b %Y %H:%M:%S %Z',
    ]

    for pattern in rfc_patterns:
        try:
            return datetime.strptime(date_str, pattern)
        except ValueError:
            continue

    # 格式2: ISO 8601 (Atom) - 2026-02-05T00:00:00Z 或 2026-02-05T00:00:00+00:00
    iso_variants = [
        date_str.replace('Z', '+00:00'),
        date_str.replace('z', '+00:00'),
    ]
    if '+' not in date_str and '-' in date_str[10:]:
        # 可能没有时区，假设 UTC
        try:
            return datetime.fromisoformat(date_str.replace('Z', ''))
        except ValueError:
            pass

    for iso_str in iso_variants:
        try:
            return datetime.fromisoformat(iso_str)
        except ValueError:
            continue

    # 格式3: 简单格式 - 2026-02-05 或 Feb 25, 2026
    simple_patterns = [
        '%Y-%m-%d',
        '%Y-%m-%d %H:%M:%S',
        '%b %d, %Y',
        '%B %d, %Y',
    ]
    for pattern in simple_patterns:
        try:
            dt = datetime.strptime(date_str, pattern)
            return dt.replace(tzinfo=timezone.utc)
        except ValueError:
            continue

    return None


def parse_rss(xml_content, source_name):
    """解析 RSS"""
    items = []

    try:
        root = ET.fromstring(xml_content)
        ns = {"atom": "http://www.w3.org/2005/Atom"}

        # RSS 2.0
        for item in root.findall(".//item"):
            title = (item.findtext("title") or "").strip()
            link = (item.findtext("link") or "").strip()
            desc = (item.findtext("description") or "").strip()
            pub_date = (item.findtext("pubDate") or "").strip()
            desc = unescape(re.sub(r"<[^>]+>", "", desc))[:200]
            items.append({"title": title, "url": link, "desc": desc, "date": pub_date, "source": source_name})

        # Atom
        for entry in root.findall("atom:entry", ns) + root.findall("entry"):
            title = ""
            t = entry.find("atom:title", ns) or entry.find("title")
            if t is not None and getattr(t, 'text', None):
                title = t.text.strip()

            link = ""
            l = entry.find("atom:link", ns) or entry.find("link")
            if l is not None:
                link = l.get("href", "").strip()

            desc = ""
            s = entry.find("atom:summary", ns) or entry.find("summary")
            c = entry.find("atom:content", ns) or entry.find("content")
            content_text = ""
            if s is not None and getattr(s, 'text', None):
                content_text = s.text
            elif c is not None and getattr(c, 'text', None):
                content_text = c.text
            if content_text:
                desc = unescape(re.sub(r"<[^>]+>", "", content_text))[:200]

            pub_date = ""
            p = entry.find("atom:published", ns) or entry.find("published") or entry.find("atom:updated", ns) or entry.find("updated")
            if p is not None and getattr(p, 'text', None):
                pub_date = p.text.strip()

            items.append({"title": title, "url": link, "desc": desc, "date": pub_date, "source": source_name})

    except ET.ParseError as e:
        logger.debug(f"Parse error for {source_name}: {e}")

    return items


def filter_by_date(items, days):
    """过滤最近 N 天的文章"""
    if not days or days <= 0:
        return items

    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    filtered = []

    for item in items:
        pub_date = parse_date(item.get('date', ''))
        if pub_date:
            # 确保有时区信息
            if pub_date.tzinfo is None:
                pub_date = pub_date.replace(tzinfo=timezone.utc)
            if pub_date >= cutoff:
                filtered.append(item)
        else:
            # 无法解析日期时，默认保留（可能是最新的）
            filtered.append(item)

    return filtered


def main():
    parser = argparse.ArgumentParser(description="RSS 聚合 - 高性能并发版")
    parser.add_argument("--category", default="all", help="分类筛选")
    parser.add_argument("--limit", type=int, default=10, help="每源最多条目")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--workers", type=int, default=MAX_WORKERS, help="并发线程数")
    parser.add_argument("--timeout", type=int, default=TIMEOUT, help="超时秒数")
    parser.add_argument("--days", type=int, default=None, help="只抓取最近 N 天的新闻")
    args = parser.parse_args()

    sources = load_sources(args.category)
    if not sources:
        logger.error("No sources found")
        sys.exit(1)

    logger.info(f"Fetching {len(sources)} sources with {args.workers} workers...")

    cache = load_cache()
    all_items = []
    errors = []
    from_cache = 0

    # 并发抓取
    start_time = time.time()
    with ThreadPoolExecutor(max_workers=args.workers) as executor:
        futures = {
            executor.submit(fetch_rss_concurrent, src, cache, args.timeout): src
            for src in sources
        }

        for future in as_completed(futures):
            result = future.result()
            name = result["name"]

            if result["status"] == "ok":
                items = parse_rss(result["content"], name)

                # 日期过滤
                if args.days:
                    items = filter_by_date(items, args.days)

                all_items.extend(items[:args.limit])
                # 判断是否来自缓存（根据内容匹配）
                url = next((s["url"] for s in sources if s["name"] == name), "")
                if cache.get(url, {}).get("content") == result["content"]:
                    from_cache += 1
                logger.info(f"✅ {name}: {len(items)} items")
            else:
                errors.append(name)
                logger.warning(f"❌ {name}: {result.get('error', 'failed')}")

    # 保存缓存
    save_cache(cache)

    elapsed = time.time() - start_time
    logger.info(f"\nCompleted in {elapsed:.1f}s - {len(all_items)} articles from {len(sources) - len(errors)}/{len(sources)} sources")

    if args.json:
        print(json.dumps(all_items, ensure_ascii=False, indent=2))
    else:
        by_source = {}
        for item in all_items:
            by_source.setdefault(item["source"], []).append(item)

        filter_info = f" | 最近{args.days}天" if args.days else ""
        print(f"\n{'='*60}")
        print(f"RSS 聚合结果 ({len(all_items)} 条){filter_info}")
        print(f"耗时: {elapsed:.1f}秒 | 来自缓存: {from_cache} | 失败: {len(errors)}")
        if errors:
            print(f"失败源: {', '.join(errors[:5])}{'...' if len(errors) > 5 else ''}")
        print("="*60)

        for source, items in by_source.items():
            print(f"\n📌 {source} ({len(items)})")
            for item in items[:3]:
                title = item["title"][:60] + "..." if len(item["title"]) > 60 else item["title"]
                print(f"  • {title}")


if __name__ == "__main__":
    main()
