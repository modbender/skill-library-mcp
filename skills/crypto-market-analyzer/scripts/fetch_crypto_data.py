#!/usr/bin/env python3
"""
Fetch cryptocurrency data from Binance API.
Supports multiple symbols and intervals.
"""

import requests
import json
import sys
from datetime import datetime, timedelta
from typing import List, Dict, Any

# Binance API endpoints
BASE_URL = "https://api.binance.com"

def fetch_klines(symbol: str, interval: str, limit: int) -> List[List]:
    """
    Fetch kline (candlestick) data from Binance.

    Args:
        symbol: Trading pair (e.g., "BTCUSDT", "ETHUSDT")
        interval: Timeframe (e.g., "1h", "4h", "1d")
        limit: Number of candles to fetch (max 1000)

    Returns:
        List of klines where each kline is:
        [open_time, open, high, low, close, volume, close_time, ...]
    """
    url = f"{BASE_URL}/api/v3/klines"
    params = {
        "symbol": symbol,
        "interval": interval,
        "limit": limit
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data for {symbol}: {e}", file=sys.stderr)
        return []

def calculate_ema(prices: List[float], period: int) -> float:
    """Calculate Exponential Moving Average."""
    if len(prices) < period:
        return None

    multiplier = 2 / (period + 1)
    ema = sum(prices[:period]) / period

    for price in prices[period:]:
        ema = (price - ema) * multiplier + ema

    return ema

def calculate_technical_indicators(klines: List[List]) -> Dict[str, Any]:
    """
    Calculate technical indicators from kline data.

    Returns:
        Dictionary with RSI, MACD, SMAs, EMAs, Bollinger Bands, etc.
    """
    if not klines:
        return {}

    closes = [float(k[4]) for k in klines]
    highs = [float(k[2]) for k in klines]
    lows = [float(k[3]) for k in klines]
    volumes = [float(k[5]) for k in klines]

    # Simple Moving Averages
    sma_20 = sum(closes[-20:]) / 20 if len(closes) >= 20 else None
    sma_50 = sum(closes[-50:]) / 50 if len(closes) >= 50 else None

    # Exponential Moving Averages
    ema_12 = calculate_ema(closes, 12)
    ema_26 = calculate_ema(closes, 26)

    # MACD
    macd = (ema_12 - ema_26) if ema_12 and ema_26 else None

    # MACD Signal (9-period EMA of MACD)
    if macd and len(closes) >= 26 + 9:
        # Calculate MACD history for signal line
        macd_history = []
        for i in range(26, len(closes)):
            ema_12_i = calculate_ema(closes[:i+1], 12)
            ema_26_i = calculate_ema(closes[:i+1], 26)
            if ema_12_i and ema_26_i:
                macd_history.append(ema_12_i - ema_26_i)

        if len(macd_history) >= 9:
            macd_signal = calculate_ema(macd_history, 9)
            macd_histogram = macd - macd_signal
        else:
            macd_signal = None
            macd_histogram = None
    else:
        macd_signal = None
        macd_histogram = None

    # RSI (Relative Strength Index) - 14 period
    def calculate_rsi(prices: List[float], period: int = 14) -> float:
        if len(prices) < period + 1:
            return None

        gains = []
        losses = []

        for i in range(1, len(prices)):
            change = prices[i] - prices[i-1]
            gains.append(max(change, 0))
            losses.append(abs(min(change, 0)))

        avg_gain = sum(gains[-period:]) / period
        avg_loss = sum(losses[-period:]) / period

        if avg_loss == 0:
            return 100

        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        return rsi

    rsi = calculate_rsi(closes)

    # Bollinger Bands (20-period, 2 standard deviations)
    if len(closes) >= 20:
        bb_middle = sma_20
        bb_std = (sum([(x - bb_middle) ** 2 for x in closes[-20:]]) / 20) ** 0.5
        bb_upper = bb_middle + (2 * bb_std)
        bb_lower = bb_middle - (2 * bb_std)
        bb_width = ((bb_upper - bb_lower) / bb_middle) * 100
    else:
        bb_middle = None
        bb_upper = None
        bb_lower = None
        bb_width = None

    # Support and Resistance (recent lows and highs)
    recent_lows = sorted(lows[-20:])[:5]
    recent_highs = sorted(highs[-20:], reverse=True)[:5]

    support = sum(recent_lows) / len(recent_lows) if recent_lows else None
    resistance = sum(recent_highs) / len(recent_highs) if recent_highs else None

    # Volume Analysis
    avg_volume = sum(volumes[-20:]) / 20 if len(volumes) >= 20 else None
    current_volume = volumes[-1] if volumes else None
    volume_ratio = (current_volume / avg_volume) if avg_volume and current_volume else None

    return {
        "current_price": closes[-1],
        "sma_20": sma_20,
        "sma_50": sma_50,
        "ema_12": ema_12,
        "ema_26": ema_26,
        "macd": macd,
        "macd_signal": macd_signal,
        "macd_histogram": macd_histogram,
        "rsi": rsi,
        "bb_upper": bb_upper,
        "bb_middle": bb_middle,
        "bb_lower": bb_lower,
        "bb_width": bb_width,
        "support": support,
        "resistance": resistance,
        "volume_ratio": volume_ratio
    }

def get_indicator_explanation(indicators: Dict[str, Any]) -> Dict[str, str]:
    """Generate beginner-friendly explanations for each indicator."""
    explanations = {}

    # RSI Explanation
    rsi = indicators.get("rsi")
    if rsi:
        if rsi < 30:
            explanations["rsi"] = f"RSI是{rsi:.1f}，低于30，说明市场超卖了。简单说就是跌太多了，可能会反弹，像弹簧被压到底要弹起来一样。"
        elif rsi > 70:
            explanations["rsi"] = f"RSI是{rsi:.1f}，高于70，说明市场超买了。简单说就是涨太多了，可能会回调，像气球吹太大会漏气一样。"
        elif rsi > 50:
            explanations["rsi"] = f"RSI是{rsi:.1f}，在50以上，说明多头力量占优势，买方比卖方积极。"
        else:
            explanations["rsi"] = f"RSI是{rsi:.1f}，在50以下，说明空头力量占优势，卖方比买方积极。"

    # Moving Averages Explanation
    sma_20 = indicators.get("sma_20")
    sma_50 = indicators.get("sma_50")
    current_price = indicators.get("current_price")

    if sma_20 and current_price:
        if current_price > sma_20:
            explanations["sma_20"] = f"价格在20日均线(${sma_20:,.2f})上方，说明短期趋势向上，最近20天买家占上风。"
        else:
            explanations["sma_20"] = f"价格在20日均线(${sma_20:,.2f})下方，说明短期趋势向下，最近20天卖家占上风。"

    if sma_50 and current_price:
        if current_price > sma_50:
            explanations["sma_50"] = f"价格在50日均线(${sma_50:,.2f})上方，说明中期趋势向上，最近50天整体是涨的。"
        else:
            explanations["sma_50"] = f"价格在50日均线(${sma_50:,.2f})下方，说明中期趋势向下，最近50天整体是跌的。"

    # MACD Explanation
    macd = indicators.get("macd")
    macd_signal = indicators.get("macd_signal")
    macd_histogram = indicators.get("macd_histogram")

    if macd and macd_histogram:
        if macd > 0 and macd_histogram > 0:
            explanations["macd"] = f"MACD线({macd:.2f})在零轴上方，且柱状图为正，说明多头动能强劲，上涨趋势还在。"
        elif macd < 0 and macd_histogram < 0:
            explanations["macd"] = f"MACD线({macd:.2f})在零轴下方，且柱状图为负，说明空头动能强劲，下跌趋势还在。"
        elif macd > 0 and macd_histogram < 0:
            explanations["macd"] = f"MACD线({macd:.2f})在零轴上方但柱状图转负，说明上涨动能减弱，可能要回调。"
        elif macd < 0 and macd_histogram > 0:
            explanations["macd"] = f"MACD线({macd:.2f})在零轴下方但柱状图转正，说明下跌动能减弱，可能要反弹。"

    # Bollinger Bands Explanation
    bb_upper = indicators.get("bb_upper")
    bb_lower = indicators.get("bb_lower")
    bb_width = indicators.get("bb_width")

    if bb_upper and bb_lower and current_price:
        if current_price > bb_upper:
            explanations["bb"] = f"价格突破了布林带上轨(${bb_upper:,.2f})，说明涨得很猛，但也可能要回调了。"
        elif current_price < bb_lower:
            explanations["bb"] = f"价格跌破了布林带下轨(${bb_lower:,.2f})，说明跌得很猛，但也可能要反弹了。"
        else:
            explanations["bb"] = f"价格在布林带中间区域(${bb_lower:,.2f} - ${bb_upper:,.2f})，属于正常波动范围。"

    if bb_width:
        if bb_width < 2:
            explanations["bb_width"] = f"布林带宽度{bb_width:.2f}%很窄，说明波动很小，市场在横盘整理，可能要变盘了。"
        elif bb_width > 10:
            explanations["bb_width"] = f"布林带宽度{bb_width:.2f}%很宽，说明波动很大，市场很活跃，风险也高。"
        else:
            explanations["bb_width"] = f"布林带宽度{bb_width:.2f}%，波动适中。"

    # Volume Explanation
    volume_ratio = indicators.get("volume_ratio")
    if volume_ratio:
        if volume_ratio > 2:
            explanations["volume"] = f"成交量是平均值的{volume_ratio:.1f}倍，说明今天交易很活跃，有大量资金进出，可能是大行情的前兆。"
        elif volume_ratio < 0.5:
            explanations["volume"] = f"成交量只有平均值的{volume_ratio:.1f}倍，说明交易很清淡，市场在观望，没什么人买卖。"
        else:
            explanations["volume"] = f"成交量是平均值的{volume_ratio:.1f}倍，交易活跃度正常。"

    # Support/Resistance Explanation
    support = indicators.get("support")
    resistance = indicators.get("resistance")

    if support and current_price:
        distance_to_support = ((current_price - support) / current_price) * 100
        if distance_to_support < 5:
            explanations["support"] = f"价格离支撑位(${support:,.2f})很近（{distance_to_support:.2f}%），如果跌破可能会加速下跌，如果能守住可能会反弹。"
        else:
            explanations["support"] = f"支撑位在${support:,.2f}，这是最近20天的低点区域，价格跌到这里可能会有买盘托底。"

    if resistance and current_price:
        distance_to_resistance = ((resistance - current_price) / current_price) * 100
        if distance_to_resistance < 5:
            explanations["resistance"] = f"价格离阻力位(${resistance:,.2f})很近（{distance_to_resistance:.2f}%），如果能突破可能会加速上涨，如果突破不了可能会回调。"
        else:
            explanations["resistance"] = f"阻力位在${resistance:,.2f}，这是最近20天的高点区域，价格涨到这里可能会有卖盘压制。"

    return explanations

def analyze_sentiment(indicators: Dict[str, Any]) -> Dict[str, Any]:
    """
    Analyze market sentiment based on technical indicators.

    Returns:
        Dictionary with sentiment analysis
    """
    if not indicators:
        return {"sentiment": "N/A", "confidence": 0, "reasons": []}

    reasons = []
    bullish_signals = 0
    bearish_signals = 0

    # RSI Analysis
    rsi = indicators.get("rsi")
    if rsi:
        if rsi < 30:
            reasons.append(f"RSI ({rsi:.1f}) indicates oversold - potential bounce")
            bullish_signals += 1
        elif rsi > 70:
            reasons.append(f"RSI ({rsi:.1f}) indicates overbought - potential pullback")
            bearish_signals += 1
        elif rsi > 50:
            reasons.append(f"RSI ({rsi:.1f}) shows bullish momentum")
            bullish_signals += 0.5
        else:
            reasons.append(f"RSI ({rsi:.1f}) shows bearish momentum")
            bearish_signals += 0.5

    # Moving Average Analysis
    sma_20 = indicators.get("sma_20")
    sma_50 = indicators.get("sma_50")
    current_price = indicators.get("current_price")

    if sma_20 and sma_50 and current_price:
        if current_price > sma_20 > sma_50:
            reasons.append(f"Price above both SMAs (20d and 50d) - bullish trend")
            bullish_signals += 1
        elif current_price < sma_20 < sma_50:
            reasons.append(f"Price below both SMAs (20d and 50d) - bearish trend")
            bearish_signals += 1
        elif current_price > sma_20:
            reasons.append(f"Price above 20d SMA - short-term bullish")
            bullish_signals += 0.5
        else:
            reasons.append(f"Price below 20d SMA - short-term bearish")
            bearish_signals += 0.5

    # MACD Analysis
    macd = indicators.get("macd")
    macd_histogram = indicators.get("macd_histogram")
    if macd and macd_histogram:
        if macd > 0 and macd_histogram > 0:
            reasons.append("MACD bullish - strong upward momentum")
            bullish_signals += 1
        elif macd < 0 and macd_histogram < 0:
            reasons.append("MACD bearish - strong downward momentum")
            bearish_signals += 1
        elif macd > 0 and macd_histogram < 0:
            reasons.append("MACD weakening - potential reversal")
            bearishr_signals += 0.5
        elif macd < 0 and macd_histogram > 0:
            reasons.append("MACD strengthening - potential reversal")
            bullish_signals += 0.5

    # Bollinger Bands Analysis
    bb_upper = indicators.get("bb_upper")
    bb_lower = indicators.get("bb_lower")
    if bb_upper and bb_lower and current_price:
        if current_price > bb_upper:
            reasons.append("Price above upper BB - overextended")
            bearish_signals += 0.5
        elif current_price < bb_lower:
            reasons.append("Price below lower BB - oversold")
            bullish_signals += 0.5

    # Price Change Analysis (use 4h data for 24h change)
    change_24h = indicators.get("price_change_4h_24h")
    if change_24h:
        if change_24h > 5:
            reasons.append(f"Strong 24h gain ({change_24h:.2f}%) - bullish")
            bullish_signals += 1
        elif change_24h < -5:
            reasons.append(f"Strong 24h drop ({change_24h:.2f}%) - bearish")
            bearish_signals += 1

    # Determine overall sentiment
    total_signals = bullish_signals + bearish_signals
    if total_signals == 0:
        sentiment = "Neutral"
        confidence = 0.3
    elif bullish_signals > bearish_signals:
        sentiment = "Bullish (看涨)"
        confidence = min(bullish_signals / total_signals + 0.3, 0.9)
    elif bearish_signals > bullish_signals:
        sentiment = "Bearish (看跌)"
        confidence = min(bearish_signals / total_signals + 0.3, 0.9)
    else:
        sentiment = "Neutral (中性)"
        confidence = 0.5

    return {
        "sentiment": sentiment,
        "confidence": confidence,
        "reasons": reasons
    }

def get_reference_explanations() -> Dict[str, str]:
    """Get reference explanations for all indicators."""
    return {
        "RSI": "相对强弱指标，衡量价格涨跌的力度。0-100之间，低于30表示超卖（可能反弹），高于70表示超买（可能回调），50是中位线。",
        "SMA": "简单移动平均线，计算一定周期内的平均价格。20日线看短期趋势，50日线看中期趋势。价格在均线上方是多头，下方是空头。",
        "EMA": "指数移动平均线，比SMA对近期价格更敏感，反应更快。12日和26日EMA用于计算MACD。",
        "MACD": "指数平滑异同移动平均线，由快线（12日EMA）、慢线（26日EMA）和信号线（9日EMA）组成。MACD线在零轴上方是多头，下方是空头。柱状图反映快慢线差值，正值扩大表示上涨动能增强，负值扩大表示下跌动能增强。",
        "Bollinger Bands": "布林带，由中轨（20日SMA）、上轨（中轨+2倍标准差）、下轨（中轨-2倍标准差）组成。价格触及上轨可能超买，触及下轨可能超卖。带宽反映波动性，带宽窄表示横盘，带宽宽表示波动大。",
        "支撑位": "价格下跌时遇到的买盘支撑区域，价格跌到这里可能会有反弹。通常是近期低点的平均值。",
        "阻力位": "价格上涨时遇到的卖盘压制区域，价格涨到这里可能会回调。通常是近期高点的平均值。",
        "成交量": "一定时间内的交易量。成交量放大表示市场活跃，有大量资金进出；成交量缩小表示市场清淡。价格配合成交量变化更有意义。"
    }

def main():
    """Main function to fetch and analyze crypto data."""
    symbols = ["BTCUSDT", "ETHUSDT"]

    # Fetch 4h data (last 24h = 6 candles)
    # Fetch 1d data (last 30 days = 30 candles)
    results = {}

    for symbol in symbols:
        # Fetch 4h data (for 24h price change)
        klines_4h = fetch_klines(symbol, "4h", 6)

        # Fetch 1d data (for technical indicators)
        klines_1d = fetch_klines(symbol, "1d", 30)

        # Use 1d data for technical indicators (more reliable)
        indicators = calculate_technical_indicators(klines_1d)

        # Calculate 24h price change from 4h data
        if klines_4h and len(klines_4h) >= 6:
            closes_4h = [float(k[4]) for k in klines_4h]
            price_change_24h = ((closes_4h[-1] - closes_4h[0]) / closes_4h[0] * 100)
            indicators["price_change_4h_24h"] = price_change_24h
        else:
            indicators["price_change_4h_24h"] = None

        # Calculate 7d price change from 1d data
        # Need at least 8 candles: today (-1) and 7 days ago (-8)
        if klines_1d and len(klines_1d) >= 8:
            closes_1d = [float(k[4]) for k in klines_1d]
            price_change_7d = ((closes_1d[-1] - closes_1d[-8]) / closes_1d[-8] * 100)
            indicators["price_change_7d"] = price_change_7d
        else:
            indicators["price_change_7d"] = None

        sentiment = analyze_sentiment(indicators)
        explanations = get_indicator_explanation(indicators)

        results[symbol] = {
            "indicators": indicators,
            "sentiment": sentiment,
            "explanations": explanations,
            "timestamp": datetime.now().isoformat()
        }

    # Output as JSON
    print(json.dumps(results, indent=2))

if __name__ == "__main__":
    main()
