#!/usr/bin/env python3
"""Technical analysis: SMA, EMA, RSI, MACD, Bollinger Bands."""

import sys, os, json, argparse
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lib.formatters import detect_asset_type
from lib.rate_limiter import wait_if_needed
import pandas as pd
import numpy as np


def fetch_history(symbol, period="6mo"):
    import yfinance as yf
    asset_type = detect_asset_type(symbol)
    ticker_sym = symbol
    if asset_type == "stock_bist" and not symbol.endswith(".IS"): ticker_sym = symbol + ".IS"
    if asset_type == "crypto": ticker_sym = symbol + "-USD"
    wait_if_needed("yfinance")
    df = yf.Ticker(ticker_sym).history(period=period)
    if df.empty: raise ValueError(f"No data for {ticker_sym}")
    return df


def calc_sma(s, p): return s.rolling(window=p).mean()
def calc_ema(s, p): return s.ewm(span=p, adjust=False).mean()

def calc_rsi(s, p=14):
    delta = s.diff()
    gain = delta.where(delta > 0, 0).rolling(window=p).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=p).mean()
    return 100 - (100 / (1 + gain / loss))

def calc_macd(s, fast=12, slow=26, signal=9):
    ml = calc_ema(s, fast) - calc_ema(s, slow)
    sl = calc_ema(ml, signal)
    return ml, sl, ml - sl

def calc_bollinger(s, p=20, std=2):
    sma = calc_sma(s, p)
    sd = s.rolling(window=p).std()
    return sma + sd * std, sma, sma - sd * std


def analyze(symbol, period="6mo"):
    df = fetch_history(symbol, period)
    close = df["Close"]
    last = close.iloc[-1]
    sma20 = calc_sma(close, 20).iloc[-1]
    sma50 = calc_sma(close, 50).iloc[-1]
    sma200 = calc_sma(close, 200).iloc[-1] if len(close) >= 200 else None
    rsi = calc_rsi(close).iloc[-1]
    macd_l, sig_l, hist = calc_macd(close)
    bb_u, bb_m, bb_l = calc_bollinger(close)

    signals = []
    signals.append(f"Price {'above' if last > sma50 else 'below'} SMA50 ({'bullish' if last > sma50 else 'bearish'})")
    if sma200 is not None:
        signals.append(f"{'Golden' if sma50 > sma200 else 'Death'} cross (SMA50 {'>' if sma50 > sma200 else '<'} SMA200)")
    if rsi > 70: signals.append(f"RSI {rsi:.1f} — Overbought")
    elif rsi < 30: signals.append(f"RSI {rsi:.1f} — Oversold")
    else: signals.append(f"RSI {rsi:.1f} — Neutral")
    signals.append(f"MACD {'bullish' if macd_l.iloc[-1] > sig_l.iloc[-1] else 'bearish'} crossover")

    return {"symbol": symbol, "price": round(last, 2),
            "sma_20": round(sma20, 2), "sma_50": round(sma50, 2),
            "sma_200": round(sma200, 2) if sma200 else None,
            "ema_12": round(calc_ema(close, 12).iloc[-1], 2),
            "ema_26": round(calc_ema(close, 26).iloc[-1], 2),
            "rsi_14": round(rsi, 2), "macd": round(macd_l.iloc[-1], 4),
            "macd_signal": round(sig_l.iloc[-1], 4), "macd_histogram": round(hist.iloc[-1], 4),
            "bb_upper": round(bb_u.iloc[-1], 2), "bb_middle": round(bb_m.iloc[-1], 2),
            "bb_lower": round(bb_l.iloc[-1], 2), "signals": signals}


def format_analysis(d):
    lines = [f"**Technical Analysis: {d['symbol']}**\n", f"Price: {d['price']}",
             f"\n**Moving Averages**", f"  SMA(20): {d['sma_20']}  |  SMA(50): {d['sma_50']}"]
    if d['sma_200']: lines.append(f"  SMA(200): {d['sma_200']}")
    lines += [f"  EMA(12): {d['ema_12']}  |  EMA(26): {d['ema_26']}",
              f"\n**Oscillators**", f"  RSI(14): {d['rsi_14']}",
              f"  MACD: {d['macd']}  |  Signal: {d['macd_signal']}  |  Hist: {d['macd_histogram']}",
              f"\n**Bollinger Bands** (20,2)",
              f"  Upper: {d['bb_upper']}  |  Middle: {d['bb_middle']}  |  Lower: {d['bb_lower']}",
              f"\n**Signals**"] + [f"  • {s}" for s in d["signals"]]
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Technical analysis")
    parser.add_argument("symbol")
    parser.add_argument("--period", default="6mo")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    try:
        r = analyze(args.symbol, args.period)
        print(json.dumps(r, indent=2) if args.json else format_analysis(r))
    except Exception as e:
        print(f"Error: {e}"); sys.exit(1)


if __name__ == "__main__":
    main()
