#!/usr/bin/env python3
"""
Base Alpha Scanner — Claw's primary on-chain intelligence script.
Fetches live data from DexScreener, GMGN, and Basescan for Base chain analysis.

Usage:
  python3 scan_base.py --mode trending      # Top trending tokens on Base (1h)
  python3 scan_base.py --mode new           # New pairs (0-45min, early launch scan)
  python3 scan_base.py --mode token <addr>  # Deep dive on a specific token
  python3 scan_base.py --mode holders <addr> # Holder distribution via Basescan
  python3 scan_base.py --mode gmgn <addr>   # GMGN smart money / wallet data
"""

import argparse
import json
import sys
import urllib.request
import urllib.parse
from datetime import datetime, timezone

DEXSCREENER_BASE = "https://api.dexscreener.com"
BASESCAN_API = "https://api.basescan.org/api"
GMGN_BASE = "https://gmgn.ai/defi/quotation/v1"

def fetch_json(url, headers=None):
    req = urllib.request.Request(url, headers=headers or {"User-Agent": "CrawlBot/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            return json.loads(r.read().decode())
    except Exception as e:
        return {"error": str(e)}

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

def score_token(p):
    """
    Quick conviction score 0-100 for second-wave / early gem filtering.
    Higher = more interesting. Does NOT replace human judgment.
    """
    score = 0
    vol = float(p.get("volume", {}).get("h1") or 0)
    liq = float(p.get("liquidity", {}).get("usd") or 0)
    txns_1h = (p.get("txns", {}).get("h1") or {})
    buys = float(txns_1h.get("buys") or 0)
    sells = float(txns_1h.get("sells") or 0)
    change_1h = float(p.get("priceChange", {}).get("h1") or 0)
    change_24h = float(p.get("priceChange", {}).get("h24") or 0)
    mcap = float(p.get("marketCap") or 0)
    age_ms = p.get("pairCreatedAt")
    age_h = ((datetime.now(timezone.utc).timestamp() * 1000 - age_ms) / 3_600_000) if age_ms else 999

    # Volume signal
    if vol > 500_000: score += 25
    elif vol > 100_000: score += 15
    elif vol > 20_000: score += 8

    # Liquidity health
    if liq > 100_000: score += 15
    elif liq > 30_000: score += 8

    # Buy pressure
    total = buys + sells
    if total > 0 and buys / total > 0.55: score += 15

    # Momentum
    if change_1h > 20: score += 10
    elif change_1h > 5: score += 5
    if change_24h > 50: score += 10

    # Age sweet spot (45min–3h = second wave window)
    if 0.75 <= age_h <= 3: score += 15
    elif 0 <= age_h < 0.75: score += 10  # Early launch
    elif 3 < age_h <= 6: score += 5

    # Mcap sanity
    if 0 < mcap < 5_000_000: score += 5

    return min(score, 100)

def scan_trending():
    print("🦞 Base Trending — 1H Score\n")
    url = f"{DEXSCREENER_BASE}/token-profiles/latest/v1"
    # Use search endpoint for Base trending
    url = f"{DEXSCREENER_BASE}/latest/dex/search?q=base"
    data = fetch_json(url)
    pairs = data.get("pairs", [])
    # Filter to Base only
    base_pairs = [p for p in pairs if p.get("chainId") == "base"]

    if not base_pairs:
        # Fallback: use boosted tokens endpoint
        print("Using fallback endpoint...")
        url2 = f"{DEXSCREENER_BASE}/token-boosts/top/v1"
        data2 = fetch_json(url2)
        print(json.dumps(data2, indent=2)[:2000])
        return

    base_pairs.sort(key=lambda p: score_token(p), reverse=True)

    for p in base_pairs[:15]:
        score = score_token(p)
        name = p.get("baseToken", {}).get("symbol", "?")
        addr = p.get("baseToken", {}).get("address", "")[:10]
        age = fmt_age(p.get("pairCreatedAt"))
        vol1h = fmt_num(p.get("volume", {}).get("h1"))
        liq = fmt_num(p.get("liquidity", {}).get("usd"))
        mcap = fmt_num(p.get("marketCap"))
        ch1h = p.get("priceChange", {}).get("h1", 0)
        ch24h = p.get("priceChange", {}).get("h24", 0)
        txns = p.get("txns", {}).get("h1", {})
        makers = txns.get("buys", 0) + txns.get("sells", 0)

        bar = "█" * (score // 10) + "░" * (10 - score // 10)
        print(f"[{score:3d}] {bar} {name:<12} age={age:<8} vol1h={vol1h:<10} liq={liq:<10} mcap={mcap:<10} 1h={ch1h:+.1f}% 24h={ch24h:+.1f}% txns={makers}")
        if addr:
            print(f"       addr: {addr}... | dex: https://dexscreener.com/base/{p.get('pairAddress','')}")
        print()

def scan_new():
    print("🔍 Base New Pairs (Early Launch Scanner)\n")
    url = f"{DEXSCREENER_BASE}/latest/dex/search?q=base"
    data = fetch_json(url)
    pairs = data.get("pairs", [])
    base_pairs = [p for p in pairs if p.get("chainId") == "base"]

    now_ms = datetime.now(timezone.utc).timestamp() * 1000
    cutoff_45min = now_ms - (45 * 60 * 1000)
    cutoff_3h = now_ms - (3 * 3600 * 1000)

    early = [p for p in base_pairs if p.get("pairCreatedAt", 0) > cutoff_45min]
    second_wave = [p for p in base_pairs if cutoff_3h < p.get("pairCreatedAt", 0) <= cutoff_45min]

    print(f"=== EARLY (0–45min): {len(early)} pairs ===")
    for p in sorted(early, key=lambda x: score_token(x), reverse=True)[:5]:
        _print_token_row(p)

    print(f"\n=== SECOND WAVE (45min–3h): {len(second_wave)} pairs ===")
    for p in sorted(second_wave, key=lambda x: score_token(x), reverse=True)[:10]:
        _print_token_row(p)

def _print_token_row(p):
    score = score_token(p)
    name = p.get("baseToken", {}).get("symbol", "?")
    age = fmt_age(p.get("pairCreatedAt"))
    vol1h = fmt_num(p.get("volume", {}).get("h1"))
    liq = fmt_num(p.get("liquidity", {}).get("usd"))
    mcap = fmt_num(p.get("marketCap"))
    ch1h = p.get("priceChange", {}).get("h1", 0)
    pair_addr = p.get("pairAddress", "")
    token_addr = p.get("baseToken", {}).get("address", "")
    dex = p.get("dexId", "")
    print(f"  [{score:3d}] {name:<12} age={age:<8} vol1h={vol1h:<10} liq={liq:<10} mcap={mcap:<10} 1h={ch1h:+.1f}%")
    print(f"         dex={dex} | https://dexscreener.com/base/{pair_addr}")
    print(f"         token: https://basescan.org/token/{token_addr}")
    print()

def scan_token(addr):
    print(f"🔎 Token Deep Dive: {addr}\n")
    url = f"{DEXSCREENER_BASE}/latest/dex/tokens/{addr}"
    data = fetch_json(url)
    pairs = [p for p in data.get("pairs", []) if p.get("chainId") == "base"]
    if not pairs:
        print("No pairs found on Base for this address.")
        return

    # Show top pair by volume
    pairs.sort(key=lambda p: float(p.get("volume", {}).get("h24") or 0), reverse=True)
    p = pairs[0]

    name = p.get("baseToken", {}).get("name", "?")
    symbol = p.get("baseToken", {}).get("symbol", "?")
    price = p.get("priceUsd", "?")
    age = fmt_age(p.get("pairCreatedAt"))
    mcap = fmt_num(p.get("marketCap"))
    fdv = fmt_num(p.get("fdv"))
    liq = fmt_num(p.get("liquidity", {}).get("usd"))

    print(f"Name:    {name} ({symbol})")
    print(f"Price:   ${price}")
    print(f"Age:     {age}")
    print(f"MCap:    {mcap}  |  FDV: {fdv}")
    print(f"Liq:     {liq}")
    print()

    for tf in ["m5", "h1", "h6", "h24"]:
        vol = fmt_num(p.get("volume", {}).get(tf))
        ch = p.get("priceChange", {}).get(tf, 0)
        txns = p.get("txns", {}).get(tf, {})
        buys = txns.get("buys", 0)
        sells = txns.get("sells", 0)
        print(f"  {tf:>3}: vol={vol:<10} change={ch:+.2f}%  buys={buys} sells={sells}")

    print(f"\nConviction Score: {score_token(p)}/100")
    print(f"DexScreener: https://dexscreener.com/base/{p.get('pairAddress','')}")

    if len(pairs) > 1:
        print(f"\nOther pairs ({len(pairs)-1}):")
        for pp in pairs[1:4]:
            print(f"  {pp.get('dexId')}: {fmt_num(pp.get('volume',{}).get('h24'))} 24h vol")

def scan_holders(addr, basescan_key=None):
    print(f"👥 Holder Distribution: {addr}\n")
    if not basescan_key:
        print("No Basescan API key — fetching public holder page instead.")
        print(f"  → https://basescan.org/token/tokenholderchart/{addr}")
        print()
        # Try the free endpoint
        url = f"https://api.basescan.org/api?module=token&action=tokenholderlist&contractaddress={addr}&page=1&offset=20&apikey=YourApiKeyToken"
        data = fetch_json(url)
        if data.get("status") == "1":
            holders = data.get("result", [])
            print(f"Top {len(holders)} holders:")
            total = sum(int(h.get("TokenHolderQuantity", 0)) for h in holders)
            for i, h in enumerate(holders[:10], 1):
                qty = int(h.get("TokenHolderQuantity", 0))
                pct = qty / total * 100 if total else 0
                print(f"  #{i:2d} {h['TokenHolderAddress'][:12]}...  {pct:.2f}%")
        else:
            print("Basescan free tier — add BASESCAN_API_KEY for full holder data.")
        return

    url = f"{BASESCAN_API}?module=token&action=tokenholderlist&contractaddress={addr}&page=1&offset=50&apikey={basescan_key}"
    data = fetch_json(url)
    if data.get("status") != "1":
        print(f"Error: {data.get('message', 'unknown')}")
        return

    holders = data.get("result", [])
    total = sum(int(h.get("TokenHolderQuantity", 0)) for h in holders)
    print(f"Top {len(holders)} holders (of visible supply):\n")
    for i, h in enumerate(holders[:20], 1):
        qty = int(h.get("TokenHolderQuantity", 0))
        pct = qty / total * 100 if total else 0
        addr_str = h["TokenHolderAddress"]
        flag = " ⚠️ WHALE" if pct > 10 else (" 🐳" if pct > 5 else "")
        print(f"  #{i:2d} {addr_str[:14]}...  {pct:6.2f}%{flag}")

    # Concentration check
    top5 = sum(int(h.get("TokenHolderQuantity", 0)) for h in holders[:5])
    top5_pct = top5 / total * 100 if total else 0
    print(f"\nTop-5 concentration: {top5_pct:.1f}% {'⚠️ HIGH' if top5_pct > 40 else '✅ OK'}")

def scan_gmgn(addr):
    print(f"🧠 GMGN Smart Money: {addr}\n")
    # GMGN public endpoints (no auth required for basic data)
    url = f"{GMGN_BASE}/rank/base/swaps/1h?orderby=swaps&direction=desc&filters[]=not_wash_trade"
    print(f"Fetching GMGN rank data...")
    data = fetch_json(url)
    if "error" in data:
        print(f"GMGN error: {data['error']}")
        print("Tip: GMGN may require browser-like headers or session. Use browser tool for full access.")
        print(f"GMGN link: https://gmgn.ai/base/token/{addr}")
        return

    print(json.dumps(data, indent=2)[:3000])

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Base Alpha Scanner")
    parser.add_argument("--mode", choices=["trending", "new", "token", "holders", "gmgn"], required=True)
    parser.add_argument("addr", nargs="?", help="Token or pair address")
    parser.add_argument("--basescan-key", default=None, help="Basescan API key for holder data")
    args = parser.parse_args()

    if args.mode == "trending":
        scan_trending()
    elif args.mode == "new":
        scan_new()
    elif args.mode == "token":
        if not args.addr:
            print("Error: --mode token requires an address")
            sys.exit(1)
        scan_token(args.addr)
    elif args.mode == "holders":
        if not args.addr:
            print("Error: --mode holders requires an address")
            sys.exit(1)
        scan_holders(args.addr, args.basescan_key)
    elif args.mode == "gmgn":
        if not args.addr:
            print("Error: --mode gmgn requires an address")
            sys.exit(1)
        scan_gmgn(args.addr)
