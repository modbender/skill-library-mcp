#!/usr/bin/env python3
"""Check current position markets and scan for opportunities."""
import httpx, json

GAMMA = "https://gamma-api.polymarket.com"

print("=" * 70)
print("CURRENT POSITION MARKETS")
print("=" * 70)

for q in ["US strikes Iran", "Shelton Federal Reserve"]:
    resp = httpx.get(f"{GAMMA}/markets?_limit=5&query={q}", timeout=15)
    for m in resp.json():
        prices = json.loads(m.get("outcomePrices", "[0,0]"))
        closed = m.get("closed", False)
        end = m.get("endDate", "")[:10]
        status = "[CLOSED]" if closed else "[OPEN]"
        print(f"{status} {m['question'][:70]}")
        print(f"  YES={float(prices[0]):.3f} NO={float(prices[1]):.3f} end={end}")
        print(f"  conditionId={m.get('conditionId','')[:16]}... negRisk={m.get('negRisk',False)}")
    print()

print("=" * 70)
print("TRENDING / HIGH VOLUME MARKETS")
print("=" * 70)

# Get trending markets
resp = httpx.get(f"{GAMMA}/markets?_limit=30&active=true&closed=false&order=volume24hr&ascending=false", timeout=15)
for m in resp.json():
    prices = json.loads(m.get("outcomePrices", "[0,0]"))
    vol24 = float(m.get("volume24hr", 0))
    end = m.get("endDate", "")[:10]
    neg = m.get("negRisk", False)
    yes_p = float(prices[0])
    # Focus on markets with mid-range prices (0.10-0.90) - more trading opportunity
    if 0.05 < yes_p < 0.95:
        print(f"YES={yes_p:.2f} | vol24=${vol24:,.0f} | end={end} | neg={neg}")
        print(f"  {m['question'][:75]}")
        tokens = json.loads(m.get("clobTokenIds", '["",""]'))
        print(f"  conditionId={m.get('conditionId','')[:20]}...")
        print()

print("=" * 70)
print("NEAR-TERM MARKETS (ending soon)")
print("=" * 70)

# Markets ending soon - higher chance of resolution = profit
resp = httpx.get(f"{GAMMA}/markets?_limit=30&active=true&closed=false&order=endDate&ascending=true", timeout=15)
for m in resp.json():
    prices = json.loads(m.get("outcomePrices", "[0,0]"))
    end = m.get("endDate", "")[:10]
    yes_p = float(prices[0])
    vol = float(m.get("volume", 0))
    if 0.05 < yes_p < 0.95 and vol > 10000:
        print(f"YES={yes_p:.2f} | vol=${vol:,.0f} | end={end}")
        print(f"  {m['question'][:75]}")
        print(f"  conditionId={m.get('conditionId','')[:20]}...")
        print()
