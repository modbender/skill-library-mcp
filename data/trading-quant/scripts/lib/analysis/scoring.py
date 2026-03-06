"""TradingScore V2 — multi-dimensional stock scoring engine."""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any

from config import get_config
from data_sources.base import QuoteData
from .technical import TechnicalSignal, compute_technical
from .capital_flow import CapitalSignal, compute_capital
from .industry_classifier import classify_industry_by_api, classify_industry

logger = logging.getLogger(__name__)


@dataclass
class StockScore:
    """Complete multi-dimensional score for a stock."""
    code: str
    name: str
    price: float
    change_pct: float
    total_score: float = 50.0
    technical: dict = field(default_factory=dict)
    capital: dict = field(default_factory=dict)
    sentiment: dict = field(default_factory=dict)
    fundamental: dict = field(default_factory=dict)
    market: dict = field(default_factory=dict)
    signal: str = "WATCH"
    confidence: str = "中"
    risk_alerts: list[str] = field(default_factory=list)
    data_freshness: str = "fresh"

    def to_dict(self) -> dict:
        return {
            "code": self.code,
            "name": self.name,
            "price": self.price,
            "change_pct": self.change_pct,
            "score": {
                "total": round(self.total_score, 1),
                "technical": self.technical,
                "capital": self.capital,
                "fundamental": self.fundamental,
                "sentiment": self.sentiment,
                "market": self.market,
            },
            "signal": self.signal,
            "confidence": self.confidence,
            "risk_alerts": self.risk_alerts,
            "data_freshness": self.data_freshness,
        }


def _get_signal(score: float) -> tuple[str, str]:
    """Map score to signal level and confidence."""
    cfg = get_config().get("scoring", {}).get("signals", {})
    if score >= cfg.get("strong_buy", 80):
        return "STRONG_BUY", "高"
    elif score >= cfg.get("buy", 65):
        return "BUY", "中高"
    elif score >= cfg.get("watch", 50):
        return "WATCH", "中"
    elif score >= cfg.get("hold", 35):
        return "HOLD", "中低"
    elif score >= cfg.get("sell", 22):
        return "SELL", "低"
    elif score >= cfg.get("strong_sell", 18):
        return "STRONG_SELL", "极低"
    else:
        return "STRONG_SELL", "极低"






INDUSTRY_PE_RANGES = {
    "银行": {"undervalued": 5, "fair": 8, "high": 12, "extreme": 20},
    "地产": {"undervalued": 5, "fair": 10, "high": 15, "extreme": 25},
    "钢铁": {"undervalued": 5, "fair": 10, "high": 15, "extreme": 25},
    "煤炭": {"undervalued": 5, "fair": 8, "high": 12, "extreme": 20},
    "石油": {"undervalued": 6, "fair": 12, "high": 18, "extreme": 30},
    "电力": {"undervalued": 8, "fair": 15, "high": 25, "extreme": 40},
    "有色": {"undervalued": 8, "fair": 15, "high": 25, "extreme": 45},
    "化工": {"undervalued": 8, "fair": 15, "high": 25, "extreme": 40},
    "消费": {"undervalued": 15, "fair": 25, "high": 40, "extreme": 60},
    "白酒": {"undervalued": 15, "fair": 30, "high": 45, "extreme": 70},
    "医药": {"undervalued": 15, "fair": 30, "high": 50, "extreme": 80},
    "科技": {"undervalued": 15, "fair": 35, "high": 60, "extreme": 100},
    "半导体": {"undervalued": 15, "fair": 40, "high": 70, "extreme": 120},
    "军工": {"undervalued": 20, "fair": 40, "high": 70, "extreme": 100},
    "新能源": {"undervalued": 15, "fair": 30, "high": 50, "extreme": 80},
    "ETF": {"undervalued": 0, "fair": 999, "high": 999, "extreme": 999},
    "default": {"undervalued": 10, "fair": 20, "high": 40, "extreme": 80},
}

INDUSTRY_KEYWORDS = {
    "银行": ["银行", "Bank"],
    "地产": ["地产", "置业", "置地"],
    "钢铁": ["钢铁", "钢材", "不锈钢"],
    "煤炭": ["煤炭", "煤业", "能源"],
    "石油": ["石油", "石化", "中海油"],
    "电力": ["电力", "电网", "发电"],
    "有色": ["有色", "铜", "铝", "锌", "镍", "锡", "铅", "银锡", "矿业", "紫金"],
    "化工": ["化工", "化学"],
    "消费": ["食品", "饮料", "乳业", "调味"],
    "白酒": ["茅台", "五粮液", "洋河", "泸州", "汾酒", "酒"],
    "医药": ["医药", "生物", "制药", "疫苗"],
    "科技": ["科技", "软件", "信息", "数据", "AI", "智能"],
    "半导体": ["芯片", "半导体", "存储", "光刻"],
    "军工": ["军工", "航天", "航空", "兵器", "船舶", "导弹", "国防"],
    "新能源": ["光伏", "风电", "锂电", "新能源", "电池", "储能", "金风"],
    "ETF": ["ETF"],
}


# 保留旧函数别名以兼容现有代码，但标记为废弃
def _classify_industry(name: str) -> str:
    """
    [废弃] 根据股票名称推断行业分类.
    
    请使用 classify_industry_by_api(code, name) 替代.
    """
    from .industry_classifier import _classify_industry_by_name
    return _classify_industry_by_name(name)


def _get_pe_ranges(industry: str) -> dict:
    """获取行业PE合理区间."""
    return INDUSTRY_PE_RANGES.get(industry, INDUSTRY_PE_RANGES["default"])


def _compute_fundamental(quote: QuoteData) -> dict:
    """Compute fundamental score from PE/PB data."""
    score = 50.0
    signals = []

    pe = quote.pe
    pb = quote.pb

    if pe <= 0:
        signals.append("PE数据缺失(中性)")
        return {"score": score, "signals": signals, "pe": pe, "pb": pb}

    # PE scoring with industry classification
    industry = classify_industry(quote.code)
    pe_ranges = _get_pe_ranges(industry)
    
    if pe < pe_ranges["undervalued"]:
        score += 15
        signals.append(f"PE={pe:.1f}(低估值,{industry})")
    elif pe < pe_ranges["fair"]:
        score += 8
        signals.append(f"PE={pe:.1f}(合理,{industry})")
    elif pe < pe_ranges["high"]:
        signals.append(f"PE={pe:.1f}(偏高,{industry})")
    elif pe < pe_ranges["extreme"]:
        score -= 8
        signals.append(f"PE={pe:.1f}(高估,{industry})")
    else:
        score -= 15
        signals.append(f"PE={pe:.1f}(极高估,{industry})")

    # PB scoring
    if pb > 0:
        if pb < 1:
            score += 10
            signals.append(f"PB={pb:.2f}(破净)")
        elif pb < 2:
            score += 5
            signals.append(f"PB={pb:.2f}(低PB)")
        elif pb > 10:
            score -= 5
            signals.append(f"PB={pb:.2f}(高PB)")

    score = max(0, min(100, score))
    return {"score": round(score, 1), "signals": signals, "pe": pe, "pb": pb, "market_cap": quote.market_cap}

def compute_stock_score(
    quote: QuoteData,
    daily_df: Any,
    avg_volume: float = 0,
    avg_amount: float = 0,
    extra: dict = None,
    capital_flow_data: dict = None,  # 新增：主力资金数据
) -> StockScore:
    """Compute TradingScore V2 for a single stock.

    Combines technical (30%), capital (35%), sentiment (20%), market (15%).
    Sentiment and market scores default to neutral when data unavailable.
    
    Args:
        capital_flow_data: 主力资金数据 (来自主力接口或龙虎榜)
    """
    if extra is None:
        extra = {}
    cfg = get_config().get("scoring", {}).get("weights", {})
    w_tech = cfg.get("technical", 0.25)
    w_cap = cfg.get("capital", 0.30)
    w_fund = cfg.get("fundamental", 0.10)
    w_sent = cfg.get("sentiment", 0.20)
    w_mkt = cfg.get("market", 0.15)

    w_total = w_tech + w_cap + w_fund + w_sent + w_mkt
    if abs(w_total - 1.0) > 0.001:
        w_tech /= w_total
        w_cap /= w_total
        w_fund /= w_total
        w_sent /= w_total
        w_mkt /= w_total

    tech = compute_technical(daily_df)
    cap = compute_capital(quote, avg_volume=avg_volume, avg_amount=avg_amount, main_force_data=capital_flow_data)
    fund = _compute_fundamental(quote)

    sent_score = 50.0
    sent_signals = []
    news_sentiment = extra.get("news_sentiment", None)
    if news_sentiment is not None:
        news_count = extra.get("news_count", 0)
        # Map news sentiment (-5 to +5) to score (30 to 70)
        sent_score = 50.0 + news_sentiment * 4.0
        sent_score = max(30.0, min(70.0, sent_score))
        if news_sentiment > 0.5:
            sent_signals.append(f"新闻偏多({news_count}条,情绪+{news_sentiment})")
        elif news_sentiment < -0.5:
            sent_signals.append(f"新闻偏空({news_count}条,情绪{news_sentiment})")
        else:
            sent_signals.append(f"新闻中性({news_count}条)")
        top_news = extra.get("top_news", [])
        for t in top_news[:1]:
            sent_signals.append(f"热点:{t[:20]}")
    else:
        sent_signals.append("消息面暂无数据(中性)")

    mkt_data = extra.get("market_sentiment", None)
    if mkt_data and isinstance(mkt_data, dict):
        mkt_score = float(mkt_data.get("score", 50.0))
        mkt_signals = mkt_data.get("signals", ["市场情绪数据加载中"])
        
        # 大盘连涨天数惩罚(从extra中获取)
        consecutive_up_days = extra.get("consecutive_up_days", 0)
        if consecutive_up_days >= 5:
            mkt_score -= 10
            mkt_signals.append(f"大盘连涨{consecutive_up_days}天(过热风险)-10")
        elif consecutive_up_days >= 3:
            mkt_score -= 5
            mkt_signals.append(f"大盘连涨{consecutive_up_days}天(谨慎)-5")
        
        consecutive_down_days = extra.get("consecutive_down_days", 0)
        if consecutive_down_days >= 5:
            mkt_score += 8
            mkt_signals.append(f"大盘连跌{consecutive_down_days}天(超跌反弹概率)+8")
        elif consecutive_down_days >= 3:
            mkt_score += 4
            mkt_signals.append(f"大盘连跌{consecutive_down_days}天(关注底部)+4")
        
        # 北向资金连续净流出
        nb_consecutive_outflow = extra.get("nb_consecutive_outflow_days", 0)
        if nb_consecutive_outflow >= 5:
            mkt_score -= 8
            mkt_signals.append(f"北向连续净流出{nb_consecutive_outflow}天(外资撤退)-8")
        elif nb_consecutive_outflow >= 3:
            mkt_score -= 4
            mkt_signals.append(f"北向连续净流出{nb_consecutive_outflow}天(外资谨慎)-4")
        
        mkt_score = max(15, min(85, mkt_score))
    else:
        mkt_score = 50.0
        mkt_signals = ["市场情绪暂无数据(中性)"]

    total = (
        tech.score * w_tech
        + cap.score * w_cap
        + fund["score"] * w_fund
        + sent_score * w_sent
        + mkt_score * w_mkt
    )

    # 防追涨杀跌: 动量惩罚 (涨幅越大, 越可能是追涨)
    momentum_penalty = 0
    chg = abs(quote.change_pct)
    if (quote.change_pct or 0) >= 9.5:
        momentum_penalty = 12
    elif quote.change_pct >= 7:
        momentum_penalty = 6
    elif (quote.change_pct or 0) >= 5:
        momentum_penalty = 3
    elif quote.change_pct <= -9.5:
        momentum_penalty = -8  # 跌停时逆向加分(超跌反弹概率)
    elif (quote.change_pct or 0) <= -7:
        momentum_penalty = -4
    
    if momentum_penalty != 0:
        total -= momentum_penalty  # 涨多扣分, 跌多加分(逆向)
    total = max(10, min(90, total))

    risk_alerts = _detect_risks(quote, tech, cap)
    signal, confidence = _get_signal(total)
    
    # RSI超买时限制最高信号为WATCH
    rsi_val = tech.indicators.get("rsi", 50)
    if rsi_val > 80 and signal in ("STRONG_BUY", "BUY"):
        signal = "WATCH"
        confidence = "中"
        risk_alerts.append(f"RSI={rsi_val:.0f}超买,信号降级为WATCH")
    
    # RSI超卖时保底信号为WATCH
    if rsi_val < 20 and signal in ("STRONG_SELL", "SELL"):
        signal = "WATCH"
        confidence = "中"
        risk_alerts.append(f"RSI={rsi_val:.0f}超卖,可能超跌反弹")

    data_freshness = "fresh"
    if quote.timestamp:
        data_freshness = "fresh"
    elif daily_df is not None and not daily_df.empty:
        data_freshness = "stale"
    else:
        data_freshness = "cached"

    return StockScore(
        code=quote.code,
        name=quote.name,
        price=quote.price,
        change_pct=quote.change_pct,
        total_score=round(total, 1),
        technical={"score": round(tech.score, 1), "signals": tech.signals, "indicators": tech.indicators},
        capital={"score": round(cap.score, 1), "signals": cap.signals, "metrics": cap.metrics},
        fundamental={"score": fund["score"], "signals": fund["signals"], "pe": fund.get("pe", 0), "pb": fund.get("pb", 0)},
        sentiment={"score": sent_score, "signals": sent_signals},
        market={"score": mkt_score, "signals": mkt_signals},
        signal=signal,
        confidence=confidence,
        risk_alerts=risk_alerts,
        data_freshness=data_freshness,
    )


def _detect_risks(quote: QuoteData, tech: TechnicalSignal, cap: CapitalSignal) -> list[str]:
    """Detect risk conditions from combined analysis."""
    alerts = []

    if quote.change_pct >= 9.5:
        alerts.append(f"涨停{quote.change_pct:.1f}%(追高风险)")
    elif quote.change_pct >= 7:
        alerts.append(f"大涨{quote.change_pct:.1f}%(短期回调风险)")
    elif quote.change_pct <= -9.5:
        alerts.append(f"跌停{quote.change_pct:.1f}%(恐慌信号)")
    elif (quote.change_pct or 0) <= -5:
        alerts.append(f"大跌{quote.change_pct:.1f}%(止损关注)")

    rsi = tech.indicators.get("rsi", 50)
    if rsi > 80:
        alerts.append(f"RSI={rsi:.0f}(极度超买)")
    elif rsi < 20:
        alerts.append(f"RSI={rsi:.0f}(极度超卖)")

    vr = cap.metrics.get("volume_ratio", 1)
    if vr > 5 and quote.change_pct > 5:
        alerts.append(f"量比{vr:.1f}+涨幅{quote.change_pct:.1f}%(游资炒作可能)")

    if hasattr(quote, "pe") and (quote.pe or 0) > 100:
        alerts.append(f"PE={quote.pe:.0f}(极高估值风险)")
    if hasattr(quote, "pb") and quote.pb is not None and 0 < quote.pb < 0.8:
        alerts.append(f"PB={quote.pb:.2f}(破净，注意基本面)")

    return alerts
