#!/usr/bin/env python3
"""Generate price charts using mplfinance."""

import sys, os, argparse
from datetime import datetime
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lib.formatters import detect_asset_type
from lib.rate_limiter import wait_if_needed
from lib.config import get_skill_dir

import pandas as pd
import matplotlib
matplotlib.use("Agg")
import mplfinance as mpf

CHART_DIR = os.path.join(get_skill_dir(), "data", "charts")


def fetch_history(symbol, period="3mo", interval="1d"):
    import yfinance as yf
    asset_type = detect_asset_type(symbol)
    ticker_sym = symbol
    if asset_type == "stock_bist" and not symbol.endswith(".IS"): ticker_sym = symbol + ".IS"
    if asset_type == "crypto": ticker_sym = symbol + "-USD"
    wait_if_needed("yfinance")
    df = yf.Ticker(ticker_sym).history(period=period, interval=interval)
    if df.empty: raise ValueError(f"No data for {ticker_sym}")
    return df


def generate_candlestick(symbol, period="3mo", interval="1d", volume=True, sma=None):
    df = fetch_history(symbol, period, interval)
    os.makedirs(CHART_DIR, exist_ok=True)
    filename = f"{symbol.replace('/', '_')}_{period}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
    filepath = os.path.join(CHART_DIR, filename)
    mc = mpf.make_marketcolors(up="green", down="red", inherit=True)
    style = mpf.make_mpf_style(marketcolors=mc, gridstyle=":", y_on_right=True)
    add_plots = []
    if sma:
        for p in sma:
            if len(df) >= p:
                add_plots.append(mpf.make_addplot(df["Close"].rolling(window=p).mean(), label=f"SMA{p}"))
    kwargs = {"type": "candle", "style": style, "volume": volume,
              "title": f"\n{symbol} — {period.upper()} ({interval})",
              "figsize": (12, 7), "savefig": filepath}
    if add_plots: kwargs["addplot"] = add_plots
    mpf.plot(df, **kwargs)
    return filepath


def generate_line(symbol, period="1y", interval="1d"):
    df = fetch_history(symbol, period, interval)
    os.makedirs(CHART_DIR, exist_ok=True)
    filename = f"{symbol.replace('/', '_')}_line_{period}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
    filepath = os.path.join(CHART_DIR, filename)
    mc = mpf.make_marketcolors(up="green", down="red", inherit=True)
    style = mpf.make_mpf_style(marketcolors=mc, gridstyle=":")
    mpf.plot(df, type="line", style=style, title=f"\n{symbol} — {period.upper()}",
             figsize=(12, 6), savefig=filepath)
    return filepath


def main():
    parser = argparse.ArgumentParser(description="Generate price charts")
    parser.add_argument("symbol")
    parser.add_argument("--type", choices=["candle", "line"], default="candle")
    parser.add_argument("--period", default="3mo")
    parser.add_argument("--interval", default="1d")
    parser.add_argument("--no-volume", action="store_true")
    parser.add_argument("--sma", nargs="+", type=int)
    args = parser.parse_args()
    try:
        if args.type == "candle":
            path = generate_candlestick(args.symbol, args.period, args.interval,
                                        not args.no_volume, args.sma)
        else:
            path = generate_line(args.symbol, args.period, args.interval)
        print(f"Chart saved: {path}")
    except Exception as e:
        print(f"Error: {e}"); sys.exit(1)


if __name__ == "__main__":
    main()
