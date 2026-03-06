#!/usr/bin/env python3
"""Portfolio Live View - Read positions from Polymarket Data API (SSoT)."""
import json, ssl, urllib.request
from datetime import datetime, timezone

WALLET = "0x2aacf919270Ae303fD3FE8e27D96CBA250936B9F"

def fetch_positions():
    ctx = ssl.create_default_context()
    url = "https://data-api.polymarket.com/positions?user=%s&sizeThreshold=0" % WALLET
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=30, context=ctx) as resp:
        return json.loads(resp.read())

def get_portfolio_costs():
    try:
        with open("/root/.openclaw/skills/polyclaw/portfolio.json") as f:
            p = json.load(f)
        costs = {}
        for slug, pos in p.get("positions", {}).items():
            costs[slug] = {
                "total_cost": float(pos.get("total_cost", 0)),
                "channel": pos.get("channel", "unknown"),
                "side": pos.get("side", "").upper(),
            }
        return costs
    except Exception:
        return {}

def live_portfolio():
    positions = fetch_positions()
    costs = get_portfolio_costs()
    markets = {}
    for p in positions:
        slug = p.get("slug", p.get("eventSlug", "unknown"))
        outcome = p.get("outcome", "?")
        key = "%s|%s" % (slug, outcome)
        size = float(p.get("size", 0))
        value = float(p.get("currentValue", 0))
        cash_pnl = float(p.get("cashPnl", 0))
        if key not in markets:
            markets[key] = {
                "title": p.get("title", slug)[:65],
                "slug": slug,
                "outcome": outcome.upper(),
                "size": 0,
                "total_value": 0,
                "cash_pnl": 0,
                "cur_price": float(p.get("curPrice", 0)),
                "avg_price": float(p.get("avgPrice", 0)),
                "end_date": p.get("endDate", ""),
                "redeemable": False,
                "cost": 0,
                "channel": "unknown",
            }
        markets[key]["size"] += size
        markets[key]["total_value"] += value
        markets[key]["cash_pnl"] += cash_pnl
        if p.get("redeemable"):
            markets[key]["redeemable"] = True

    # Match cost basis from portfolio.json by slug
    for key, market in markets.items():
        slug = market["slug"]
        cost_data = costs.get(slug)
        if cost_data:
            market["cost"] = cost_data["total_cost"]
            market["channel"] = cost_data["channel"]

    return markets

def print_portfolio():
    markets = live_portfolio()
    active = {k: v for k, v in markets.items() if v["size"] >= 0.1}
    redeemable = {k: v for k, v in active.items() if v["redeemable"]}
    live = {k: v for k, v in active.items() if not v["redeemable"] and v["total_value"] >= 0.01}
    dead = {k: v for k, v in active.items() if not v["redeemable"] and v["total_value"] < 0.01}
    total_value = sum(v["total_value"] for v in active.values())
    sep = "=" * 75
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    print("Portfolio Live -- %s" % now)
    print(sep)
    if live:
        live_val = sum(v["total_value"] for v in live.values())
        print("\nLIVE (%d positions, $%.2f value)" % (len(live), live_val))
        for key, ev in sorted(live.items(), key=lambda x: -x[1]["total_value"]):
            # Use cashPnl from Data API (most accurate), fall back to cost basis calc
            if ev["cash_pnl"] != 0:
                pnl_str = "PnL $%+.2f" % ev["cash_pnl"]
            elif ev["cost"] > 0:
                pnl_str = "PnL $%+.2f" % (ev["total_value"] - ev["cost"])
            else:
                pnl_str = "no cost basis"
            print("  $%7.2f | %3s | %5.0f tok | %-15s | %s" % (
                ev["total_value"], ev["outcome"], ev["size"], pnl_str, ev["title"]))
    if redeemable:
        print("\nREDEEMABLE (%d positions)" % len(redeemable))
        for key, ev in sorted(redeemable.items(), key=lambda x: -x[1]["total_value"]):
            print("  $%7.2f | %3s | %5.0f tok | %s" % (
                ev["total_value"], ev["outcome"], ev["size"], ev["title"]))
    if dead:
        print("\nDEAD/EXPIRED (%d positions, 0 value)" % len(dead))
        items = sorted(dead.items(), key=lambda x: -x[1]["size"])
        for key, ev in items[:5]:
            print("  %3s | %5.0f tok | %s" % (ev["outcome"], ev["size"], ev["title"]))
        if len(items) > 5:
            print("  ... and %d more" % (len(items) - 5))
    print("\n" + sep)
    print("Total on-chain value: $%.2f" % total_value)
    return markets

if __name__ == "__main__":
    print_portfolio()
