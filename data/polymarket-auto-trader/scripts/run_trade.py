#!/usr/bin/env python3
"""Polymarket Auto-Trader - LIVE TRADING via direct CLOB API."""
import os, sys, json, time, logging
from datetime import datetime, timezone
from pathlib import Path

WORKSPACE = Path(__file__).resolve().parent
os.chdir(WORKSPACE)
from dotenv import load_dotenv
load_dotenv(WORKSPACE / ".env")

import requests as http_requests
from web3 import Web3
from py_clob_client.client import ClobClient
from py_clob_client.clob_types import OrderArgs, OrderType
from py_clob_client.order_builder.constants import BUY

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger("trader")

PRIVATE_KEY = os.environ["PRIVATE_KEY"]
LLM_API_KEY = os.environ["LLM_API_KEY"]
BUDGET_PATH = WORKSPACE / "budget_spent.txt"
LOG_PATH = WORKSPACE / "trades.jsonl"
USDC_E = "0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174"
MIN_SHARES = 5.1  # Polymarket minimum is 5

class Budget:
    def __init__(self):
        self.spent = 0.0
        if BUDGET_PATH.exists():
            try: self.spent = float(BUDGET_PATH.read_text().strip())
            except: pass
    def record(self, inp, out):
        cost = (inp/1e6)*0.25 + (out/1e6)*1.25
        self.spent += cost
        BUDGET_PATH.write_text(f"{self.spent:.6f}")
        return cost
    @property
    def remaining(self): return max(0, 5.0 - self.spent)

def get_bankroll():
    """Get actual USDC.e balance from chain."""
    try:
        w3 = Web3(Web3.HTTPProvider('https://polygon-rpc.com', request_kwargs={'timeout':15}))
        acct = w3.eth.account.from_key(PRIVATE_KEY)
        abi = [{"inputs":[{"name":"a","type":"address"}],"name":"balanceOf","outputs":[{"name":"","type":"uint256"}],"stateMutability":"view","type":"function"}]
        usdc = w3.eth.contract(address=Web3.to_checksum_address(USDC_E), abi=abi)
        bal = usdc.functions.balanceOf(acct.address).call()
        return bal / 1e6
    except Exception as e:
        log.warning(f"Failed to get balance: {e}")
        return 0

budget = Budget()
log.info(f"Budget: ${budget.spent:.4f} spent, ${budget.remaining:.4f} remaining")

bankroll = get_bankroll()
log.info(f"Bankroll (USDC.e on-chain): ${bankroll:.2f}")
if bankroll < 2:
    log.error("Not enough USDC.e to trade. Exiting.")
    sys.exit(1)

log.info("Authenticating with CLOB...")
client = ClobClient("https://clob.polymarket.com", key=PRIVATE_KEY, chain_id=137, signature_type=0)
creds = client.create_or_derive_api_creds()
client.set_api_creds(creds)
log.info("CLOB auth OK")

log.info("Scanning markets...")
all_markets = []
for offset in range(0, 500, 100):
    resp = http_requests.get("https://gamma-api.polymarket.com/markets", params={"limit": 100, "offset": offset, "active": "true", "closed": "false"}, timeout=30)
    batch = resp.json()
    if not batch: break
    for m in batch:
        try:
            prices = json.loads(m.get("outcomePrices", "[]"))
            tokens = json.loads(m.get("clobTokenIds", "[]"))
            if len(prices) >= 2 and len(tokens) >= 2:
                p0 = float(prices[0])
                if p0 < 0.05 or p0 > 0.95: continue
                all_markets.append({"question": m.get("question",""), "description": m.get("description","")[:400], "prices": [float(p) for p in prices], "tokens": tokens, "volume": float(m.get("volume",0)), "end_date": m.get("endDate","")[:10]})
        except: continue
all_markets.sort(key=lambda x: x["volume"], reverse=True)
log.info(f"Found {len(all_markets)} tradeable markets")

def evaluate(market):
    prompt = f"Estimate TRUE probability (0.0-1.0) YES wins. Be contrarian when justified.\n\nQ: {market['question']}\nDesc: {market['description'][:200]}\nYES price: {market['prices'][0]:.3f}\nEnd: {market['end_date']}\n\nReply ONLY a number."
    resp = http_requests.post("https://api.anthropic.com/v1/messages", headers={"x-api-key": LLM_API_KEY, "anthropic-version": "2023-06-01", "Content-Type": "application/json"}, json={"model": "claude-3-5-haiku-20241022", "max_tokens": 20, "messages": [{"role": "user", "content": prompt}]}, timeout=30)
    data = resp.json()
    usage = data.get("usage", {})
    cost = budget.record(usage.get("input_tokens", 300), usage.get("output_tokens", 10))
    text = data["content"][0]["text"].strip()
    for w in text.split():
        try:
            v = float(w.strip(".,;:()"))
            if 0 <= v <= 1: return v, cost
        except: continue
    return None, cost

# Check existing positions to avoid duplicating
existing = set()
if LOG_PATH.exists():
    for line in LOG_PATH.read_text().strip().split("\n"):
        try:
            d = json.loads(line)
            existing.add(d.get("market",""))
        except: pass

opportunities = []
total_eval_cost = 0
# Prioritize short-term markets
import datetime as _dt
_now = _dt.datetime.now(_dt.timezone.utc)
_short = [m for m in all_markets if m.get("end_date") and (_dt.datetime.fromisoformat(m["end_date"]+"T00:00:00+00:00") - _now).days <= 30]
_long = [m for m in all_markets if m not in _short]
all_markets_sorted = _short + _long[:max(0, 40-len(_short))]
for m in all_markets_sorted[:40]:
    if budget.remaining < 0.001: break
    if m["question"] in existing:
        continue  # skip already traded
    fair, cost = evaluate(m)
    total_eval_cost += cost
    if fair is None: continue
    mkt = m["prices"][0]
    edge = abs(fair - mkt)
    if edge > 0.05:  # higher edge threshold for quality
        log.info(f"  EDGE: {m['question'][:60]} | mkt={mkt:.3f} fair={fair:.3f} edge={edge:.3f}")
        opportunities.append((m, fair, edge))
log.info(f"Found {len(opportunities)} NEW opportunities. Eval cost: ${total_eval_cost:.4f}")

# Reserve 20% of bankroll, spread across up to 8 trades
usable = bankroll * 0.80
max_per_trade = usable / 4  # max 25% of usable per trade
trades_placed = 0
for market, fair, edge in sorted(opportunities, key=lambda x: -x[2])[:8]:
    mkt_price = market["prices"][0]
    if fair > mkt_price:
        side, token_idx = "YES", 0
        prob, price = fair, mkt_price
    else:
        side, token_idx = "NO", 1
        prob, price = 1.0 - fair, 1.0 - mkt_price
    # Kelly criterion
    b = (1 - price) / price
    f = (b * prob - (1 - prob)) / b
    if f <= 0: continue
    frac = min(f * 0.5, 0.25)  # half-Kelly, cap 25%
    size_usdc = min(frac * bankroll, max_per_trade)
    shares = round(size_usdc / price, 1)
    if shares < MIN_SHARES:
        shares = MIN_SHARES  # meet minimum
        size_usdc = shares * price
    if size_usdc > usable * 0.3:  # don't blow more than 30% on one trade
        continue
    price_rounded = round(price, 2)
    if price_rounded < 0.01: price_rounded = 0.01
    if price_rounded > 0.99: price_rounded = 0.99
    token_id = market["tokens"][token_idx]
    log.info(f"PLACING: {side} {shares}sh @ ${price_rounded} on '{market['question'][:50]}'")
    try:
        order_args = OrderArgs(token_id=token_id, price=price_rounded, size=shares, side=BUY)
        signed = client.create_order(order_args)
        resp = client.post_order(signed, OrderType.GTC)
        oid = resp.get("orderID", "unknown") if isinstance(resp, dict) else str(resp)
        status = resp.get("status", "unknown") if isinstance(resp, dict) else "unknown"
        log.info(f"ORDER {status.upper()}: {oid}")
        with open(LOG_PATH, "a") as fh:
            fh.write(json.dumps({"ts": datetime.now(timezone.utc).isoformat(), "market": market["question"], "side": side, "shares": shares, "price": price_rounded, "size_usdc": round(size_usdc,2), "edge": round(edge,4), "order_id": oid, "status": status}) + "\n")
        trades_placed += 1
    except Exception as e:
        log.error(f"Trade failed: {e}")

log.info(f"=== DONE: {trades_placed} trades placed, bankroll=${bankroll:.2f} ===")
log.info(f"Inference budget: ${budget.spent:.4f} spent, ${budget.remaining:.4f} remaining")
