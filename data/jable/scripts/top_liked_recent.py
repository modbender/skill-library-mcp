#!/usr/bin/env python3
"""Fetch Jable latest updates and output top liked videos within a time window.

Uses:
- RSS feed for publish times (https://jable.tv/rss/)
- latest-updates pages for like counts (https://jable.tv/latest-updates/)

No third-party dependencies (stdlib only).
"""

from __future__ import annotations

import argparse
import re
import urllib.request
import xml.etree.ElementTree as ET
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta, timezone

UA = "Mozilla/5.0"
RSS_URL = "https://jable.tv/rss/"
LATEST_BASE = "https://jable.tv/latest-updates/"


def http_get(url: str) -> str:
    opener = urllib.request.build_opener()
    opener.addheaders = [("User-Agent", UA)]
    with opener.open(url, timeout=25) as resp:
        return resp.read().decode("utf-8", "ignore")


def parse_rss_recent(hours: int):
    xml_text = http_get(RSS_URL)
    root = ET.fromstring(xml_text)
    cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)

    recent = {}
    for item in root.findall("./channel/item"):
        link = (item.findtext("link") or "").strip()
        title = " ".join((item.findtext("title") or "").split())
        pub = (item.findtext("pubDate") or "").strip()
        if not link or not pub:
            continue
        try:
            dt = datetime.strptime(pub, "%a %d %b %Y %H:%M:%S %z").astimezone(timezone.utc)
        except ValueError:
            continue
        if dt >= cutoff:
            recent[link] = {"title": title, "pub": dt}
    return recent


def parse_likes_from_latest(max_pages: int, workers: int):
    likes = {}
    cards = {}
    page_seen = {}

    pattern = re.compile(
        r'<h6 class="title"><a href="(https://jable\.tv/videos/[^"]+/)">(.*?)</a></h6>\s*<p class="sub-title">(.*?)</p>',
        re.S,
    )

    def fetch_page(page: int):
        url = LATEST_BASE if page == 1 else f"{LATEST_BASE}{page}/"
        try:
            return page, http_get(url)
        except Exception:
            return page, ""

    with ThreadPoolExecutor(max_workers=max(1, workers)) as ex:
        futures = [ex.submit(fetch_page, page) for page in range(1, max_pages + 1)]
        for fut in as_completed(futures):
            page_no, html = fut.result()
            if not html:
                continue
            for m in pattern.finditer(html):
                vurl, raw_title, sub = m.groups()
                n = re.search(r'icon-heart-inline\"></use></svg>\s*([0-9 ]+)', sub)
                if not n:
                    continue
                likes[vurl] = int(n.group(1).replace(" ", ""))
                cards[vurl] = " ".join(re.sub(r"<.*?>", "", raw_title).split())
                page_seen[vurl] = min(page_seen.get(vurl, page_no), page_no)

    return likes, cards, page_seen


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--hours", type=int, default=48, help="Recent window in hours (default: 48)")
    ap.add_argument("--top", type=int, default=3, help="Top N results (default: 3)")
    ap.add_argument("--pages", type=int, default=10, help="latest-updates pages to scan for likes (default: 10)")
    ap.add_argument("--workers", type=int, default=6, help="Concurrent page fetch workers (default: 6)")
    args = ap.parse_args()

    recent = parse_rss_recent(args.hours)
    likes, cards, page_seen = parse_likes_from_latest(args.pages, args.workers)

    # RSS may miss some videos that are still present in latest-updates menu.
    # For 48h-style requests, include early latest pages as a fallback set.
    fallback_recent_pages = 1

    rows = []
    for url, like_count in likes.items():
        in_rss_window = url in recent
        in_fallback_pages = page_seen.get(url, 9999) <= fallback_recent_pages
        if not (in_rss_window or in_fallback_pages):
            continue
        rows.append(
            {
                "url": url,
                "title": cards.get(url) or (recent.get(url) or {}).get("title") or url,
                "likes": like_count,
                "pub": (recent.get(url) or {}).get("pub"),
            }
        )

    rows.sort(key=lambda x: x["likes"], reverse=True)

    if not rows:
        print("No results found in the selected time window.")
        return

    for i, r in enumerate(rows[: args.top], start=1):
        print(f"{i}️⃣ {r['title']}")
        print(f"❤️ {r['likes']}")
        print(f"🔗 {r['url']}")
        print()


if __name__ == "__main__":
    main()
