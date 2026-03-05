"""Capital flow analysis — volume/turnover/bid-ask based scoring."""

from __future__ import annotations

import logging
from dataclasses import dataclass, field

from data_sources.base import QuoteData

logger = logging.getLogger(__name__)


@dataclass
class CapitalSignal:
    """Capital flow analysis result."""
    score: float = 50.0
    signals: list[str] = field(default_factory=list)
    metrics: dict = field(default_factory=dict)


def compute_capital(quote: QuoteData, avg_volume: float = 0, avg_amount: float = 0, main_force_data: dict = None) -> CapitalSignal:
    """Compute capital flow score from real-time quote data.

    Uses volume ratio, turnover rate, bid-ask spread, and amount anomaly.
    avg_volume/avg_amount: 5-day average for comparison.
    
    Args:
        main_force_data: 主力资金数据 (来自主力接口)
            {
                "main_net_inflow_wan": -10653,  # 主力净流入 (万)
                "super_big_net_wan": -15104,    # 超大单
                "big_net_wan": 4451,            # 大单
                "signal": "主力流出"
            }
    """
    score = 50.0
    signals = []
    metrics = {}

    # Volume ratio (量比)
    vr = quote.volume_ratio
    if vr > 0:
        metrics["volume_ratio"] = round(vr, 2)
        if vr > 5:
            score += 8
            signals.append(f"量比{vr:.1f}极度放量+8")
        elif vr > 3:
            score += 5
            signals.append(f"量比{vr:.1f}显著放量+5")
        elif vr > 1.5:
            score += 2
            signals.append(f"量比{vr:.1f}温和放量+2")
        elif vr < 0.5:
            score -= 3
            signals.append(f"量比{vr:.1f}缩量-3")

    # Turnover rate (换手率)
    tr = quote.turnover_rate
    if tr > 0:
        metrics["turnover_rate"] = round(tr, 2)
        if tr > 15:
            score += 3
            signals.append(f"换手率{tr:.1f}%高度活跃+3")
        elif tr > 8:
            score += 1
            signals.append(f"换手率{tr:.1f}%活跃+1")
        elif tr < 1:
            score -= 2
            signals.append(f"换手率{tr:.1f}%低迷-2")

    # Amount comparison (成交额对比)
    if avg_amount > 0 and quote.amount > 0:
        amount_ratio = quote.amount / avg_amount
        metrics["amount_ratio"] = round(amount_ratio, 2)
        if amount_ratio > 3:
            score += 5
            signals.append(f"成交额{amount_ratio:.1f}倍均值+5")
        elif amount_ratio > 1.5:
            score += 2
            signals.append(f"成交额{amount_ratio:.1f}倍均值+2")
        elif amount_ratio < 0.5:
            score -= 2
            signals.append(f"成交额仅{amount_ratio:.1f}倍均值-2")

    # Bid-ask pressure (买卖压力)
    if quote.bid1 > 0 and quote.ask1 > 0:
        spread = (quote.ask1 - quote.bid1) / quote.bid1 * 100
        metrics["spread_pct"] = round(spread, 3)
        if spread < 0.05:
            score += 2
            signals.append("买卖价差极窄 (流动性好)+2")

    # Price-volume divergence: price up but volume down => warning
    if quote.change_pct > 2 and vr > 0 and vr < 0.8:
        score -= 4
        signals.append(f"涨{quote.change_pct:.1f}%但缩量 (量价背离)-4")
    elif quote.change_pct < -2 and vr > 3:
        score -= 3
        signals.append(f"跌{quote.change_pct:.1f}%且放量 (资金出逃)-3")

    # 量比 + 方向修正：放量上涨谨慎，放量下跌警惕
    if quote.volume_ratio > 2:
        if quote.change_pct > 3:
            score -= 3
            signals.append(f"放量大涨 (量比{quote.volume_ratio:.1f})-3(追高风险)")
        elif quote.change_pct < -3:
            score -= 5
            signals.append(f"放量大跌 (量比{quote.volume_ratio:.1f})-5(出逃信号)")
        elif quote.change_pct > 1:
            signals.append(f"放量上涨 (量比{quote.volume_ratio:.1f},温和)")

    # 主力资金净流入 (新增)
    if main_force_data and "error" not in main_force_data:
        main_net = main_force_data.get("main_net_inflow_wan", 0)
        super_big = main_force_data.get("super_big_net_wan", 0)
        big = main_force_data.get("big_net_wan", 0)
        signal = main_force_data.get("signal", "")
        source = main_force_data.get("source", "unknown")
        
        metrics["main_net_inflow_wan"] = round(main_net, 2)
        metrics["super_big_net_wan"] = round(super_big, 2)
        metrics["big_net_wan"] = round(big, 2)
        metrics["main_force_source"] = source
        
        # 主力净流入评分
        if main_net > 50000:  # >5 亿
            score += 15
            signals.append(f"主力巨额流入+{main_net/10000:.2f}亿+15[{source}]")
        elif main_net > 5000:  # >5000 万
            score += 10
            signals.append(f"主力大幅流入+{main_net/10000:.2f}亿+10[{source}]")
        elif main_net > 1000:  # >1000 万
            score += 5
            signals.append(f"主力流入+{main_net/10000:.2f}亿+5[{source}]")
        elif main_net < -50000:
            score -= 15
            signals.append(f"主力巨额流出{main_net/10000:.2f}亿-15[{source}]")
        elif main_net < -5000:
            score -= 10
            signals.append(f"主力大幅流出{main_net/10000:.2f}亿-10[{source}]")
        elif main_net < -1000:
            score -= 5
            signals.append(f"主力流出{main_net/10000:.2f}亿-5[{source}]")
        else:
            signals.append(f"主力中性 ({main_net/10000:.2f}亿)[{source}]")
        
        # 超大单修正
        if super_big > 3000:
            score += 3
            signals.append(f"超大单流入+{super_big/10000:.2f}亿+3[{source}]")
        elif super_big < -3000:
            score -= 3
            signals.append(f"超大单流出{super_big/10000:.2f}亿-3[{source}]")
    # 腾讯内外盘差作为主力替代信号
    elif hasattr(quote, 'outer_vol') and hasattr(quote, 'inner_vol'):
        outer_vol = getattr(quote, 'outer_vol', 0) or 0
        inner_vol = getattr(quote, 'inner_vol', 0) or 0
        
        if outer_vol > 0 or inner_vol > 0:
            outer_inner_diff = outer_vol - inner_vol  # 手
            metrics["outer_vol"] = int(outer_vol)
            metrics["inner_vol"] = int(inner_vol)
            metrics["outer_inner_diff"] = int(outer_inner_diff)
            metrics["main_force_source"] = "tencent_outer_inner"
            
            # 内外盘差评分映射 (考虑量比修正)
            base_score = 0
            if outer_inner_diff > 100000:  # >10 万手
                base_score = 8
                signals.append(f"外盘强势 +{outer_inner_diff/10000:.1f}万手+8[腾讯]")
            elif outer_inner_diff > 50000:  # >5 万手
                base_score = 5
                signals.append(f"外盘偏强 +{outer_inner_diff/10000:.1f}万手+5[腾讯]")
            elif outer_inner_diff < -100000:
                base_score = -8
                signals.append(f"内盘强势 {outer_inner_diff/10000:.1f}万手 -8[腾讯]")
            elif outer_inner_diff < -50000:
                base_score = -5
                signals.append(f"内盘偏强 {outer_inner_diff/10000:.1f}万手 -5[腾讯]")
            else:
                signals.append(f"内外盘平衡 (差{outer_inner_diff/10000:.1f}万手)[腾讯]")
            
            # 量比修正 (放量更可信)
            if quote.volume_ratio > 3:
                base_score = int(base_score * 1.3)
                signals.append(f"显著放量，可信度 +30%")
            elif quote.volume_ratio > 1.5:
                base_score = int(base_score * 1.1)
                signals.append(f"温和放量，可信度 +10%")
            elif quote.volume_ratio < 0.8:
                base_score = int(base_score * 0.7)
                signals.append(f"缩量，可信度 -30%")
            
            score += base_score
        else:
            metrics["main_force_source"] = "missing"
            signals.append("主力资金数据缺失 (东方财富不稳定，AKShare 未安装)")
    else:
        # 主力数据缺失，标注数据来源状态
        metrics["main_force_source"] = "missing"
        signals.append("主力资金数据缺失 (东方财富不稳定，AKShare 未安装)")

    return CapitalSignal(
        score=max(0, min(100, score)),
        signals=signals,
        metrics=metrics,
    )
