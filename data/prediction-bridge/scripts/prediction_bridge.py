#!/usr/bin/env python3
"""
Prediction Bridge API Client

CLI tool to query the Prediction Bridge API.
Uses only Python stdlib — no pip install needed.

Usage:
    python prediction_bridge.py search "bitcoin price"
    python prediction_bridge.py events --limit 5
    python prediction_bridge.py event 1839
    python prediction_bridge.py news --limit 5
    python prediction_bridge.py stats
    python prediction_bridge.py whale-trades --limit 5
    python prediction_bridge.py whale-trades --address 0x1234...
    python prediction_bridge.py market-history polymarket 18454
    python prediction_bridge.py smart-pnl 18454
    python prediction_bridge.py top-holders 18454
    python prediction_bridge.py leaderboard
    python prediction_bridge.py user-summary 0x1234...
    python prediction_bridge.py languages

Environment:
    PREDICTION_BRIDGE_URL  Override base URL (default: https://prediction-bridge.onrender.com)
"""

import json
import os
import sys
import urllib.request
import urllib.error
import urllib.parse

BASE_URL = os.environ.get("PREDICTION_BRIDGE_URL", "https://prediction-bridge.onrender.com")
API_V1 = f"{BASE_URL}/api/v1"
API_ANALYTICS = f"{BASE_URL}/api/analytics"


def _get(url, params=None):
    if params:
        params = {k: v for k, v in params.items() if v is not None}
        if params:
            url = f"{url}?{urllib.parse.urlencode(params)}"
    req = urllib.request.Request(url, headers={"Accept": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        try:
            body = json.loads(body)
        except Exception:
            pass
        return {"error": e.code, "detail": body}
    except urllib.error.URLError as e:
        return {"error": "connection_failed", "detail": str(e.reason)}


def _post(url, data):
    payload = json.dumps(data).encode()
    req = urllib.request.Request(
        url,
        data=payload,
        headers={"Content-Type": "application/json", "Accept": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        try:
            body = json.loads(body)
        except Exception:
            pass
        return {"error": e.code, "detail": body}
    except urllib.error.URLError as e:
        return {"error": "connection_failed", "detail": str(e.reason)}


def _out(data):
    print(json.dumps(data, indent=2, ensure_ascii=False, default=str))


# ── Commands ──────────────────────────────────────────────────────────

def cmd_search(args):
    """Semantic search for prediction market events."""
    if len(args) < 1:
        print("Usage: prediction_bridge.py search <query> [--limit N] [--include-inactive]")
        sys.exit(1)

    query_parts = []
    limit = 10
    include_inactive = False
    include_markets = True
    i = 0
    while i < len(args):
        if args[i] == "--limit" and i + 1 < len(args):
            limit = int(args[i + 1])
            i += 2
        elif args[i] == "--include-inactive":
            include_inactive = True
            i += 1
        elif args[i] == "--no-markets":
            include_markets = False
            i += 1
        else:
            query_parts.append(args[i])
            i += 1

    text = " ".join(query_parts)
    if not text:
        print("Error: search query is required")
        sys.exit(1)

    body = {
        "text": text,
        "limit": limit,
        "include_inactive": include_inactive,
        "include_markets": include_markets,
    }
    _out(_post(f"{API_V1}/search/query", body))


def cmd_events(args):
    """List prediction market events (feed view with cross-platform data)."""
    params = {}
    i = 0
    while i < len(args):
        if args[i] == "--limit" and i + 1 < len(args):
            params["limit"] = args[i + 1]
            i += 2
        elif args[i] == "--offset" and i + 1 < len(args):
            params["offset"] = args[i + 1]
            i += 2
        elif args[i] == "--source" and i + 1 < len(args):
            params["source"] = args[i + 1]
            i += 2
        elif args[i] == "--status" and i + 1 < len(args):
            params["status"] = args[i + 1]
            i += 2
        elif args[i] == "--category" and i + 1 < len(args):
            params["category"] = args[i + 1]
            i += 2
        elif args[i] == "--sort" and i + 1 < len(args):
            params["sort_by"] = args[i + 1]
            i += 2
        else:
            i += 1

    if "limit" not in params:
        params["limit"] = "10"

    _out(_get(f"{API_V1}/events/feed", params))


def cmd_event(args):
    """Get detailed info for a single event by ID."""
    if len(args) < 1:
        print("Usage: prediction_bridge.py event <event_id>")
        sys.exit(1)
    event_id = args[0]
    _out(_get(f"{API_V1}/events/{event_id}"))


def cmd_news(args):
    """List recent news matched to prediction market events."""
    params = {}
    i = 0
    while i < len(args):
        if args[i] == "--limit" and i + 1 < len(args):
            params["limit"] = args[i + 1]
            i += 2
        elif args[i] == "--offset" and i + 1 < len(args):
            params["offset"] = args[i + 1]
            i += 2
        else:
            i += 1

    if "limit" not in params:
        params["limit"] = "10"

    _out(_get(f"{API_V1}/news/", params))


def cmd_stats(args):
    """Platform statistics: event counts, crawler status, volumes."""
    _out(_get(f"{API_V1}/stats/summary"))


def cmd_whale_trades(args):
    """List large on-chain trades from whale monitor."""
    params = {}
    i = 0
    while i < len(args):
        if args[i] == "--limit" and i + 1 < len(args):
            params["limit"] = args[i + 1]
            i += 2
        elif args[i] == "--offset" and i + 1 < len(args):
            params["skip"] = args[i + 1]
            i += 2
        elif args[i] == "--address" and i + 1 < len(args):
            params["address"] = args[i + 1]
            i += 2
        elif args[i] == "--min-value" and i + 1 < len(args):
            params["min_value_usd"] = args[i + 1]
            i += 2
        elif args[i] == "--asset-id" and i + 1 < len(args):
            params["asset_id"] = args[i + 1]
            i += 2
        elif args[i] == "--event-slug" and i + 1 < len(args):
            params["event_slug"] = args[i + 1]
            i += 2
        elif args[i] == "--only-alerts":
            params["only_alerts"] = "true"
            i += 1
        elif args[i] == "--sort" and i + 1 < len(args):
            params["sort_by"] = args[i + 1]
            i += 2
        else:
            i += 1

    if "limit" not in params:
        params["limit"] = "10"

    _out(_get(f"{API_V1}/whale-monitor/trades", params))


def cmd_market_history(args):
    """Get price history for a specific market."""
    if len(args) < 2:
        print("Usage: prediction_bridge.py market-history <source> <market_id> [--interval 1h]")
        sys.exit(1)

    source = args[0]
    market_id = args[1]
    params = {}
    i = 2
    while i < len(args):
        if args[i] == "--interval" and i + 1 < len(args):
            params["interval"] = args[i + 1]
            i += 2
        else:
            i += 1

    _out(_get(f"{API_V1}/market-data/{source}/{market_id}/history", params))


def cmd_market_candles(args):
    """Get OHLCV candles for a specific market."""
    if len(args) < 2:
        print("Usage: prediction_bridge.py market-candles <source> <market_id> [--interval 1h]")
        sys.exit(1)

    source = args[0]
    market_id = args[1]
    params = {}
    i = 2
    while i < len(args):
        if args[i] == "--interval" and i + 1 < len(args):
            params["interval"] = args[i + 1]
            i += 2
        else:
            i += 1

    _out(_get(f"{API_V1}/market-data/{source}/{market_id}/candles", params))


def cmd_smart_pnl(args):
    """Get Smart PnL for a market (sum of top wallets' unrealized PnL)."""
    if len(args) < 1:
        print("Usage: prediction_bridge.py smart-pnl <market_id>")
        sys.exit(1)
    market_id = args[0]
    _out(_get(f"{API_ANALYTICS}/market/{market_id}/smart-pnl"))


def cmd_top_holders(args):
    """Get detailed top holders breakdown for a market."""
    if len(args) < 1:
        print("Usage: prediction_bridge.py top-holders <market_id>")
        sys.exit(1)
    market_id = args[0]
    _out(_get(f"{API_ANALYTICS}/market/{market_id}/top-holders-detailed"))


def cmd_leaderboard(args):
    """Get top trader rankings."""
    params = {}
    i = 0
    while i < len(args):
        if args[i] == "--limit" and i + 1 < len(args):
            params["limit"] = args[i + 1]
            i += 2
        else:
            i += 1

    _out(_get(f"{API_ANALYTICS}/leaderboard", params))


def cmd_user_summary(args):
    """Get user portfolio summary by wallet address."""
    if len(args) < 1:
        print("Usage: prediction_bridge.py user-summary <wallet_address>")
        sys.exit(1)
    address = args[0]
    _out(_get(f"{API_ANALYTICS}/user/{address}/summary"))


def cmd_user_pnl(args):
    """Get user realized PnL (all time) by wallet address."""
    if len(args) < 1:
        print("Usage: prediction_bridge.py user-pnl <wallet_address>")
        sys.exit(1)
    address = args[0]
    _out(_get(f"{API_ANALYTICS}/user/{address}/pnl-all-time"))


def cmd_languages(args):
    """List supported search languages."""
    _out(_get(f"{API_V1}/search/languages"))


# ── Main ──────────────────────────────────────────────────────────────

COMMANDS = {
    "search": cmd_search,
    "events": cmd_events,
    "event": cmd_event,
    "news": cmd_news,
    "stats": cmd_stats,
    "whale-trades": cmd_whale_trades,
    "market-history": cmd_market_history,
    "market-candles": cmd_market_candles,
    "smart-pnl": cmd_smart_pnl,
    "top-holders": cmd_top_holders,
    "leaderboard": cmd_leaderboard,
    "user-summary": cmd_user_summary,
    "user-pnl": cmd_user_pnl,
    "languages": cmd_languages,
}

HELP = """Prediction Bridge API Client

Commands:
  search <query> [--limit N]              Semantic search for events
  events [--limit N] [--source X]         List events (feed view)
  event <id>                              Event detail by ID
  news [--limit N]                        Recent news with event matches
  stats                                   Platform statistics
  whale-trades [--limit N] [--address X]  On-chain whale trades
  market-history <source> <market_id>     Price history
  market-candles <source> <market_id>     OHLCV candles
  smart-pnl <market_id>                   Smart PnL (top wallets)
  top-holders <market_id>                 Detailed holder breakdown
  leaderboard [--limit N]                 Top trader rankings
  user-summary <address>                  User portfolio summary
  user-pnl <address>                      User realized PnL (all time)
  languages                               Supported search languages

Options:
  --limit N          Max results (default 10)
  --offset N         Skip N results
  --source X         Filter by platform (polymarket, kalshi, ...)
  --status X         Filter by status (active, closed, resolved)
  --category X       Filter by category
  --address X        Filter whale trades by wallet
  --min-value N      Min USD value for whale trades
  --only-alerts      Only show trades above alert threshold
  --include-inactive Include non-active events in search
  --no-markets       Exclude market data from search results

Environment:
  PREDICTION_BRIDGE_URL   Override API base URL
                          Default: https://prediction-bridge.onrender.com
"""


def main():
    if len(sys.argv) < 2 or sys.argv[1] in ("-h", "--help", "help"):
        print(HELP)
        sys.exit(0)

    cmd = sys.argv[1]
    if cmd not in COMMANDS:
        print(f"Unknown command: {cmd}")
        print(f"Available: {', '.join(COMMANDS.keys())}")
        sys.exit(1)

    COMMANDS[cmd](sys.argv[2:])


if __name__ == "__main__":
    main()
