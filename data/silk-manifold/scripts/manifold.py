#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "requests>=2.28.0",
# ]
# ///
"""Manifold Markets CLI — search, trade, and manage prediction markets."""

import argparse
import json
import os
from pathlib import Path
import sys
from urllib.parse import quote

import requests

# Auto-load .env from data/ directory next to scripts/
_data_env = Path(__file__).resolve().parent.parent / "data" / ".env"
if _data_env.exists():
    for line in _data_env.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            v = v.strip().strip('"').strip("'")
            os.environ.setdefault(k.strip(), v)

BASE = "https://api.manifold.markets/v0"
KEY = os.environ.get("MANIFOLD_API_KEY", "")


def headers():
    h = {"Content-Type": "application/json"}
    if KEY:
        h["Authorization"] = f"Key {KEY}"
    return h


def api_get(path, params=None):
    r = requests.get(f"{BASE}{path}", headers=headers(), params=params, timeout=30)
    r.raise_for_status()
    return r.json()


def api_post(path, body=None):
    if not KEY:
        print(json.dumps({"error": "MANIFOLD_API_KEY not set"}))
        sys.exit(1)
    r = requests.post(f"{BASE}{path}", headers=headers(), json=body or {}, timeout=30)
    r.raise_for_status()
    return r.json()


# ── Commands ──────────────────────────────────────────────────────────


def cmd_me(_args):
    """Get authenticated user profile and balance."""
    data = api_get("/me")
    print(json.dumps(data, indent=2))


def cmd_balance(_args):
    """Show current mana balance."""
    data = api_get("/me")
    out = {
        "username": data.get("username"),
        "balance": data.get("balance"),
        "totalDeposits": data.get("totalDeposits"),
    }
    print(json.dumps(out, indent=2))


def cmd_search(args):
    """Search for markets."""
    params = {"term": args.term, "limit": args.limit}
    if args.filter:
        params["filter"] = args.filter
    if args.sort:
        params["sort"] = args.sort
    if args.contract_type:
        params["contractType"] = args.contract_type
    data = api_get("/search-markets", params)
    results = []
    for m in data:
        entry = {
            "id": m["id"],
            "question": m["question"],
            "url": m["url"],
            "probability": m.get("probability"),
            "volume": m.get("volume"),
            "volume24Hours": m.get("volume24Hours"),
            "uniqueBettorCount": m.get("uniqueBettorCount"),
            "closeTime": m.get("closeTime"),
            "isResolved": m.get("isResolved"),
            "outcomeType": m.get("outcomeType"),
        }
        if m.get("resolution"):
            entry["resolution"] = m["resolution"]
        results.append(entry)
    print(json.dumps(results, indent=2))


def cmd_market(args):
    """Get full market details by ID or slug."""
    identifier = args.id
    # Try slug first if it looks like a slug (contains no uppercase, has hyphens)
    if "-" in identifier and identifier == identifier.lower():
        try:
            data = api_get(f"/slug/{quote(identifier, safe='')}")
            print(json.dumps(data, indent=2))
            return
        except requests.HTTPError:
            pass
    data = api_get(f"/market/{quote(identifier, safe='')}")
    print(json.dumps(data, indent=2))


def cmd_prob(args):
    """Get current probability for a market."""
    data = api_get(f"/market/{quote(args.id, safe='')}")
    out = {
        "id": data["id"],
        "question": data["question"],
        "probability": data.get("probability"),
        "outcomeType": data.get("outcomeType"),
    }
    if data.get("answers"):
        out["answers"] = [
            {"id": a["id"], "text": a["text"], "probability": a.get("probability")}
            for a in data["answers"]
        ]
    print(json.dumps(out, indent=2))


def cmd_bet(args):
    """Place a bet (market order or limit order)."""
    body = {
        "amount": args.amount,
        "contractId": args.contract_id,
        "outcome": args.outcome.upper(),
    }
    if args.limit_prob is not None:
        body["limitProb"] = args.limit_prob
    if args.answer_id:
        body["answerId"] = args.answer_id
    if args.dry_run:
        body["dryRun"] = True
    if args.expires_ms:
        body["expiresMillisAfter"] = args.expires_ms
    data = api_post("/bet", body)
    print(json.dumps(data, indent=2))


def cmd_sell(args):
    """Sell shares in a market."""
    body = {}
    if args.outcome:
        body["outcome"] = args.outcome.upper()
    if args.shares is not None:
        body["shares"] = args.shares
    if args.answer_id:
        body["answerId"] = args.answer_id
    data = api_post(f"/market/{quote(args.contract_id, safe='')}/sell", body)
    print(json.dumps(data, indent=2))


def cmd_cancel(args):
    """Cancel a limit order."""
    data = api_post(f"/bet/cancel/{quote(args.bet_id, safe='')}")
    print(json.dumps(data, indent=2))


def cmd_portfolio(args):
    """Get portfolio metrics."""
    user_id = args.user_id
    if not user_id:
        me = api_get("/me")
        user_id = me["id"]
    data = api_get("/get-user-portfolio", {"userId": user_id})
    print(json.dumps(data, indent=2))


def cmd_positions(args):
    """Get positions for a market."""
    params = {}
    if args.user_id:
        params["userId"] = args.user_id
    if args.top:
        params["top"] = args.top
    if args.order:
        params["order"] = args.order
    data = api_get(
        f"/market/{quote(args.contract_id, safe='')}/positions", params
    )
    print(json.dumps(data, indent=2))


def cmd_bets(args):
    """List bets with optional filters."""
    params = {"limit": args.limit}
    if args.contract_id:
        params["contractId"] = args.contract_id
    if args.username:
        params["username"] = args.username
    if args.kinds:
        params["kinds"] = args.kinds
    data = api_get("/bets", params)
    print(json.dumps(data, indent=2))


def cmd_my_positions(args):
    """Get the authenticated user's positions with contract data."""
    me = api_get("/me")
    params = {
        "userId": me["id"],
        "limit": args.limit,
    }
    if args.order:
        params["order"] = args.order
    data = api_get("/get-user-contract-metrics-with-contracts", params)
    print(json.dumps(data, indent=2))


# ── CLI ───────────────────────────────────────────────────────────────


def main():
    p = argparse.ArgumentParser(description="Manifold Markets CLI")
    sub = p.add_subparsers(dest="command", required=True)

    # me
    sub.add_parser("me", help="Get your profile")

    # balance
    sub.add_parser("balance", help="Show mana balance")

    # search
    s = sub.add_parser("search", help="Search markets")
    s.add_argument("term", nargs="?", default="", help="Search query")
    s.add_argument("--filter", choices=["all", "open", "closed", "resolved", "closing-week", "closing-month", "closing-day"])
    s.add_argument("--sort", choices=["most-popular", "newest", "score", "daily-score", "24-hour-vol", "liquidity", "close-date", "prob-descending", "prob-ascending"])
    s.add_argument("--contract-type", choices=["ALL", "BINARY", "MULTIPLE_CHOICE", "BOUNTY", "POLL"])
    s.add_argument("--limit", type=int, default=10)

    # market
    s = sub.add_parser("market", help="Get market details")
    s.add_argument("id", help="Market ID or slug")

    # prob
    s = sub.add_parser("prob", help="Get market probability")
    s.add_argument("id", help="Market ID")

    # bet
    s = sub.add_parser("bet", help="Place a bet")
    s.add_argument("contract_id", help="Market/contract ID")
    s.add_argument("amount", type=float, help="Mana amount")
    s.add_argument("outcome", choices=["YES", "NO", "yes", "no"], help="YES or NO")
    s.add_argument("--limit-prob", type=float, help="Limit order probability (0.01-0.99)")
    s.add_argument("--answer-id", help="Answer ID for multiple-choice markets")
    s.add_argument("--dry-run", action="store_true", help="Simulate without executing")
    s.add_argument("--expires-ms", type=int, help="Limit order expiry in ms from now")

    # sell
    s = sub.add_parser("sell", help="Sell shares")
    s.add_argument("contract_id", help="Market/contract ID")
    s.add_argument("--outcome", choices=["YES", "NO"])
    s.add_argument("--shares", type=float, help="Number of shares (omit to sell all)")
    s.add_argument("--answer-id", help="Answer ID for multiple-choice markets")

    # cancel
    s = sub.add_parser("cancel", help="Cancel a limit order")
    s.add_argument("bet_id", help="Bet/order ID to cancel")

    # portfolio
    s = sub.add_parser("portfolio", help="Get portfolio metrics")
    s.add_argument("--user-id", help="User ID (default: self)")

    # positions
    s = sub.add_parser("positions", help="Get positions for a market")
    s.add_argument("contract_id", help="Market/contract ID")
    s.add_argument("--user-id", help="Filter to specific user")
    s.add_argument("--top", type=int, help="Number of top positions")
    s.add_argument("--order", choices=["shares", "profit"])

    # bets
    s = sub.add_parser("bets", help="List bets")
    s.add_argument("--contract-id", help="Filter by market")
    s.add_argument("--username", help="Filter by username")
    s.add_argument("--kinds", choices=["open-limit"], help="Filter bet kinds")
    s.add_argument("--limit", type=int, default=20)

    # my-positions
    s = sub.add_parser("my-positions", help="Get your positions with contracts")
    s.add_argument("--limit", type=int, default=20)
    s.add_argument("--order", choices=["lastBetTime", "profit"])

    args = p.parse_args()
    cmd_map = {
        "me": cmd_me,
        "balance": cmd_balance,
        "search": cmd_search,
        "market": cmd_market,
        "prob": cmd_prob,
        "bet": cmd_bet,
        "sell": cmd_sell,
        "cancel": cmd_cancel,
        "portfolio": cmd_portfolio,
        "positions": cmd_positions,
        "bets": cmd_bets,
        "my-positions": cmd_my_positions,
    }
    try:
        cmd_map[args.command](args)
    except requests.HTTPError as e:
        err = {"error": str(e)}
        try:
            err["detail"] = e.response.json()
        except Exception:
            err["detail"] = e.response.text
        print(json.dumps(err, indent=2))
        sys.exit(1)
    except Exception as e:
        print(json.dumps({"error": str(e)}, indent=2))
        sys.exit(1)


if __name__ == "__main__":
    main()
