#!/usr/bin/env python3
"""Scan Polymarket for trading opportunities with proper API calls."""
import httpx
import json

GAMMA = "https://gamma-api.polymarket.com"
CLOB = "https://clob.polymarket.com"

# ========================================================
# 1. Check on-chain positions via CLOB API
# ========================================================
print("=" * 70)
print("WALLET POSITIONS (CLOB API)")
print("=" * 70)

try:
    # Get positions from Gamma profile
    resp = httpx.get(
        f"{GAMMA}/markets?_limit=50&active=true&closed=false",
        timeout=15
    )
    # This returns all active markets, not positions
except Exception as e:
    print(f"Error: {e}")

# ========================================================
# 2. Scan high-volume current markets
# ========================================================
print("\n" + "=" * 70)
print("HIGH VOLUME ACTIVE MARKETS (sorted by 24h volume)")
print("=" * 70)

# Use events endpoint for better results
resp = httpx.get(
    f"{GAMMA}/events?_limit=50&active=true&closed=false&order=volume24hr&ascending=false",
    timeout=15
)
events = resp.json()

interesting = []
for event in events:
    for m in event.get("markets", []):
        prices = json.loads(m.get("outcomePrices", "[0,0]"))
        yes_p = float(prices[0])
        vol24 = float(m.get("volume24hr", 0))
        vol = float(m.get("volume", 0))
        end = m.get("endDate", "")[:10]
        neg = m.get("negRisk", False)
        cond = m.get("conditionId", "")
        q = m.get("question", "")
        slug = event.get("slug", "")

        # Skip extreme prices - we want mid-range for opportunity
        if vol24 > 50000 and 0.03 < yes_p < 0.97:
            interesting.append({
                "q": q, "yes": yes_p, "vol24": vol24, "vol": vol,
                "end": end, "neg": neg, "cond": cond, "slug": slug
            })

# Sort by 24h volume
interesting.sort(key=lambda x: x["vol24"], reverse=True)

for i, m in enumerate(interesting[:25]):
    print(f"\n{i+1}. YES={m['yes']:.2f} | 24h=${m['vol24']:,.0f} | total=${m['vol']:,.0f} | end={m['end']}")
    print(f"   {m['q'][:75]}")
    print(f"   slug={m['slug'][:40]} neg={m['neg']} cond={m['cond'][:20]}...")

# ========================================================
# 3. Near-term events (ending within 7 days)
# ========================================================
print("\n\n" + "=" * 70)
print("EVENTS ENDING WITHIN 7 DAYS")
print("=" * 70)

resp = httpx.get(
    f"{GAMMA}/events?_limit=30&active=true&closed=false&order=endDate&ascending=true",
    timeout=15
)
events = resp.json()

for event in events:
    for m in event.get("markets", []):
        end = m.get("endDate", "")[:10]
        if not end:
            continue
        # Filter for markets ending soon
        if end <= "2026-02-18":
            prices = json.loads(m.get("outcomePrices", "[0,0]"))
            yes_p = float(prices[0])
            vol = float(m.get("volume", 0))
            if 0.03 < yes_p < 0.97 and vol > 5000:
                q = m.get("question", "")
                cond = m.get("conditionId", "")
                slug = event.get("slug", "")
                print(f"\nYES={yes_p:.2f} | vol=${vol:,.0f} | end={end}")
                print(f"  {q[:75]}")
                print(f"  slug={slug[:40]} cond={cond[:20]}...")

# ========================================================
# 4. Search for geopolitical/crypto markets (our specialty)
# ========================================================
print("\n\n" + "=" * 70)
print("GEOPOLITICAL & CRYPTO MARKETS")
print("=" * 70)

for tag in ["crypto", "geopolitics", "politics", "finance"]:
    resp = httpx.get(
        f"{GAMMA}/events?_limit=10&active=true&closed=false&tag={tag}&order=volume24hr&ascending=false",
        timeout=15
    )
    events = resp.json()
    if events:
        print(f"\n--- {tag.upper()} ---")
    for event in events[:5]:
        for m in event.get("markets", []):
            prices = json.loads(m.get("outcomePrices", "[0,0]"))
            yes_p = float(prices[0])
            if 0.03 < yes_p < 0.97:
                vol24 = float(m.get("volume24hr", 0))
                end = m.get("endDate", "")[:10]
                cond = m.get("conditionId", "")
                print(f"  YES={yes_p:.2f} | 24h=${vol24:,.0f} | end={end}")
                print(f"    {m['question'][:70]}")
                print(f"    cond={cond[:20]}...")
