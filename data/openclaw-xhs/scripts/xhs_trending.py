#!/usr/bin/env python3
"""
Scrape trending content from Xiaohongshu explore page.

Usage:
    uv run --project $XHS_TOOLKIT_DIR xhs_trending.py --category "综合" --limit 20
    uv run --project $XHS_TOOLKIT_DIR xhs_trending.py --keyword "AI" --limit 30
"""

import argparse
import json
import os
import random
import sys
import time
from collections import Counter
from datetime import datetime
from pathlib import Path

CATEGORY_MAP = {
    "综合": "",
    "时尚": "fashion",
    "美食": "food",
    "旅行": "travel",
    "美妆": "beauty",
    "科技": "tech",
    "健身": "fitness",
    "宠物": "pet",
    "家居": "home",
    "教育": "education",
}


def setup_driver():
    """Create a Selenium Chrome driver directly (bypasses xhs-toolkit's
    ChromeDriverManager which hardcodes a Linux-only profile directory)."""
    import tempfile
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.chrome.service import Service

    cookies_file = os.environ.get(
        "XHS_COOKIES_FILE",
        os.path.expanduser("~/.openclaw/credentials/xhs_cookies.json"),
    )

    chrome_path = os.environ.get(
        "CHROME_PATH",
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    )

    # Use persistent Chrome profile (shares login state with publish scripts)
    profile_dir = os.environ.get(
        "XHS_CHROME_PROFILE",
        os.path.expanduser("~/.openclaw/skills/xhs/chrome-data"),
    )
    os.makedirs(profile_dir, exist_ok=True)

    options = Options()
    options.binary_location = chrome_path

    # Headless mode
    options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument(f"--user-data-dir={profile_dir}")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-notifications")
    options.add_argument("--disable-popup-blocking")
    options.add_argument("--no-first-run")
    options.add_argument("--disable-default-apps")
    options.add_argument(
        "--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
    )
    options.add_experimental_option("excludeSwitches", ["enable-logging"])
    options.add_experimental_option("useAutomationExtension", False)

    driver = webdriver.Chrome(options=options)

    # Load cookies for authenticated access
    if Path(cookies_file).exists():
        try:
            data = json.loads(Path(cookies_file).read_text())
            cookies = data.get("cookies", data) if isinstance(data, dict) else data
            driver.get("https://www.xiaohongshu.com")
            time.sleep(2)
            for cookie in cookies:
                cookie_clean = {k: v for k, v in cookie.items()
                                if k in ("name", "value", "domain", "path", "secure", "httpOnly")}
                if "domain" in cookie_clean:
                    cookie_clean["domain"] = cookie_clean["domain"].lstrip(".")
                    if "xiaohongshu" not in cookie_clean["domain"]:
                        continue
                try:
                    driver.add_cookie(cookie_clean)
                except Exception:
                    pass
        except Exception:
            pass

    return driver, profile_dir


def scrape_explore(driver, category: str = "", limit: int = 20) -> list[dict]:
    """Scrape the explore page for trending notes."""
    base_url = "https://www.xiaohongshu.com/explore"
    if category:
        url = f"{base_url}?channel={category}"
    else:
        url = base_url

    driver.get(url)
    time.sleep(3 + random.uniform(0.5, 2.0))

    notes = []
    scroll_count = 0
    max_scrolls = min(limit // 5 + 2, 15)

    while len(notes) < limit and scroll_count < max_scrolls:
        # Try multiple selectors for note cards
        selectors = [
            "section.note-item",
            ".note-item",
            "[class*='note-item']",
            ".feeds-page .note-item",
            "a[href*='/explore/']",
            ".explore-feed .note-item",
        ]

        elements = []
        for sel in selectors:
            try:
                elements = driver.find_elements("css selector", sel)
                if elements:
                    break
            except Exception:
                continue

        if not elements:
            # Try XPath as fallback
            try:
                elements = driver.find_elements("xpath", "//section[contains(@class,'note')]")
            except Exception:
                pass

        for el in elements:
            if len(notes) >= limit:
                break
            try:
                note = extract_note_data(el, driver)
                if note and note.get("title") and note["title"] not in {n["title"] for n in notes}:
                    notes.append(note)
            except Exception:
                continue

        # Scroll down
        driver.execute_script("window.scrollBy(0, 800);")
        time.sleep(1.5 + random.uniform(0.5, 1.5))
        scroll_count += 1

    return notes[:limit]


def scrape_search(driver, keyword: str, limit: int = 20) -> list[dict]:
    """Scrape search results for a keyword."""
    from urllib.parse import quote
    url = f"https://www.xiaohongshu.com/search_result?keyword={quote(keyword)}&source=web_search_result_notes"

    driver.get(url)
    time.sleep(3 + random.uniform(0.5, 2.0))

    notes = []
    scroll_count = 0
    max_scrolls = min(limit // 5 + 2, 15)

    while len(notes) < limit and scroll_count < max_scrolls:
        selectors = [
            "section.note-item",
            ".note-item",
            "[class*='note-item']",
            "a[href*='/search_result/']",
            ".feeds-container .note-item",
        ]

        elements = []
        for sel in selectors:
            try:
                elements = driver.find_elements("css selector", sel)
                if elements:
                    break
            except Exception:
                continue

        for el in elements:
            if len(notes) >= limit:
                break
            try:
                note = extract_note_data(el, driver)
                if note and note.get("title") and note["title"] not in {n["title"] for n in notes}:
                    notes.append(note)
            except Exception:
                continue

        driver.execute_script("window.scrollBy(0, 800);")
        time.sleep(1.5 + random.uniform(0.5, 1.5))
        scroll_count += 1

    return notes[:limit]


def extract_note_data(element, driver) -> dict | None:
    """Extract data from a single note card element."""
    note = {}

    # Title
    title_selectors = [
        ".title", "a .title", ".note-title",
        "[class*='title']", "span[class*='title']",
    ]
    for sel in title_selectors:
        try:
            title_el = element.find_element("css selector", sel)
            note["title"] = title_el.text.strip()
            if note["title"]:
                break
        except Exception:
            continue

    if not note.get("title"):
        try:
            note["title"] = element.text.strip().split("\n")[0][:100]
        except Exception:
            return None

    # Like count
    like_selectors = [
        ".like-wrapper .count",
        "[class*='like'] [class*='count']",
        ".engagement .like",
        "span[class*='like']",
    ]
    for sel in like_selectors:
        try:
            like_el = element.find_element("css selector", sel)
            note["likes"] = parse_count(like_el.text.strip())
            break
        except Exception:
            continue
    note.setdefault("likes", 0)

    # Link
    try:
        link_el = element.find_element("css selector", "a[href]")
        href = link_el.get_attribute("href") or ""
        if href:
            note["url"] = href if href.startswith("http") else f"https://www.xiaohongshu.com{href}"
    except Exception:
        note["url"] = ""

    # Cover image
    try:
        img_el = element.find_element("css selector", "img")
        note["cover"] = img_el.get_attribute("src") or ""
    except Exception:
        note["cover"] = ""

    # Author
    author_selectors = [
        ".author-wrapper .name",
        "[class*='author'] [class*='name']",
        ".nickname",
    ]
    for sel in author_selectors:
        try:
            author_el = element.find_element("css selector", sel)
            note["author"] = author_el.text.strip()
            break
        except Exception:
            continue
    note.setdefault("author", "")

    return note


def parse_count(text: str) -> int:
    """Parse count text like '1.2万' to integer."""
    text = text.strip()
    if not text:
        return 0
    try:
        if "万" in text:
            return int(float(text.replace("万", "")) * 10000)
        elif "w" in text.lower():
            return int(float(text.lower().replace("w", "")) * 10000)
        elif "k" in text.lower():
            return int(float(text.lower().replace("k", "")) * 1000)
        return int(text.replace(",", ""))
    except (ValueError, TypeError):
        return 0


def analyze_topics(notes: list[dict]) -> dict:
    """Analyze trending topics using jieba word segmentation."""
    import jieba

    all_titles = " ".join(n.get("title", "") for n in notes)

    words = jieba.cut(all_titles, cut_all=False)
    # Filter short words and common stopwords
    stopwords = {"的", "了", "在", "是", "我", "有", "和", "就", "不", "人", "都",
                 "一", "一个", "上", "也", "很", "到", "说", "要", "去", "你",
                 "会", "着", "没有", "看", "好", "自己", "这", "他", "她", "吗",
                 "什么", "那", "最", "出", "真的", "太", "让", "把", "被", "从",
                 "还是", "还", "啊", "呢", "吧", "嘛", "哦", "哈", "呀", "啦",
                 "可以", "怎么", "这个", "那个", "如何", "为什么", "但", "但是",
                 "因为", "所以", "如果", "虽然", "而且", "或者", "以及"}
    word_counts = Counter()
    for w in words:
        w = w.strip()
        if len(w) >= 2 and w not in stopwords:
            word_counts[w] += 1

    # Weight by engagement
    weighted = Counter()
    for note in notes:
        title = note.get("title", "")
        likes = note.get("likes", 0) or 1
        title_words = jieba.cut(title, cut_all=False)
        for w in title_words:
            w = w.strip()
            if len(w) >= 2 and w not in stopwords:
                weighted[w] += likes

    return {
        "top_keywords": word_counts.most_common(20),
        "top_weighted_keywords": weighted.most_common(20),
        "total_notes": len(notes),
        "avg_likes": sum(n.get("likes", 0) for n in notes) / max(len(notes), 1),
    }


def main():
    parser = argparse.ArgumentParser(description="Scrape trending content from Xiaohongshu")
    parser.add_argument("--category", default="综合",
                        help=f"Category ({'/'.join(CATEGORY_MAP.keys())})")
    parser.add_argument("--keyword", default="", help="Search keyword")
    parser.add_argument("--limit", type=int, default=20, help="Max notes to scrape (default 20, max 50)")
    parser.add_argument("--output", default="", help="Output file path")
    parser.add_argument("--no-analysis", action="store_true", help="Skip keyword analysis")
    args = parser.parse_args()

    limit = min(args.limit, 50)

    print(json.dumps({
        "status": "starting",
        "message": f"开始爬取小红书{'搜索: ' + args.keyword if args.keyword else '热门: ' + args.category}...",
    }))
    sys.stdout.flush()

    driver = None
    profile_dir = None
    try:
        driver, profile_dir = setup_driver()

        if args.keyword:
            notes = scrape_search(driver, args.keyword, limit)
        else:
            category_code = CATEGORY_MAP.get(args.category, "")
            notes = scrape_explore(driver, category_code, limit)

        # Sort by likes descending
        notes.sort(key=lambda x: x.get("likes", 0), reverse=True)

        # Keyword analysis
        analysis = {}
        if not args.no_analysis and notes:
            analysis = analyze_topics(notes)

        # Prepare compact output (limit notes detail to avoid flooding agent context)
        compact_notes = [
            {"title": n.get("title", ""), "likes": n.get("likes", 0), "author": n.get("author", "")}
            for n in notes[:10]
        ]

        result_summary = {
            "status": "success",
            "message": f"成功爬取 {len(notes)} 条{'搜索' if args.keyword else '热门'}笔记。",
            "total_notes": len(notes),
        }
        if analysis:
            result_summary["top_keywords"] = [w for w, _ in analysis["top_keywords"][:10]]
            result_summary["avg_likes"] = round(analysis["avg_likes"], 1)
        result_summary["top_notes"] = compact_notes

        # Save full data to file
        data_dir = os.environ.get(
            "XHS_DATA_DIR",
            os.path.expanduser("~/.openclaw/skills/xhs/data"),
        )
        full_result = {
            "status": "success",
            "query": {
                "category": args.category if not args.keyword else None,
                "keyword": args.keyword or None,
                "limit": limit,
            },
            "scraped_at": datetime.now().isoformat(),
            "notes": notes,
        }
        if analysis:
            full_result["analysis"] = {
                "total_notes": analysis["total_notes"],
                "avg_likes": round(analysis["avg_likes"], 1),
                "top_keywords": [{"word": w, "count": c} for w, c in analysis["top_keywords"]],
                "top_weighted_keywords": [{"word": w, "score": s} for w, s in analysis["top_weighted_keywords"]],
            }

        if args.output:
            output_path = Path(args.output)
        else:
            trending_dir = Path(data_dir) / "trending"
            trending_dir.mkdir(parents=True, exist_ok=True)
            ts = datetime.now().strftime("%Y-%m-%d_%H%M%S")
            tag = args.keyword or args.category
            output_path = trending_dir / f"{ts}_{tag}.json"

        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(full_result, ensure_ascii=False, indent=2))
        result_summary["output_file"] = str(output_path)

        # Print compact summary (agent parses this); full data is in the file
        print(json.dumps(result_summary, ensure_ascii=False))

    except Exception as e:
        print(json.dumps({
            "status": "error",
            "message": f"爬取过程出错: {str(e)}",
            "error": str(e),
        }))
        sys.exit(1)
    finally:
        if driver:
            try:
                driver.quit()
            except Exception:
                pass
        pass  # persistent profile dir — do not delete


if __name__ == "__main__":
    main()
