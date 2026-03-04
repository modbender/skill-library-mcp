#!/usr/bin/env python3
"""Solana Token Safety Analyzer — Takes raw scan data and produces safety report."""

import json
import sys

def analyze(data: dict) -> dict:
    score = 100
    flags = []
    info = {}
    
    mint = data.get("mint", "unknown")
    
    # --- DexScreener Analysis ---
    dex = data.get("dexscreener", {})
    pairs = dex.get("pairs") or []
    
    if not pairs:
        score -= 40
        flags.append("NO_DEX_LISTING: Token not found on any DEX — cannot verify liquidity")
    else:
        pair = pairs[0]  # Primary pair
        info["name"] = pair.get("baseToken", {}).get("name", "Unknown")
        info["symbol"] = pair.get("baseToken", {}).get("symbol", "???")
        info["price_usd"] = pair.get("priceUsd", "0")
        info["price_native"] = pair.get("priceNative", "0")
        info["dex"] = pair.get("dexId", "unknown")
        
        # Liquidity check
        liq = pair.get("liquidity", {})
        liq_usd = float(liq.get("usd", 0))
        info["liquidity_usd"] = liq_usd
        
        if liq_usd < 1000:
            score -= 35
            flags.append(f"EXTREMELY_LOW_LIQUIDITY: ${liq_usd:.0f} — almost certainly a rug or dead token")
        elif liq_usd < 10000:
            score -= 20
            flags.append(f"LOW_LIQUIDITY: ${liq_usd:.0f} — high slippage, hard to exit")
        elif liq_usd < 50000:
            score -= 10
            flags.append(f"MODERATE_LIQUIDITY: ${liq_usd:.0f} — be cautious with size")
        
        # Volume check
        vol_24h = float(pair.get("volume", {}).get("h24", 0))
        info["volume_24h"] = vol_24h
        
        if vol_24h < 100:
            score -= 15
            flags.append(f"NO_VOLUME: ${vol_24h:.0f} 24h volume — dead token")
        elif vol_24h < 1000:
            score -= 10
            flags.append(f"LOW_VOLUME: ${vol_24h:.0f} 24h volume")
        
        # Market cap
        mc = float(pair.get("marketCap", 0) or pair.get("fdv", 0) or 0)
        info["market_cap"] = mc
        
        # Price change
        pc = pair.get("priceChange", {})
        pc_24h = float(pc.get("h24", 0))
        info["price_change_24h"] = pc_24h
        
        if pc_24h < -50:
            score -= 15
            flags.append(f"CRASH: {pc_24h:.1f}% in 24h — severe dump")
        elif pc_24h < -20:
            score -= 5
            flags.append(f"DECLINING: {pc_24h:.1f}% in 24h")
        
        # Pair age
        created = pair.get("pairCreatedAt", 0)
        if created:
            import time
            age_hours = (time.time() * 1000 - created) / (1000 * 3600)
            info["pair_age_hours"] = round(age_hours, 1)
            if age_hours < 24:
                score -= 10
                flags.append(f"VERY_NEW: Pair created {age_hours:.1f}h ago — high risk")
            elif age_hours < 168:  # 1 week
                score -= 5
                flags.append(f"NEW: Pair created {age_hours/24:.1f} days ago")
        
        # Number of pairs (more pairs = more legitimate)
        info["num_pairs"] = len(pairs)
    
    # --- Supply Analysis ---
    supply_data = data.get("supply", {})
    result = supply_data.get("result", {})
    if result and "value" in result:
        val = result["value"]
        info["total_supply"] = val.get("uiAmountString", "unknown")
        info["decimals"] = val.get("decimals", 0)
    
    # --- Holder Concentration ---
    holders_data = data.get("largest_holders", {})
    h_result = holders_data.get("result", {})
    if h_result and "value" in h_result:
        holders = h_result["value"]
        info["top_holders_count"] = len(holders)
        
        total_supply_raw = float(result.get("value", {}).get("amount", 0)) if result and "value" in result else 0
        
        if total_supply_raw > 0 and holders:
            top1_pct = float(holders[0].get("amount", 0)) / total_supply_raw * 100
            top5_pct = sum(float(h.get("amount", 0)) for h in holders[:5]) / total_supply_raw * 100
            top10_pct = sum(float(h.get("amount", 0)) for h in holders[:10]) / total_supply_raw * 100
            
            info["top1_holder_pct"] = round(top1_pct, 2)
            info["top5_holders_pct"] = round(top5_pct, 2)
            info["top10_holders_pct"] = round(top10_pct, 2)
            
            if top1_pct > 50:
                score -= 30
                flags.append(f"EXTREME_CONCENTRATION: Top holder owns {top1_pct:.1f}% — rug pull risk")
            elif top1_pct > 20:
                score -= 15
                flags.append(f"HIGH_CONCENTRATION: Top holder owns {top1_pct:.1f}%")
            elif top5_pct > 50:
                score -= 10
                flags.append(f"CONCENTRATED: Top 5 holders own {top5_pct:.1f}%")
    
    # --- Score Classification ---
    score = max(0, min(100, score))
    
    if score >= 80:
        recommendation = "RELATIVELY_SAFE"
        emoji = "🟢"
    elif score >= 60:
        recommendation = "CAUTION"
        emoji = "🟡"
    elif score >= 40:
        recommendation = "HIGH_RISK"
        emoji = "🟠"
    else:
        recommendation = "AVOID"
        emoji = "🔴"
    
    return {
        "mint": mint,
        "score": score,
        "recommendation": recommendation,
        "emoji": emoji,
        "info": info,
        "flags": flags,
        "flag_count": len(flags),
    }


def format_report(result: dict) -> str:
    r = result
    i = r["info"]
    
    lines = []
    lines.append(f"{r['emoji']} Token Safety Report")
    lines.append(f"{'='*40}")
    lines.append(f"Mint: {r['mint']}")
    
    if "name" in i:
        lines.append(f"Name: {i['name']} ({i.get('symbol', '?')})")
    if "price_usd" in i:
        lines.append(f"Price: ${i['price_usd']}")
    if "market_cap" in i:
        mc = i['market_cap']
        lines.append(f"Market Cap: ${mc:,.0f}" if mc else "Market Cap: Unknown")
    if "volume_24h" in i:
        lines.append(f"24h Volume: ${i['volume_24h']:,.0f}")
    if "liquidity_usd" in i:
        lines.append(f"Liquidity: ${i['liquidity_usd']:,.0f}")
    if "price_change_24h" in i:
        lines.append(f"24h Change: {i['price_change_24h']:+.1f}%")
    if "dex" in i:
        lines.append(f"Primary DEX: {i['dex']}")
    if "pair_age_hours" in i:
        h = i['pair_age_hours']
        lines.append(f"Pair Age: {h:.0f}h ({h/24:.1f} days)" if h > 24 else f"Pair Age: {h:.1f} hours")
    
    lines.append("")
    lines.append(f"Holder Distribution:")
    if "top1_holder_pct" in i:
        lines.append(f"  Top 1: {i['top1_holder_pct']:.1f}%")
        lines.append(f"  Top 5: {i['top5_holders_pct']:.1f}%")
        lines.append(f"  Top 10: {i['top10_holders_pct']:.1f}%")
    
    lines.append("")
    lines.append(f"Safety Score: {r['score']}/100 — {r['recommendation']}")
    
    if r["flags"]:
        lines.append("")
        lines.append(f"Flags ({r['flag_count']}):")
        for f in r["flags"]:
            lines.append(f"  ⚠️  {f}")
    else:
        lines.append("  No red flags detected.")
    
    return "\n".join(lines)


if __name__ == "__main__":
    if len(sys.argv) > 1:
        with open(sys.argv[1]) as f:
            data = json.load(f)
    else:
        data = json.load(sys.stdin)
    
    result = analyze(data)
    print(format_report(result))
