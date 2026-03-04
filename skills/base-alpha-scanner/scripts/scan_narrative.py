#!/usr/bin/env python3
"""
Narrative + AI Project Scanner for Base chain.
Scans Bankr.fun, Clanker, and Virtual/AI agent ecosystems for high-quality early tokens.

Usage:
  python3 scan_narrative.py --mode clanker     # Latest Clanker deployments
  python3 scan_narrative.py --mode bankr       # Bankr.fun trending
  python3 scan_narrative.py --mode virtual     # VIRTUAL ecosystem AI agents
  python3 scan_narrative.py --mode ai          # Broad AI narrative scan on Base
"""

import argparse
import json
import urllib.request
import urllib.parse
from datetime import datetime, timezone

def fetch_json(url, headers=None):
    default_headers = {
        "User-Agent": "Mozilla/5.0 (compatible; CrawlBot/1.0)",
        "Accept": "application/json",
    }
    if headers:
        default_headers.update(headers)
    req = urllib.request.Request(url, headers=default_headers)
    try:
        with urllib.request.urlopen(req, timeout=12) as r:
            return json.loads(r.read().decode())
    except Exception as e:
        return {"error": str(e)}

def fetch_html(url):
    req = urllib.request.Request(url, headers={
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
    })
    try:
        with urllib.request.urlopen(req, timeout=12) as r:
            return r.read().decode(errors="replace")
    except Exception as e:
        return f"ERROR: {e}"

def fmt_num(n):
    if n is None: return "N/A"
    n = float(n)
    if n >= 1_000_000: return f"${n/1_000_000:.2f}M"
    if n >= 1_000: return f"${n/1_000:.1f}K"
    return f"${n:.4f}"

def fmt_age(created_at_ms):
    if not created_at_ms: return "unknown"
    age_s = (datetime.now(timezone.utc).timestamp() * 1000 - created_at_ms) / 1000
    if age_s < 3600: return f"{int(age_s/60)}min"
    if age_s < 86400: return f"{age_s/3600:.1f}h"
    return f"{age_s/86400:.1f}d"

AI_KEYWORDS = [
    "ai", "agent", "gpt", "llm", "neural", "robot", "robo", "intelligence",
    "autonomous", "ml", "model", "brain", "cognitive", "compute", "agi",
    "virtual", "fabric", "kuroro", "toru", "ceo", "studio"
]

def is_ai_narrative(name, desc=""):
    combined = (name + " " + desc).lower()
    return any(kw in combined for kw in AI_KEYWORDS)

def scan_clanker():
    """Scan Clanker.world for latest Base token deployments."""
    print("🤖 Clanker — Latest Base Deployments\n")

    # Clanker API v2
    endpoints = [
        "https://www.clanker.world/api/tokens?sort=desc&page=1&limit=30",
        "https://www.clanker.world/api/tokens?sort=trending&page=1&limit=30",
        "https://clanker.world/api/tokens?page=1&limit=30",
    ]
    data = {"error": "not tried"}
    for url in endpoints:
        data = fetch_json(url)
        if "error" not in data:
            break

    if "error" in data:
        print(f"Clanker API not directly accessible (may require auth): {data['error']}")
        print("Use browser tool: https://www.clanker.world")
        print("Or search Warpcast: https://warpcast.com/~/channel/clanker")
        print("\nHigh-signal Clanker patterns to watch:")
        print("  - Power user deployers (>5K Farcaster followers)")
        print("  - Cast gets 100+ likes before token launch")
        print("  - AI/agent/tech narrative with real product")
        print("  - Not copy-paste of existing token")
        return

    tokens = data if isinstance(data, list) else data.get("tokens", data.get("data", data.get("items", [])))

    if not tokens or not isinstance(tokens, list):
        print(f"Raw response (first 1000 chars):")
        print(str(data)[:1000])
        print(f"\nManual check: https://www.clanker.world")
        return

    print(f"Found {len(tokens)} recent Clanker deployments:\n")
    for t in tokens[:20]:
        name = t.get("name", t.get("symbol", "?"))
        symbol = t.get("symbol", "")
        addr = t.get("contract_address", t.get("address", t.get("tokenAddress", "")))
        deployer = t.get("deployer", t.get("requestor_fid", ""))
        cast_hash = t.get("cast_hash", "")
        created = t.get("created_at", t.get("createdAt", ""))
        pool = t.get("pool_address", t.get("poolAddress", ""))

        ai_flag = " 🤖 AI" if is_ai_narrative(name) else ""
        print(f"  {symbol:<12} {name:<20}{ai_flag}")
        if addr:
            print(f"    addr: {addr[:16]}... | dex: https://dexscreener.com/base/{pool or addr}")
        if deployer:
            print(f"    deployer: {str(deployer)[:20]}")
        if created:
            print(f"    created: {created[:19]}")
        print()

def scan_bankr():
    """Scan Bankr.fun for trending Base tokens."""
    print("🏦 Bankr.fun — Trending Base Tokens\n")

    # Bankr API endpoints
    endpoints = [
        "https://api.bankr.bot/tokens/trending?chain=base&limit=20",
        "https://bankr.fun/api/tokens?chain=base&sort=trending&limit=20",
        "https://api.bankr.fun/v1/tokens/trending?chain=base",
    ]

    data = {"error": "not tried"}
    for url in endpoints:
        data = fetch_json(url)
        if "error" not in data:
            break

    if "error" in data:
        print(f"Bankr API not directly accessible: {data['error']}")
        print("Bankr operates via Farcaster/Warpcast — manual scan recommended.")
        print("\nDirect links:")
        print("  Bankr trending: https://bankr.fun")
        print("  Warpcast /bankr channel: https://warpcast.com/~/channel/bankr")
        print("\nFor Bankr alpha: Watch Farcaster casts with /bankr frame interactions")
        print("High-signal: tokens where multiple Farcaster power users bought via Bankr frame")
        return

    tokens = data if isinstance(data, list) else data.get("tokens", data.get("data", []))
    print(f"Found {len(tokens)} Bankr trending tokens:\n")
    for t in tokens[:15]:
        name = t.get("symbol", t.get("name", "?"))
        addr = t.get("address", t.get("contract", ""))
        vol = t.get("volume24h", t.get("volume", 0))
        mcap = t.get("marketCap", t.get("market_cap", 0))
        ai_flag = " 🤖" if is_ai_narrative(name) else ""
        print(f"  {name:<15}{ai_flag}  vol={fmt_num(vol)}  mcap={fmt_num(mcap)}")
        if addr:
            print(f"    https://dexscreener.com/base/{addr}")
        print()

def scan_virtual():
    """Scan VIRTUAL Protocol ecosystem for new AI agents on Base."""
    print("⚡ VIRTUAL Protocol — AI Agent Ecosystem\n")

    # Virtual Protocol API
    url = "https://api.virtuals.io/api/virtuals?filters[status]=DEPLOYED&sort[0]=createdAt%3Adesc&pagination[page]=1&pagination[pageSize]=20"
    data = fetch_json(url)

    if "error" in data:
        print(f"Virtual API error: {data['error']}")
        # Fallback: DexScreener search for VIRTUAL pairs
        print("Falling back to DexScreener VIRTUAL pairs...\n")
        url2 = "https://api.dexscreener.com/latest/dex/tokens/0x0b3e328455c4059EEb9e3f84b5543F74E24e7E1b"
        data2 = fetch_json(url2)
        pairs = [p for p in data2.get("pairs", []) if p.get("chainId") == "base"]
        print(f"Found {len(pairs)} VIRTUAL pairs on Base:\n")
        for p in sorted(pairs, key=lambda x: float(x.get("volume", {}).get("h24") or 0), reverse=True)[:10]:
            name = p.get("baseToken", {}).get("symbol", "?")
            vol24 = fmt_num(p.get("volume", {}).get("h24"))
            ch24 = p.get("priceChange", {}).get("h24", 0)
            age = fmt_age(p.get("pairCreatedAt"))
            print(f"  {name:<15} vol24h={vol24:<10} 24h={ch24:+.1f}% age={age}")
            print(f"    https://dexscreener.com/base/{p.get('pairAddress','')}")
            print()
        return

    agents = data.get("data", [])
    print(f"Latest {len(agents)} VIRTUAL AI agents:\n")
    for a in agents[:15]:
        name = a.get("name", "?")
        symbol = a.get("symbol", "?")
        addr = a.get("tokenAddress", "")
        mcap = a.get("marketCap", 0)
        status = a.get("status", "")
        category = a.get("category", "")
        created = a.get("createdAt", "")[:10]

        print(f"  {symbol:<12} {name:<20}")
        print(f"    mcap={fmt_num(mcap)}  category={category}  created={created}")
        if addr:
            print(f"    https://dexscreener.com/base/{addr}")
        print()

def scan_ai():
    """Broad AI narrative scan: search DexScreener Base for AI-themed tokens."""
    print("🧬 AI Narrative Scan — Base Chain\n")

    ai_terms = ["ai", "agent", "robo", "virtual", "gpt", "neural", "agi", "brain"]
    results = []

    for term in ai_terms[:4]:  # Limit API calls
        url = f"https://api.dexscreener.com/latest/dex/search?q={term}"
        data = fetch_json(url)
        pairs = [p for p in data.get("pairs", []) if p.get("chainId") == "base"]
        results.extend(pairs)

    # Deduplicate by pair address
    seen = set()
    unique = []
    for p in results:
        pa = p.get("pairAddress", "")
        if pa not in seen:
            seen.add(pa)
            unique.append(p)

    # Filter: min $10k liquidity, some volume
    filtered = [
        p for p in unique
        if float(p.get("liquidity", {}).get("usd") or 0) > 10_000
        and float(p.get("volume", {}).get("h24") or 0) > 5_000
    ]

    # Score and sort
    filtered.sort(key=lambda p: (
        float(p.get("volume", {}).get("h1") or 0) *
        (1 + float(p.get("priceChange", {}).get("h1") or 0) / 100)
    ), reverse=True)

    print(f"Found {len(filtered)} AI-narrative tokens on Base (min $10k liq, $5k 24h vol):\n")
    for p in filtered[:20]:
        name = p.get("baseToken", {}).get("symbol", "?")
        full_name = p.get("baseToken", {}).get("name", "")
        vol1h = fmt_num(p.get("volume", {}).get("h1"))
        vol24 = fmt_num(p.get("volume", {}).get("h24"))
        liq = fmt_num(p.get("liquidity", {}).get("usd"))
        mcap = fmt_num(p.get("marketCap"))
        ch1h = p.get("priceChange", {}).get("h1", 0)
        ch24h = p.get("priceChange", {}).get("h24", 0)
        age = fmt_age(p.get("pairCreatedAt"))
        pair = p.get("pairAddress", "")

        print(f"  {name:<12} ({full_name[:20]})")
        print(f"    age={age:<8} vol1h={vol1h:<10} vol24={vol24:<10} liq={liq:<10} mcap={mcap}")
        print(f"    1h={ch1h:+.1f}%  24h={ch24h:+.1f}%")
        print(f"    https://dexscreener.com/base/{pair}")
        print()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Base Narrative Scanner")
    parser.add_argument("--mode", choices=["clanker", "bankr", "virtual", "ai"], required=True)
    args = parser.parse_args()

    if args.mode == "clanker":
        scan_clanker()
    elif args.mode == "bankr":
        scan_bankr()
    elif args.mode == "virtual":
        scan_virtual()
    elif args.mode == "ai":
        scan_ai()
