"""多数据源新闻聚合: 东方财富 + 财联社 + 金十数据."""

from __future__ import annotations
import json
import logging
import re
import time
from dataclasses import dataclass, field
from typing import Optional
import httpx

logger = logging.getLogger(__name__)

UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"

BULLISH_KW = [
    "利好", "上涨", "大涨", "涨停", "突破", "新高", "增长", "超预期",
    "加仓", "买入", "增持", "回购", "分红", "盈利", "景气", "复苏",
    "反弹", "放量", "净流入", "降息", "降准", "宽松", "强势",
    "签约", "中标", "订单", "创新", "营收增长", "利润增长",
]
BEARISH_KW = [
    "利空", "下跌", "大跌", "跌停", "破位", "新低", "下滑", "不及预期",
    "减持", "质押", "亏损", "下调", "萎缩", "疲软", "衰退", "暴跌",
    "抛售", "净流出", "制裁", "加息", "收紧", "紧缩", "恐慌",
    "违规", "处罚", "退市", "问询", "立案", "风险", "警告",
]
NEG_CONTEXT = ["跌幅", "降幅", "亏损", "收窄", "减少"]


@dataclass
class NewsItem:
    title: str
    time: str
    source: str
    url: str = ""
    sentiment: float = 0.0
    keywords: list[str] = field(default_factory=list)
    importance: int = 0  # 0=normal, 1=important, 2=critical


VIP_PERSONS = ["特朗普", "川普", "Trump", "马斯克", "Musk", "鲍威尔", "Powell",
               "耶伦", "Yellen", "拜登", "Biden", "习近平", "李强", "潘功胜",
               "易会满", "巴菲特", "Buffett"]
SECTOR_KEYWORDS = ["降息", "加息", "关税", "制裁", "芯片", "AI", "人工智能",
                   "黄金", "原油", "地缘", "战争", "军事"]


def score_sentiment(text: str) -> tuple[float, list[str]]:
    """基于关键词的情绪评分 (-5 to +5)."""
    score = 0.0
    matched = []
    for kw in BULLISH_KW:
        if kw in text:
            neg = any(n + kw in text or kw + n in text for n in NEG_CONTEXT)
            if neg:
                score -= 0.5
                matched.append(f"~{kw}(反向)")
            else:
                score += 1.0
                matched.append(f"+{kw}")
    for kw in BEARISH_KW:
        if kw in text:
            score -= 1.0
            matched.append(f"-{kw}")
    return round(max(-5.0, min(5.0, score)), 1), matched


class CailiansheSource:
    """财联社快讯 (cls.cn telegraph)."""

    API_URL = "https://www.cls.cn/nodeapi/updateTelegraphList"

    async def fetch(self, limit: int = 30) -> list[NewsItem]:
        params = {"app": "CailianpressWeb", "os": "web", "sv": "8.4.6", "rn": str(limit)}
        try:
            async with httpx.AsyncClient(timeout=10) as c:
                r = await c.get(self.API_URL, params=params, headers={
                    "User-Agent": UA, "Referer": "https://www.cls.cn/telegraph"
                })
                r.raise_for_status()
                data = r.json()

            items = []
            roll_data = data.get("data", {}).get("roll_data", [])
            for n in roll_data:
                title = n.get("title", "") or n.get("brief", "") or n.get("content", "")
                title = re.sub(r"<[^>]+>", "", title).strip()
                if not title:
                    continue
                pub_time = n.get("ctime", "")
                if isinstance(pub_time, (int, float)):
                    import datetime
                    pub_time = datetime.datetime.fromtimestamp(pub_time).strftime("%Y-%m-%d %H:%M:%S")
                importance = 2 if n.get("level", "") == "A" else (1 if n.get("level", "") == "B" else 0)
                sentiment, kw = score_sentiment(title)
                items.append(NewsItem(
                    title=title[:200], time=pub_time, source="财联社",
                    url=f"https://www.cls.cn/detail/{n.get('id', '')}",
                    sentiment=sentiment, keywords=kw, importance=importance,
                ))
            return items
        except Exception as e:
            logger.warning("CLS news failed: %s", e)
            return []


class Jin10Source:
    """金十数据快讯."""

    API_URL = "https://flash-api.jin10.com/get_flash_list"

    async def fetch(self, limit: int = 30) -> list[NewsItem]:
        import datetime
        now = datetime.datetime.now()
        params = {
            "channel": "-8200",
            "vip": "0",
            "max_time": now.strftime("%Y-%m-%d %H:%M:%S"),
        }
        try:
            async with httpx.AsyncClient(timeout=10) as c:
                r = await c.get(self.API_URL, params=params, headers={
                    "User-Agent": UA,
                    "Referer": "https://www.jin10.com",
                    "x-app-id": "bVBF4FyRTn5NJF5n",
                    "x-version": "1.0.0",
                })
                r.raise_for_status()
                data = r.json()

            items = []
            for n in data.get("data", [])[:limit]:
                content = n.get("data", {})
                title = content.get("content", "") or content.get("title", "")
                title = re.sub(r"<[^>]+>", "", title).strip()
                if not title:
                    continue
                pub_time = n.get("time", "")
                importance = 1 if content.get("important", 0) else 0
                star = content.get("star", 0)
                if star and star >= 3:
                    importance = 2
                sentiment, kw = score_sentiment(title)
                items.append(NewsItem(
                    title=title[:200], time=pub_time, source="金十数据",
                    sentiment=sentiment, keywords=kw, importance=importance,
                ))
            return items
        except Exception as e:
            logger.warning("Jin10 news failed: %s", e)
            return []


class EastMoneySource:
    """东方财富快讯."""

    API_URL = "https://newsapi.eastmoney.com/kuaixun/v1/getlist_102_ajaxResult_{limit}_{page}_.html"

    async def fetch(self, limit: int = 30) -> list[NewsItem]:
        url = self.API_URL.format(limit=limit, page=1)
        try:
            async with httpx.AsyncClient(timeout=10) as c:
                r = await c.get(url, headers={"User-Agent": UA, "Referer": "https://finance.eastmoney.com"})
                r.raise_for_status()
            m = re.search(r"var ajaxResult=(\{.*\})", r.text, re.DOTALL)
            if not m:
                return []
            data = json.loads(m.group(1))
            items = []
            for n in data.get("LivesList", []):
                title = n.get("title", "") or n.get("digest", "")
                if not title:
                    continue
                sentiment, kw = score_sentiment(title)
                digest = n.get("digest", "")
                if digest and digest != title:
                    s2, kw2 = score_sentiment(digest)
                    sentiment = round((sentiment + s2) / 2, 1)
                    kw.extend(kw2)
                items.append(NewsItem(
                    title=title[:200], time=n.get("showtime", ""), source="东方财富",
                    url=n.get("url_w", ""), sentiment=sentiment, keywords=list(set(kw)),
                ))
            return items
        except Exception as e:
            logger.warning("EastMoney news failed: %s", e)
            return []




class SinaLiveSource:
    """新浪财经 7x24 快讯 (zhibo.sina.com.cn)."""

    API_URL = "https://zhibo.sina.com.cn/api/zhibo/feed"

    async def fetch(self, limit: int = 30) -> list[NewsItem]:
        params = {"page": "1", "page_size": str(limit), "zhibo_id": "152", "tag_id": "0", "dire": "f", "dpc": "1"}
        try:
            async with httpx.AsyncClient(timeout=10) as c:
                r = await c.get(self.API_URL, params=params, headers={
                    "User-Agent": UA, "Referer": "https://finance.sina.com.cn"
                })
                r.raise_for_status()
                data = r.json()

            items = []
            feed_list = data.get("result", {}).get("data", {}).get("feed", {}).get("list", [])
            for n in feed_list:
                rich_text = n.get("rich_text", "")
                title = re.sub(r"<[^>]+>", "", rich_text).strip()
                if not title or len(title) < 5:
                    continue
                pub_time = n.get("create_time", "")
                importance = 1 if n.get("is_top", 0) or n.get("is_red", 0) else 0
                sentiment, kw = score_sentiment(title)
                items.append(NewsItem(
                    title=title[:200], time=pub_time, source="新浪财经",
                    sentiment=sentiment, keywords=kw, importance=importance,
                ))
            return items
        except Exception as e:
            logger.warning("Sina live news failed: %s", e)
            return []


class WallStreetCNSource:
    """华尔街见闻快讯 (wallstreetcn.com)."""

    API_URL = "https://api-one-wscn.awtmt.com/apiv1/content/lives"

    async def fetch(self, limit: int = 30) -> list[NewsItem]:
        params = {"channel": "global-channel", "client": "pc", "limit": str(limit), "first_page": "true", "accept": "live"}
        try:
            async with httpx.AsyncClient(timeout=10) as c:
                r = await c.get(self.API_URL, params=params, headers={
                    "User-Agent": UA, "Referer": "https://wallstreetcn.com/live/global"
                })
                r.raise_for_status()
                data = r.json()

            items = []
            for n in data.get("data", {}).get("items", []):
                content_text = n.get("content_text", "") or n.get("title", "")
                title = re.sub(r"<[^>]+>", "", content_text).strip()
                if not title or len(title) < 5:
                    continue
                import datetime
                ts = n.get("display_time", 0)
                pub_time = datetime.datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M:%S") if ts else ""
                importance = 1 if n.get("score", 0) and n["score"] > 50 else 0
                sentiment, kw = score_sentiment(title)
                items.append(NewsItem(
                    title=title[:200], time=pub_time, source="华尔街见闻",
                    sentiment=sentiment, keywords=kw, importance=importance,
                ))
            return items
        except Exception as e:
            logger.warning("WallStreetCN news failed: %s", e)
            return []


async def aggregate_news(limit_per_source: int = 20) -> dict:
    """从多源聚合新闻并返回结构化结果."""
    import asyncio
    sources = [
        ("cls", CailiansheSource()),
        ("jin10", Jin10Source()),
        ("eastmoney", EastMoneySource()),
        ("sina", SinaLiveSource()),
        ("wallstreetcn", WallStreetCNSource()),
    ]

    tasks = [src.fetch(limit_per_source) for _, src in sources]
    try:
        results = await asyncio.wait_for(
            asyncio.gather(*tasks, return_exceptions=True),
            timeout=30.0
        )
    except asyncio.TimeoutError:
        results = []

    all_news = []
    source_status = {}
    for (name, _), result in zip(sources, results):
        if isinstance(result, Exception):
            source_status[name] = {"status": "error", "error": str(result), "count": 0}
        else:
            source_status[name] = {"status": "ok", "count": len(result)}
            all_news.extend(result)

    # Boost importance for VIP person mentions and key sector events
    for n in all_news:
        for vip in VIP_PERSONS:
            if vip in n.title:
                n.importance = max(n.importance, 2)
                n.keywords.append(f"VIP:{vip}")
                break
        for sk in SECTOR_KEYWORDS:
            if sk in n.title and n.importance < 1:
                n.importance = 1

    # Deduplicate by title similarity
    seen_titles = set()
    unique_news = []
    for n in all_news:
        short = n.title[:30]
        if short not in seen_titles:
            seen_titles.add(short)
            unique_news.append(n)

    # Sort: importance desc, then time desc
    unique_news.sort(key=lambda x: (-x.importance, x.time or ""), reverse=False)

    # Compute overall sentiment
    if unique_news:
        avg_score = sum(n.sentiment for n in unique_news) / len(unique_news)
    else:
        avg_score = 0
    bullish = sum(1 for n in unique_news if n.sentiment > 0)
    bearish = sum(1 for n in unique_news if n.sentiment < 0)

    if avg_score > 0.5:
        sentiment = "bullish"
    elif avg_score < -0.5:
        sentiment = "bearish"
    else:
        sentiment = "neutral"

    critical = [{"title": n.title, "source": n.source, "time": n.time, "sentiment": n.sentiment}
                for n in unique_news if n.importance >= 2][:5]
    important = [{"title": n.title, "source": n.source, "time": n.time, "sentiment": n.sentiment}
                 for n in unique_news if n.importance == 1][:10]
    top_movers = [{"title": n.title, "source": n.source, "time": n.time, "sentiment": n.sentiment, "keywords": n.keywords[:3]}
                  for n in sorted(unique_news, key=lambda x: abs(x.sentiment), reverse=True)][:5]

    return {
        "sentiment": sentiment,
        "score": round(avg_score, 2),
        "bullish_count": bullish,
        "bearish_count": bearish,
        "total_news": len(unique_news),
        "sources": source_status,
        "critical_news": critical,
        "important_news": important,
        "top_sentiment_movers": top_movers,
    }
