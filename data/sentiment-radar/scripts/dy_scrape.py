#!/usr/bin/env python3
"""Douyin search scraper via browser automation (bypasses API-level blocking).
Usage: python3 dy_scrape.py --keyword "拍学机" --output ./data/dy_results.json
Requires: playwright, Chrome with CDP on port 9222
"""
import argparse
import asyncio
import json
import sys
from datetime import datetime
from pathlib import Path

from playwright.async_api import async_playwright


async def scrape_douyin_search(keyword: str, max_scrolls: int = 10):
    """Open douyin search page and extract video cards via DOM scraping."""
    results = []

    async with async_playwright() as p:
        browser = await p.chromium.connect_over_cdp("http://localhost:9222")
        context = browser.contexts[0]
        page = await context.new_page()

        search_url = f"https://www.douyin.com/search/{keyword}?type=video"
        print(f"Navigating to: {search_url}")
        await page.goto(search_url, wait_until="domcontentloaded", timeout=30000)
        await asyncio.sleep(3)

        for scroll in range(max_scrolls):
            # Extract video cards from current DOM
            cards = await page.evaluate("""() => {
                const items = [];
                // Try multiple selectors for video search results
                const selectors = [
                    '[class*="search-result"] li',
                    '[class*="video-list"] li', 
                    '[data-e2e="scroll-list"] > div',
                    'ul[class*="list"] > li',
                    '[class*="search"] [class*="card"]',
                    '[class*="result"] [class*="item"]'
                ];
                
                let elements = [];
                for (const sel of selectors) {
                    const found = document.querySelectorAll(sel);
                    if (found.length > elements.length) elements = found;
                }
                
                // Fallback: get all links that look like video links
                if (elements.length === 0) {
                    const links = document.querySelectorAll('a[href*="/video/"]');
                    links.forEach(a => {
                        const title = a.textContent?.trim()?.substring(0, 200) || '';
                        const href = a.href || '';
                        if (title && href) {
                            items.push({
                                title: title,
                                url: href,
                                author: '',
                                likes: '',
                                source: 'link_fallback'
                            });
                        }
                    });
                    return items;
                }
                
                elements.forEach(el => {
                    const titleEl = el.querySelector('a, [class*="title"], h2, h3, p');
                    const authorEl = el.querySelector('[class*="author"], [class*="name"], [class*="user"]');
                    const likeEl = el.querySelector('[class*="like"], [class*="count"]');
                    const linkEl = el.querySelector('a[href*="/video/"]') || el.querySelector('a');
                    
                    const title = titleEl?.textContent?.trim()?.substring(0, 200) || '';
                    const author = authorEl?.textContent?.trim() || '';
                    const likes = likeEl?.textContent?.trim() || '';
                    const url = linkEl?.href || '';
                    
                    if (title || url) {
                        items.push({ title, author, likes, url, source: 'card' });
                    }
                });
                return items;
            }""")

            for card in cards:
                # Deduplicate by URL
                if card.get("url") and not any(r["url"] == card["url"] for r in results):
                    results.append(card)

            print(f"Scroll {scroll+1}/{max_scrolls}: found {len(cards)} cards, total unique: {len(results)}")

            if scroll < max_scrolls - 1:
                await page.evaluate("window.scrollBy(0, window.innerHeight * 2)")
                await asyncio.sleep(2)

        await page.close()
        await browser.close()

    return results


def main():
    parser = argparse.ArgumentParser(description="Douyin Search Scraper")
    parser.add_argument("--keyword", required=True, help="Search keyword")
    parser.add_argument("--output", default="./data/dy_results.json", help="Output JSON path")
    parser.add_argument("--scrolls", type=int, default=10, help="Number of page scrolls")
    args = parser.parse_args()

    results = asyncio.run(scrape_douyin_search(args.keyword, args.scrolls))

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    data = {
        "keyword": args.keyword,
        "scraped_at": datetime.now().isoformat(),
        "count": len(results),
        "results": results
    }
    output_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nSaved {len(results)} results to {output_path}")


if __name__ == "__main__":
    main()
