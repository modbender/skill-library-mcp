"""
Polymarket Scanner - Automated prediction market trader via Simmer API
Usage:
  python scanner.py              # Auto-scan and trade
  python scanner.py --status     # Check agent balance
  python scanner.py --positions  # List active positions
"""

import requests
import json
import os
import sys
from datetime import datetime, timezone

SIMMER_API_KEY = os.environ.get("SIMMER_API_KEY")
if not SIMMER_API_KEY:
    print("ERROR: Set SIMMER_API_KEY environment variable")
    print("Get your key at https://simmer.markets")
    sys.exit(1)

HEADERS = {"Authorization": f"Bearer {SIMMER_API_KEY}", "Content-Type": "application/json"}
BASE_URL = "https://api.simmer.markets/api/sdk"
LOG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "trading_log.jsonl")

# Trading rules - configurable
CONFIG = {
    "min_score": int(os.environ.get("SCANNER_MIN_SCORE", "25")),
    "min_divergence": float(os.environ.get("SCANNER_MIN_DIVERGENCE", "0.03")),
    "max_positions": int(os.environ.get("SCANNER_MAX_POSITIONS", "5")),
    "trade_pct": float(os.environ.get("SCANNER_TRADE_PCT", "0.05")),
    "max_trade": float(os.environ.get("SCANNER_MAX_TRADE", "500")),
    "min_balance": float(os.environ.get("SCANNER_MIN_BALANCE", "100")),
    "max_spread_warning": float(os.environ.get("SCANNER_MAX_SPREAD", "10")),
}


def log(msg, data=None):
    entry = {"time": datetime.now(timezone.utc).isoformat(), "msg": msg}
    if data:
        entry["data"] = data
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    except Exception:
        pass
    print(f"[{entry['time'][:19]}] {msg}")


def api_get(path):
    r = requests.get(f"{BASE_URL}/{path}", headers=HEADERS, timeout=15)
    r.raise_for_status()
    return r.json()


def api_post(path, payload):
    r = requests.post(f"{BASE_URL}/{path}", headers=HEADERS, json=payload, timeout=15)
    r.raise_for_status()
    return r.json()


def cmd_status():
    status = api_get("agents/me")
    balance = status.get("balance", 0)
    name = status.get("name", "unknown")
    print(f"\nAgent: {name}")
    print(f"Balance: ${balance:,.2f} SIM")
    print(f"Real trading: {'enabled' if status.get('real_trading_enabled') else 'disabled'}")
    return status


def cmd_positions():
    positions = api_get("positions")
    active = [p for p in positions.get("positions", []) if p.get("shares", 0) > 0.01]
    print(f"\nActive positions: {len(active)}")
    for p in active:
        q = p.get("question", p.get("market_id", "?"))[:60]
        side = p.get("side", "?")
        shares = p.get("shares", 0)
        cost = p.get("cost_basis", 0)
        current = p.get("current_value", cost)
        pnl = current - cost
        pnl_pct = (pnl / cost * 100) if cost > 0 else 0
        print(f"  [{side.upper():3s}] {q}")
        print(f"         shares={shares:.1f}  cost=${cost:.2f}  pnl=${pnl:+.2f} ({pnl_pct:+.1f}%)")
    return active


def cmd_scan():
    log("=== Market scan started ===")

    # 1. Status
    status = api_get("agents/me")
    balance = status.get("balance", 0)
    log(f"Balance: ${balance:.2f} SIM")

    if balance < CONFIG["min_balance"]:
        log(f"Balance below ${CONFIG['min_balance']}, stopping")
        return

    # 2. Positions
    positions = api_get("positions")
    active = [p for p in positions.get("positions", []) if p.get("shares", 0) > 0.01]
    log(f"Active positions: {len(active)}")

    if len(active) >= CONFIG["max_positions"]:
        log(f"Max positions ({CONFIG['max_positions']}) reached, skipping")
        return

    # 3. Scan
    opps = api_get("markets/opportunities?limit=20")
    opportunities = opps.get("opportunities", [])
    log(f"Found {len(opportunities)} opportunities")

    trades = 0
    held_ids = {p.get("market_id") for p in active}

    for opp in opportunities:
        score = opp.get("opportunity_score", 0)
        divergence = abs(opp.get("divergence", 0))
        question = opp.get("question", "")
        market_id = opp.get("id", "")
        side = opp.get("side", opp.get("recommended_side", "yes"))
        prob = opp.get("current_probability", 0)
        ext = opp.get("external_price_yes")
        resolves = opp.get("resolves_at", "")

        if score < CONFIG["min_score"]:
            continue
        if divergence < CONFIG["min_divergence"]:
            continue
        if market_id in held_ids:
            continue

        # Check warnings
        try:
            ctx = api_get(f"context/{market_id}")
            warnings = ctx.get("warnings", [])
            serious = [w for w in warnings
                       if "Wide spread" in str(w)
                       and any(c.isdigit() for c in str(w))
                       and float(''.join(c for c in str(w).split("(")[-1] if c.isdigit() or c == '.') or 99) > CONFIG["max_spread_warning"]]
            if serious:
                log(f"Skip (warnings): {question[:50]}")
                continue
        except Exception:
            continue

        # Calculate trade amount
        amount = min(balance * CONFIG["trade_pct"], CONFIG["max_trade"])

        reasoning = (
            f"Auto-scan: score={score}, div={divergence:.1%}, "
            f"prob={prob:.2%} vs ext={ext}, resolves={resolves[:10]}"
        )

        try:
            result = api_post("trade", {
                "market_id": market_id,
                "side": side,
                "amount": amount,
                "reasoning": reasoning,
                "source": "sdk:polymarket-scanner"
            })
            log(f"TRADE: {question[:50]}", {
                "side": side, "amount": amount, "score": score, "result": result
            })
            trades += 1
            held_ids.add(market_id)

            if len(held_ids) >= CONFIG["max_positions"]:
                break
        except Exception as e:
            log(f"Trade failed: {question[:50]}", {"error": str(e)})

    log(f"=== Scan complete: {trades} trades executed ===")


if __name__ == "__main__":
    try:
        if "--status" in sys.argv:
            cmd_status()
        elif "--positions" in sys.argv:
            cmd_positions()
        else:
            cmd_scan()
    except Exception as e:
        log(f"Scanner error: {e}")
        sys.exit(1)
