"""
小红书抓取 — sync Playwright 版本
基于原始 fetch_xiaohongshu_real.py 重构，修复 async→sync，改进店名提取
"""
import os
import re
import time
from typing import List
from urllib.parse import quote

from playwright.sync_api import sync_playwright

from config import (
    XHS_SESSION, BROWSER_ARGS,
    PAGE_LOAD_WAIT, SCROLL_WAIT, MAX_XHS_NOTES,
    XHS_CARD_SELECTORS,
    POSITIVE_WORDS, NEGATIVE_WORDS, NEGATION_WORDS,
    SHOP_SUFFIXES, EXCLUDE_KEYWORDS,
)
from models import XiaohongshuPost


def fetch_xiaohongshu(location: str, cuisine: str) -> List[XiaohongshuPost]:
    """
    从小红书抓取餐厅相关笔记

    Args:
        location: 地理位置，如 "深圳南山区"
        cuisine: 菜系/类型，如 "粤菜"

    Returns:
        XiaohongshuPost 列表（已按餐厅名去重合并）
    """
    raw_posts = []

    try:
        with sync_playwright() as p:
            os.makedirs(XHS_SESSION, exist_ok=True)
            ctx = p.chromium.launch_persistent_context(
                XHS_SESSION, headless=False, args=BROWSER_ARGS,
            )
            page = ctx.new_page()

            keyword = f"{location} {cuisine} 推荐"
            url = (
                f"https://www.xiaohongshu.com/search_result?"
                f"keyword={quote(keyword)}&source=web_search_result_notes"
            )
            print(f"  🔗 小红书: {url}")
            page.goto(url, timeout=30000, wait_until="domcontentloaded")
            time.sleep(PAGE_LOAD_WAIT + 1)

            # 如果被重定向，用搜索框
            if "/search_result" not in page.url:
                print("  ⚠️ 被重定向，尝试搜索框...")
                page.goto("https://www.xiaohongshu.com", timeout=30000)
                time.sleep(3)
                box = page.query_selector(
                    'input[placeholder*="搜索"], #search-input, input[type="text"]'
                )
                if box:
                    box.click()
                    box.fill(keyword)
                    time.sleep(0.5)
                    page.keyboard.press("Enter")
                    time.sleep(PAGE_LOAD_WAIT + 1)

            # 滚动加载更多
            for _ in range(3):
                page.evaluate("window.scrollBy(0, 600)")
                time.sleep(SCROLL_WAIT)

            # 抓取笔记卡片
            cards = []
            for sel in XHS_CARD_SELECTORS:
                cards = page.query_selector_all(sel)
                if cards:
                    break
            print(f"  📊 找到 {len(cards)} 篇笔记")

            if not cards:
                page.screenshot(path=os.path.expanduser("~/Downloads/xhs_debug.png"))
                print("  ⚠️ 未找到笔记，截图: ~/Downloads/xhs_debug.png")

            # 从笔记标题提取店名
            seen_names = set()
            for card in cards[:MAX_XHS_NOTES]:
                try:
                    title_el = card.query_selector('.title, [class*="title"], span, .desc')
                    title = title_el.inner_text().strip() if title_el else card.inner_text().strip()
                    if not title:
                        continue

                    # 提取点赞数
                    likes = _parse_likes(card)

                    # 提取店名
                    names = extract_restaurant_names(title)
                    sentiment = analyze_sentiment(title)
                    keywords = extract_keywords(title)

                    for name in names:
                        if name not in seen_names:
                            seen_names.add(name)
                            raw_posts.append(XiaohongshuPost(
                                restaurant_name=name,
                                likes=likes,
                                saves=0,
                                comments=0,
                                sentiment_score=sentiment,
                                keywords=keywords,
                                mention_count=1,
                            ))

                except Exception:
                    continue

            ctx.close()

    except Exception as e:
        print(f"  ❌ 小红书出错: {e}")

    # 合并同名餐厅
    return _merge_posts(raw_posts)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  辅助函数
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def _parse_likes(card) -> int:
    """从卡片元素中提取点赞数"""
    like_el = card.query_selector('[class*="like"], [class*="count"]')
    if not like_el:
        return 0
    m = re.search(r'(\d+\.?\d*)\s*(万|k)?', like_el.inner_text())
    if not m:
        return 0
    likes = float(m.group(1))
    if m.group(2) in ('万', 'k'):
        likes *= 10000
    return int(likes)


def extract_restaurant_names(text: str) -> List[str]:
    """
    从笔记标题中提取餐厅名（基于原始 fetch_xiaohongshu_real.py 的逻辑，大幅增强）
    """
    names = []

    # 1. 书名号 / 引号内的名称（小红书最常见的格式）
    for pattern in [r'「(.+?)」', r'『(.+?)』', r'《(.+?)》', r'【(.+?)】',
                    r'\[(.+?)\]', r'"(.+?)"', r'"(.+?)"']:
        names.extend(re.findall(pattern, text))

    # 2. 探店/打卡模式: "探店XXX"、"打卡XXX"（来自原始 _extract_restaurant_name）
    explore_match = re.search(
        r'(?:探店|打卡|安利|推荐|种草)[：:\s]*(.{2,20}?)(?:[！!,，。\s]|太|超|真|$)',
        text
    )
    if explore_match:
        names.append(explore_match.group(1).strip())

    # 3. 包含餐饮后缀的词组
    suffix_pattern = '|'.join(re.escape(s) for s in SHOP_SUFFIXES)
    names.extend(re.findall(
        rf'([\u4e00-\u9fff\w]{{2,12}}(?:{suffix_pattern}))',
        text
    ))

    # 4. 分隔符分割的片段（如 "店名A｜店名B｜探店"）
    if any(sep in text for sep in ['|', '｜', '/', '·']):
        for part in re.split(r'[|｜/·]', text):
            part = part.strip()
            if 2 <= len(part) <= 15 and not any(k in part for k in EXCLUDE_KEYWORDS):
                names.append(part)

    # 去重保序，过滤太短的
    seen = set()
    result = []
    for n in names:
        n = n.strip()
        # 去除 emoji
        n = re.sub(r'[💕🔥✨🌟📍❗🍜🍲🥘🍱🍣🍻☕🎉👍💯]+', '', n).strip()
        if len(n) >= 2 and n not in seen:
            seen.add(n)
            result.append(n)
    return result


def analyze_sentiment(text: str) -> float:
    """
    情感分析（基于原始 fetch_xiaohongshu_real.py 的逻辑，带否定词处理）
    返回 -1 ~ 1
    """
    pos_count, neg_count = 0, 0

    for word in POSITIVE_WORDS:
        idx = text.find(word)
        while idx >= 0:
            context = text[max(0, idx - 2):idx]
            if any(context.endswith(n) for n in NEGATION_WORDS):
                neg_count += 1
            else:
                pos_count += 1
            idx = text.find(word, idx + len(word))

    for word in NEGATIVE_WORDS:
        idx = text.find(word)
        while idx >= 0:
            context = text[max(0, idx - 2):idx]
            if any(context.endswith(n) for n in NEGATION_WORDS):
                pos_count += 1  # 双重否定 = 正面
            else:
                neg_count += 1
            idx = text.find(word, idx + len(word))

    total = pos_count + neg_count
    if total == 0:
        return 0.0
    return (pos_count - neg_count) / total


def extract_keywords(text: str) -> List[str]:
    """从文本中提取关键词"""
    keyword_list = [
        '好吃', '美味', '环境', '服务', '性价比', '新鲜', '正宗', '值得',
        '推荐', '宝藏', '排队', '回头客', '惊艳',
    ]
    return [kw for kw in keyword_list if kw in text][:5]


def _merge_posts(posts: List[XiaohongshuPost]) -> List[XiaohongshuPost]:
    """合并同名餐厅的帖子"""
    merged = {}
    for p in posts:
        name = p.restaurant_name
        if name in merged:
            m = merged[name]
            m.mention_count += 1
            m.likes += p.likes
            # 取各篇情感的平均值
            m.sentiment_score = (m.sentiment_score * (m.mention_count - 1) + p.sentiment_score) / m.mention_count
            # 合并关键词
            for kw in p.keywords:
                if kw not in m.keywords:
                    m.keywords.append(kw)
        else:
            merged[name] = XiaohongshuPost(
                restaurant_name=name,
                likes=p.likes, saves=p.saves, comments=p.comments,
                sentiment_score=p.sentiment_score,
                keywords=list(p.keywords),
                mention_count=1,
            )
    return list(merged.values())
