#!/usr/bin/env python3
"""Spartan P&L Tracker v2 - Uses slug/question search for price matching."""
import os, sys, json, logging
from datetime import datetime, timezone
from pathlib import Path
from collections import defaultdict

WORKSPACE = Path(__file__).resolve().parent
os.chdir(WORKSPACE)
from dotenv import load_dotenv
load_dotenv(WORKSPACE / ".env")

import requests as http_requests
from web3 import Web3
from py_clob_client.client import ClobClient

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger("pnl")

PRIVATE_KEY = os.environ["PRIVATE_KEY"]
LOG_PATH = WORKSPACE / "trades.jsonl"
PNL_PATH = WORKSPACE / "pnl_report.json"
USDC_E = "0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174"

w3 = Web3(Web3.HTTPProvider('https://polygon-rpc.com', request_kwargs={'timeout':15}))
acct = w3.eth.account.from_key(PRIVATE_KEY)
abi = [{"inputs":[{"name":"a","type":"address"}],"name":"balanceOf","outputs":[{"name":"","type":"uint256"}],"stateMutability":"view","type":"function"}]
usdc_contract = w3.eth.contract(address=Web3.to_checksum_address(USDC_E), abi=abi)
usdc_balance = usdc_contract.functions.balanceOf(acct.address).call() / 1e6

client = ClobClient("https://clob.polymarket.com", key=PRIVATE_KEY, chain_id=137, signature_type=0)
creds = client.create_or_derive_api_creds()
client.set_api_creds(creds)

# Load trades, group by market
trades = []
if LOG_PATH.exists():
    for line in LOG_PATH.read_text().strip().split("\n"):
        try: trades.append(json.loads(line))
        except: pass

positions = defaultdict(lambda: {"side": None, "total_cost": 0.0, "total_shares": 0.0, "orders": []})
for t in trades:
    mkt = t.get("market","")
    p = positions[mkt]
    p["side"] = t.get("side")
    p["total_cost"] += float(t.get("size_usdc", 0))
    p["total_shares"] += float(t.get("shares", 0))
    p["orders"].append(t.get("order_id",""))

log.info(f"Loaded {len(positions)} positions from {len(trades)} trade records")

# For each position, look up current price via gamma search
def search_market(question):
    """Search gamma API for a market by question keywords."""
    # Use first 5 significant words as search
    words = [w for w in question.split() if len(w) > 2][:6]
    query = " ".join(words)
    try:
        resp = http_requests.get("https://gamma-api.polymarket.com/markets",
            params={"limit": 5, "closed": "false", "q": query}, timeout=15)
        results = resp.json()
        if results:
            return results[0]
        # Try closed markets too
        resp = http_requests.get("https://gamma-api.polymarket.com/markets",
            params={"limit": 5, "closed": "true", "q": query}, timeout=15)
        results = resp.json()
        if results:
            return results[0]
    except:
        pass
    return None

# Also try fetching broader set
all_market_data = {}
for offset in range(0, 1200, 100):
    try:
        resp = http_requests.get("https://gamma-api.polymarket.com/markets",
            params={"limit":100, "offset":offset}, timeout=30)
        batch = resp.json()
        if not batch: break
        for m in batch:
            all_market_data[m.get("question","")] = m
    except: break

# Also closed
for offset in range(0, 400, 100):
    try:
        resp = http_requests.get("https://gamma-api.polymarket.com/markets",
            params={"limit":100, "offset":offset, "closed":"true"}, timeout=30)
        batch = resp.json()
        if not batch: break
        for m in batch:
            all_market_data[m.get("question","")] = m
    except: break

log.info(f"Fetched {len(all_market_data)} markets from gamma API")

def find_market(question):
    """Find market data by exact match or fuzzy."""
    if question in all_market_data:
        return all_market_data[question]
    # Fuzzy: find best substring match
    q_lower = question.lower().strip()
    for k, v in all_market_data.items():
        if k.lower().strip() == q_lower:
            return v
    # Partial match
    for k, v in all_market_data.items():
        if q_lower[:40] in k.lower():
            return v
    return search_market(question)

total_invested = 0
total_current_value = 0
resolved_pnl = 0
open_positions = []
resolved_positions = []

for mkt_name, pos in positions.items():
    cost = pos["total_cost"]
    shares = pos["total_shares"]
    side = pos["side"]
    total_invested += cost

    m = find_market(mkt_name)
    if not m:
        open_positions.append({"market": mkt_name[:60], "side": side, "cost": round(cost,2),
            "shares": round(shares,1), "value": round(cost,2), "pnl": 0, "status": "no-data"})
        total_current_value += cost
        continue

    try:
        prices = json.loads(m.get("outcomePrices","[]"))
        yes_p = float(prices[0]) if prices else 0
        no_p = float(prices[1]) if len(prices)>1 else 0
    except:
        yes_p, no_p = 0.5, 0.5

    closed = m.get("closed", False)
    # Check resolution
    if closed:
        if yes_p > 0.99:
            winner = "YES"
        elif no_p > 0.99:
            winner = "NO"
        else:
            winner = ""

        if winner == side:
            payout = shares
            pnl = payout - cost
            status = "WON"
        elif winner and winner != side:
            payout = 0
            pnl = -cost
            status = "LOST"
        else:
            payout = shares * (yes_p if side == "YES" else no_p)
            pnl = payout - cost
            status = "closed"

        resolved_pnl += pnl
        total_current_value += payout
        resolved_positions.append({"market": mkt_name[:60], "side": side, "cost": round(cost,2),
            "payout": round(payout,2), "pnl": round(pnl,2), "status": status})
    else:
        cur_price = yes_p if side == "YES" else no_p
        value = shares * cur_price
        pnl = value - cost
        total_current_value += value
        open_positions.append({"market": mkt_name[:60], "side": side, "cost": round(cost,2),
            "shares": round(shares,1), "value": round(value,2), "pnl": round(pnl,2), "status": "open"})

# Check open orders
open_orders = client.get_orders()
open_order_value = sum(float(o.get('price',0)) * (float(o.get('original_size',0)) - float(o.get('size_matched',0))) for o in open_orders)

# Sort open by P&L
open_positions.sort(key=lambda x: x["pnl"])

report = {
    "timestamp": datetime.now(timezone.utc).isoformat(),
    "usdc_balance": round(usdc_balance, 4),
    "open_order_value": round(open_order_value, 2),
    "total_invested": round(total_invested, 2),
    "portfolio_mtm": round(total_current_value, 2),
    "unrealized_pnl": round(total_current_value - total_invested, 2),
    "resolved_pnl": round(resolved_pnl, 2),
    "total_value": round(usdc_balance + total_current_value + open_order_value, 2),
    "num_open": len(open_positions),
    "num_resolved": len(resolved_positions),
    "open": open_positions,
    "resolved": resolved_positions
}

with open(PNL_PATH, "w") as f:
    json.dump(report, f, indent=2)

print(f"\n{'='*65}")
print(f" POLYMARKET TRADER P&L — {report['timestamp'][:19]} UTC")
print(f"{'='*65}")
print(f" USDC.e liquid:      ${usdc_balance:>8.2f}")
print(f" Open order value:   ${open_order_value:>8.2f}")
print(f" Position value:     ${total_current_value:>8.2f}")
print(f" Total portfolio:    ${usdc_balance + total_current_value + open_order_value:>8.2f}")
print(f" Total cost basis:   ${total_invested:>8.2f}")
print(f" Unrealized P&L:     ${total_current_value - total_invested:>+8.2f}")
print(f" Resolved P&L:       ${resolved_pnl:>+8.2f}")
print(f" Positions:          {len(open_positions)} open / {len(resolved_positions)} resolved")
print(f"{'='*65}")

if resolved_positions:
    print(f"\n RESOLVED:")
    for p in resolved_positions:
        print(f"  {p['status']:6} {p['side']:3} cost=${p['cost']:5.2f} pay=${p['payout']:5.2f} pnl=${p['pnl']:+6.2f} | {p['market']}")

print(f"\n OPEN (worst to best):")
for p in open_positions:
    print(f"  {p['side']:3} cost=${p['cost']:5.2f} val=${p['value']:5.2f} pnl=${p['pnl']:+6.2f} | {p['market']}")

print(f"{'='*65}")
