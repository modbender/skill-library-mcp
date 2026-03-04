"""东方财富新闻/快讯抓取 + 基于 FinBERT 的情绪评分.

该模块支持两种情感分析方式：
1. FinBERT 深度学习模型（推荐，更准确）
2. 基于关键词的规则匹配（备用，无需额外依赖）
"""

from __future__ import annotations
import json
import logging
import re
import time
import os
import sys
from dataclasses import dataclass, field
from typing import Optional, List
import httpx

logger = logging.getLogger(__name__)

# FinBERT 情感分析器（延迟加载）
_finbert_analyzer = None

def _get_finbert_analyzer():
    """FinBERT disabled — raw news passed to LLM for sentiment analysis."""
    return None

# 添加父目录到路径以导入 sentiment 模块
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

# 尝试导入 FinBERT 情感分析器
try:
    from analysis.sentiment import (
        FinBERTSentimentAnalyzer,
        get_sentiment_analyzer,
        SentimentResult,
        SentimentLabel
    )
    FINBERT_AVAILABLE = True
except ImportError:
    FINBERT_AVAILABLE = False
    logger.warning("FinBERT not available, using keyword-based sentiment analysis")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)",
    "Referer": "https://finance.eastmoney.com",
}

BULLISH_KEYWORDS = [
    "利好", "上涨", "大涨", "涨停", "突破", "新高", "增长", "超预期",
    "加仓", "买入", "增持", "回购", "分红", "提高", "超额", "盈利",
    "景气", "复苏", "反弹", "放量", "主力", "净流入", "抄底",
    "刺激", "降息", "降准", "宽松", "扩大", "加速", "强势",
    "签约", "中标", "订单", "创新", "突破性", "营收增长", "利润增长",
]
BEARISH_KEYWORDS = [
    "利空", "下跌", "大跌", "跌停", "破位", "新低", "下滑", "不及预期",
    "减仓", "卖出", "减持", "质押", "亏损", "下调", "低于", "萎缩",
    "疲软", "衰退", "暴跌", "缩量", "抛售", "净流出", "割肉",
    "制裁", "加息", "收紧", "紧缩", "风险", "警告", "恐慌",
    "违规", "处罚", "退市", "ST", "问询", "立案", "调查",
]


@dataclass
class NewsItem:
    title: str
    time: str
    source: str
    url: str = ""
    sentiment: float = 0.0
    keywords: list[str] = field(default_factory=list)


class EastMoneyNewsFetcher:
    """东方财富快讯和个股新闻."""

    KUAIXUN_API = "https://newsapi.eastmoney.com/kuaixun/v1/getlist_102_ajaxResult_{limit}_{page}_.html"

    async def get_market_news(self, limit: int = 30) -> list[NewsItem]:
        """获取财经快讯(7x24)."""
        url = self.KUAIXUN_API.format(limit=limit, page=1)
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                resp = await client.get(url, headers=HEADERS)
                resp.raise_for_status()
                text = resp.text

            json_match = re.search(r"var ajaxResult=(\{.*\})", text, re.DOTALL)
            if not json_match:
                logger.warning("EastMoney kuaixun: no JSON in response")
                return []

            data = json.loads(json_match.group(1))
            items = []
            for n in data.get("LivesList", []):
                title = n.get("title", "") or n.get("digest", "")
                if not title:
                    continue
                pub_time = n.get("showtime", "")
                source = n.get("source", "东方财富")
                news_url = n.get("url_w", "")
                digest = n.get("digest", "")
                sentiment, kw = self._score_sentiment(title, digest)
                items.append(NewsItem(
                    title=title, time=pub_time, source=source,
                    url=news_url, sentiment=sentiment, keywords=kw,
                ))
            return items
        except Exception as e:
            logger.warning("EastMoney market news failed: %s", e)
            return []

    async def get_stock_news(self, code: str, name: str = "", limit: int = 10) -> list[NewsItem]:
        """获取个股相关新闻(东方财富搜索)."""
        search_term = name or code
        url = "https://search-api-web.eastmoney.com/search/jsonp"
        cb = "jQuery_news_%d" % int(time.time() * 1000)
        search_params = {
            "cb": cb,
            "param": json.dumps({
                "uid": "",
                "keyword": search_term,
                "type": ["cmsArticleWebOld"],
                "client": "web",
                "clientType": "web",
                "clientVersion": "curr",
                "param": {
                    "cmsArticleWebOld": {
                        "searchScope": "default",
                        "sort": "default",
                        "pageIndex": 1,
                        "pageSize": limit,
                    }
                }
            }),
        }
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                resp = await client.get(url, params=search_params, headers=HEADERS)
                resp.raise_for_status()
                text = resp.text

            json_match = re.search(cb + r"\((.*)\)", text, re.DOTALL)
            if not json_match:
                return []
            data = json.loads(json_match.group(1))

            items = []
            article_data = data.get("result", {})
            if isinstance(article_data, dict):
                results = article_data.get("cmsArticleWebOld", {})
                if isinstance(results, dict):
                    result_list = results.get("list", [])
                elif isinstance(results, list):
                    result_list = results
                else:
                    result_list = []
            else:
                result_list = []

            for r in result_list:
                if not isinstance(r, dict):
                    continue
                title = r.get("title", "").replace("<em>", "").replace("</em>", "")
                pub_time = r.get("date", "")
                source = r.get("mediaName", "")
                news_url = r.get("url", "")
                content = r.get("content", "")
                sentiment, kw = self._score_sentiment(title, content)
                items.append(NewsItem(
                    title=title, time=pub_time, source=source,
                    url=news_url, sentiment=sentiment, keywords=kw,
                ))
            return items
        except Exception as e:
            logger.warning("EastMoney stock news for %s failed: %s", code, e)
            return []

    NEGATIVE_CONTEXT = ["跌幅", "降幅", "亏损", "收窄", "减少"]

    def _score_sentiment(self, text: str, summary: str = "") -> tuple[float, list[str]]:
        """情感评分 - 优先使用 FinBERT，回退到关键词规则.

        Args:
            text: 主文本（标题）
            summary: 摘要/内容

        返回标准化情感分数 (-1.0 to 1.0) 和关键词列表.
        """
        # 尝试使用 FinBERT
        analyzer = _get_finbert_analyzer()
        if analyzer:
            try:
                if summary and len(summary) > 10:
                    # 标题 + 摘要加权分析
                    title_result = analyzer.analyze(text)
                    summary_result = analyzer.analyze(summary[:300])
                    # 标题权重 70%，摘要 30%
                    score = title_result.score * 0.7 + summary_result.score * 0.3
                    keywords = [f"finbert:{title_result.label}", f"sum:{summary_result.label}"]
                else:
                    result = analyzer.analyze(text)
                    score = result.score
                    keywords = [f"finbert:{result.label}"]
                return round(score, 3), keywords
            except Exception as e:
                logger.debug(f"FinBERT failed, using keyword fallback: {e}")

        # FinBERT 不可用，使用关键词规则
        return self._keyword_based_sentiment(text)

    def _keyword_based_sentiment(self, text: str) -> tuple[float, list[str]]:
        """基于关键词的情绪评分 (-1.0 to 1.0)."""
        score = 0.0
        matched = []
        for kw in BULLISH_KEYWORDS:
            if kw in text:
                # Check if this bullish word appears in a negative context
                neg_context = any(neg + kw in text or kw + neg in text for neg in self.NEGATIVE_CONTEXT)
                if neg_context:
                    score -= 0.1
                    matched.append(f"~{kw}(反向)")
                else:
                    score += 0.2
                    matched.append(f"+{kw}")
        for kw in BEARISH_KEYWORDS:
            if kw in text:
                score -= 0.2
                matched.append(f"-{kw}")

        # 归一化到 -1.0 ~ 1.0
        score = max(-1.0, min(1.0, score))
        return round(score, 3), matched


async def get_market_sentiment_from_news(limit: int = 20) -> dict:
    """获取市场情绪汇总."""
    fetcher = EastMoneyNewsFetcher()
    news = await fetcher.get_market_news(limit=limit)
    if not news:
        return {"sentiment": "neutral", "score": 0, "news_count": 0, "headlines": []}

    avg_score = sum(n.sentiment for n in news) / len(news) if news else 0
    bullish = sum(1 for n in news if n.sentiment > 0)
    bearish = sum(1 for n in news if n.sentiment < 0)
    neutral = sum(1 for n in news if n.sentiment == 0)

    if avg_score > 0.5:
        sentiment = "bullish"
    elif avg_score < -0.5:
        sentiment = "bearish"
    else:
        sentiment = "neutral"

    top_headlines = []
    for n in sorted(news, key=lambda x: abs(x.sentiment), reverse=True)[:5]:
        top_headlines.append({
            "title": n.title,
            "sentiment": n.sentiment,
            "time": n.time,
            "keywords": n.keywords[:3],
        })

    return {
        "sentiment": sentiment,
        "score": round(avg_score, 2),
        "bullish_count": bullish,
        "bearish_count": bearish,
        "neutral_count": neutral,
        "news_count": len(news),
        "top_headlines": top_headlines,
    }
