#!/usr/bin/env python3
"""Profit & Loss calculations with live market prices."""

import sys, os, json, argparse
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lib.db import get_connection
from lib.formatters import fmt_price
from scripts.quote import get_quote


def calculate_pnl(symbol=None):
    conn = get_connection()
    try:
        if symbol:
            positions = conn.execute("SELECT * FROM positions WHERE symbol=?", (symbol.upper(),)).fetchall()
        else:
            positions = conn.execute("SELECT * FROM positions ORDER BY symbol").fetchall()
        results = []
        for p in positions:
            buys = conn.execute("SELECT COALESCE(SUM(shares),0) as s, COALESCE(SUM(shares*price),0) as c, COALESCE(SUM(fees),0) as f FROM transactions WHERE position_id=? AND action='buy'", (p["id"],)).fetchone()
            sells = conn.execute("SELECT COALESCE(SUM(shares),0) as s, COALESCE(SUM(shares*price),0) as c, COALESCE(SUM(fees),0) as f FROM transactions WHERE position_id=? AND action='sell'", (p["id"],)).fetchone()
            holding = buys["s"] - sells["s"]
            if holding <= 0: continue
            cost = buys["c"] + buys["f"] - sells["c"] + sells["f"]
            avg = cost / holding if holding else 0
            try:
                q = get_quote(p["symbol"])
                cp = q["price"]; mv = holding * cp; pnl = mv - cost
                pct = (pnl / cost * 100) if cost else 0
            except Exception:
                cp = mv = pnl = pct = None
            results.append({"symbol": p["symbol"], "asset_type": p["asset_type"], "currency": p["currency"],
                            "shares": holding, "avg_cost": round(avg, 2), "cost_basis": round(cost, 2),
                            "current_price": round(cp, 2) if cp else None, "market_value": round(mv, 2) if mv else None,
                            "unrealized_pnl": round(pnl, 2) if pnl is not None else None,
                            "unrealized_pct": round(pct, 2) if pct is not None else None})
        return results
    finally: conn.close()


def format_pnl(results):
    if not results: return "No open positions."
    lines = ["**Portfolio P&L**\n"]
    tc = tv = tp = 0
    for r in results:
        c = r["currency"]
        lines.append(f"**{r['symbol']}** — {r['shares']} shares @ avg {fmt_price(r['avg_cost'], c)}")
        if r["current_price"] is not None:
            e = "🟢" if r["unrealized_pnl"] >= 0 else "🔴"
            s = "+" if r["unrealized_pnl"] >= 0 else ""
            lines.append(f"  Now: {fmt_price(r['current_price'], c)} | Value: {fmt_price(r['market_value'], c)}")
            lines.append(f"  {e} P&L: {s}{fmt_price(r['unrealized_pnl'], c)} ({s}{r['unrealized_pct']:.2f}%)")
            tc += r["cost_basis"]; tv += r["market_value"]; tp += r["unrealized_pnl"]
        lines.append("")
    if tc > 0:
        e = "🟢" if tp >= 0 else "🔴"; s = "+" if tp >= 0 else ""
        lines += ["---", f"**Total**: {fmt_price(tv, 'USD')} | {e} {s}{fmt_price(tp, 'USD')} ({s}{tp/tc*100:.2f}%)"]
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Portfolio P&L")
    parser.add_argument("--symbol", "-s")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    results = calculate_pnl(args.symbol)
    print(json.dumps(results, indent=2, default=str) if args.json else format_pnl(results))


if __name__ == "__main__":
    main()
