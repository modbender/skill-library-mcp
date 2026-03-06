#!/usr/bin/env python3
"""Cron job: check all active alerts against current prices."""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lib.db import get_connection
from lib.config import get_api_key
from lib.rate_limiter import wait_if_needed
import requests


def fetch_price(symbol, asset_type):
    if asset_type == "crypto":
        pair = symbol if symbol.endswith("USDT") else symbol + "USDT"
        wait_if_needed("binance")
        return float(requests.get("https://api.binance.com/api/v3/ticker/price",
                                  params={"symbol": pair}, timeout=10).json()["price"])
    elif asset_type == "forex":
        parts = symbol.replace("/", "")
        base, target = parts[:3], parts[3:]
        api_key = get_api_key("exchangeRateApiKey")
        if api_key:
            wait_if_needed("exchangerate")
            return requests.get(f"https://v6.exchangerate-api.com/v6/{api_key}/pair/{base}/{target}",
                                timeout=10).json()["conversion_rate"]
        wait_if_needed("exchangerate")
        return requests.get(f"https://open.er-api.com/v6/latest/{base}", timeout=10).json()["rates"].get(target, 0)
    else:
        api_key = get_api_key("finnhubApiKey")
        if asset_type == "stock_us" and api_key:
            wait_if_needed("finnhub")
            data = requests.get("https://finnhub.io/api/v1/quote",
                                params={"symbol": symbol, "token": api_key}, timeout=10).json()
            if data.get("c", 0) > 0: return data["c"]
        import yfinance as yf
        wait_if_needed("yfinance")
        return yf.Ticker(symbol).fast_info.last_price


def check_alerts():
    conn = get_connection()
    try:
        conn.execute("UPDATE alerts SET status='active' WHERE status='snoozed' AND snoozed_until < datetime('now')")
        conn.commit()
        alerts = conn.execute("SELECT * FROM alerts WHERE status='active'").fetchall()
        if not alerts: return None
        triggered = []
        for a in alerts:
            try:
                price = fetch_price(a["symbol"], a["asset_type"])
                if price is None: continue
                hit = False
                if a["condition"] == "above" and price >= a["target_value"]: hit = True
                elif a["condition"] == "below" and price <= a["target_value"]: hit = True
                elif a["condition"] == "change_pct" and a["current_value_at_creation"]:
                    if abs((price - a["current_value_at_creation"]) / a["current_value_at_creation"] * 100) >= abs(a["target_value"]): hit = True
                if hit:
                    conn.execute("UPDATE alerts SET status='triggered', triggered_at=CURRENT_TIMESTAMP WHERE id=?", (a["id"],))
                    triggered.append({"id": a["id"], "symbol": a["symbol"], "condition": a["condition"],
                                      "target": a["target_value"], "current_price": price, "note": a["note"]})
            except Exception: continue
        conn.commit()
        return triggered if triggered else None
    finally: conn.close()


if __name__ == "__main__":
    triggered = check_alerts()
    if triggered:
        print("**Price Alert Triggered!**\n")
        for t in triggered:
            cond = {"above": f"above {t['target']}", "below": f"below {t['target']}",
                    "change_pct": f"changed by {t['target']}%"}.get(t["condition"], t["condition"])
            print(f"  #{t['id']} **{t['symbol']}** — now {t['current_price']:.4f} (target: {cond})")
            if t.get("note"): print(f"    Note: {t['note']}")
    else:
        print("No alerts triggered.")
