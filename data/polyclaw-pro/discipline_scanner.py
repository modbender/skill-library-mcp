#!/usr/bin/env python3
"""Discipline Scanner: Check all positions, sell if up 20%+ WITH slippage protection.
Run via cron alongside whale_monitor. Prevents holding winners too long.

Cron: */30 * * * * cd /root/.openclaw/skills/polyclaw && export $(grep -v "^#" .env | xargs) && .venv/bin/python3 discipline_scanner.py >> /var/log/polyclaw-discipline.log 2>&1
"""
import os, json, urllib.request, ssl, sys, time
from datetime import datetime, timezone
from pathlib import Path

BASE = Path("/root/.openclaw/skills/polyclaw")
sys.path.insert(0, str(BASE))

now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
print(f"\n[{now}] Discipline scan")

# Load params
params = json.loads((BASE / "cfo_params.json").read_text())
TP_THRESHOLD = params.get("DISCIPLINE_TP_PCT", 0.20)
MIN_SELL_VALUE = 1.0  # Don't bother selling < $1

wallet = "0x2aacf919270Ae303fD3FE8e27D96CBA250936B9F"
ctx = ssl.create_default_context()

req = urllib.request.Request(
    f"https://data-api.polymarket.com/positions?user={wallet}&sizeThreshold=0",
    headers={"User-Agent": "Mozilla/5.0"}
)
with urllib.request.urlopen(req, timeout=15, context=ctx) as r:
    positions = json.loads(r.read())

live = [p for p in positions if not p.get("redeemable") and float(p.get("currentValue", 0)) > MIN_SELL_VALUE]

sell_targets = []
for p in live:
    entry = float(p.get("avgPrice", 0))
    cur = float(p.get("curPrice", 0))
    val = float(p.get("currentValue", 0))
    size = float(p.get("size", 0))
    asset = p.get("asset", "")
    title = p.get("title", "")[:50]

    if entry <= 0 or cur >= 0.99 or not asset:
        continue

    pnl_pct = (cur - entry) / entry
    if pnl_pct >= TP_THRESHOLD:
        sell_targets.append({
            "title": title, "asset": asset, "size": int(size),
            "entry": entry, "cur": cur, "val": val, "pnl_pct": pnl_pct
        })

if not sell_targets:
    print("  No positions at %.0f%%+ profit" % (TP_THRESHOLD * 100))
    exit(0)

print(f"  Found {len(sell_targets)} positions at TP threshold")

# Import trade functions
from trade_tor import patch_httpx_for_tor, get_client
import httpx
from py_clob_client.clob_types import OrderArgs, OrderType
from py_clob_client.order_builder.constants import SELL as SELL_SIDE

patch_httpx_for_tor()
client = get_client()

total_sold = 0
for t in sell_targets:
    token_id = t["asset"]
    sell_size = t["size"]
    if sell_size < 1:
        continue

    # === SLIPPAGE PROTECTION ===
    # Get orderbook and check bid depth
    try:
        ob = client.get_order_book(token_id)
        bids = ob.bids if ob.bids else []
        best_bid = float(bids[0].price) if bids else 0
    except:
        best_bid = 0

    # Guard: don't sell if best_bid < 50% of our expected price
    min_acceptable = t["cur"] * 0.50
    if best_bid < min_acceptable:
        print(f"  SKIP {t['title']}: bid=${best_bid:.3f} too low vs cur=${t['cur']:.3f} (min ${min_acceptable:.3f})")
        print(f"    This position should wait for settlement or better liquidity")
        continue

    # Guard: don't sell if absolute bid < $0.05 (dust orders)
    if best_bid < 0.05:
        print(f"  SKIP {t['title']}: bid=${best_bid:.3f} is dust, wait for settlement")
        continue

    expected_return = sell_size * best_bid
    print(f"  SELL {t['title']} | {sell_size} @ bid=${best_bid:.3f} | ~${expected_return:.2f} | ({t['pnl_pct']:+.0%})")

    try:
        order = client.create_order(
            OrderArgs(token_id=token_id, price=best_bid, size=sell_size, side=SELL_SIDE)
        )
        result = client.post_order(order, OrderType.FOK)
        if result and result.get("success"):
            taking = float(result.get("takingAmount", 0) or 0)
            print(f"    ✅ received ${taking:.2f}")
            total_sold += taking
        else:
            print(f"    ⚠️ {result.get('status', str(result)[:60])}")
    except Exception as e:
        print(f"    ❌ {str(e)[:100]}")

    time.sleep(2)

if total_sold > 0:
    print(f"\n  Total recovered: ${total_sold:.2f} — ready to redeploy")
else:
    print(f"\n  No sells executed (slippage guard protected all)")
