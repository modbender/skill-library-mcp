#!/usr/bin/env python3
"""
Find arbitrage opportunities across exchanges.

Usage:
    # Basic - find BTC/USDT opportunities
    python find_arb_opps.py --base BTC --quote USDT

    # Include fungible tokens (BTC = WBTC, USDT = USDC)
    python find_arb_opps.py --base BTC,WBTC --quote USDT,USDC

    # Filter by connectors
    python find_arb_opps.py --base BTC --quote USDT --connectors binance,kraken

    # Minimum spread filter
    python find_arb_opps.py --base ETH --quote USDT --min-spread 0.1

Environment:
    HUMMINGBOT_API_URL - API base URL (default: http://localhost:8000)
    API_USER - API username (default: admin)
    API_PASS - API password (default: admin)
"""

import argparse
import base64
import json
import os
import sys
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed


def load_env():
    """Load environment from .env files."""
    for path in ["hummingbot-api/.env", os.path.expanduser("~/.hummingbot/.env"), ".env"]:
        if os.path.exists(path):
            with open(path) as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        key, value = line.split("=", 1)
                        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))
            break


def get_api_config():
    """Get API configuration from environment."""
    load_env()
    return {
        "url": os.environ.get("HUMMINGBOT_API_URL", "http://localhost:8000"),
        "user": os.environ.get("API_USER", "admin"),
        "password": os.environ.get("API_PASS", "admin"),
    }


def api_request(method: str, endpoint: str, data: dict | None = None, timeout: int = 30) -> dict:
    """Make authenticated API request."""
    config = get_api_config()
    url = f"{config['url']}{endpoint}"

    credentials = base64.b64encode(f"{config['user']}:{config['password']}".encode()).decode()
    headers = {
        "Authorization": f"Basic {credentials}",
        "Content-Type": "application/json",
    }

    body = json.dumps(data).encode() if data else None
    req = urllib.request.Request(url, data=body, headers=headers, method=method)

    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        error_body = e.read().decode() if e.fp else ""
        raise RuntimeError(f"HTTP {e.code}: {error_body}")
    except urllib.error.URLError as e:
        raise RuntimeError(f"Connection failed: {e.reason}")


def get_available_connectors() -> list[str]:
    """Get list of available connectors from API."""
    try:
        result = api_request("GET", "/connectors/")
        # API returns a list directly
        if isinstance(result, list):
            return result
        return []
    except RuntimeError as e:
        print(f"Warning: Could not fetch connectors: {e}", file=sys.stderr)
        return []


def get_connector_trading_pairs(connector: str) -> list[str]:
    """Get trading pairs for a connector via trading-rules endpoint."""
    try:
        result = api_request("GET", f"/connectors/{connector}/trading-rules", timeout=15)
        # API returns dict with pair names as keys
        if isinstance(result, dict) and "detail" not in result:
            return list(result.keys())
        return []
    except RuntimeError:
        return []


def fetch_prices(connector: str, trading_pairs: list[str]) -> dict:
    """Fetch prices for trading pairs on a connector."""
    try:
        result = api_request("POST", "/market-data/prices", {
            "connector_name": connector,
            "trading_pairs": trading_pairs,
        }, timeout=15)
        # API returns {"connector": ..., "prices": {...}, "timestamp": ...}
        if "prices" in result:
            return result["prices"]
        return result
    except RuntimeError as e:
        return {"error": str(e)}


def find_matching_pairs(trading_pairs: list[str], base_tokens: list[str], quote_tokens: list[str]) -> list[str]:
    """Find trading pairs that match base/quote token combinations."""
    matches = []
    base_set = {t.upper() for t in base_tokens}
    quote_set = {t.upper() for t in quote_tokens}

    for pair in trading_pairs:
        # Handle both BTC-USDT and BTC/USDT formats
        if "-" in pair:
            base, quote = pair.upper().split("-", 1)
        elif "/" in pair:
            base, quote = pair.upper().split("/", 1)
        else:
            continue

        if base in base_set and quote in quote_set:
            matches.append(pair)

    return matches


def format_price(price: float) -> str:
    """Format price for display."""
    if price >= 1000:
        return f"${price:,.2f}"
    elif price >= 1:
        return f"${price:.4f}"
    else:
        return f"${price:.8f}"


def main():
    parser = argparse.ArgumentParser(description="Find arbitrage opportunities across exchanges")
    parser.add_argument("--base", required=True, help="Base token(s), comma-separated (e.g., BTC,WBTC)")
    parser.add_argument("--quote", required=True, help="Quote token(s), comma-separated (e.g., USDT,USDC)")
    parser.add_argument("--connectors", help="Filter to specific connectors, comma-separated")
    parser.add_argument("--min-spread", type=float, default=0.0, help="Minimum spread %% to show (default: 0.0)")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    args = parser.parse_args()

    base_tokens = [t.strip() for t in args.base.split(",")]
    quote_tokens = [t.strip() for t in args.quote.split(",")]

    # Get connectors
    if args.connectors:
        connectors = [c.strip() for c in args.connectors.split(",")]
    else:
        connectors = get_available_connectors()
        if not connectors:
            print("Error: No connectors available. Check API connection.", file=sys.stderr)
            sys.exit(1)

    # Step 1: Find matching trading pairs on each connector
    connector_pairs = {}
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = {executor.submit(get_connector_trading_pairs, c): c for c in connectors}
        for future in as_completed(futures):
            connector = futures[future]
            try:
                all_pairs = future.result()
                matching = find_matching_pairs(all_pairs, base_tokens, quote_tokens)
                if matching:
                    connector_pairs[connector] = matching
            except Exception:
                pass  # Silently skip connectors that fail

    if not connector_pairs:
        print(f"No trading pairs found matching {base_tokens} / {quote_tokens}", file=sys.stderr)
        sys.exit(1)

    # Step 2: Fetch prices from all connectors in parallel
    prices = []  # List of {connector, pair, price}

    # Create set of valid pairs for filtering
    valid_pairs = set()
    for pairs in connector_pairs.values():
        valid_pairs.update(p.upper() for p in pairs)

    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = {
            executor.submit(fetch_prices, connector, pairs): (connector, pairs)
            for connector, pairs in connector_pairs.items()
        }
        for future in as_completed(futures):
            connector, requested_pairs = futures[future]
            requested_set = {p.upper() for p in requested_pairs}
            try:
                result = future.result()
                if "error" in result:
                    continue

                # Extract prices from response - filter to only requested pairs
                for pair, price_data in result.items():
                    if pair == "error":
                        continue
                    # Only include pairs we actually requested
                    if pair.upper() not in requested_set:
                        continue

                    if isinstance(price_data, dict):
                        price = price_data.get("mid_price") or price_data.get("price")
                        bid = price_data.get("best_bid")
                        ask = price_data.get("best_ask")
                    else:
                        price = price_data
                        bid = ask = None

                    if price is not None and float(price) > 0:
                        prices.append({
                            "connector": connector,
                            "pair": pair,
                            "price": float(price),
                            "bid": float(bid) if bid else None,
                            "ask": float(ask) if ask else None,
                        })
            except Exception:
                pass  # Silently skip connectors that fail

    if not prices:
        print("No prices retrieved from any connector", file=sys.stderr)
        sys.exit(1)

    # Sort by price
    prices.sort(key=lambda x: x["price"])

    # Filter outliers (prices > 20% from median)
    if len(prices) >= 3:
        median_price = prices[len(prices) // 2]["price"]
        filtered_prices = [
            p for p in prices
            if abs(p["price"] - median_price) / median_price <= 0.20
        ]
        outliers = [p for p in prices if p not in filtered_prices]
    else:
        filtered_prices = prices
        outliers = []

    # Calculate arbitrage opportunities from filtered prices
    opportunities = []
    for i, buy in enumerate(filtered_prices):
        for sell in filtered_prices[i + 1:]:
            spread = (sell["price"] - buy["price"]) / buy["price"] * 100
            if spread >= args.min_spread:
                opportunities.append({
                    "buy_connector": buy["connector"],
                    "buy_pair": buy["pair"],
                    "buy_price": buy["price"],
                    "sell_connector": sell["connector"],
                    "sell_pair": sell["pair"],
                    "sell_price": sell["price"],
                    "spread_pct": spread,
                    "spread_abs": sell["price"] - buy["price"],
                })

    # Sort by spread descending
    opportunities.sort(key=lambda x: x["spread_pct"], reverse=True)

    # Output
    if args.json:
        print(json.dumps({
            "base_tokens": base_tokens,
            "quote_tokens": quote_tokens,
            "prices": filtered_prices,
            "outliers": outliers,
            "opportunities": opportunities[:20],
        }, indent=2))
    else:
        # Header
        print(f"\n{'='*60}")
        print(f"  {'/'.join(base_tokens)} / {'/'.join(quote_tokens)} Arbitrage Scanner")
        print(f"{'='*60}")

        # Price summary
        if filtered_prices:
            low = filtered_prices[0]
            high = filtered_prices[-1]
            spread_pct = (high["price"] - low["price"]) / low["price"] * 100
            print(f"\n  Lowest:  {low['connector']:20} {format_price(low['price'])}")
            print(f"  Highest: {high['connector']:20} {format_price(high['price'])}")
            print(f"  Spread:  {spread_pct:.3f}% ({format_price(high['price'] - low['price'])})")
            print(f"  Sources: {len(filtered_prices)} prices from {len(set(p['connector'] for p in filtered_prices))} connectors")

        # Best opportunities
        if opportunities:
            print(f"\n  Top Arbitrage Opportunities:")
            print(f"  {'-'*56}")
            for i, opp in enumerate(opportunities[:5], 1):
                print(f"  {i}. Buy  {opp['buy_connector']:18} @ {format_price(opp['buy_price'])}")
                print(f"     Sell {opp['sell_connector']:18} @ {format_price(opp['sell_price'])}")
                print(f"     Profit: {opp['spread_pct']:.3f}% ({format_price(opp['spread_abs'])})")
                if i < min(5, len(opportunities)):
                    print()
        else:
            print(f"\n  No opportunities found with spread >= {args.min_spread}%")

        # Outliers warning
        if outliers:
            print(f"\n  ⚠ {len(outliers)} outlier(s) excluded: ", end="")
            print(", ".join(f"{o['connector']} ({format_price(o['price'])})" for o in outliers[:3]))

        print()


if __name__ == "__main__":
    main()
