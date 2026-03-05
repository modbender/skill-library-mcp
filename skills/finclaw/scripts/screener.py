#!/usr/bin/env python3
"""Stock screener for US, BIST, and crypto markets."""

import sys, os, json, argparse
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lib.formatters import fmt_price
from lib.rate_limiter import wait_if_needed

POPULAR_US = ["AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "META", "TSLA", "BRK.B",
              "JPM", "V", "UNH", "MA", "HD", "PG", "XOM"]
POPULAR_BIST = ["THYAO.IS", "GARAN.IS", "AKBNK.IS", "ISCTR.IS", "YKBNK.IS",
                "KCHOL.IS", "SAHOL.IS", "TUPRS.IS", "EREGL.IS", "BIMAS.IS",
                "ASELS.IS", "SISE.IS", "TCELL.IS", "TOASO.IS", "PGSUS.IS"]


def screen_by_change(symbols, direction="top"):
    import yfinance as yf
    results = []
    for sym in symbols:
        try:
            wait_if_needed("yfinance")
            info = yf.Ticker(sym).fast_info
            price, prev = info.last_price, info.previous_close
            if not prev: continue
            results.append({"symbol": sym, "price": round(price, 2),
                            "change_pct": round((price - prev) / prev * 100, 2)})
        except Exception: continue
    results.sort(key=lambda x: x["change_pct"], reverse=(direction == "top"))
    return results


def main():
    parser = argparse.ArgumentParser(description="Stock screener")
    parser.add_argument("market", choices=["us", "bist", "crypto"])
    parser.add_argument("--direction", choices=["top", "bottom"], default="top")
    parser.add_argument("--limit", type=int, default=10)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    if args.market == "crypto":
        from crypto import binance_top_gainers
        results = binance_top_gainers(args.limit)
        if args.json: print(json.dumps(results, indent=2)); return
        print(f"**Top {args.limit} Crypto Gainers (24h)**\n")
        for i, r in enumerate(results, 1):
            s = "+" if r["change_pct"] >= 0 else ""
            print(f"{i}. **{r['symbol']}** — ${r['price']:.2f} ({s}{r['change_pct']:.2f}%)")
        return

    symbols = POPULAR_US if args.market == "us" else POPULAR_BIST
    results = screen_by_change(symbols, args.direction)[:args.limit]
    if args.json: print(json.dumps(results, indent=2)); return
    currency_sym = "$" if args.market == "us" else "₺"
    label = "US" if args.market == "us" else "BIST"
    d = "Gainers" if args.direction == "top" else "Losers"
    print(f"**Top {label} {d}**\n")
    for i, r in enumerate(results, 1):
        s = "+" if r["change_pct"] >= 0 else ""
        a = "▲" if r["change_pct"] >= 0 else "▼"
        print(f"{i}. **{r['symbol']}** — {currency_sym}{r['price']:.2f} {a} {s}{r['change_pct']:.2f}%")


if __name__ == "__main__":
    main()
