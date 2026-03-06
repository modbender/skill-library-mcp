#!/usr/bin/env python3
"""Manual Trade Placement — polymarket-manual-trade skill.

Place trades on Polymarket by market ID or full Polymarket URL.
Supports FAK (instant fill) and GTC (limit order on book).

Usage:
    python3 manual_trade.py --market <market_id_or_url> --side YES --amount 10
    python3 manual_trade.py --market <url> --side NO --amount 20 --order GTC --price 0.35
    python3 manual_trade.py --market <id> --side YES --amount 10 --dry-run
"""
import argparse
import json
import os
import sys
import urllib.request

try:
    from dotenv import load_dotenv
    load_dotenv("/root/.openclaw/.env")
except Exception:
    pass

from simmer_sdk import SimmerClient

SKILL_SLUG   = "polymarket-manual-trade"
TRADE_SOURCE = f"sdk:{SKILL_SLUG}"

_client = None

def get_client(venue="polymarket"):
    global _client
    if _client is None:
        _client = SimmerClient(
            api_key=os.environ["SIMMER_API_KEY"],
            venue=venue,
        )
    return _client


# ── Helpers ──────────────────────────────────────────────────────────────────

def api_get(path):
    API_KEY = os.environ.get("SIMMER_API_KEY", "")
    url = f"https://api.simmer.markets{path}"
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {API_KEY}", "User-Agent": "Mozilla/5.0"})
    try:
        resp = urllib.request.urlopen(req, timeout=15)
        return json.loads(resp.read())
    except Exception:
        return None


def get_best_ask(token_id):
    """Fetch live CLOB order book. Best ask = lowest ask, best bid = highest bid."""
    try:
        url = f"https://clob.polymarket.com/book?token_id={token_id}"
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        book = json.loads(urllib.request.urlopen(req, timeout=10).read())
        asks = book.get("asks", [])
        bids = book.get("bids", [])
        # Sort to ensure correct best prices regardless of API sort order
        asks_sorted = sorted(asks, key=lambda x: float(x["price"]))
        bids_sorted = sorted(bids, key=lambda x: float(x["price"]), reverse=True)
        return {
            "best_ask": float(asks_sorted[0]["price"]) if asks_sorted else None,
            "best_bid": float(bids_sorted[0]["price"]) if bids_sorted else None,
            "ask_size": float(asks_sorted[0]["size"]) if asks_sorted else 0,
        }
    except Exception:
        return None


def normalize_tokens(market):
    """Map polymarket_token_id → clob_token_ids list."""
    if market.get("clob_token_ids"):
        return
    yes = market.get("polymarket_token_id", "")
    no  = market.get("polymarket_no_token_id", "")
    market["clob_token_ids"] = [t for t in [yes, no] if t]


def import_from_url(polymarket_url):
    """Import a Polymarket URL into Simmer and return the full market dict (with CLOB tokens)."""
    API_KEY = os.environ.get("SIMMER_API_KEY", "")
    payload = json.dumps({"polymarket_url": polymarket_url}).encode()
    req = urllib.request.Request(
        "https://api.simmer.markets/api/sdk/markets/import",
        data=payload,
        headers={"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"},
        method="POST",
    )
    try:
        resp = urllib.request.urlopen(req, timeout=30)
        data = json.loads(resp.read())
        markets = data.get("markets", [])
        if not markets:
            return None
        # Match by URL slug
        slug = polymarket_url.rstrip("/").split("/")[-1]
        matched = None
        for m in markets:
            if slug.replace("-", " ") in m.get("question", "").lower():
                matched = m
                break
        if not matched:
            matched = markets[0]

        # Import response only returns market_id/question/current_probability —
        # fetch full market to get CLOB tokens for price discovery
        market_id = matched.get("market_id")
        if market_id:
            full = api_get(f"/api/sdk/markets/{market_id}")
            if full:
                full_m = full.get("market") or full
                if full_m.get("id"):
                    return full_m
        return matched
    except Exception as e:
        print(f"  ❌ Import failed: {e}")
        return None


def resolve_market(market_input):
    """Resolve market ID or Polymarket URL → Simmer market dict."""
    if market_input.startswith("http"):
        print(f"  📥 Importing from URL...")
        return import_from_url(market_input)
    resp = api_get(f"/api/sdk/markets/{market_input}")
    if resp:
        m = resp.get("market") or resp
        if m.get("id"):
            return m
    return None


# ── Main ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Place a manual trade on Polymarket")
    parser.add_argument("--market", "-m", required=True, help="Simmer market ID or full Polymarket event URL")
    parser.add_argument("--cancel", action="store_true", help="Cancel all open orders on this market and exit")
    parser.add_argument("--cancel-side", choices=["yes", "no"], default=None, help="Cancel only YES or NO side orders")
    parser.add_argument("--side",   "-s", required=False, choices=["YES", "NO", "yes", "no"])
    parser.add_argument("--amount", "-a", type=float, default=10.0, help="Dollar amount (default $10)")
    parser.add_argument("--order",  "-o", default="FAK", choices=["FAK", "GTC", "FOK"])
    parser.add_argument("--price",  "-p", type=float, default=None, help="Limit price (auto-fetches ask+0.01 if omitted)")
    parser.add_argument("--venue",  "-v", default="polymarket", choices=["polymarket", "sim"])
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    print(f"\n{'='*55}")
    print(f"🎯  Manual Trade Placement  [{SKILL_SLUG}]")
    print(f"{'='*55}")

    market = resolve_market(args.market)
    if not market:
        print(f"  ❌ Could not resolve market: {args.market}")
        sys.exit(1)

    market_id = market.get("market_id") or market.get("id")
    question  = market.get("question", "")
    print(f"  ✅ {question[:70]}")
    print(f"     ID: {market_id}")

    # ── Cancel mode ──
    if args.cancel:
        client = get_client(venue=args.venue)
        cancel_side = args.cancel_side
        try:
            if cancel_side:
                result = client.cancel_market_orders(market_id, side=cancel_side)
                print(f"  🧹 Cancelled {cancel_side.upper()} orders on {market_id}")
            else:
                result = client.cancel_market_orders(market_id)
                print(f"  🧹 Cancelled all orders on {market_id}")
        except Exception as e:
            print(f"  ❌ Cancel failed: {e}")
            sys.exit(1)
        print(f"{'='*55}\n")
        return

    if not args.side:
        print("  ❌ --side is required for placing trades")
        sys.exit(1)

    side = args.side.upper()
    print(f"  Side: {side} | Amount: ${args.amount:.2f} | Order: {args.order} | Venue: {args.venue}")

    # CLOB price discovery
    normalize_tokens(market)
    tokens    = market.get("clob_token_ids", [])
    yes_token = tokens[0] if tokens else market.get("polymarket_token_id")
    no_token  = tokens[1] if len(tokens) > 1 else market.get("polymarket_no_token_id")
    trade_token = yes_token if side == "YES" else no_token

    limit_price = args.price
    book = get_best_ask(trade_token) if trade_token else None

    if limit_price is None:
        if book and book.get("best_ask"):
            limit_price = round(min(book["best_ask"] + 0.01, 0.97), 4)
            print(f"  📊 Book: ask={book['best_ask']} bid={book['best_bid']} → auto-price={limit_price}")
        else:
            limit_price = 0.55
            print(f"  ⚠️  No book data — using fallback price: {limit_price}")
    else:
        if book:
            print(f"  📊 Book: ask={book.get('best_ask')} bid={book.get('best_bid')} | manual price={limit_price}")

    if args.order == "GTC":
        print(f"  ℹ️  GTC: funds locked on placement, fills when market reaches {limit_price}")
    elif args.order == "FAK":
        print(f"  ℹ️  FAK: fills instantly at {limit_price}, remainder cancelled")

    if args.dry_run:
        print(f"\n  🔍 DRY RUN — {side} ${args.amount:.2f} @ {limit_price} ({args.order}) on {market_id}")
        print(f"{'='*55}\n")
        return

    print(f"\n  🚀 Placing order...")

    client = get_client(venue=args.venue)
    result = client.trade(
        market_id  = market_id,
        side       = side.lower(),
        amount     = args.amount,
        price      = limit_price,
        order_type = args.order,
        source     = TRADE_SOURCE,
        skill_slug = SKILL_SLUG,
        allow_rebuy= True,   # allow multiple buys on same market from different calls
        reasoning  = f"Manual trade: {side} ${args.amount:.2f} @ {limit_price} ({args.order})",
    )

    status = getattr(result, "order_status", "") or getattr(result, "status", "?")
    shares = getattr(result, "shares_bought", 0) or getattr(result, "shares_sold", 0) or 0
    cost   = getattr(result, "cost", 0) or 0
    err    = getattr(result, "error", "") or ""
    tid    = getattr(result, "trade_id", "") or ""

    print(f"\n{'='*55}")
    if cost > 0 or shares > 0:
        print(f"  ✅ {status.upper()} | {shares:.2f} shares | ${cost:.2f} spent")
        if tid:
            print(f"     Trade ID: {tid}")
    elif args.order == "GTC" and status == "live":
        print(f"  📬 GTC order live on book @ {limit_price} — funds locked, waiting for fill")
    else:
        print(f"  ❌ {status} | {err}")
    print(f"{'='*55}\n")


if __name__ == "__main__":
    main()
