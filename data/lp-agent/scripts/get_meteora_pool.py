#!/usr/bin/env python3
"""
Get detailed information about a Meteora DLMM pool.

Usage:
    python scripts/get_meteora_pool.py <pool_address>
    python scripts/get_meteora_pool.py <pool_address> --json

Examples:
    python scripts/get_meteora_pool.py BGm1tav58oGcsQJehL9WXBFXF7D27vZsKefj4xJKD5Y
    python scripts/get_meteora_pool.py BGm1tav58oGcsQJehL9WXBFXF7D27vZsKefj4xJKD5Y --json
"""

import argparse
import json
import urllib.request
import urllib.parse
import os

METEORA_API = "https://dlmm.datapi.meteora.ag"
GATEWAY_HOST = os.environ.get("GATEWAY_HOST", "localhost")
GATEWAY_PORT = os.environ.get("GATEWAY_PORT", "15888")


def fetch_pool_meteora(address: str) -> dict:
    """Fetch pool details from Meteora DLMM API."""
    url = f"{METEORA_API}/pools/{address}"
    req = urllib.request.Request(url, headers={
        "Accept": "application/json",
        "User-Agent": "Mozilla/5.0 (compatible; hummingbot-skills/1.0)",
    })
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode())


def fetch_pool_gateway(address: str) -> tuple:
    """Fetch pool info from Gateway API (includes liquidity distribution).

    Returns: (data, error_message) tuple
    """
    url = f"http://{GATEWAY_HOST}:{GATEWAY_PORT}/connectors/meteora/clmm/pool-info?network=mainnet-beta&poolAddress={address}"
    req = urllib.request.Request(url, headers={"Accept": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return json.loads(resp.read().decode()), None
    except urllib.error.URLError as e:
        return None, f"Gateway not reachable at {GATEWAY_HOST}:{GATEWAY_PORT}"
    except Exception as e:
        return None, str(e)


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


def format_number_raw(value, decimals=6):
    """Format number without suffixes."""
    if value is None:
        return "—"
    try:
        return f"{float(value):,.{decimals}f}"
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


def format_price_smart(price: float) -> str:
    """Format price with appropriate precision based on magnitude."""
    if price is None or price == 0:
        return "0"
    if price >= 1000:
        return f"{price:,.0f}"
    elif price >= 1:
        return f"{price:.2f}"
    elif price >= 0.0001:
        return f"{price:.6f}"
    else:
        # Scientific notation for very small prices
        return f"{price:.2e}"


def format_price_subscript(price: float) -> str:
    """Format price with subscript notation for small decimals (e.g., 0.0₄167 means 0.0000167)."""
    if price is None or price == 0:
        return "0"
    if price >= 0.01:
        return f"{price:.4f}"

    # Count leading zeros after decimal point
    price_str = f"{price:.12f}"
    after_decimal = price_str.split(".")[1]
    leading_zeros = 0
    for c in after_decimal:
        if c == "0":
            leading_zeros += 1
        else:
            break

    # Get significant digits (up to 3)
    significant = after_decimal[leading_zeros:leading_zeros + 3]

    # Subscript digits
    subscripts = "₀₁₂₃₄₅₆₇₈₉"
    sub_zeros = subscripts[leading_zeros] if leading_zeros < 10 else str(leading_zeros)

    return f"0.0{sub_zeros}{significant}"


def render_liquidity_chart(bins: list, active_bin_id: int, current_price: float, base_symbol: str = "", quote_symbol: str = "", chart_height: int = 12) -> str:
    """Render ASCII vertical bar chart showing liquidity distribution like Meteora UI."""
    if not bins:
        return "No liquidity data available."

    # Calculate liquidity per bin
    bin_data = []
    for b in bins:
        price = b.get("price", 0)
        base = b.get("baseTokenAmount", 0) or 0
        quote = b.get("quoteTokenAmount", 0) or 0
        bin_data.append({
            "binId": b.get("binId"),
            "price": price,
            "base": base,
            "quote": quote,
            "base_value": base * price,  # in quote terms
            "quote_value": quote,
        })

    if not bin_data:
        return "No liquidity data available."

    # Sort by price
    bin_data.sort(key=lambda x: x["price"])

    # Sample to ~60 bins centered on active
    max_bins = 60
    if len(bin_data) > max_bins:
        active_idx = next((i for i, b in enumerate(bin_data) if b["binId"] == active_bin_id), len(bin_data) // 2)
        half = max_bins // 2
        start = max(0, active_idx - half)
        end = min(len(bin_data), start + max_bins)
        if end - start < max_bins:
            start = max(0, end - max_bins)
        bin_data = bin_data[start:end]

    # Find max values for scaling
    max_base = max((b["base_value"] for b in bin_data), default=0)
    max_quote = max((b["quote_value"] for b in bin_data), default=0)
    max_val = max(max_base, max_quote, 0.0001)

    # Find active bin index
    active_idx = next((i for i, b in enumerate(bin_data) if b["binId"] == active_bin_id), None)

    lines = []
    lines.append("Liquidity Distribution")
    lines.append(f"▓ {base_symbol}  ░ {quote_symbol}  │ Current Price: {format_price_subscript(current_price)} {quote_symbol}/{base_symbol}")
    lines.append("")

    # Build vertical bar chart (row by row from top)
    for row in range(chart_height, 0, -1):
        threshold = (row / chart_height) * max_val
        row_chars = []

        for i, b in enumerate(bin_data):
            is_active = (i == active_idx)
            base_val = b["base_value"]
            quote_val = b["quote_value"]

            # Determine character
            if base_val >= threshold and quote_val >= threshold:
                char = "█"  # Both tokens
            elif quote_val >= threshold:
                char = "░"  # Quote only (lighter - SOL)
            elif base_val >= threshold:
                char = "▓"  # Base only (darker - Percolator)
            elif is_active:
                char = "│"  # Active price line
            else:
                char = " "

            row_chars.append(char)

        lines.append("".join(row_chars))

    # X-axis
    axis = list("─" * len(bin_data))
    if active_idx is not None and active_idx < len(axis):
        axis[active_idx] = "┴"
    lines.append("".join(axis))

    # Price labels
    if bin_data:
        min_p = format_price_subscript(bin_data[0]["price"])
        max_p = format_price_subscript(bin_data[-1]["price"])
        cur_p = format_price_subscript(current_price)

        # Build label line
        label_width = len(bin_data)
        if active_idx is not None:
            # Position current price label at active bin
            cur_start = max(0, active_idx - len(cur_p) // 2)
            cur_end = cur_start + len(cur_p)

            label = min_p + " " * (cur_start - len(min_p))
            if cur_start > len(min_p):
                label += cur_p
                remaining = label_width - len(label) - len(max_p)
                if remaining > 0:
                    label += " " * remaining + max_p
            else:
                remaining = label_width - len(min_p) - len(max_p)
                label = min_p + " " * max(1, remaining) + max_p
        else:
            remaining = label_width - len(min_p) - len(max_p)
            label = min_p + " " * max(1, remaining) + max_p

        lines.append(label)

    return "\n".join(lines)


def print_summary_table(pool: dict, gateway: dict = None, gateway_error: str = None):
    """Print pool summary as markdown table."""
    name = pool.get("name", "Unknown")
    address = pool.get("address", "")
    token_x = pool.get("token_x", {})
    token_y = pool.get("token_y", {})
    config = pool.get("pool_config", {})
    volume = pool.get("volume", {})
    fees = pool.get("fees", {})
    fee_tvl = pool.get("fee_tvl_ratio", {})

    print(f"\n## {name}")
    print(f"**Address:** `{address}`")
    print(f"**Solscan:** https://solscan.io/account/{address}\n")

    # Summary Table
    print("### Pool Summary\n")
    print("| Metric | Value |")
    print("|--------|-------|")
    print(f"| Current Price | {format_number_raw(pool.get('current_price'), 4)} {token_y.get('symbol', '')}/{token_x.get('symbol', '')} |")
    print(f"| TVL | {format_number(pool.get('tvl'), prefix='$')} |")
    print(f"| 24h Volume | {format_number(volume.get('24h'), prefix='$')} |")
    print(f"| 24h Fees | {format_number(fees.get('24h'), prefix='$')} |")
    print(f"| APR | {format_percent(pool.get('apr'))} |")
    print(f"| APY | {format_percent(pool.get('apy'))} |")
    print(f"| Fee Tier | {format_percent(config.get('base_fee_pct'))} |")
    print(f"| Bin Step | {config.get('bin_step', '—')} |")

    # Max width calculation
    bin_step = config.get("bin_step")
    if bin_step:
        max_width = float(bin_step) * 69 / 100
        print(f"| Max Range Width | ~{max_width:.1f}% |")

    print(f"| Has Farm | {'Yes' if pool.get('has_farm') else 'No'} |")

    # Token Info Table
    print("\n### Token Info\n")
    print("| Token | Symbol | Mint | Price | Decimals | Market Cap |")
    print("|-------|--------|------|-------|----------|------------|")
    print(f"| Base (X) | {token_x.get('symbol', '?')} | `{token_x.get('address', '—')}` | ${format_number_raw(token_x.get('price'), 4)} | {token_x.get('decimals', '—')} | {format_number(token_x.get('market_cap'), prefix='$')} |")
    print(f"| Quote (Y) | {token_y.get('symbol', '?')} | `{token_y.get('address', '—')}` | ${format_number_raw(token_y.get('price'), 4)} | {token_y.get('decimals', '—')} | {format_number(token_y.get('market_cap'), prefix='$')} |")

    # Reserves
    print("\n### Reserves\n")
    print("| Token | Amount | Value |")
    print("|-------|--------|-------|")
    base_amount = pool.get("token_x_amount", 0)
    quote_amount = pool.get("token_y_amount", 0)
    base_price = token_x.get("price", 0) or 0
    quote_price = token_y.get("price", 0) or 0
    print(f"| {token_x.get('symbol', 'X')} | {format_number(base_amount)} | {format_number(base_amount * base_price if base_amount and base_price else None, prefix='$')} |")
    print(f"| {token_y.get('symbol', 'Y')} | {format_number(quote_amount)} | {format_number(quote_amount * quote_price if quote_amount and quote_price else None, prefix='$')} |")

    # Volume & Fees by Time Window
    print("\n### Volume & Fees by Time Window\n")
    print("| Window | Volume | Fees | Fee/TVL Ratio |")
    print("|--------|--------|------|---------------|")
    for window in ["30m", "1h", "4h", "12h", "24h"]:
        v = format_number(volume.get(window), prefix="$")
        f = format_number(fees.get(window), prefix="$")
        r = format_percent(fee_tvl.get(window))
        print(f"| {window} | {v} | {f} | {r} |")

    # Cumulative Metrics
    cumulative = pool.get("cumulative_metrics", {})
    if cumulative:
        print("\n### Cumulative Metrics (All Time)\n")
        print("| Metric | Value |")
        print("|--------|-------|")
        print(f"| Total Volume | {format_number(cumulative.get('volume'), prefix='$')} |")
        print(f"| Total Trade Fees | {format_number(cumulative.get('trade_fee'), prefix='$')} |")
        print(f"| Total Protocol Fees | {format_number(cumulative.get('protocol_fee'), prefix='$')} |")

    # Liquidity Distribution from Gateway
    if gateway and gateway.get("bins"):
        # Show Gateway price (real-time) vs Meteora price
        gateway_price = gateway.get("price")
        if gateway_price:
            print("\n### Real-Time Price (from Gateway)\n")
            print(f"**{format_price_subscript(gateway_price)} {token_y.get('symbol', '')}/{token_x.get('symbol', '')}**")

        print("\n### Liquidity Distribution\n")
        print("```")
        chart = render_liquidity_chart(
            gateway.get("bins", []),
            gateway.get("activeBinId", 0),
            gateway.get("price", pool.get("current_price", 0)),
            base_symbol=token_x.get("symbol", ""),
            quote_symbol=token_y.get("symbol", ""),
        )
        print(chart)
        print("```")

        # Gateway-specific info
        print("\n### Active Bin Info\n")
        print("| Metric | Value |")
        print("|--------|-------|")
        print(f"| Active Bin ID | {gateway.get('activeBinId', '—')} |")
        print(f"| Min Bin ID | {gateway.get('minBinId', '—')} |")
        print(f"| Max Bin ID | {gateway.get('maxBinId', '—')} |")
        print(f"| Dynamic Fee | {format_percent(gateway.get('dynamicFeePct'))} |")
    else:
        print("\n### Liquidity Distribution\n")
        if gateway_error:
            print(f"*{gateway_error}*")
        else:
            print("*Gateway not available - run with Gateway for bin distribution*")


def print_json(pool: dict, gateway: dict = None):
    """Print combined JSON output."""
    output = {
        "meteora": pool,
    }
    if gateway:
        output["gateway"] = gateway
    print(json.dumps(output, indent=2))


def main():
    parser = argparse.ArgumentParser(
        description="Get detailed Meteora DLMM pool information",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s BGm1tav58oGcsQJehL9WXBFXF7D27vZsKefj4xJKD5Y
  %(prog)s BGm1tav58oGcsQJehL9WXBFXF7D27vZsKefj4xJKD5Y --json

Environment variables:
  GATEWAY_HOST  Gateway host (default: localhost)
  GATEWAY_PORT  Gateway port (default: 15888)
        """,
    )
    parser.add_argument(
        "address",
        help="Pool address to look up",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output as JSON",
    )
    parser.add_argument(
        "--no-gateway",
        action="store_true",
        help="Skip Gateway API call (no liquidity distribution)",
    )

    args = parser.parse_args()

    try:
        # Fetch from Meteora API
        pool = fetch_pool_meteora(args.address)

        # Fetch from Gateway API (optional)
        gateway = None
        gateway_error = None
        if not args.no_gateway:
            gateway, gateway_error = fetch_pool_gateway(args.address)

        if args.json:
            print_json(pool, gateway)
        else:
            print_summary_table(pool, gateway, gateway_error)

    except urllib.error.HTTPError as e:
        if e.code == 404:
            print(f"Error: Pool not found: {args.address}")
        else:
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
