#!/usr/bin/env python3
"""Check order books for target markets."""
import os, json, httpx
from py_clob_client.client import ClobClient
from py_clob_client.clob_types import BalanceAllowanceParams
import py_clob_client.http_helpers.helpers as clob_helpers

CLOB_HOST = "https://clob.polymarket.com"
GAMMA_API = "https://gamma-api.polymarket.com"
TOR_PROXY = "socks5://127.0.0.1:9050"
PK = os.environ.get("POLYCLAW_PRIVATE_KEY", "")
WALLET = "0x2aacf919270Ae303fD3FE8e27D96CBA250936B9F"

def patch():
    clob_helpers._http_client = httpx.Client(proxy=TOR_PROXY, timeout=30.0, follow_redirects=True)
patch()

def get_client():
    c = ClobClient(CLOB_HOST, key=PK, chain_id=137, signature_type=0, funder=WALLET)
    creds = c.create_or_derive_api_creds()
    c.set_api_creds(creds)
    return c

client = get_client()

# Target event slugs
slugs = [
    "us-strikes-iran-by",
    "fed-decision-in-march-885",
    "2026-winter-olympics-most-gold-medals",
    "who-will-trump-nominate-as-fed-chair",
]

for slug in slugs:
    resp = httpx.get(f"{GAMMA_API}/events?slug={slug}", timeout=15)
    events = resp.json()
    if not events:
        continue
    event = events[0]
    print(f"\n{'='*70}")
    print(f"EVENT: {event.get('title', slug)}")
    print(f"{'='*70}")

    for m in event.get("markets", []):
        q = m.get("question", "")
        prices = json.loads(m.get("outcomePrices", "[0,0]"))
        tokens = json.loads(m.get("clobTokenIds", '["",""]'))
        neg = m.get("negRisk", False)
        end = m.get("endDate", "")[:10]
        yes_p = float(prices[0])
        cond = m.get("conditionId", "")

        if yes_p < 0.02 or yes_p > 0.98:
            continue

        print(f"\n  {q[:70]}")
        print(f"  Mid: YES={yes_p:.3f} | end={end} | neg={neg}")
        print(f"  conditionId={cond[:40]}")

        for side_name, token_id in [("YES", tokens[0]), ("NO", tokens[1])]:
            if not token_id:
                continue
            try:
                ob = client.get_order_book(token_id)
                best_ask = float(ob.asks[0].price) if ob.asks else None
                best_bid = float(ob.bids[0].price) if ob.bids else None
                ask_sizes = [(float(a.price), float(a.size)) for a in ob.asks[:5]]
                bid_sizes = [(float(b.price), float(b.size)) for b in ob.bids[:5]]

                if best_ask and best_bid:
                    spread = best_ask - best_bid
                    sp_str = f"{spread:.3f}"
                else:
                    sp_str = "N/A"

                print(f"    {side_name}: Bid={best_bid} Ask={best_ask} Spread={sp_str}")
                if ask_sizes:
                    print(f"      Asks: {ask_sizes[:3]}")
                if bid_sizes:
                    print(f"      Bids: {bid_sizes[:3]}")
            except Exception as e:
                print(f"    {side_name}: Error - {str(e)[:60]}")
