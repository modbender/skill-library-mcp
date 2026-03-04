"""Technical indicator calculations using pandas-ta."""

from __future__ import annotations

import logging
from dataclasses import dataclass, field

import pandas as pd

logger = logging.getLogger(__name__)


@dataclass
class TechnicalSignal:
    """Result of technical analysis for a single stock."""
    score: float = 0.0
    signals: list[str] = field(default_factory=list)
    indicators: dict = field(default_factory=dict)


def compute_technical(df: pd.DataFrame) -> TechnicalSignal:
    """Compute technical indicators and generate score from daily K-line data.

    Expects columns: date, open, high, low, close, volume.
    Returns: TechnicalSignal with score (0-100), signal descriptions, raw indicators.
    """
    if df is None or len(df) < 20:
        return TechnicalSignal(score=50.0, signals=["数据不足,使用中性评分"])

    try:
        import pandas_ta as ta
    except ImportError:
        logger.warning("pandas-ta not installed, using basic calculations")
        return _compute_basic(df)

    result = TechnicalSignal()
    close = df["close"].astype(float)
    score = 50.0

    # MACD
    try:
        macd = ta.macd(close)
        if macd is not None and not macd.empty:
            macd_val = macd.iloc[-1].get("MACD_12_26_9", 0)
            macd_signal = macd.iloc[-1].get("MACDs_12_26_9", 0)
            macd_hist = macd.iloc[-1].get("MACDh_12_26_9", 0)
            result.indicators["macd"] = round(float(macd_val), 3)
            result.indicators["macd_signal"] = round(float(macd_signal), 3)

            if macd_hist > 0 and (len(macd) < 2 or macd.iloc[-2].get("MACDh_12_26_9", 0) <= 0):
                score += 6
                result.signals.append(f"MACD金叉+6")
            elif macd_hist < 0 and (len(macd) < 2 or macd.iloc[-2].get("MACDh_12_26_9", 0) >= 0):
                score -= 6
                result.signals.append(f"MACD死叉-6")
            elif macd_hist > 0:
                score += 2
                result.signals.append(f"MACD多头+2")
            elif macd_hist < 0:
                score -= 2
                result.signals.append(f"MACD空头-2")
    except Exception as e:
        logger.debug(f"MACD calculation error: {e}")

    # RSI
    try:
        rsi = ta.rsi(close, length=14)
        if rsi is not None and not rsi.empty:
            rsi_val = float(rsi.iloc[-1])
            result.indicators["rsi"] = round(rsi_val, 1)
            if rsi_val > 80:
                score -= 4
                result.signals.append(f"RSI={rsi_val:.0f}超买-4")
            elif rsi_val > 70:
                score -= 2
                result.signals.append(f"RSI={rsi_val:.0f}偏高-2")
            elif rsi_val < 20:
                score += 4
                result.signals.append(f"RSI={rsi_val:.0f}超卖+4")
            elif rsi_val < 30:
                score += 2
                result.signals.append(f"RSI={rsi_val:.0f}偏低+2")
            else:
                result.signals.append(f"RSI={rsi_val:.0f}中性")

            rsi6 = ta.rsi(close, length=6)
            if rsi6 is not None and not rsi6.empty:
                rsi6_val = float(rsi6.iloc[-1])
                result.indicators["rsi6"] = round(rsi6_val, 1)
                if rsi6_val > 85:
                    score -= 2
                    result.signals.append(f"RSI6={rsi6_val:.0f}短线极度超买-2")
                elif rsi6_val < 15:
                    score += 2
                    result.signals.append(f"RSI6={rsi6_val:.0f}短线极度超卖+2")
    except Exception as e:
        logger.debug(f"RSI calculation error: {e}")

    # KDJ
    try:
        stoch = ta.stoch(df["high"].astype(float), df["low"].astype(float), close)
        if stoch is not None and not stoch.empty:
            k = float(stoch.iloc[-1].get("STOCHk_14_3_3", 50))
            d = float(stoch.iloc[-1].get("STOCHd_14_3_3", 50))
            result.indicators["kdj_k"] = round(k, 1)
            result.indicators["kdj_d"] = round(d, 1)
            if k > d and len(stoch) >= 2:
                prev_k = float(stoch.iloc[-2].get("STOCHk_14_3_3", 50))
                prev_d = float(stoch.iloc[-2].get("STOCHd_14_3_3", 50))
                if prev_k <= prev_d:
                    if k > 80:
                        score -= 1
                        result.signals.append(f"KDJ高位金叉(K={k:.0f}>80,钝化)-1")
                    else:
                        score += 4
                        result.signals.append(f"KDJ金叉+4")
                else:
                    if k > 85:
                        result.signals.append(f"KDJ高位钝化(K={k:.0f})")
                    else:
                        score += 1
            elif k < d:
                if k < 20:
                    score += 2
                    result.signals.append(f"KDJ低位死叉(超卖区)+2")
                else:
                    score -= 2
                    result.signals.append(f"KDJ空头-2")
    except Exception as e:
        logger.debug(f"KDJ calculation error: {e}")

    # Moving averages alignment
    try:
        ma5 = close.rolling(5).mean().iloc[-1]
        ma10 = close.rolling(10).mean().iloc[-1]
        ma20 = close.rolling(20).mean().iloc[-1]
        ma60 = close.rolling(60).mean().iloc[-1] if len(close) >= 60 else None
        current = float(close.iloc[-1])

        result.indicators["ma5"] = round(float(ma5), 2)
        result.indicators["ma20"] = round(float(ma20), 2)

        if current > ma5 > ma10 > ma20:
            score += 4
            result.signals.append("均线多头排列+4")
        elif current < ma5 < ma10 < ma20:
            score -= 4
            result.signals.append("均线空头排列-4")

        if current > ma20 and float(close.iloc[-2]) <= float(close.rolling(20).mean().iloc[-2]):
            score += 3
            result.signals.append("突破MA20+3")

        if ma60 is not None:
            result.indicators["ma60"] = round(float(ma60), 2)
            if current > ma60:
                score += 2
                result.signals.append("站上MA60+2")
            else:
                score -= 1
                result.signals.append("低于MA60-1")

        ma120 = close.rolling(120).mean().iloc[-1] if len(close) >= 120 else None
        if ma120 is not None:
            result.indicators["ma120"] = round(float(ma120), 2)
            if current > ma120:
                score += 1
                result.signals.append("站上MA120+1(中长期趋势向好)")
            else:
                score -= 1
                result.signals.append("低于MA120-1(中长期趋势偏弱)")
    except Exception as e:
        logger.debug(f"MA calculation error: {e}")

    # Bollinger Bands position
    try:
        bbands = ta.bbands(close, length=20)
        if bbands is not None and not bbands.empty:
            upper = float(bbands.iloc[-1].get("BBU_20_2.0", 0))
            lower = float(bbands.iloc[-1].get("BBL_20_2.0", 0))
            mid = float(bbands.iloc[-1].get("BBM_20_2.0", 0))
            current = float(close.iloc[-1])
            if upper > lower:
                bb_pos = (current - lower) / (upper - lower)
                result.indicators["bb_position"] = round(bb_pos, 2)
                if bb_pos > 0.95:
                    score -= 3
                    result.signals.append(f"布林上轨压力-3")
                elif bb_pos < 0.05:
                    score += 3
                    result.signals.append(f"布林下轨支撑+3")
    except Exception as e:
        logger.debug(f"Bollinger calculation error: {e}")

    # Volume-Price Pattern Analysis
    try:
        volume = df["volume"].astype(float)
        if len(volume) >= 10:
            avg_vol_10 = volume.rolling(10).mean().iloc[-1]
            current_vol = float(volume.iloc[-1])
            vol_ratio = current_vol / avg_vol_10 if avg_vol_10 > 0 else 1.0
            result.indicators["vol_ratio_10d"] = round(vol_ratio, 2)

            # 近5日价格位置判断
            recent_high = float(df["high"].tail(60).max()) if len(df) >= 60 else float(df["high"].max())
            recent_low = float(df["low"].tail(60).min()) if len(df) >= 60 else float(df["low"].min())
            price_range = recent_high - recent_low
            if price_range > 0:
                price_position = (current - recent_low) / price_range
                result.indicators["price_position_60d"] = round(price_position, 2)

                # 底部放量（价格在60日低位20%以内 + 成交量>1.5倍均量）
                if price_position < 0.2 and vol_ratio > 1.5:
                    score += 5
                    result.signals.append(f"底部放量(位置{price_position:.0%},量比{vol_ratio:.1f})+5")

                # 顶部放量（价格在60日高位80%以上 + 成交量>2倍均量）
                elif price_position > 0.8 and vol_ratio > 2.0:
                    score -= 5
                    result.signals.append(f"顶部放量(位置{price_position:.0%},量比{vol_ratio:.1f})-5(出货风险)")

                # 顶部缩量（价格高位但成交量萎缩）
                elif price_position > 0.8 and vol_ratio < 0.5:
                    score -= 2
                    result.signals.append(f"顶部缩量(位置{price_position:.0%},量比{vol_ratio:.1f})-2(上涨乏力)")

            # 缩量回调（连续3天缩量 + 价格小幅回调 < 5%）
            if len(volume) >= 5:
                recent_3vol = volume.tail(3).values
                prev_3vol = volume.tail(6).head(3).values
                avg_recent = sum(recent_3vol) / 3
                avg_prev = sum(prev_3vol) / 3
                recent_change = float(close.pct_change().tail(3).sum())

                if avg_prev > 0 and avg_recent / avg_prev < 0.6 and -0.05 < recent_change < 0:
                    score += 3
                    result.signals.append(f"缩量回调(量缩{avg_recent/avg_prev:.0%},跌{recent_change:.1%})+3(洗盘)")
    except Exception as e:
        logger.debug(f"Volume-price analysis error: {e}")

    # Consecutive candle pattern
    try:
        if len(df) >= 5:
            opens = df["open"].astype(float).tail(5).values
            closes = close.tail(5).values
            up_count = sum(1 for o, c in zip(opens, closes) if c > o)
            down_count = sum(1 for o, c in zip(opens, closes) if c < o)

            result.indicators["consecutive_up_candles_5d"] = up_count
            result.indicators["consecutive_down_candles_5d"] = down_count

            if up_count >= 4:
                score += 2
                result.signals.append(f"近5日{up_count}阳线+2(强势)")
            elif down_count >= 4:
                score -= 1
                result.signals.append(f"近5日{down_count}阴线-1(弱势)")
    except Exception as e:
        logger.debug(f"Candle pattern error: {e}")

    # Breakout detection
    try:
        if len(df) >= 20:
            prev_20_high = float(df["high"].tail(21).head(20).max())
            prev_20_low = float(df["low"].tail(21).head(20).min())

            if current > prev_20_high:
                score += 3
                result.signals.append(f"突破20日高点{prev_20_high:.2f}+3")
            elif current < prev_20_low:
                score -= 3
                result.signals.append(f"跌破20日低点{prev_20_low:.2f}-3")
    except Exception as e:
        logger.debug(f"Breakout detection error: {e}")

    # Gap detection
    try:
        if len(df) >= 2:
            today_low = float(df["low"].iloc[-1])
            today_high = float(df["high"].iloc[-1])
            yesterday_high = float(df["high"].iloc[-2])
            yesterday_low = float(df["low"].iloc[-2])

            if today_low > yesterday_high:
                gap_pct = (today_low - yesterday_high) / yesterday_high * 100
                if gap_pct > 1:
                    score += 2
                    result.signals.append(f"向上跳空{gap_pct:.1f}%+2")
            elif today_high < yesterday_low:
                gap_pct = (yesterday_low - today_high) / yesterday_low * 100
                if gap_pct > 1:
                    score -= 2
                    result.signals.append(f"向下跳空{gap_pct:.1f}%-2")
    except Exception as e:
        logger.debug(f"Gap detection error: {e}")


    # Fibonacci 0.618 retracement support/resistance
    try:
        if len(df) >= 60:
            high_60 = float(df["high"].tail(60).max())
            low_60 = float(df["low"].tail(60).min())
            fib_range = high_60 - low_60
            if fib_range > 0:
                fib_382 = high_60 - fib_range * 0.382
                fib_500 = high_60 - fib_range * 0.500
                fib_618 = high_60 - fib_range * 0.618
                result.indicators["fib_618"] = round(fib_618, 2)
                result.indicators["fib_382"] = round(fib_382, 2)

                tolerance = fib_range * 0.02

                # Price near 0.618 support (golden ratio retracement)
                if abs(current - fib_618) < tolerance and current > fib_618:
                    rsi_val = result.indicators.get("rsi", 50)
                    if rsi_val < 45:
                        score += 6
                        result.signals.append(f"黄金分割0.618支撑({fib_618:.2f})+RSI低位+6(高胜率)")
                    else:
                        score += 4
                        result.signals.append(f"黄金分割0.618支撑位({fib_618:.2f})+4")
                elif abs(current - fib_382) < tolerance and current < fib_382:
                    score -= 3
                    result.signals.append(f"0.382压力位({fib_382:.2f})-3")

                # Fibonacci extension target
                if current > high_60 * 0.98:
                    fib_1618 = low_60 + fib_range * 1.618
                    result.indicators["fib_1618_target"] = round(fib_1618, 2)
    except Exception as e:
        logger.debug(f"Fibonacci analysis error: {e}")

    # MACD-Price Divergence (top/bottom divergence, very high win rate)
    try:
        if len(df) >= 30:
            macd_full = ta.macd(close)
            if macd_full is not None and len(macd_full) >= 20:
                macd_hist_series = macd_full["MACDh_12_26_9"].astype(float)
                close_10 = close.tail(10).values
                macd_10 = macd_hist_series.tail(10).values

                price_making_low = close_10[-1] < min(close_10[:5])
                macd_making_high = macd_10[-1] > min(macd_10[:5])
                if price_making_low and macd_making_high:
                    score += 5
                    result.signals.append("MACD底背离+5(高胜率反转)")

                price_making_high = close_10[-1] > max(close_10[:5])
                macd_making_low = macd_10[-1] < max(macd_10[:5])
                if price_making_high and macd_making_low:
                    score -= 5
                    result.signals.append("MACD顶背离-5(高胜率见顶)")
    except Exception as e:
        logger.debug(f"MACD divergence error: {e}")

    # Bollinger Band squeeze (low volatility -> breakout imminent)
    try:
        if len(df) >= 20:
            bbands2 = ta.bbands(close, length=20)
            if bbands2 is not None and not bbands2.empty:
                bbu = bbands2["BBU_20_2.0"].astype(float)
                bbl = bbands2["BBL_20_2.0"].astype(float)
                bandwidth = (bbu - bbl) / ((bbu + bbl) / 2) * 100
                bw_current = float(bandwidth.iloc[-1])
                bw_avg = float(bandwidth.tail(20).mean())
                result.indicators["bb_bandwidth"] = round(bw_current, 2)

                if bw_current < bw_avg * 0.5:
                    score += 3
                    result.signals.append(f"布林收口(带宽{bw_current:.1f}%<均值{bw_avg:.1f}%的50%)+3(变盘信号)")
    except Exception as e:
        logger.debug(f"Bollinger squeeze error: {e}")

    # RSI-Price Divergence
    try:
        rsi_full = ta.rsi(close, length=14)
        if rsi_full is not None and len(rsi_full) >= 10:
            rsi_10 = rsi_full.tail(10).values
            close_10_vals = close.tail(10).values

            if close_10_vals[-1] < min(close_10_vals[:5]) and rsi_10[-1] > min(rsi_10[:5]):
                score += 4
                result.signals.append("RSI底背离+4(超卖反转)")
            elif close_10_vals[-1] > max(close_10_vals[:5]) and rsi_10[-1] < max(rsi_10[:5]):
                score -= 4
                result.signals.append("RSI顶背离-4(超买见顶)")
    except Exception as e:
        logger.debug(f"RSI divergence error: {e}")

    # MA golden/death cross (MA5 x MA20)
    try:
        if len(close) >= 22:
            ma5_series = close.rolling(5).mean()
            ma20_series = close.rolling(20).mean()
            if len(ma5_series) >= 2 and len(ma20_series) >= 2:
                today_5 = float(ma5_series.iloc[-1])
                today_20 = float(ma20_series.iloc[-1])
                yest_5 = float(ma5_series.iloc[-2])
                yest_20 = float(ma20_series.iloc[-2])

                if yest_5 <= yest_20 and today_5 > today_20:
                    score += 4
                    result.signals.append("MA5/MA20金叉+4")
                elif yest_5 >= yest_20 and today_5 < today_20:
                    score -= 4
                    result.signals.append("MA5/MA20死叉-4")
    except Exception as e:
        logger.debug(f"MA cross error: {e}")

    # Volume-price confirmation (rising price + rising volume = healthy trend)
    try:
        if len(df) >= 5:
            vol_5 = df["volume"].astype(float).tail(5)
            close_5 = close.tail(5)
            price_up = float(close_5.iloc[-1]) > float(close_5.iloc[0])
            vol_up = float(vol_5.iloc[-1]) > float(vol_5.mean())

            if price_up and vol_up:
                score += 2
                result.signals.append("量价齐升+2(健康上涨)")
            elif price_up and not vol_up:
                score -= 1
                result.signals.append("价升量缩-1(上涨动能不足)")
            elif not price_up and vol_up:
                score -= 2
                result.signals.append("价跌量增-2(恐慌抛售)")
    except Exception as e:
        logger.debug(f"Volume-price confirmation error: {e}")

    # W-bottom pattern (double bottom near same level)
    try:
        if len(df) >= 30:
            lows = df["low"].astype(float).tail(30).values
            mid_idx = len(lows) // 2
            first_low = min(lows[:mid_idx])
            second_low = min(lows[mid_idx:])
            mid_high = max(df["high"].astype(float).tail(30).values[mid_idx-3:mid_idx+3])
            neckline_dist = mid_high - max(first_low, second_low)
            tolerance_w = neckline_dist * 0.05 if neckline_dist > 0 else 0

            if tolerance_w > 0 and abs(first_low - second_low) < neckline_dist * 0.03:
                if current > mid_high:
                    score += 5
                    result.signals.append(f"W底突破颈线{mid_high:.2f}+5(反转)")
                elif current > second_low and current < mid_high:
                    score += 2
                    result.signals.append(f"疑似W底形成中(底{second_low:.2f}颈{mid_high:.2f})+2")
    except Exception as e:
        logger.debug(f"W-bottom detection error: {e}")

    # M-top pattern (double top)
    try:
        if len(df) >= 30:
            highs = df["high"].astype(float).tail(30).values
            mid_idx_m = len(highs) // 2
            first_high = max(highs[:mid_idx_m])
            second_high = max(highs[mid_idx_m:])
            mid_low = min(df["low"].astype(float).tail(30).values[mid_idx_m-3:mid_idx_m+3])
            neckline_dist_m = min(first_high, second_high) - mid_low

            if neckline_dist_m > 0 and abs(first_high - second_high) < neckline_dist_m * 0.03:
                if current < mid_low:
                    score -= 5
                    result.signals.append(f"M顶跌破颈线{mid_low:.2f}-5(反转下跌)")
                elif current < second_high and current > mid_low:
                    score -= 2
                    result.signals.append(f"疑似M顶形成中(顶{second_high:.2f}颈{mid_low:.2f})-2")
    except Exception as e:
        logger.debug(f"M-top detection error: {e}")



    # Vegas Channel (EMA 144/169 - weekly trend channel on daily chart)
    try:
        if len(close) >= 170:
            ema_144 = ta.ema(close, length=144)
            ema_169 = ta.ema(close, length=169)
            if ema_144 is not None and ema_169 is not None:
                ema144_val = float(ema_144.iloc[-1])
                ema169_val = float(ema_169.iloc[-1])
                result.indicators["vegas_ema144"] = round(ema144_val, 2)
                result.indicators["vegas_ema169"] = round(ema169_val, 2)
                channel_width = abs(ema144_val - ema169_val) / ema169_val * 100

                if current > max(ema144_val, ema169_val):
                    score += 3
                    result.signals.append(f"Vegas通道上方+3(中长期多头)")
                elif current < min(ema144_val, ema169_val):
                    score -= 3
                    result.signals.append(f"Vegas通道下方-3(中长期空头)")
                elif min(ema144_val, ema169_val) <= current <= max(ema144_val, ema169_val):
                    result.signals.append(f"Vegas通道内(通道宽{channel_width:.1f}%,观望)")
    except Exception as e:
        logger.debug(f"Vegas channel error: {e}")

    # ATR Volatility (Average True Range)
    try:
        atr = ta.atr(df["high"].astype(float), df["low"].astype(float), close, length=14)
        if atr is not None and not atr.empty:
            atr_val = float(atr.iloc[-1])
            atr_pct = atr_val / float(close.iloc[-1]) * 100
            result.indicators["atr_14"] = round(atr_val, 2)
            result.indicators["atr_pct"] = round(atr_pct, 2)

            atr_avg = float(atr.tail(20).mean())
            if atr_val > atr_avg * 1.5:
                result.signals.append(f"ATR放大({atr_pct:.1f}%,波动加剧)")
            elif atr_val < atr_avg * 0.6:
                result.signals.append(f"ATR收窄({atr_pct:.1f}%,变盘临近)")
    except Exception as e:
        logger.debug(f"ATR calculation error: {e}")

    # Ichimoku Cloud (simplified - tenkan/kijun cross + cloud position)
    try:
        ichimoku = ta.ichimoku(df["high"].astype(float), df["low"].astype(float), close)
        if ichimoku is not None and isinstance(ichimoku, tuple) and len(ichimoku) >= 1:
            ich = ichimoku[0]
            if ich is not None and not ich.empty:
                tenkan = ich.iloc[-1].get("ITS_9", None)
                kijun = ich.iloc[-1].get("IKS_26", None)
                span_a = ich.iloc[-1].get("ISA_9", None)
                span_b = ich.iloc[-1].get("ISB_26", None)

                if all(v is not None for v in [tenkan, kijun, span_a, span_b]):
                    tenkan = float(tenkan)
                    kijun = float(kijun)
                    span_a = float(span_a)
                    span_b = float(span_b)
                    cloud_top = max(span_a, span_b)
                    cloud_bottom = min(span_a, span_b)
                    result.indicators["ichimoku_tenkan"] = round(tenkan, 2)
                    result.indicators["ichimoku_kijun"] = round(kijun, 2)

                    if current > cloud_top and tenkan > kijun:
                        score += 3
                        result.signals.append("一目均衡:云上+转换>基准+3(强势)")
                    elif current < cloud_bottom and tenkan < kijun:
                        score -= 3
                        result.signals.append("一目均衡:云下+转换<基准-3(弱势)")
                    elif cloud_bottom <= current <= cloud_top:
                        result.signals.append("一目均衡:云中(方向不明)")
    except Exception as e:
        logger.debug(f"Ichimoku calculation error: {e}")


    result.score = max(0, min(100, score))
    return result


def _compute_basic(df: pd.DataFrame) -> TechnicalSignal:
    """Fallback: basic calculations without pandas-ta."""
    close = df["close"].astype(float)
    score = 50.0
    signals = []

    ma5 = close.rolling(5).mean().iloc[-1]
    ma20 = close.rolling(20).mean().iloc[-1]
    current = float(close.iloc[-1])

    if current > ma5 > ma20:
        score += 5
        signals.append("均线多头+5")
    elif current < ma5 < ma20:
        score -= 5
        signals.append("均线空头-5")

    changes = close.pct_change().dropna()
    if len(changes) >= 14:
        gains = changes[changes > 0].rolling(14).mean().iloc[-1] if len(changes[changes > 0]) >= 14 else 0
        losses = abs(changes[changes < 0].rolling(14).mean().iloc[-1]) if len(changes[changes < 0]) >= 14 else 1
        rsi = 100 - 100 / (1 + gains / max(losses, 0.001)) if losses else 50
        if rsi > 70:
            score -= 3
            signals.append(f"RSI={rsi:.0f}偏高-3")
        elif rsi < 30:
            score += 3
            signals.append(f"RSI={rsi:.0f}偏低+3")

    return TechnicalSignal(score=max(0, min(100, score)), signals=signals)
