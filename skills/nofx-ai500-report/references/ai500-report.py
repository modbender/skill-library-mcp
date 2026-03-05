#!/usr/bin/env python3
"""NOFX AI500 Report Generator - fetches real data via curl, outputs formatted report sections."""
import json, subprocess, sys
from datetime import datetime

BASE = "https://nofxos.ai"
KEY = "cm_568c67eae410d912c54c"
DURATIONS = ["5m", "15m", "30m", "1h", "4h", "8h", "24h"]

def curl_json(url):
    try:
        r = subprocess.run(["curl", "-s", "-f", url], capture_output=True, text=True, timeout=15)
        if r.returncode != 0:
            return None
        return json.loads(r.stdout)
    except:
        return None

def nofx(endpoint, params=""):
    url = f"{BASE}{endpoint}?auth={KEY}"
    if params:
        url += f"&{params}"
    return curl_json(url)

def binance_klines(symbol, interval, limit=10):
    return curl_json(f"https://fapi.binance.com/fapi/v1/klines?symbol={symbol}&interval={interval}&limit={limit}")

def analyze_klines(klines):
    if not klines or len(klines) < 7:
        return None
    closes = [float(k[4]) for k in klines]
    opens = [float(k[1]) for k in klines]
    highs = [float(k[2]) for k in klines]
    lows = [float(k[3]) for k in klines]
    volumes = [float(k[5]) for k in klines]
    
    last3 = closes[-3:]
    if last3[0] < last3[1] < last3[2]:
        trend = "📈Bullish"
    elif last3[0] > last3[1] > last3[2]:
        trend = "📉Bearish"
    else:
        trend = "↔️Sideways"
    
    bulls = sum(1 for i in range(len(klines)) if closes[i] >= opens[i])
    bears = len(klines) - bulls
    ma3 = sum(closes[-3:]) / 3
    ma7 = sum(closes[-7:]) / 7
    ma_align = "Bullish" if ma3 > ma7 else "Bearish"
    
    vol_recent = sum(volumes[-3:]) / 3
    vol_prev = sum(volumes[-6:-3]) / 3
    vol_chg = ((vol_recent - vol_prev) / vol_prev * 100) if vol_prev > 0 else 0
    
    return {
        "trend": trend, "bulls": bulls, "bears": bears,
        "ma_align": ma_align, "vol_chg": vol_chg,
        "support": min(lows), "resistance": max(highs),
        "price": closes[-1]
    }

def fmt_num(n):
    if n is None: return "N/A"
    n = float(n)
    sign = "+" if n >= 0 else ""
    an = abs(n)
    if an >= 1e9: return f"{sign}${n/1e9:.2f}B"
    elif an >= 1e6: return f"{sign}${n/1e6:.2f}M"
    elif an >= 1e3: return f"{sign}${n/1e3:.1f}K"
    else: return f"{sign}${n:.0f}"

def find_in_list(items, symbol_key, symbol):
    """Find symbol in a list of dicts."""
    sym = symbol.upper()
    for item in items:
        if isinstance(item, dict):
            s = item.get(symbol_key, "").upper()
            if sym in s or s in sym + "USDT":
                return item
    return None

def main():
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    
    # 1. AI500 list
    ai500 = nofx("/api/ai500/list")
    if not ai500 or not ai500.get("success"):
        print("ERROR: Failed to fetch AI500 list")
        sys.exit(1)
    
    coins = ai500["data"]["coins"]
    count = len(coins)
    sections = []
    
    # Header
    sections.append(f"""```
╔══════════════════════════════════════╗
║   NOFX AI500 Intelligence Report            ║
║   {now}                     ║
║   Active selections: {count} coins                   ║
╚══════════════════════════════════════╝
```""")
    
    # 2. Fetch all OI/netflow rankings
    oi_top = {}; oi_low = {}; nf_top = {}; nf_low = {}
    for d in DURATIONS:
        oi_top[d] = nofx("/api/oi/top-ranking", f"duration={d}")
        oi_low[d] = nofx("/api/oi/low-ranking", f"duration={d}")
        nf_top[d] = nofx("/api/netflow/top-ranking", f"type=institution&trade=future&duration={d}")
        nf_low[d] = nofx("/api/netflow/low-ranking", f"type=institution&trade=future&duration={d}")
    
    # Funding rate
    fr_top = nofx("/api/funding-rate/top-ranking")
    
    # 3. Per-coin detail
    for coin in coins:
        pair = coin["pair"]
        symbol = pair.replace("USDT", "")
        score = coin["score"]
        max_score = coin["max_score"]
        start_price = coin["start_price"]
        increase = coin["increase_percent"]
        
        # Find OI for this coin across durations
        oi_vals = {}
        oi_val_usd = {}
        for d in DURATIONS:
            val = None
            val_usd = None
            for src in [oi_top[d], oi_low[d]]:
                if src and src.get("success"):
                    positions = src.get("data", {}).get("positions", [])
                    found = find_in_list(positions, "symbol", pair)
                    if found:
                        val = found.get("oi_delta_percent")
                        val_usd = found.get("oi_delta_value")
                        break
            oi_vals[d] = val
            oi_val_usd[d] = val_usd
        
        # Find netflow for this coin
        nf_vals = {}
        for d in DURATIONS:
            val = None
            for src in [nf_top[d], nf_low[d]]:
                if src and src.get("success"):
                    netflows = src.get("data", {}).get("netflows", [])
                    found = find_in_list(netflows, "symbol", pair)
                    if found:
                        val = found.get("amount")
                        break
            nf_vals[d] = val
        
        # Funding rate - search in top data
        fr_val = None
        if fr_top and fr_top.get("success"):
            fr_data = fr_top.get("data", {})
            # Could be a single item or list
            if isinstance(fr_data, dict) and fr_data.get("symbol"):
                if pair.upper() in fr_data["symbol"].upper():
                    fr_val = fr_data.get("funding_rate")
        
        # K-line
        kline_analysis = {}
        for interval in ["15m", "1h", "4h"]:
            klines = binance_klines(pair, interval)
            if klines:
                kline_analysis[interval] = analyze_klines(klines)
        
        current_price = kline_analysis.get("15m", {}).get("price") if kline_analysis.get("15m") else None
        
        fr_str = f"{float(fr_val)*100:.4f}%" if fr_val else "N/A"
        price_str = f"${current_price}" if current_price else "N/A"
        
        # Format OI lines as table
        oi_lines = []
        for d in DURATIONS:
            v = oi_vals[d]
            usd = oi_val_usd[d]
            if v is not None:
                vf = float(v)
                icon = "🟢" if vf >= 0 else "🔴"
                pct_str = f"{icon}{vf:+.2f}%"
                if usd is not None:
                    usd_signed = abs(float(usd)) if vf >= 0 else -abs(float(usd))
                    usd_str = fmt_num(usd_signed)
                else:
                    usd_str = "—"
                oi_lines.append((d, pct_str, usd_str))
            else:
                oi_lines.append((d, "—", "—"))
        
        # Format netflow line
        nf_parts = []
        for d in ["1h", "4h", "8h", "24h"]:
            v = nf_vals[d]
            if v is not None:
                nf_parts.append(f"{d}:{fmt_num(v)}")
            else:
                nf_parts.append(f"{d}:—")
        
        # Build OI table rows
        oi_table = ""
        for d, pct, usd in oi_lines:
            oi_table += f"\n│ {d:>4}  │ {pct:<14} │ {usd:>10} │"
        
        s = f"""```
┌──────────────────────────────────────┐
│ 🪙 {symbol:<8} Score:{score:.1f}  Peak:{max_score:.1f}
│ Price:{price_str}  Entry:${start_price}
│ Return:{increase:.1f}%  FR:{fr_str}
├─ OI Changes ──────────────────────────────┤
│ Period│ Change         │    Value     │{oi_table}
├─ Inst. Flows ──────────────────────────┤
│ {' │ '.join(nf_parts)}
├─ K-line ──────────────────────────────────┤"""
        
        for interval in ["15m", "1h", "4h"]:
            ka = kline_analysis.get(interval)
            if ka:
                s += f"\n│ {interval}: {ka['trend']} Bull/Bear:{ka['bulls']}/{ka['bears']} {ka['ma_align']}"
                s += f"\n│     Vol:{ka['vol_chg']:+.1f}% Sup:{ka['support']} Res:{ka['resistance']}"
        
        s += "\n└──────────────────────────────────────┘\n```"
        sections.append(s)
    
    # 4. OI Rankings
    for d in ["1h", "4h", "24h"]:
        lines = [f"╔═ OI Rank {d} ══════════════════════════╗"]
        
        lines.append("║ 📈 Top 8 Increase:")
        top = oi_top[d]
        if top and top.get("success"):
            for item in top["data"].get("positions", [])[:8]:
                sym = item.get("symbol", "?").replace("USDT", "")
                pct = item.get("oi_delta_percent", 0)
                usd = item.get("oi_delta_value")
                usd_str = fmt_num(usd) if usd is not None else ""
                lines.append(f"║  {item.get('rank','-')}. {sym:<10} {float(pct):+.2f}%  {usd_str}")
        
        lines.append("║ 📉 Top 8 Decrease:")
        low = oi_low[d]
        if low and low.get("success"):
            for item in low["data"].get("positions", [])[:8]:
                sym = item.get("symbol", "?").replace("USDT", "")
                pct = item.get("oi_delta_percent", 0)
                usd = item.get("oi_delta_value")
                usd_str = fmt_num(usd) if usd is not None else ""
                lines.append(f"║  {item.get('rank','-')}. {sym:<10} {float(pct):+.2f}%  {usd_str}")
        
        lines.append("╚══════════════════════════════════════╝")
        sections.append("```\n" + "\n".join(lines) + "\n```")
    
    # 5. Netflow Rankings
    for d in ["1h", "4h", "24h"]:
        lines = [f"╔═ Inst. Flow {d} ════════════════════════╗"]
        
        lines.append("║ 💰 Top 8 Inflow:")
        top = nf_top[d]
        if top and top.get("success"):
            for item in top["data"].get("netflows", [])[:8]:
                sym = item.get("symbol", "?").replace("USDT", "")
                amt = item.get("amount", 0)
                lines.append(f"║  {item.get('rank','-')}. {sym:<10} {fmt_num(amt)}")
        
        lines.append("║ 💸 Top 8 Outflow:")
        low = nf_low[d]
        if low and low.get("success"):
            for item in low["data"].get("netflows", [])[:8]:
                sym = item.get("symbol", "?").replace("USDT", "")
                amt = item.get("amount", 0)
                lines.append(f"║  {item.get('rank','-')}. {sym:<10} {fmt_num(amt)}")
        
        lines.append("╚══════════════════════════════════════╝")
        sections.append("```\n" + "\n".join(lines) + "\n```")
    
    # 6. Summary
    summary_lines = ["╔══════════════════════════════════════╗",
                      "║  📋 Summary & Signals                    ║",
                      "╠══════════════════════════════════════╣"]
    for coin in coins:
        symbol = coin["pair"].replace("USDT", "")
        score = coin["score"]
        increase = coin["increase_percent"]
        # Check if coin has positive OI on 1h
        oi_1h = None
        if oi_top.get("1h") and oi_top["1h"].get("success"):
            found = find_in_list(oi_top["1h"]["data"].get("positions", []), "symbol", coin["pair"])
            if found:
                oi_1h = found.get("oi_delta_percent", 0)
        
        if oi_1h and float(oi_1h) > 1:
            signal = "📈 Strong OI increase, watch for long"
        elif oi_1h and float(oi_1h) < -1:
            signal = "📉 OI declining, watch for risk"
        else:
            signal = "↔️ OI stable, wait and see"
        
        summary_lines.append(f"║ • {symbol}: Score:{score:.1f} Return:{increase:.1f}%")
        summary_lines.append(f"║   {signal}")
    
    summary_lines.append("╚══════════════════════════════════════╝")
    sections.append("```\n" + "\n".join(summary_lines) + "\n```")
    
    # Output with separator
    print("===SECTION===".join(sections))

if __name__ == "__main__":
    main()
