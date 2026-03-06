"""Trend Following Strategy (MA Crossover + RSI + MACD)"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from logger import get_logger
from okx_client import OKXClient

log = get_logger("okx.trend")


def sma(prices: list, n: int) -> float:
    return sum(prices[-n:]) / n if len(prices) >= n else 0.0


def ema(prices: list, n: int) -> float:
    if len(prices) < n:
        return 0.0
    k = 2 / (n + 1)
    result = sum(prices[:n]) / n
    for p in prices[n:]:
        result = p * k + result * (1 - k)
    return result


def rsi(prices: list, n: int = 14) -> float:
    if len(prices) < n + 1:
        return 50.0
    deltas = [prices[i] - prices[i - 1] for i in range(1, len(prices))]
    gains = [max(d, 0) for d in deltas]
    losses = [max(-d, 0) for d in deltas]
    avg_gain = sum(gains[:n]) / n
    avg_loss = sum(losses[:n]) / n
    for g, l in zip(gains[n:], losses[n:]):
        avg_gain = (avg_gain * (n - 1) + g) / n
        avg_loss = (avg_loss * (n - 1) + l) / n
    if avg_loss == 0:
        return 100.0
    return 100 - (100 / (1 + avg_gain / avg_loss))


def macd(prices: list, fast: int = 12, slow: int = 26, signal: int = 9) -> tuple[float, float, float]:
    if len(prices) < slow:
        return 0.0, 0.0, 0.0
    kf = 2 / (fast + 1)
    ks = 2 / (slow + 1)
    # Seed fast EMA with SMA of first `fast` bars, then advance to position `slow`
    ema_fast = sum(prices[:fast]) / fast
    for p in prices[fast:slow]:
        ema_fast = p * kf + ema_fast * (1 - kf)
    # Seed slow EMA with SMA of first `slow` bars
    ema_slow = sum(prices[:slow]) / slow
    # Build MACD line history incrementally — O(n) instead of O(n²)
    macd_history = [ema_fast - ema_slow]
    for p in prices[slow:]:
        ema_fast = p * kf + ema_fast * (1 - kf)
        ema_slow = p * ks + ema_slow * (1 - ks)
        macd_history.append(ema_fast - ema_slow)
    macd_line = ema_fast - ema_slow
    signal_line = ema(macd_history, signal) if len(macd_history) >= signal else macd_line
    histogram = macd_line - signal_line
    return macd_line, signal_line, histogram


def analyze(inst_id: str, bar: str = "1H", fast_ma: int = 20,
            slow_ma: int = 50, rsi_period: int = 14) -> dict:
    client = OKXClient()
    candles_data = client.candles(inst_id, bar=bar, limit=100)
    if candles_data.get("code") != "0":
        return {"error": candles_data.get("msg")}

    # OKX candles: [ts, open, high, low, close, vol, volCcy, volCcyQuote, confirm]
    candles = candles_data["data"]
    prices = [float(c[4]) for c in reversed(candles)]  # close prices, oldest first

    current = prices[-1]
    fast = sma(prices, fast_ma)
    slow = sma(prices, slow_ma)
    rsi_val = rsi(prices, rsi_period)
    macd_line, signal_line, histogram = macd(prices)

    # Signal logic
    signal = "hold"
    reasons = []

    if fast > slow:
        reasons.append(f"MA{fast_ma}({fast:.2f}) > MA{slow_ma}({slow:.2f}) ✅")
        if rsi_val < 70:
            reasons.append(f"RSI({rsi_val:.1f}) not overbought ✅")
            if histogram > 0:
                reasons.append(f"MACD histogram positive ✅")
                signal = "buy"
            else:
                reasons.append(f"MACD histogram negative ⚠️")
        else:
            reasons.append(f"RSI({rsi_val:.1f}) overbought ⚠️")
    elif fast < slow:
        reasons.append(f"MA{fast_ma}({fast:.2f}) < MA{slow_ma}({slow:.2f}) ❌")
        if rsi_val > 30:
            reasons.append(f"RSI({rsi_val:.1f}) not oversold ✅")
            if histogram < 0:
                reasons.append(f"MACD histogram negative ✅")
                signal = "sell"

    if signal == "buy":
        market_regime = "strong_bull" if rsi_val < 40 and histogram > 0 else "weak_bull"
    elif signal == "sell":
        market_regime = "strong_bear" if rsi_val > 60 and histogram < 0 else "weak_bear"
    else:
        market_regime = "ranging"

    result = {
        "inst_id": inst_id,
        "bar": bar,
        "current_price": current,
        "ma_fast": round(fast, 4),
        "ma_slow": round(slow, 4),
        "rsi": round(rsi_val, 2),
        "macd_line": round(macd_line, 4),
        "macd_signal": round(signal_line, 4),
        "macd_histogram": round(histogram, 4),
        "signal": signal,
        "market_regime": market_regime,
        "reasons": reasons,
    }
    return result


def run(inst_id: str, sz: str, td_mode: str = "cash", pos_side: str = "",
        bar: str = "1H", tp_pct: float = 0.05, sl_pct: float = 0.03,
        dry_run: bool = False) -> None:
    result = analyze(inst_id, bar)
    if "error" in result:
        log.error(f"Error: {result['error']}")
        return

    log.info(f"\n{'='*50}")
    log.info(f"Trend Analysis: {inst_id} [{bar}]")
    log.info(f"Price: {result['current_price']:.4f}")
    log.info(f"MA20: {result['ma_fast']:.4f} | MA50: {result['ma_slow']:.4f}")
    log.info(f"RSI: {result['rsi']:.2f} | MACD: {result['macd_histogram']:.4f}")
    log.info(f"\nSignal: {'🟢 BUY' if result['signal']=='buy' else '🔴 SELL' if result['signal']=='sell' else '⚪ HOLD'}")
    for r in result["reasons"]:
        log.info(f"  {r}")

    if dry_run or result["signal"] == "hold":
        return

    from execute import place_order
    current = result["current_price"]
    if result["signal"] == "buy":
        tp = str(round(current * (1 + tp_pct), 4))
        sl = str(round(current * (1 - sl_pct), 4))
        log.info(f"\n→ Placing BUY | TP: {tp} | SL: {sl}")
        place_order(inst_id, "buy", "market", sz, td_mode, pos_side=pos_side, tp=tp, sl=sl)
    elif result["signal"] == "sell":
        tp = str(round(current * (1 - tp_pct), 4))
        sl = str(round(current * (1 + sl_pct), 4))
        log.info(f"\n→ Placing SELL | TP: {tp} | SL: {sl}")
        place_order(inst_id, "sell", "market", sz, td_mode, pos_side=pos_side, tp=tp, sl=sl)


if __name__ == "__main__":
    """
    Usage:
      python trend.py analyze BTC-USDT --bar 1H
      python trend.py run BTC-USDT 0.01 --bar 4H --tp 0.05 --sl 0.03
      python trend.py run BTC-USDT-SWAP 1 --td cross --pos long --bar 1H --dry
    """
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("cmd", choices=["analyze", "run"])
    parser.add_argument("inst_id")
    parser.add_argument("sz", nargs="?", default="0.01")
    parser.add_argument("--bar", default="1H")
    parser.add_argument("--td", default="cash")
    parser.add_argument("--pos", default="")
    parser.add_argument("--tp", type=float, default=0.05)
    parser.add_argument("--sl", type=float, default=0.03)
    parser.add_argument("--dry", action="store_true")
    args = parser.parse_args()

    if args.cmd == "analyze":
        result = analyze(args.inst_id, args.bar)
        print(json.dumps(result, indent=2))
    else:
        run(args.inst_id, args.sz, args.td, args.pos, args.bar, args.tp, args.sl, args.dry)
