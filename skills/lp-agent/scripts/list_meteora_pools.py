#!/usr/bin/env python3
"""
List and search Meteora DLMM pools.

Usage:
    python scripts/list_meteora_pools.py                          # Top 10 pools by 24h volume
    python scripts/list_meteora_pools.py --query SOL              # Search by token/name/address
    python scripts/list_meteora_pools.py --query USDC --sort tvl  # Sort by TVL
    python scripts/list_meteora_pools.py --limit 20               # Show more results

Examples:
    python scripts/list_meteora_pools.py --query SOL-USDC
    python scripts/list_meteora_pools.py --query "JUP" --sort fees
    python scripts/list_meteora_pools.py --sort apr --limit 20
"""

import argparse
import json
import urllib.request
import urllib.parse

API_BASE = "https://dlmm.datapi.meteora.ag"

# Default number of results
DEFAULT_LIMIT = 10


def fetch_pools(
    query: str = None,
    sort_by: str = "volume",
    order: str = "desc",
    page: int = 1,
    limit: int = DEFAULT_LIMIT,
) -> dict:
    """Fetch pools from Meteora DLMM API."""
    params = {
        "page": page,
        "page_size": limit,
    }

    if query:
        params["query"] = query

    # Map friendly sort names to API field names
    sort_map = {
        "volume": "volume_24h",
        "tvl": "tvl",
        "fees": "fee_24h",
        "apr": "apr_24h",
        "apy": "apy_24h",
    }
    sort_field = sort_map.get(sort_by, "volume_24h")
    params["sort_by"] = f"{sort_field}:{order}"

    url = f"{API_BASE}/pools?{urllib.parse.urlencode(params)}"

    req = urllib.request.Request(url, headers={
        "Accept": "application/json",
        "User-Agent": "Mozilla/5.0 (compatible; hummingbot-skills/1.0)",
    })
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode())


def format_number(value, decimals=2, prefix="", suffix=""):
    """Format number with K/M/B suffixes."""
    if value is None:
        return "—"
    try:
        num = float(value)
        if num >= 1_000_000_000:
            return f"{prefix}{num/1_000_000_000:.{decimals}f}B{suffix}"
        elif num >= 1_000_000:
            return f"{prefix}{num/1_000_000:.{decimals}f}M{suffix}"
        elif num >= 1_000:
            return f"{prefix}{num/1_000:.{decimals}f}K{suffix}"
        else:
            return f"{prefix}{num:.{decimals}f}{suffix}"
    except (ValueError, TypeError):
        return "—"


def format_percent(value):
    """Format as percentage."""
    if value is None:
        return "—"
    try:
        return f"{float(value):.2f}%"
    except (ValueError, TypeError):
        return "—"


def short_address(address: str, chars: int = 4) -> str:
    """Shorten address to first and last N characters."""
    if not address or len(address) <= chars * 2 + 2:
        return address or "—"
    return f"{address[:chars]}..{address[-chars:]}"


def print_markdown_table(data: dict, sort_by: str):
    """Print pools as a markdown table for AI assistants."""
    pools = data.get("data", [])
    total = data.get("total", 0)
    page = data.get("current_page", 1)
    pages = data.get("pages", 1)

    if not pools:
        print("No pools found.")
        return

    print(f"Found {total} pools (showing page {page}/{pages}, sorted by {sort_by})\n")

    # Markdown table header
    print("| # | Pool | Pool Address | Base (mint) | Quote (mint) | TVL | Vol 24h | Fees 24h | APR | Fee | Bin |")
    print("|---|------|--------------|-------------|--------------|-----|---------|----------|-----|-----|-----|")

    for i, pool in enumerate(pools, 1):
        name = pool.get("name", "Unknown")
        address = pool.get("address", "")
        token_x = pool.get("token_x", {})
        token_y = pool.get("token_y", {})
        base_symbol = token_x.get("symbol", "?")
        base_mint = short_address(token_x.get("address", ""))
        quote_symbol = token_y.get("symbol", "?")
        quote_mint = short_address(token_y.get("address", ""))
        tvl = format_number(pool.get("tvl"), prefix="$")
        volume = format_number(pool.get("volume", {}).get("24h"), prefix="$")
        fees = format_number(pool.get("fees", {}).get("24h"), prefix="$")
        apr = format_percent(pool.get("apr"))
        pool_config = pool.get("pool_config", {})
        fee_tier = format_percent(pool_config.get("base_fee_pct"))
        bin_step = pool_config.get("bin_step", "—")

        print(f"| {i} | {name} | `{short_address(address, 6)}` | {base_symbol} (`{base_mint}`) | {quote_symbol} (`{quote_mint}`) | {tvl} | {volume} | {fees} | {apr} | {fee_tier} | {bin_step} |")

    print(f"\nUse `get_meteora_pool.py <pool_address>` for detailed pool info including full token mints.")


def print_json(data: dict):
    """Print simplified JSON output for programmatic use."""
    pools = data.get("data", [])
    result = []

    for pool in pools:
        token_x = pool.get("token_x", {})
        token_y = pool.get("token_y", {})
        result.append({
            "name": pool.get("name"),
            "address": pool.get("address"),
            "tvl": pool.get("tvl"),
            "volume_24h": pool.get("volume", {}).get("24h"),
            "fees_24h": pool.get("fees", {}).get("24h"),
            "apr": pool.get("apr"),
            "apy": pool.get("apy"),
            "bin_step": pool.get("pool_config", {}).get("bin_step"),
            "base_fee_pct": pool.get("pool_config", {}).get("base_fee_pct"),
            "token_x_symbol": token_x.get("symbol"),
            "token_x_mint": token_x.get("address"),
            "token_y_symbol": token_y.get("symbol"),
            "token_y_mint": token_y.get("address"),
        })

    output = {
        "total": data.get("total"),
        "page": data.get("current_page"),
        "pages": data.get("pages"),
        "pools": result,
    }
    print(json.dumps(output, indent=2))


def main():
    parser = argparse.ArgumentParser(
        description="List and search Meteora DLMM pools",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                              # Top 10 pools by 24h volume
  %(prog)s --query SOL                  # Search for SOL pools
  %(prog)s --query USDC --sort tvl      # USDC pools sorted by TVL
  %(prog)s --sort apr --limit 20        # Top 20 by APR
  %(prog)s --query <address>            # Search by pool address
        """,
    )
    parser.add_argument(
        "-q", "--query",
        help="Search by pool name, token symbol, or address",
    )
    parser.add_argument(
        "-s", "--sort",
        default="volume",
        choices=["volume", "tvl", "fees", "apr", "apy"],
        help="Sort by metric (default: volume)",
    )
    parser.add_argument(
        "--order",
        default="desc",
        choices=["asc", "desc"],
        help="Sort order (default: desc)",
    )
    parser.add_argument(
        "-n", "--limit",
        type=int,
        default=DEFAULT_LIMIT,
        help=f"Number of results (default: {DEFAULT_LIMIT}, max: 1000)",
    )
    parser.add_argument(
        "-p", "--page",
        type=int,
        default=1,
        help="Page number (default: 1)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output as JSON",
    )

    args = parser.parse_args()

    try:
        data = fetch_pools(
            query=args.query,
            sort_by=args.sort,
            order=args.order,
            page=args.page,
            limit=min(args.limit, 1000),
        )

        if args.json:
            print_json(data)
        else:
            print_markdown_table(data, sort_by=args.sort)

    except urllib.error.HTTPError as e:
        print(f"API error: {e.code} {e.reason}")
        return 1
    except urllib.error.URLError as e:
        print(f"Network error: {e.reason}")
        return 1
    except json.JSONDecodeError as e:
        print(f"Failed to parse API response: {e}")
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
