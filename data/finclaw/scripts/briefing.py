#!/usr/bin/env python3
"""Generate daily market briefings."""

import sys, os, hashlib, argparse
from datetime import datetime
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lib.db import get_connection
from lib.formatters import fmt_price
from scripts.quote import get_quote


def market_snapshot():
    symbols = {"S&P 500": "SPY", "Nasdaq": "QQQ", "BIST 100": "XU100.IS",
               "BTC": "BTC", "ETH": "ETH", "USD/TRY": "USD/TRY", "EUR/USD": "EUR/USD", "Gold": "GLD"}
    snap = {}
    for label, sym in symbols.items():
        try:
            q = get_quote(sym, force=True)
            snap[label] = {"price": q["price"], "change_pct": q.get("change_pct"), "currency": q.get("currency", "USD")}
        except: snap[label] = {"error": True}
    return snap


def portfolio_snapshot():
    conn = get_connection()
    try:
        positions = conn.execute("SELECT * FROM positions").fetchall()
        result = []
        for p in positions:
            b = conn.execute("SELECT COALESCE(SUM(shares),0) as s FROM transactions WHERE position_id=? AND action='buy'", (p["id"],)).fetchone()["s"]
            s = conn.execute("SELECT COALESCE(SUM(shares),0) as s FROM transactions WHERE position_id=? AND action='sell'", (p["id"],)).fetchone()["s"]
            if b - s > 0: result.append({"symbol": p["symbol"], "shares": b - s})
        return result
    finally: conn.close()


def gen_morning():
    now = datetime.now()
    lines = [f"**Good morning! Market Briefing — {now.strftime('%A, %B %d, %Y')}**\n", "**Market Overview**"]
    for label, d in market_snapshot().items():
        if d.get("error"): lines.append(f"  {label}: _unavailable_"); continue
        c = d.get("currency", "USD")
        chg = f" {'▲' if d['change_pct'] >= 0 else '▼'} {'+' if d['change_pct'] >= 0 else ''}{d['change_pct']:.2f}%" if d.get("change_pct") is not None else ""
        lines.append(f"  {label}: {fmt_price(d['price'], c)}{chg}")
    portfolio = portfolio_snapshot()
    if portfolio:
        lines.append(f"\n**Your Portfolio** ({len(portfolio)} positions)")
        for p in portfolio:
            try:
                q = get_quote(p["symbol"])
                chg = f" ({'+' if q.get('change_pct', 0) >= 0 else ''}{q.get('change_pct', 0):.2f}%)" if q.get("change_pct") is not None else ""
                lines.append(f"  {p['symbol']}: {fmt_price(q['price'], q.get('currency', 'USD'))}{chg}")
            except: lines.append(f"  {p['symbol']}: _unavailable_")
    conn = get_connection()
    ac = conn.execute("SELECT COUNT(*) as c FROM alerts WHERE status='active'").fetchone()["c"]
    conn.close()
    if ac: lines.append(f"\n**Active Alerts**: {ac}")
    return "\n".join(lines)


def gen_close():
    lines = [f"**Market Close — {datetime.now().strftime('%B %d, %Y')}**\n"]
    for label, d in market_snapshot().items():
        if d.get("error"): continue
        c = d.get("currency", "USD")
        chg = f" {'▲' if d['change_pct'] >= 0 else '▼'} {'+' if d['change_pct'] >= 0 else ''}{d['change_pct']:.2f}%" if d.get("change_pct") is not None else ""
        lines.append(f"  {label}: {fmt_price(d['price'], c)}{chg}")
    return "\n".join(lines)


def gen_weekend():
    lines = ["**Weekend Market Recap**\n", "**Crypto (24/7)**"]
    for sym in ["BTC", "ETH", "SOL", "BNB"]:
        try:
            q = get_quote(sym, force=True)
            s = "+" if (q.get("change_pct") or 0) >= 0 else ""
            lines.append(f"  {sym}: {fmt_price(q['price'], 'USD')} ({s}{q.get('change_pct', 0):.2f}%)")
        except: pass
    lines.append("\n**Forex**")
    for pair in ["USD/TRY", "EUR/USD"]:
        try:
            q = get_quote(pair, force=True)
            lines.append(f"  {pair}: {q['price']:.4f}")
        except: pass
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Market briefings")
    parser.add_argument("type", choices=["morning", "close", "weekend"])
    args = parser.parse_args()
    content = {"morning": gen_morning, "close": gen_close, "weekend": gen_weekend}[args.type]()
    print(content)
    conn = get_connection()
    conn.execute("INSERT INTO briefing_log (briefing_type, content_hash) VALUES (?,?)",
                 (args.type, hashlib.md5(content.encode()).hexdigest()))
    conn.commit(); conn.close()


if __name__ == "__main__":
    main()
