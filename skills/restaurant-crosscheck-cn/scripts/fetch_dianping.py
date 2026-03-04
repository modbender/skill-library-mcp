"""
大众点评抓取 — sync Playwright 版本
基于原始 fetch_dianping_real.py 重构，修复 async→sync
"""
import os
import re
import time
from typing import List
from urllib.parse import quote

from playwright.sync_api import sync_playwright

from config import (
    CITY_CODES, DIANPING_SESSION, BROWSER_ARGS,
    PAGE_LOAD_WAIT, MAX_DIANPING_ITEMS,
    DP_LIST_SELECTORS, DP_NAME_SELECTORS, DP_SCORE_SELECTORS,
    DP_REVIEW_SELECTORS, DP_PRICE_SELECTORS, DP_ADDR_SELECTORS,
    DP_TAG_SELECTORS,
)
from models import DianpingRestaurant


def get_city_code(location: str) -> int:
    """从位置字符串中匹配大众点评城市代码"""
    for city, code in CITY_CODES.items():
        if city in location:
            return code
    return 0


def fetch_dianping(location: str, cuisine: str) -> List[DianpingRestaurant]:
    """
    从大众点评抓取餐厅数据

    Args:
        location: 地理位置，如 "深圳南山区"
        cuisine: 菜系/类型，如 "粤菜"

    Returns:
        DianpingRestaurant 列表
    """
    restaurants = []
    city_code = get_city_code(location)

    try:
        with sync_playwright() as p:
            os.makedirs(DIANPING_SESSION, exist_ok=True)
            ctx = p.chromium.launch_persistent_context(
                DIANPING_SESSION, headless=False, args=BROWSER_ARGS,
            )
            page = ctx.new_page()

            # 构造搜索 URL（使用正确的城市代码）
            search_term = f"{location} {cuisine}"
            url = f"https://www.dianping.com/search/keyword/{city_code}/0_{quote(search_term)}"
            print(f"  🔗 大众点评: {url}")
            page.goto(url, timeout=30000, wait_until="domcontentloaded")
            time.sleep(PAGE_LOAD_WAIT)

            # 如果 URL 搜索被重定向，改用搜索框
            if "/search/" not in page.url:
                print("  ⚠️ URL 搜索被重定向，尝试搜索框...")
                page.goto("https://www.dianping.com", timeout=30000)
                time.sleep(2)
                box = page.query_selector(
                    'input[placeholder*="商户"], input[name="keyword"], '
                    '#J_search_input, input[type="text"]'
                )
                if box:
                    box.click()
                    box.fill(search_term)
                    time.sleep(0.5)
                    page.keyboard.press("Enter")
                    time.sleep(PAGE_LOAD_WAIT)

            # 用多种选择器找到列表
            items = []
            for sel in DP_LIST_SELECTORS:
                items = page.query_selector_all(sel)
                if items:
                    print(f"  📊 找到 {len(items)} 个候选")
                    break

            if not items:
                page.screenshot(path=os.path.expanduser("~/Downloads/dianping_debug.png"))
                print("  ⚠️ 未找到列表，截图: ~/Downloads/dianping_debug.png")

            # 提取每家店的信息
            for item in items[:MAX_DIANPING_ITEMS]:
                try:
                    r = _parse_item(item)
                    if r:
                        restaurants.append(r)
                except Exception:
                    continue

            ctx.close()

    except Exception as e:
        print(f"  ❌ 大众点评出错: {e}")

    return restaurants


def _parse_item(item) -> DianpingRestaurant | None:
    """解析单个搜索结果项"""
    # 店名
    name = None
    for sel in DP_NAME_SELECTORS:
        el = item.query_selector(sel)
        if el:
            name = el.inner_text().strip()
            if name:
                break
    if not name:
        link = item.query_selector('a[href*="/shop/"]')
        if link:
            name = link.inner_text().strip()
    if not name or len(name) < 2:
        return None

    # 评分
    rating = 0.0
    for sel in DP_SCORE_SELECTORS:
        el = item.query_selector(sel)
        if el:
            cls = el.get_attribute('class') or ''
            m = re.search(r'star[_-]?(\d+)', cls)
            if m:
                rating = int(m.group(1)) / 10.0
                break
            txt = el.inner_text().strip()
            m = re.search(r'(\d+\.?\d*)', txt)
            if m:
                rating = float(m.group(1))
                break

    # 评论数
    review_count = 0
    for sel in DP_REVIEW_SELECTORS:
        el = item.query_selector(sel)
        if el:
            m = re.search(r'(\d+)', el.inner_text())
            if m:
                review_count = int(m.group(1))
                break

    # 人均价格
    price_range = ""
    for sel in DP_PRICE_SELECTORS:
        el = item.query_selector(sel)
        if el:
            txt = el.inner_text().strip()
            m = re.search(r'¥?\d+', txt)
            if m:
                price_range = txt
                break

    # 地址
    address = ""
    for sel in DP_ADDR_SELECTORS:
        el = item.query_selector(sel)
        if el:
            address = el.inner_text().strip()
            break

    # 标签
    tags = []
    for sel in DP_TAG_SELECTORS:
        els = item.query_selector_all(sel)
        if els:
            tags = [e.inner_text().strip() for e in els[:5] if e.inner_text().strip()]
            break

    # URL
    url = ""
    link = item.query_selector('a[href*="/shop/"]')
    if link:
        href = link.get_attribute('href') or ''
        url = href if href.startswith('http') else f"https://www.dianping.com{href}"

    return DianpingRestaurant(
        name=name, rating=rating, review_count=review_count,
        price_range=price_range, address=address, tags=tags, url=url,
    )
