#!/usr/bin/env python3
import argparse
import asyncio
import json
import time
from pathlib import Path

import browser_cookie3
from playwright.async_api import async_playwright


def load_cookies(domain_name: str):
    jar = browser_cookie3.chrome(domain_name=domain_name)
    cookies = []
    for cookie in jar:
        if domain_name not in cookie.domain and "twitter.com" not in cookie.domain:
            continue
        cookies.append(
            {
                "name": cookie.name,
                "value": cookie.value,
                "domain": cookie.domain,
                "path": cookie.path or "/",
                "expires": float(cookie.expires) if cookie.expires and cookie.expires > 0 else -1,
                "httpOnly": False,
                "secure": bool(cookie.secure),
                "sameSite": "Lax",
            }
        )
    return cookies


def parse_body_text(body_text: str, limit: int):
    lines = [line.strip() for line in body_text.splitlines() if line.strip()]
    trends = []
    news = []
    in_trends = False
    in_news = False

    i = 0
    while i < len(lines):
        line = lines[i]
        if line == "Global Trending":
            in_trends = True
            in_news = False
            i += 1
            continue
        if line == "Today’s News":
            in_trends = False
            in_news = True
            i += 1
            continue
        if line == "Who to follow":
            break

        if in_trends and line.isdigit() and i + 3 < len(lines):
            category = lines[i + 2]
            title = lines[i + 3]
            detail = ""
            if i + 4 < len(lines):
                maybe_detail = lines[i + 4]
                if "Trending with" in maybe_detail or "posts" in maybe_detail:
                    detail = maybe_detail
            trends.append(
                {
                    "rank": int(line),
                    "category": category,
                    "title": title,
                    "detail": detail,
                }
            )
            i += 1
            continue

        if in_news and i + 1 < len(lines):
            meta = lines[i + 1]
            if "News" in meta or "posts" in meta or "Trending now" in meta:
                news.append({"headline": line, "meta": meta})
                i += 2
                continue

        i += 1

    return trends[:limit], news[: max(2, min(5, limit // 2 or 2))]


async def fetch_hotspots(chrome_path: str, trending_url: str, domain_name: str, limit: int):
    cookies = load_cookies(domain_name)
    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(headless=True, executable_path=chrome_path)
        context = await browser.new_context(
            viewport={"width": 1440, "height": 2200},
            user_agent=(
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/122.0.0.0 Safari/537.36"
            ),
        )
        await context.add_cookies(cookies)
        page = await context.new_page()
        await page.goto(trending_url, wait_until="domcontentloaded", timeout=60000)
        await page.wait_for_timeout(5000)
        body_text = await page.locator("body").inner_text(timeout=30000)
        title = await page.title()
        current_url = page.url
        await browser.close()

    trends, news = parse_body_text(body_text, limit)
    highlights = []
    for item in trends[:3]:
        extra = f" {item['detail']}" if item["detail"] else ""
        highlights.append(f"{item['title']} ({item['category']}){extra}".strip())
    for item in news[:2]:
        highlights.append(f"{item['headline']} [{item['meta']}]")

    return {
        "fetched_at": int(time.time()),
        "source": "x-trending",
        "url": current_url,
        "title": title,
        "trends": trends,
        "news": news,
        "highlights": highlights[:5],
    }


def main():
    parser = argparse.ArgumentParser(description="Fetch hotspot topics from a signed-in X trending page.")
    parser.add_argument("--chrome-path", required=True)
    parser.add_argument("--trending-url", default="https://x.com/explore/tabs/trending")
    parser.add_argument("--domain-name", default="x.com")
    parser.add_argument("--limit", type=int, default=10)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    result = asyncio.run(
        fetch_hotspots(
            chrome_path=args.chrome_path,
            trending_url=args.trending_url,
            domain_name=args.domain_name,
            limit=args.limit,
        )
    )
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
