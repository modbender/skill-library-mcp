#!/usr/bin/env python3
"""
Hyperliquid Trading Toolkit - CLI for Claude Code to trade on Hyperliquid.

Usage:
    python hyperliquid_tools.py status              # Account balance, positions, PnL
    python hyperliquid_tools.py positions           # Detailed position info
    python hyperliquid_tools.py price BTC           # Current price
    python hyperliquid_tools.py funding BTC         # Funding rate
    python hyperliquid_tools.py book BTC            # Order book
    python hyperliquid_tools.py buy BTC 0.01        # Market buy
    python hyperliquid_tools.py sell BTC 0.01       # Market sell
    python hyperliquid_tools.py limit-buy BTC 0.01 85000   # Limit buy
    python hyperliquid_tools.py limit-sell BTC 0.01 95000  # Limit sell
    python hyperliquid_tools.py close BTC           # Close position
    python hyperliquid_tools.py swap 20             # Swap USDC → USDH for HIP-3
    python hyperliquid_tools.py orders              # List open orders
    python hyperliquid_tools.py cancel ORDER_ID     # Cancel order
    python hyperliquid_tools.py cancel-all          # Cancel all orders
"""

import os
import sys
import json
import time
import argparse
from datetime import datetime
from typing import Optional
from dotenv import load_dotenv

# Load environment variables (HL_ENV_FILE overrides default .env discovery)
_env_file = os.getenv('HL_ENV_FILE')
if _env_file:
    load_dotenv(_env_file, override=True)
else:
    load_dotenv()

# Hyperliquid SDK imports
try:
    from hyperliquid.info import Info
    from hyperliquid.exchange import Exchange
    from hyperliquid.utils import constants
    from eth_account import Account
except ImportError:
    print("Error: hyperliquid-python-sdk not installed.")
    print("Run: pip install hyperliquid-python-sdk")
    sys.exit(1)

# ANSI colors
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    BOLD = '\033[1m'
    DIM = '\033[2m'
    END = '\033[0m'


def get_config(require_credentials: bool = True):
    """Get Hyperliquid configuration from environment."""
    account_address = os.getenv('HL_ACCOUNT_ADDRESS')
    secret_key = os.getenv('HL_SECRET_KEY')
    use_testnet = os.getenv('HL_TESTNET', 'false').lower() == 'true'

    if require_credentials and (not account_address or not secret_key):
        print(f"{Colors.RED}Error: Hyperliquid credentials not configured.{Colors.END}")
        print(f"\nAdd to your .env file:")
        print(f"  HL_ACCOUNT_ADDRESS=0x...  # Your wallet address")
        print(f"  HL_SECRET_KEY=0x...       # API wallet private key")
        print(f"  HL_TESTNET=true           # Optional: use testnet")
        sys.exit(1)

    base_api_url = constants.TESTNET_API_URL if use_testnet else constants.MAINNET_API_URL
    api_url = os.getenv('HL_PROXY_URL') or base_api_url

    return {
        'account_address': account_address or '',
        'secret_key': secret_key or '',
        'api_url': api_url,
        'base_api_url': base_api_url,
        'is_testnet': use_testnet
    }


def get_all_dex_names(api_url: str) -> list:
    """Fetch all available HIP-3 dex names from the API."""
    try:
        # Create a basic Info client to query available dexes
        basic_info = Info(api_url, skip_ws=True)
        all_dexes = basic_info.perp_dexs()
        # Extract dex names, add '' for native perps
        dex_names = ['']  # Native perps
        for dex in all_dexes:
            if dex is not None and dex.get('name'):
                dex_names.append(dex.get('name'))
        return dex_names
    except Exception:
        # Fallback to known dexes if API call fails
        return ['', 'xyz', 'vntl', 'flx', 'hyna', 'km', 'abcd', 'cash']


def setup_info(skip_ws: bool = True, require_credentials: bool = False, include_hip3: bool = True) -> tuple:
    """Setup Info client for read-only operations."""
    config = get_config(require_credentials=require_credentials)
    # Fetch all available HIP-3 dexes dynamically
    perp_dexs = get_all_dex_names(config['api_url']) if include_hip3 else None
    info = Info(config['api_url'], skip_ws=skip_ws, perp_dexs=perp_dexs)
    return info, config


def setup_exchange(skip_ws: bool = True, include_hip3: bool = True) -> tuple:
    """Setup Exchange client for trading operations."""
    config = get_config()
    # Create wallet from private key
    wallet = Account.from_key(config['secret_key'])
    # Fetch all available HIP-3 dexes dynamically
    perp_dexs = get_all_dex_names(config['api_url']) if include_hip3 else None
    # Exchange uses the real API URL (not proxy) so signing uses the correct chain domain.
    # The SDK checks base_url == MAINNET_API_URL to determine mainnet vs testnet signing.
    exchange = Exchange(wallet, config['base_api_url'], account_address=config['account_address'], perp_dexs=perp_dexs)
    # Info client uses proxy URL for cached reads
    info = Info(config['api_url'], skip_ws=skip_ws, perp_dexs=perp_dexs)
    return exchange, info, config


def format_price(price: float) -> str:
    """Format price for display."""
    if price >= 1000:
        return f"${price:,.2f}"
    elif price >= 1:
        return f"${price:.2f}"
    else:
        return f"${price:.6f}"


def format_pnl(pnl: float) -> str:
    """Format PnL with color."""
    if pnl >= 0:
        return f"{Colors.GREEN}+${pnl:,.2f}{Colors.END}"
    else:
        return f"{Colors.RED}-${abs(pnl):,.2f}{Colors.END}"


def _invalidate_proxy_cache(config: dict):
    """Invalidate cached user state on the proxy after a trade.

    Trades bypass the proxy (SDK signs against the real API URL), so the proxy
    doesn't know state changed.  This pokes POST /cache/clear to drop stale
    entries so the next status/positions call sees fresh data.
    """
    proxy_url = os.getenv('HL_PROXY_URL')
    if not proxy_url:
        return
    address = config.get('account_address', '')
    if not address:
        return
    try:
        import requests
        requests.post(f"{proxy_url}/cache/clear", json={"user": address}, timeout=2)
    except Exception:
        pass  # Proxy may be down; not critical


def get_account_summary(info, address: str) -> dict:
    """Detect account abstraction mode and compute true portfolio value.

    In unified/dexAbstraction mode, spot and perp are separate pools.
    The perp clearinghouse accountValue only reflects perp margin + PnL.
    Total portfolio = perp accountValue + spot balances.

    Returns dict with keys:
        mode              - 'unified', 'portfolio_margin', or 'standard'
        mode_label        - display string like '[unified]'
        portfolio_value   - true portfolio value (float)
        account_value     - raw perp accountValue (float)
        margin_used       - total margin used in perps (float)
        withdrawable      - withdrawable amount (float)
        spot_balances     - list of {coin, total, hold} dicts (may be empty)
        perp_state        - raw user_state dict (for position access)
    """
    # Always fetch perp state (retry up to 3 times to avoid false $0 reports)
    perp_state = None
    last_error = None
    for attempt in range(3):
        try:
            result = info.user_state(address)
            if isinstance(result, dict) and 'marginSummary' in result:
                perp_state = result
                break
            last_error = "Malformed API response (missing marginSummary)"
        except Exception as e:
            last_error = str(e)
        if attempt < 2:
            time.sleep(2)

    if perp_state is None:
        raise RuntimeError(f"Failed to fetch account state after 3 attempts: {last_error}")

    margin_summary = perp_state['marginSummary']
    account_value = float(margin_summary.get('accountValue', 0))
    margin_used = float(margin_summary.get('totalMarginUsed', 0))
    withdrawable = float(perp_state.get('withdrawable', 0))

    # Detect abstraction mode
    mode = 'standard'
    try:
        abstraction = info.query_user_abstraction_state(address)
        # API may return a plain string or a dict with a 'mode' key
        if isinstance(abstraction, str):
            ab_mode = abstraction
        elif isinstance(abstraction, dict):
            ab_mode = abstraction.get('mode', '')
        else:
            ab_mode = ''
        if ab_mode in ('unifiedAccount', 'dexAbstraction'):
            mode = 'unified'
        elif ab_mode == 'portfolioMargin':
            mode = 'portfolio_margin'
    except Exception:
        pass

    spot_balances = []
    portfolio_value = account_value

    if mode != 'standard':
        # Fetch spot state for the true USDC balance
        try:
            spot_state = info.spot_user_state(address)
            raw_balances = spot_state.get('balances', [])
            for b in raw_balances:
                total = float(b.get('total', 0))
                hold = float(b.get('hold', 0))
                if total > 0.001 or hold > 0.001:
                    spot_balances.append({
                        'coin': b.get('coin', '?'),
                        'total': total,
                        'hold': hold,
                    })

            # In unified mode, spot USDC "hold" is the USDC locked as perp
            # margin.  perp accountValue is derived FROM that held USDC +
            # unrealized PnL.  Using spot total would double-count the held
            # portion, so we use free (total - hold) for spot and add it to
            # perp accountValue.
            #
            # TODO: This assumes spot balances are stablecoins (1 unit ≈ $1).
            # If spot trading of non-stablecoins is added (BTC, HYPE, etc.),
            # each balance must be converted to USD via mid price.
            spot_free = sum(b['total'] - b['hold'] for b in spot_balances)
            portfolio_value = account_value + spot_free
            withdrawable = float(perp_state.get('withdrawable', 0)) + spot_free
        except Exception:
            # Fallback: use perp values if spot query fails
            portfolio_value = account_value

    mode_labels = {
        'unified': f'{Colors.MAGENTA}[unified]{Colors.END}',
        'portfolio_margin': f'{Colors.MAGENTA}[portfolio margin]{Colors.END}',
        'standard': f'{Colors.DIM}[standard]{Colors.END}',
    }

    return {
        'mode': mode,
        'mode_label': mode_labels[mode],
        'portfolio_value': portfolio_value,
        'account_value': account_value,
        'margin_used': margin_used,
        'withdrawable': withdrawable,
        'spot_balances': spot_balances,
        'perp_state': perp_state,
    }


# Rate limiting note: Hyperliquid's REST API allows 1,200 weight/minute per IP.
# user_state (clearinghouseState) costs weight 2, so 8 dex calls = 16 weight (~1.3% of budget).
# frontend_open_orders costs weight 20, so 8 calls = 160 weight (~13% of budget).
# No delay needed between calls. The proxy cache further reduces upstream hits.
# Ref: https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/rate-limits-and-user-limits

def _get_all_positions(info, address):
    """Fetch positions from native perps + all HIP-3 dexes."""
    positions = []
    try:
        state = info.user_state(address)
        positions.extend(state.get('assetPositions', []))
    except Exception:
        pass
    try:
        for dex in info.perp_dexs():
            if dex is None:
                continue
            name = dex.get('name', '')
            if not name:
                continue
            try:
                dex_state = info.user_state(address, dex=name)
                positions.extend(dex_state.get('assetPositions', []))
            except Exception:
                pass
    except Exception:
        pass
    return positions


def _get_all_open_orders(info, address):
    """Fetch open orders from native perps + all HIP-3 dexes."""
    orders = []
    try:
        orders.extend(info.frontend_open_orders(address))
    except Exception:
        pass
    try:
        for dex in info.perp_dexs():
            if dex is None:
                continue
            name = dex.get('name', '')
            if not name:
                continue
            try:
                orders.extend(info.frontend_open_orders(address, dex=name))
            except Exception:
                pass
    except Exception:
        pass
    return orders


# ============================================================================
# READ-ONLY COMMANDS
# ============================================================================

def cmd_status(args):
    """Show account status: balance, equity, positions summary."""
    info, config = setup_info(require_credentials=True, include_hip3=True)

    print(f"\n{Colors.BOLD}{Colors.CYAN}HYPERLIQUID ACCOUNT STATUS{Colors.END}")
    if config['is_testnet']:
        print(f"{Colors.YELLOW}[TESTNET]{Colors.END}")
    print("=" * 60)

    try:
        summary = get_account_summary(info, config['account_address'])

        print(f"\n{Colors.BOLD}Account Summary:{Colors.END} {summary['mode_label']}")
        print(f"  Portfolio Value: {format_price(summary['portfolio_value'])}")
        if summary['mode'] != 'standard':
            print(f"  Perp Margin:     {format_price(summary['account_value'])}")
        print(f"  Margin Used:     {format_price(summary['margin_used'])}")
        print(f"  Withdrawable:    {format_price(summary['withdrawable'])}")

        # Spot balances for unified/portfolio margin
        if summary['spot_balances']:
            print(f"\n{Colors.BOLD}Spot Balances:{Colors.END}")
            for bal in summary['spot_balances']:
                hold_str = f" (hold: ${bal['hold']:,.2f})" if bal['hold'] > 0.01 else ""
                print(f"  {bal['coin']:<8} ${bal['total']:,.2f}{hold_str}")

        # Positions (native + all HIP-3 dexes)
        all_positions = _get_all_positions(info, config['account_address'])
        open_positions = [p for p in all_positions if float(p['position']['szi']) != 0]

        if open_positions:
            print(f"\n{Colors.BOLD}Open Positions ({len(open_positions)}):{Colors.END}")
            print(f"  {'Asset':<12} {'Side':<6} {'Size':>12} {'Entry':>12} {'Mark':>12} {'PnL':>15}")
            print("  " + "-" * 70)

            total_unrealized = 0
            for pos in open_positions:
                p = pos['position']
                coin = p['coin']
                size = float(p['szi'])
                entry_px = float(p['entryPx'])
                unrealized_pnl = float(p['unrealizedPnl'])

                # Get mark price
                mark_px = entry_px  # Fallback
                if 'markPx' in p:
                    mark_px = float(p['markPx'])

                side = "LONG" if size > 0 else "SHORT"
                side_color = Colors.GREEN if size > 0 else Colors.RED

                total_unrealized += unrealized_pnl

                print(f"  {coin:<12} {side_color}{side:<6}{Colors.END} {abs(size):>12.4f} {format_price(entry_px):>12} {format_price(mark_px):>12} {format_pnl(unrealized_pnl):>15}")

            print("  " + "-" * 70)
            print(f"  {'Total Unrealized PnL:':<52} {format_pnl(total_unrealized):>15}")
        else:
            print(f"\n{Colors.DIM}No open positions{Colors.END}")

        return 0
    except Exception as e:
        print(f"{Colors.RED}Error fetching account status: {e}{Colors.END}")
        return 1


def cmd_positions(args):
    """Show detailed position information."""
    info, config = setup_info(require_credentials=True, include_hip3=True)

    print(f"\n{Colors.BOLD}{Colors.CYAN}POSITION DETAILS{Colors.END}")
    print("=" * 60)

    try:
        all_positions = _get_all_positions(info, config['account_address'])
        open_positions = [p for p in all_positions if float(p['position']['szi']) != 0]

        if not open_positions:
            print(f"\n{Colors.DIM}No open positions{Colors.END}")
            return 0

        for pos in open_positions:
            p = pos['position']
            coin = p['coin']
            size = float(p['szi'])
            entry_px = float(p['entryPx'])
            unrealized_pnl = float(p['unrealizedPnl'])
            leverage = p.get('leverage', {})
            liq_px = float(p.get('liquidationPx', 0)) if p.get('liquidationPx') else None

            side = "LONG" if size > 0 else "SHORT"
            side_color = Colors.GREEN if size > 0 else Colors.RED

            print(f"\n{Colors.BOLD}{coin}{Colors.END}")
            print(f"  Side:           {side_color}{side}{Colors.END}")
            print(f"  Size:           {abs(size):.4f}")
            print(f"  Entry Price:    {format_price(entry_px)}")
            print(f"  Unrealized PnL: {format_pnl(unrealized_pnl)}")
            if leverage:
                lev_type = leverage.get('type', 'unknown')
                lev_val = leverage.get('value', 0)
                max_lev = _get_max_leverage(info, coin)
                max_str = f" / max {max_lev}x" if max_lev else ""
                print(f"  Leverage:       {lev_val}x ({lev_type}{max_str})")
            if liq_px:
                print(f"  Liquidation:    {format_price(liq_px)}")

        return 0
    except Exception as e:
        print(f"{Colors.RED}Error fetching positions: {e}{Colors.END}")
        return 1


def cmd_check(args):
    """Position health check - shows book ratio, funding, price change for all open positions."""
    import requests as req
    info, config = setup_info(require_credentials=False, include_hip3=True)

    address = args.address if hasattr(args, 'address') and args.address else config.get('account_address', '')
    if not address:
        print(f"{Colors.RED}Error: No account address. Set HL_ACCOUNT_ADDRESS or use --address.{Colors.END}")
        return 1

    print(f"\n{Colors.BOLD}{Colors.CYAN}POSITION HEALTH CHECK{Colors.END}")
    if config['is_testnet']:
        print(f"{Colors.YELLOW}[TESTNET]{Colors.END}")
    print("=" * 90)

    try:
        # Get account summary with mode detection
        summary = get_account_summary(info, address)
        positions = _get_all_positions(info, address)
        open_positions = [p for p in positions if float(p['position']['szi']) != 0]

        if not open_positions:
            print(f"\n{Colors.DIM}No open positions{Colors.END}")
            return 0

        print(f"\n  Portfolio Value: {format_price(summary['portfolio_value'])} {summary['mode_label']} | Withdrawable: {format_price(summary['withdrawable'])}")
        print()

        # Pre-fetch predicted funding rates in bulk (one call for native, one per HIP-3 dex)
        funding_rates = {}  # coin -> predicted funding rate (float)
        try:
            meta = info.meta_and_asset_ctxs()
            for i, asset in enumerate(meta[0]['universe']):
                funding_rates[asset['name']] = float(meta[1][i].get('funding', 0))
        except Exception:
            pass

        # For HIP-3 positions, fetch per-dex meta on demand
        hip3_dexes_fetched = set()
        hip3_coins = [p['position']['coin'] for p in open_positions if ':' in p['position']['coin']]
        for coin in hip3_coins:
            dex = coin.split(':')[0]
            if dex in hip3_dexes_fetched:
                continue
            try:
                resp = req.post(
                    config['api_url'] + "/info",
                    json={"type": "metaAndAssetCtxs", "dex": dex},
                    timeout=10
                )
                if resp.status_code == 200:
                    dex_meta = resp.json()
                    for i, asset in enumerate(dex_meta[0]['universe']):
                        funding_rates[asset['name']] = float(dex_meta[1][i].get('funding', 0))
                hip3_dexes_fetched.add(dex)
            except Exception:
                pass

        for pos in open_positions:
            p = pos['position']
            coin = p['coin']
            size = float(p['szi'])
            entry_px = float(p['entryPx'])
            unrealized_pnl = float(p['unrealizedPnl'])
            leverage = p.get('leverage', {})
            liq_px = float(p.get('liquidationPx', 0)) if p.get('liquidationPx') else None

            side = "LONG" if size > 0 else "SHORT"
            side_color = Colors.GREEN if size > 0 else Colors.RED
            notional = abs(size) * entry_px

            # Get current price from book
            mark_px = entry_px
            book_ratio_str = "N/A"
            bid_depth = 0
            ask_depth = 0
            warnings = []

            try:
                book_resp = req.post(
                    config['api_url'] + "/info",
                    json={"type": "l2Book", "coin": coin},
                    timeout=10
                )
                if book_resp.status_code == 200:
                    book = book_resp.json()
                    levels = book.get('levels', [])
                    if len(levels) >= 2 and levels[0] and levels[1]:
                        best_bid = float(levels[0][0]['px'])
                        best_ask = float(levels[1][0]['px'])
                        mark_px = (best_bid + best_ask) / 2

                        bid_depth = sum(float(b['sz']) * float(b['px']) for b in levels[0][:5])
                        ask_depth = sum(float(a['sz']) * float(a['px']) for a in levels[1][:5])

                        if ask_depth > 0 and bid_depth > 0:
                            ratio = bid_depth / ask_depth
                            if ratio >= 1:
                                book_ratio_str = f"{ratio:.1f}:1 bid"
                                book_color = Colors.GREEN
                            else:
                                inv_ratio = ask_depth / bid_depth
                                book_ratio_str = f"{inv_ratio:.1f}:1 ask"
                                book_color = Colors.RED

                            # Warn if book is against position
                            if side == "LONG" and ask_depth / bid_depth > 2.0:
                                warnings.append("Book ask-heavy vs LONG")
                            elif side == "SHORT" and bid_depth / ask_depth > 2.0:
                                warnings.append("Book bid-heavy vs SHORT")
                        else:
                            book_color = Colors.YELLOW
                            book_ratio_str = "thin"
            except Exception:
                book_color = Colors.YELLOW

            # Get predicted funding rate from pre-fetched bulk data
            funding_str = "N/A"
            funding_apr = 0
            funding = funding_rates.get(coin)
            if funding is not None:
                funding_apr = funding * 24 * 365 * 100

                # Determine if we're collecting or paying
                if side == "LONG":
                    collecting = funding < 0  # shorts pay longs
                else:
                    collecting = funding > 0  # longs pay shorts

                if collecting:
                    funding_str = f"{Colors.GREEN}{funding_apr:+.0f}% APR (collecting){Colors.END}"
                else:
                    funding_str = f"{Colors.RED}{funding_apr:+.0f}% APR (paying){Colors.END}"
                    if abs(funding_apr) > 100:
                        warnings.append(f"High funding cost: {abs(funding_apr):.0f}% APR")

            # Price change from entry
            if entry_px > 0:
                if side == "LONG":
                    pct_change = ((mark_px - entry_px) / entry_px) * 100
                else:
                    pct_change = ((entry_px - mark_px) / entry_px) * 100
                pct_color = Colors.GREEN if pct_change >= 0 else Colors.RED
                pct_str = f"{pct_color}{pct_change:+.1f}%{Colors.END}"
            else:
                pct_str = "N/A"

            # Liquidation proximity warning
            if liq_px and liq_px > 0:
                if side == "LONG":
                    liq_dist = ((mark_px - liq_px) / mark_px) * 100
                else:
                    liq_dist = ((liq_px - mark_px) / mark_px) * 100
                if liq_dist < 10:
                    warnings.append(f"Liq {liq_dist:.1f}% away @ {format_price(liq_px)}")

            # Print position line
            print(f"  {Colors.BOLD}{coin}{Colors.END} {side_color}{side}{Colors.END} | {format_price(mark_px)} ({pct_str} from entry) | PnL: {format_pnl(unrealized_pnl)}")
            print(f"    Book: {book_color}{book_ratio_str}{Colors.END} (${bid_depth:,.0f} bid / ${ask_depth:,.0f} ask) | Funding: {funding_str}")

            if leverage:
                lev_type = leverage.get('type', 'unknown')
                lev_val = leverage.get('value', 0)
                print(f"    Leverage: {lev_val}x {lev_type} | Notional: {format_price(notional)} | Size: {abs(size):.4f}")

            if warnings:
                for w in warnings:
                    print(f"    {Colors.YELLOW}⚠ {w}{Colors.END}")

            print()

        return 0
    except Exception as e:
        print(f"{Colors.RED}Error: {e}{Colors.END}")
        return 1


def cmd_price(args):
    """Get current price for an asset."""
    info, config = setup_info()
    coins = args.coins if args.coins else ['BTC', 'ETH', 'SOL']

    try:
        # Cache mids per dex to avoid repeated API calls
        mids_cache = {}

        def get_price(coin):
            """Get price for a coin, handling HIP-3 dex prefix."""
            if ':' in coin:
                # HIP-3 asset like xyz:META or vntl:ANTHROPIC
                dex = coin.split(':')[0]
                if dex not in mids_cache:
                    mids_cache[dex] = info.all_mids(dex=dex)
                return mids_cache[dex].get(coin)
            else:
                # Native perp
                if '' not in mids_cache:
                    mids_cache[''] = info.all_mids()
                return mids_cache[''].get(coin)

        print(f"\n{Colors.BOLD}Current Prices:{Colors.END}")
        for coin in coins:
            price = get_price(coin)
            if price:
                print(f"  {coin:<20} {format_price(float(price))}")
            else:
                print(f"  {coin:<20} {Colors.DIM}Not found{Colors.END}")

        return 0
    except Exception as e:
        print(f"{Colors.RED}Error fetching prices: {e}{Colors.END}")
        return 1


def _cmd_funding_predicted(config, coins):
    """Show predicted funding rates with cross-exchange comparison."""
    import requests

    try:
        resp = requests.post(
            config['api_url'] + "/info",
            json={"type": "predictedFundings"},
            timeout=10
        )
        if resp.status_code != 200:
            print(f"{Colors.RED}Error fetching predicted funding rates (HTTP {resp.status_code}){Colors.END}")
            return 1
        data = resp.json()
    except Exception as e:
        print(f"{Colors.RED}Error fetching predicted funding rates: {e}{Colors.END}")
        return 1

    # Build lookup: {coin: {venue_key: {rate, next_time, interval}}}
    venue_names = {'HlPerp': 'HL', 'BinPerp': 'Bin', 'BybitPerp': 'Bybit'}
    lookup = {}
    for entry in data:
        coin = entry[0]
        venues = {}
        for venue_key, info_dict in entry[1]:
            if info_dict is None:
                continue
            short = venue_names.get(venue_key, venue_key)
            rate = float(info_dict.get('fundingRate', '0'))
            interval = int(info_dict.get('fundingIntervalHours', 1))
            next_time = info_dict.get('nextFundingTime')
            venues[short] = {'rate': rate, 'interval': interval, 'next_time': next_time}
        lookup[coin] = venues

    now_ms = int(time.time() * 1000)

    print(f"\n{Colors.BOLD}Predicted Funding Rates (next interval):{Colors.END}")
    print(f"  {'Asset':<12} {'HL APR':>10} {'Bin APR':>10} {'Bybit APR':>10}  {'Next In':>8}")
    print("  " + "-" * 55)

    for coin in coins:
        # Strip dex prefix for lookup (HIP-3 coins won't be in predicted data)
        bare = coin.split(':')[-1] if ':' in coin else coin
        if bare not in lookup:
            reason = "HIP-3 only (no cross-exchange data)" if ':' in coin else "Not found"
            print(f"  {coin:<12} {Colors.DIM}{reason}{Colors.END}")
            continue

        venues = lookup[bare]
        cols = []
        for venue in ['HL', 'Bin', 'Bybit']:
            if venue in venues:
                v = venues[venue]
                apr = v['rate'] / v['interval'] * 24 * 365 * 100
                cols.append(f"{apr:>9.1f}%")
            else:
                cols.append(f"{'—':>10}")

        # Time until next HL funding
        hl = venues.get('HL')
        if hl and hl['next_time']:
            remaining_ms = hl['next_time'] - now_ms
            if remaining_ms > 0:
                mins = remaining_ms // 60000
                next_str = f"{mins}m"
            else:
                next_str = "now"
        else:
            next_str = "—"

        print(f"  {coin:<12} {cols[0]} {cols[1]} {cols[2]}  {next_str:>8}")

    return 0


def cmd_funding(args):
    """Get funding rates for assets."""
    info, config = setup_info()
    coins = args.coins if args.coins else ['BTC', 'ETH', 'SOL', 'DOGE', 'HYPE']

    if getattr(args, 'predicted', False):
        return _cmd_funding_predicted(config, coins)

    try:
        # Get meta and asset contexts
        meta = info.meta_and_asset_ctxs()
        universe = meta[0]['universe']
        asset_ctxs = meta[1]

        # Build name to index map
        name_to_idx = {asset['name']: i for i, asset in enumerate(universe)}

        print(f"\n{Colors.BOLD}Funding Rates:{Colors.END}")
        print(f"  {'Asset':<12} {'Hourly':>12} {'APR':>12} {'Signal':<20}")
        print("  " + "-" * 55)

        for coin in coins:
            if coin in name_to_idx:
                idx = name_to_idx[coin]
                ctx = asset_ctxs[idx]
                funding = float(ctx.get('funding', 0))
                funding_pct = funding * 100
                apr = funding * 24 * 365 * 100

                # Signal interpretation
                if funding < -0.0001:
                    signal = f"{Colors.GREEN}Shorts paying (bullish){Colors.END}"
                elif funding > 0.0005:
                    signal = f"{Colors.RED}Longs crowded (bearish){Colors.END}"
                else:
                    signal = f"{Colors.YELLOW}Neutral{Colors.END}"

                print(f"  {coin:<12} {funding_pct:>11.4f}% {apr:>11.1f}% {signal}")
            else:
                # Try HIP-3 perps - fetch dex list dynamically from API
                try:
                    all_dexes = info.perp_dexs()
                    hip3_dexes = [d.get('name') for d in all_dexes if d is not None and d.get('name')]
                except:
                    # Fallback to known dexes
                    hip3_dexes = ['xyz', 'vntl', 'flx', 'hyna', 'km', 'abcd', 'cash']
                found = False

                # Check if coin already has a dex prefix
                if ':' in coin:
                    coins_to_try = [coin]
                else:
                    coins_to_try = [f"{dex}:{coin}" for dex in hip3_dexes]

                import requests
                for try_coin in coins_to_try:
                    try:
                        resp = requests.post(
                            config['api_url'] + "/info",
                            json={"type": "fundingHistory", "coin": try_coin, "startTime": 0},
                            timeout=10
                        )
                        if resp.status_code == 200:
                            data = resp.json()
                            if data:
                                latest = data[-1]
                                funding = float(latest.get('fundingRate', 0))
                                funding_pct = funding * 100
                                apr = funding * 24 * 365 * 100
                                signal = f"{Colors.GREEN}Shorts paying{Colors.END}" if funding < 0 else f"{Colors.YELLOW}Longs paying{Colors.END}"
                                print(f"  {try_coin:<16} {funding_pct:>11.4f}% {apr:>11.1f}% {signal}")
                                found = True
                                break
                    except:
                        pass

                if not found:
                    print(f"  {coin:<12} {Colors.DIM}Not found{Colors.END}")

        return 0
    except Exception as e:
        print(f"{Colors.RED}Error fetching funding rates: {e}{Colors.END}")
        return 1


def cmd_book(args):
    """Get order book for an asset."""
    info, config = setup_info()
    coin = args.coin

    try:
        book = info.l2_snapshot(coin)

        print(f"\n{Colors.BOLD}{coin} Order Book:{Colors.END}")
        print(f"  {'Bids':<30} {'Asks':<30}")
        print("  " + "-" * 60)

        bids = book.get('levels', [[]])[0][:5]
        asks = book.get('levels', [[], []])[1][:5]

        for i in range(max(len(bids), len(asks))):
            bid_str = ""
            ask_str = ""
            if i < len(bids):
                bid_str = f"{Colors.GREEN}{format_price(float(bids[i]['px']))} x {bids[i]['sz']}{Colors.END}"
            if i < len(asks):
                ask_str = f"{Colors.RED}{format_price(float(asks[i]['px']))} x {asks[i]['sz']}{Colors.END}"
            print(f"  {bid_str:<40} {ask_str:<40}")

        # Mid price
        if bids and asks:
            mid = (float(bids[0]['px']) + float(asks[0]['px'])) / 2
            spread = float(asks[0]['px']) - float(bids[0]['px'])
            spread_pct = (spread / mid) * 100
            print(f"\n  Mid: {format_price(mid)} | Spread: {format_price(spread)} ({spread_pct:.3f}%)")

        return 0
    except Exception as e:
        print(f"{Colors.RED}Error fetching order book: {e}{Colors.END}")
        return 1


def cmd_orders(args):
    """List open orders with trigger/TP/SL details."""
    info, config = setup_info(require_credentials=True, include_hip3=True)

    try:
        open_orders = _get_all_open_orders(info, config['account_address'])

        print(f"\n{Colors.BOLD}Open Orders:{Colors.END}")

        if not open_orders:
            print(f"  {Colors.DIM}No open orders{Colors.END}")
            return 0

        print(f"  {'OID':<12} {'Asset':<12} {'Side':<6} {'Size':>12} {'Price':>12} {'Type':<12} {'Details'}")
        print("  " + "-" * 85)

        for order in open_orders:
            oid = order.get('oid', 'N/A')
            coin = order.get('coin', 'N/A')
            side = "BUY" if order.get('side') == 'B' else "SELL"
            side_color = Colors.GREEN if side == "BUY" else Colors.RED
            sz = order.get('sz', '0')
            px = float(order.get('limitPx', 0))
            order_type = order.get('orderType', 'limit')

            # Build details string from extra fields
            details = []
            if order.get('isTrigger'):
                trigger_px = order.get('triggerPx', '')
                trigger_cond = order.get('triggerCondition', '')
                details.append(f"trigger@{trigger_px} {trigger_cond}")
            if order.get('isPositionTpsl'):
                details.append("TP/SL")
            if order.get('reduceOnly'):
                details.append("reduce-only")
            tif = order.get('tif', '')
            if tif and tif != 'Gtc':
                details.append(tif)
            detail_str = ", ".join(details) if details else ""

            print(f"  {oid:<12} {coin:<12} {side_color}{side:<6}{Colors.END} {sz:>12} {format_price(px):>12} {order_type:<12} {detail_str}")

        return 0
    except Exception as e:
        print(f"{Colors.RED}Error fetching orders: {e}{Colors.END}")
        return 1


# ============================================================================
# TRADING COMMANDS
# ============================================================================

def _set_leverage(exchange, coin, leverage, is_cross=True):
    """Set leverage for an asset before trading."""
    margin_type = "cross" if is_cross else "isolated"
    try:
        result = exchange.update_leverage(leverage, coin, is_cross)
        if result.get('status') == 'ok':
            print(f"  Leverage set: {leverage}x ({margin_type})")
        else:
            print(f"{Colors.RED}Failed to set leverage: {result}{Colors.END}")
            return False
    except Exception as e:
        print(f"{Colors.RED}Error setting leverage: {e}{Colors.END}")
        return False
    return True


def _get_max_leverage(info, coin):
    """Get max leverage for an asset from metadata."""
    try:
        # Check native perps
        meta = info.meta()
        for asset in meta.get('universe', []):
            if asset['name'] == coin:
                return asset.get('maxLeverage')
        # Check HIP-3 dexes
        if ':' in coin:
            dex = coin.split(':')[0]
            meta = info.meta(dex=dex)
            for asset in meta.get('universe', []):
                if asset['name'] == coin:
                    return asset.get('maxLeverage')
    except Exception:
        pass
    return None


def cmd_leverage(args):
    """Set leverage for an asset."""
    exchange, info, config = setup_exchange()
    coin = args.coin
    leverage = args.leverage
    is_cross = not args.isolated

    max_lev = _get_max_leverage(info, coin)
    margin_type = "cross" if is_cross else "isolated"
    max_str = f" (max: {max_lev}x)" if max_lev else ""

    print(f"\n{Colors.BOLD}Setting {coin} leverage: {leverage}x ({margin_type}){max_str}{Colors.END}")

    if max_lev and leverage > max_lev:
        print(f"{Colors.RED}Error: {leverage}x exceeds max leverage of {max_lev}x for {coin}{Colors.END}")
        return 1

    try:
        result = exchange.update_leverage(leverage, coin, is_cross)
        if result.get('status') == 'ok':
            _invalidate_proxy_cache(config)
            print(f"{Colors.GREEN}Leverage updated!{Colors.END}")
            print(f"  {coin}: {leverage}x {margin_type}")
            return 0
        else:
            print(f"{Colors.RED}Failed: {result}{Colors.END}")
            return 1
    except Exception as e:
        print(f"{Colors.RED}Error: {e}{Colors.END}")
        return 1


def cmd_transfer(args):
    """Swap USDC to the collateral token required by a HIP-3 dex."""
    exchange, info, config = setup_exchange()
    amount = args.amount

    # Figure out which collateral to swap to/from
    token_name = getattr(args, 'token', None)
    spot_pair = None

    if token_name:
        # User specified the token directly
        for idx, (name, pair, _slippage) in _COLLATERAL_SPOT_PAIRS.items():
            if name.upper() == token_name.upper():
                spot_pair = pair
                token_name = name
                break
        if not spot_pair:
            print(f"{Colors.RED}Unknown collateral token: {token_name}")
            print(f"Known tokens: {', '.join(name for name, _p, _s in _COLLATERAL_SPOT_PAIRS.values())}{Colors.END}")
            return 1
    else:
        # Default to USDH (most common: km, flx, vntl)
        token_name = 'USDH'
        spot_pair = '@230'

    is_sell = args.to_usdc  # sell collateral back to USDC
    if is_sell:
        print(f"\n{Colors.BOLD}Swap: {amount:.2f} {token_name} → USDC{Colors.END}")
    else:
        print(f"\n{Colors.BOLD}Swap: {amount:.2f} USDC → {token_name}{Colors.END}")

    try:
        had_error = False

        # Show current balances
        spot_state = info.spot_user_state(config['account_address'])
        for b in spot_state.get('balances', []):
            coin = b.get('coin', '')
            if coin in ('USDC', token_name):
                total = float(b.get('total', 0))
                hold = float(b.get('hold', 0))
                hold_str = f" (hold: {hold:.2f})" if hold > 0.01 else ""
                print(f"  {coin:<8} {total:.2f}{hold_str}")

        # Execute spot swap (IOC = fill at best available price, limit just sets ceiling/floor)
        # Slippage is per-token: tight for liquid strict-list tokens, wider for thin books.
        slippage = _get_swap_slippage(token_name)
        if is_sell:
            result = exchange.order(spot_pair, False, float(amount), 1.0 - slippage, {'limit': {'tif': 'Ioc'}})
        else:
            result = exchange.order(spot_pair, True, float(amount), 1.0 + slippage, {'limit': {'tif': 'Ioc'}})

        if result.get('status') == 'ok':
            _invalidate_proxy_cache(config)
            statuses = result.get('response', {}).get('data', {}).get('statuses', [])
            for status in statuses:
                if 'filled' in status:
                    filled = status['filled']
                    print(f"\n{Colors.GREEN}Swapped {filled.get('totalSz')} {token_name} @ {filled.get('avgPx')}{Colors.END}")
                elif 'error' in status:
                    print(f"\n{Colors.RED}Error: {_humanize_error(status['error'], info)}{Colors.END}")
                    had_error = True
        else:
            print(f"\n{Colors.RED}Swap failed: {result}{Colors.END}")
            had_error = True

        # Show updated balances
        spot_state = info.spot_user_state(config['account_address'])
        print(f"\n  After:")
        for b in spot_state.get('balances', []):
            coin = b.get('coin', '')
            if coin in ('USDC', token_name):
                total = float(b.get('total', 0))
                hold = float(b.get('hold', 0))
                hold_str = f" (hold: {hold:.2f})" if hold > 0.01 else ""
                print(f"    {coin:<8} {total:.2f}{hold_str}")

        return 1 if had_error else 0
    except Exception as e:
        print(f"{Colors.RED}Error: {e}{Colors.END}")
        return 1


# Map of HIP-3 dex collateral token index → (token name, USDC spot pair coin, slippage)
# Built from perp_dex meta collateralToken field + spot pair lookup.
# Token 0 = USDC (no swap needed).
# Slippage: max distance from $1.00 for IOC fill. Tight for liquid strict-list tokens,
# wider for thin books. IOC always fills at best available — this is just a guard rail.
_COLLATERAL_SPOT_PAIRS = {
    360: ('USDH', '@230', 0.002),    # km, flx, vntl — strict list, tight spreads
    235: ('USDe', '@150', 0.002),    # hyna — strict list, tight spreads
    268: ('USDT0', '@166', 0.002),   # cash — strict list, tight spreads
    239: ('USDXL', '@152', 0.02),    # Last USD — not on strict list, wider spreads
}


def _get_dex_collateral(info, dex_name):
    """Get the collateral token info for a HIP-3 dex.

    Returns (token_index, token_name, spot_pair) or (0, 'USDC', None) if USDC.
    """
    try:
        meta = info.meta(dex=dex_name)
        token_idx = meta.get('collateralToken', 0)
        if token_idx == 0:
            return (0, 'USDC', None)
        entry = _COLLATERAL_SPOT_PAIRS.get(token_idx)
        if entry:
            return (token_idx, entry[0], entry[1])
        return (token_idx, f'token#{token_idx}', None)
    except Exception:
        return (0, 'USDC', None)


def _get_swap_slippage(token_name):
    """Get the IOC slippage limit for a collateral token swap."""
    for _idx, (name, _pair, slippage) in _COLLATERAL_SPOT_PAIRS.items():
        if name.upper() == token_name.upper():
            return slippage
    return 0.002  # default: tight



def _humanize_error(error_text: str, info) -> str:
    """Replace cryptic asset IDs in API errors with human-readable coin names.

    e.g. 'Order must have minimum value of $10. asset=184'
      -> 'Order must have minimum value of $10. asset=OM'
    """
    import re
    match = re.search(r'asset=(\d+)', error_text)
    if not match:
        return error_text
    asset_id = int(match.group(1))
    try:
        meta = info.meta_and_asset_ctxs()
        universe = meta[0]['universe']
        if 0 <= asset_id < len(universe):
            name = universe[asset_id].get('name', f'#{asset_id}')
            return error_text.replace(f'asset={asset_id}', f'asset={name}')
    except Exception:
        pass
    return error_text


def _handle_margin_error(error_text, coin, info, config):
    """Show actionable guidance when an order fails with a margin error on HIP-3."""
    if ':' not in coin:
        return

    lower = error_text.lower()
    if 'margin' not in lower and 'insufficient' not in lower:
        return

    dex = coin.split(':')[0]
    try:
        token_idx, token_name, spot_pair = _get_dex_collateral(info, dex)
        if token_idx == 0:
            return  # USDC collateral, nothing special to say

        spot_state = info.spot_user_state(config['account_address'])
        collateral_free = 0
        usdc_free = 0
        for b in spot_state.get('balances', []):
            total = float(b.get('total', 0))
            hold = float(b.get('hold', 0))
            if b.get('coin') == token_name:
                collateral_free = total - hold
            elif b.get('coin') == 'USDC':
                usdc_free = total - hold

        print(f"\n{Colors.YELLOW}{dex} dex uses {token_name} as collateral (not USDC).")
        print(f"  {token_name} balance: {collateral_free:.2f}")
        print(f"  USDC balance: {format_price(usdc_free)}")
        if spot_pair:
            print(f"  Swap USDC first: hyperliquid_tools.py swap <amount> --token {token_name}{Colors.END}")
        else:
            print(f"  Swap USDC → {token_name} via the Hyperliquid UI.{Colors.END}")
    except Exception:
        pass


def cmd_buy(args):
    """Market buy."""
    exchange, info, config = setup_exchange()
    coin = args.coin
    size = args.size

    print(f"\n{Colors.BOLD}Market Buy: {size} {coin}{Colors.END}")
    if config['is_testnet']:
        print(f"{Colors.YELLOW}[TESTNET]{Colors.END}")

    try:
        # Set leverage if specified
        if args.leverage:
            if not _set_leverage(exchange, coin, args.leverage, not getattr(args, 'isolated', False)):
                return 1

        # Get current price for reference
        if ':' in coin:
            dex = coin.split(':')[0]
            all_mids = info.all_mids(dex=dex)
        else:
            all_mids = info.all_mids()
        current_price = float(all_mids[coin]) if coin in all_mids else None

        if current_price:
            print(f"Current price: {format_price(current_price)}")
            print(f"Estimated cost: {format_price(current_price * size)}")

        # Execute market buy
        result = exchange.market_open(coin, True, size, None, 0.01)  # 1% slippage

        had_error = False
        if result.get('status') == 'ok':
            _invalidate_proxy_cache(config)
            statuses = result.get('response', {}).get('data', {}).get('statuses', [])
            for status in statuses:
                if 'filled' in status:
                    filled = status['filled']
                    print(f"\n{Colors.GREEN}Order filled!{Colors.END}")
                    print(f"  Size: {filled.get('totalSz')}")
                    print(f"  Avg Price: {format_price(float(filled.get('avgPx', 0)))}")
                    print(f"  OID: {filled.get('oid')}")
                elif 'error' in status:
                    print(f"\n{Colors.RED}Error: {_humanize_error(status['error'], info)}{Colors.END}")
                    _handle_margin_error(status['error'], coin, info, config)
                    had_error = True
        else:
            error_text = str(result)
            print(f"\n{Colors.RED}Order failed: {result}{Colors.END}")
            _handle_margin_error(error_text, coin, info, config)
            had_error = True

        return 1 if had_error else 0
    except Exception as e:
        print(f"{Colors.RED}Error executing buy: {e}{Colors.END}")
        return 1


def cmd_sell(args):
    """Market sell."""
    exchange, info, config = setup_exchange()
    coin = args.coin
    size = args.size

    print(f"\n{Colors.BOLD}Market Sell: {size} {coin}{Colors.END}")
    if config['is_testnet']:
        print(f"{Colors.YELLOW}[TESTNET]{Colors.END}")

    try:
        # Set leverage if specified
        if args.leverage:
            if not _set_leverage(exchange, coin, args.leverage, not getattr(args, 'isolated', False)):
                return 1

        # Get current price for reference
        if ':' in coin:
            dex = coin.split(':')[0]
            all_mids = info.all_mids(dex=dex)
        else:
            all_mids = info.all_mids()
        current_price = float(all_mids[coin]) if coin in all_mids else None

        if current_price:
            print(f"Current price: {format_price(current_price)}")

        # Execute market sell
        result = exchange.market_open(coin, False, size, None, 0.01)  # 1% slippage

        had_error = False
        if result.get('status') == 'ok':
            _invalidate_proxy_cache(config)
            statuses = result.get('response', {}).get('data', {}).get('statuses', [])
            for status in statuses:
                if 'filled' in status:
                    filled = status['filled']
                    print(f"\n{Colors.GREEN}Order filled!{Colors.END}")
                    print(f"  Size: {filled.get('totalSz')}")
                    print(f"  Avg Price: {format_price(float(filled.get('avgPx', 0)))}")
                    print(f"  OID: {filled.get('oid')}")
                elif 'error' in status:
                    print(f"\n{Colors.RED}Error: {_humanize_error(status['error'], info)}{Colors.END}")
                    _handle_margin_error(status['error'], coin, info, config)
                    had_error = True
        else:
            error_text = str(result)
            print(f"\n{Colors.RED}Order failed: {result}{Colors.END}")
            _handle_margin_error(error_text, coin, info, config)
            had_error = True

        return 1 if had_error else 0
    except Exception as e:
        print(f"{Colors.RED}Error executing sell: {e}{Colors.END}")
        return 1


def cmd_limit_buy(args):
    """Place limit buy order."""
    exchange, info, config = setup_exchange()
    coin = args.coin
    size = args.size
    price = args.price

    print(f"\n{Colors.BOLD}Limit Buy: {size} {coin} @ {format_price(price)}{Colors.END}")
    if config['is_testnet']:
        print(f"{Colors.YELLOW}[TESTNET]{Colors.END}")

    try:
        # Get current price for reference
        all_mids = info.all_mids()
        if coin in all_mids:
            current_price = float(all_mids[coin])
            diff_pct = ((price - current_price) / current_price) * 100
            print(f"Current price: {format_price(current_price)} ({diff_pct:+.2f}% from limit)")

        # Place limit order
        result = exchange.order(coin, True, size, price, {"limit": {"tif": "Gtc"}})

        had_error = False
        if result.get('status') == 'ok':
            _invalidate_proxy_cache(config)
            statuses = result.get('response', {}).get('data', {}).get('statuses', [])
            for status in statuses:
                if 'resting' in status:
                    print(f"\n{Colors.GREEN}Order placed!{Colors.END}")
                    print(f"  OID: {status['resting'].get('oid')}")
                elif 'filled' in status:
                    filled = status['filled']
                    print(f"\n{Colors.GREEN}Order filled immediately!{Colors.END}")
                    print(f"  Size: {filled.get('totalSz')}")
                    print(f"  Avg Price: {format_price(float(filled.get('avgPx', 0)))}")
                elif 'error' in status:
                    print(f"\n{Colors.RED}Error: {_humanize_error(status['error'], info)}{Colors.END}")
                    had_error = True
        else:
            print(f"\n{Colors.RED}Order failed: {result}{Colors.END}")
            had_error = True

        return 1 if had_error else 0
    except Exception as e:
        print(f"{Colors.RED}Error placing limit buy: {e}{Colors.END}")
        return 1


def cmd_limit_sell(args):
    """Place limit sell order."""
    exchange, info, config = setup_exchange()
    coin = args.coin
    size = args.size
    price = args.price

    print(f"\n{Colors.BOLD}Limit Sell: {size} {coin} @ {format_price(price)}{Colors.END}")
    if config['is_testnet']:
        print(f"{Colors.YELLOW}[TESTNET]{Colors.END}")

    try:
        # Get current price for reference
        all_mids = info.all_mids()
        if coin in all_mids:
            current_price = float(all_mids[coin])
            diff_pct = ((price - current_price) / current_price) * 100
            print(f"Current price: {format_price(current_price)} ({diff_pct:+.2f}% from limit)")

        # Place limit order
        result = exchange.order(coin, False, size, price, {"limit": {"tif": "Gtc"}})

        had_error = False
        if result.get('status') == 'ok':
            _invalidate_proxy_cache(config)
            statuses = result.get('response', {}).get('data', {}).get('statuses', [])
            for status in statuses:
                if 'resting' in status:
                    print(f"\n{Colors.GREEN}Order placed!{Colors.END}")
                    print(f"  OID: {status['resting'].get('oid')}")
                elif 'filled' in status:
                    filled = status['filled']
                    print(f"\n{Colors.GREEN}Order filled immediately!{Colors.END}")
                    print(f"  Size: {filled.get('totalSz')}")
                    print(f"  Avg Price: {format_price(float(filled.get('avgPx', 0)))}")
                elif 'error' in status:
                    print(f"\n{Colors.RED}Error: {_humanize_error(status['error'], info)}{Colors.END}")
                    had_error = True
        else:
            print(f"\n{Colors.RED}Order failed: {result}{Colors.END}")
            had_error = True

        return 1 if had_error else 0
    except Exception as e:
        print(f"{Colors.RED}Error placing limit sell: {e}{Colors.END}")
        return 1


def _get_position_for_coin(info, address, coin):
    """Return the open position dict for a specific coin, or None if not found."""
    dex = coin.split(':', 1)[0] if ':' in coin else ''
    try:
        state = info.user_state(address, dex=dex) if dex else info.user_state(address)
    except Exception:
        return None

    for pos in state.get('assetPositions', []):
        p = pos.get('position', {})
        if p.get('coin') != coin:
            continue
        try:
            if float(p.get('szi', 0)) != 0:
                return p
        except (TypeError, ValueError):
            continue
    return None


def _get_mid_price_for_coin(info, coin):
    """Get current mid price for native or HIP-3 coin."""
    try:
        if ':' in coin:
            dex = coin.split(':', 1)[0]
            mids = info.all_mids(dex=dex)
        else:
            mids = info.all_mids()
        px = mids.get(coin)
        return float(px) if px is not None else None
    except Exception:
        return None


def _validate_trigger_side(trigger_type: str, position_size: float, trigger_price: float, current_price: Optional[float]) -> str | None:
    """Validate trigger is on the correct side of current price for the position."""
    if current_price is None:
        return None  # Best effort only if mid price is unavailable

    is_long = position_size > 0
    if trigger_type == 'sl':
        if is_long and trigger_price >= current_price:
            return "For LONG stop-loss, trigger must be below current price."
        if not is_long and trigger_price <= current_price:
            return "For SHORT stop-loss, trigger must be above current price."
    elif trigger_type == 'tp':
        if is_long and trigger_price <= current_price:
            return "For LONG take-profit, trigger must be above current price."
        if not is_long and trigger_price >= current_price:
            return "For SHORT take-profit, trigger must be below current price."
    return None


def cmd_stop_loss(args):
    """Place a stop-loss trigger order. Closes position at market when trigger price is hit."""
    exchange, info, config = setup_exchange()
    coin = args.coin
    size = args.size
    trigger_price = args.trigger_price

    print(f"\n{Colors.BOLD}Stop-Loss: {size} {coin} @ trigger {format_price(trigger_price)}{Colors.END}")
    if config['is_testnet']:
        print(f"{Colors.YELLOW}[TESTNET]{Colors.END}")

    try:
        position = _get_position_for_coin(info, config['account_address'], coin)
        if not position:
            print(f"{Colors.RED}Error: No open position for {coin}{Colors.END}")
            return 1

        position_size = float(position.get('szi', 0))
        max_close_size = abs(position_size)
        if size <= 0:
            print(f"{Colors.RED}Error: Size must be greater than 0{Colors.END}")
            return 1
        if size > max_close_size:
            print(f"{Colors.RED}Error: Size {size} exceeds open position size {max_close_size:.4f}{Colors.END}")
            return 1

        # Closing side is defined by position direction, not trigger relative price.
        is_buy = position_size < 0
        side_label = "SHORT" if position_size < 0 else "LONG"
        print(f"Position: {side_label} {max_close_size:.4f}")

        current_price = _get_mid_price_for_coin(info, coin)
        if current_price:
            diff_pct = ((trigger_price - current_price) / current_price) * 100
            print(f"Current price: {format_price(current_price)} ({diff_pct:+.2f}% from trigger)")

        validation_error = _validate_trigger_side('sl', position_size, trigger_price, current_price)
        if validation_error:
            print(f"{Colors.RED}Error: {validation_error}{Colors.END}")
            return 1

        order_type = {
            "trigger": {
                "triggerPx": trigger_price,
                "isMarket": True,
                "tpsl": "sl"
            }
        }

        result = exchange.order(coin, is_buy, size, trigger_price, order_type, reduce_only=True)

        had_error = False
        if result.get('status') == 'ok':
            _invalidate_proxy_cache(config)
            statuses = result.get('response', {}).get('data', {}).get('statuses', [])
            for status in statuses:
                if 'resting' in status:
                    side = "BUY (close short)" if is_buy else "SELL (close long)"
                    print(f"\n{Colors.GREEN}Stop-loss placed!{Colors.END}")
                    print(f"  Side: {side}")
                    print(f"  Trigger: {format_price(trigger_price)}")
                    print(f"  Size: {size}")
                    print(f"  OID: {status['resting'].get('oid')}")
                    print(f"  Type: Market order when triggered")
                elif 'error' in status:
                    print(f"\n{Colors.RED}Error: {_humanize_error(status['error'], info)}{Colors.END}")
                    had_error = True
        else:
            print(f"\n{Colors.RED}Order failed: {result}{Colors.END}")
            had_error = True

        return 1 if had_error else 0
    except Exception as e:
        print(f"{Colors.RED}Error placing stop-loss: {e}{Colors.END}")
        return 1


def cmd_take_profit(args):
    """Place a take-profit trigger order. Closes position at market when trigger price is hit."""
    exchange, info, config = setup_exchange()
    coin = args.coin
    size = args.size
    trigger_price = args.trigger_price

    print(f"\n{Colors.BOLD}Take-Profit: {size} {coin} @ trigger {format_price(trigger_price)}{Colors.END}")
    if config['is_testnet']:
        print(f"{Colors.YELLOW}[TESTNET]{Colors.END}")

    try:
        position = _get_position_for_coin(info, config['account_address'], coin)
        if not position:
            print(f"{Colors.RED}Error: No open position for {coin}{Colors.END}")
            return 1

        position_size = float(position.get('szi', 0))
        max_close_size = abs(position_size)
        if size <= 0:
            print(f"{Colors.RED}Error: Size must be greater than 0{Colors.END}")
            return 1
        if size > max_close_size:
            print(f"{Colors.RED}Error: Size {size} exceeds open position size {max_close_size:.4f}{Colors.END}")
            return 1

        # Closing side is defined by position direction, not trigger relative price.
        is_buy = position_size < 0
        side_label = "SHORT" if position_size < 0 else "LONG"
        print(f"Position: {side_label} {max_close_size:.4f}")

        current_price = _get_mid_price_for_coin(info, coin)
        if current_price:
            diff_pct = ((trigger_price - current_price) / current_price) * 100
            print(f"Current price: {format_price(current_price)} ({diff_pct:+.2f}% from trigger)")

        validation_error = _validate_trigger_side('tp', position_size, trigger_price, current_price)
        if validation_error:
            print(f"{Colors.RED}Error: {validation_error}{Colors.END}")
            return 1

        order_type = {
            "trigger": {
                "triggerPx": trigger_price,
                "isMarket": True,
                "tpsl": "tp"
            }
        }

        result = exchange.order(coin, is_buy, size, trigger_price, order_type, reduce_only=True)

        had_error = False
        if result.get('status') == 'ok':
            _invalidate_proxy_cache(config)
            statuses = result.get('response', {}).get('data', {}).get('statuses', [])
            for status in statuses:
                if 'resting' in status:
                    side = "BUY (close short)" if is_buy else "SELL (close long)"
                    print(f"\n{Colors.GREEN}Take-profit placed!{Colors.END}")
                    print(f"  Side: {side}")
                    print(f"  Trigger: {format_price(trigger_price)}")
                    print(f"  Size: {size}")
                    print(f"  OID: {status['resting'].get('oid')}")
                    print(f"  Type: Market order when triggered")
                elif 'error' in status:
                    print(f"\n{Colors.RED}Error: {_humanize_error(status['error'], info)}{Colors.END}")
                    had_error = True
        else:
            print(f"\n{Colors.RED}Order failed: {result}{Colors.END}")
            had_error = True

        return 1 if had_error else 0
    except Exception as e:
        print(f"{Colors.RED}Error placing take-profit: {e}{Colors.END}")
        return 1


def cmd_close(args):
    """Close entire position for an asset."""
    exchange, info, config = setup_exchange()
    coin = args.coin

    print(f"\n{Colors.BOLD}Closing {coin} position{Colors.END}")
    if config['is_testnet']:
        print(f"{Colors.YELLOW}[TESTNET]{Colors.END}")

    try:
        # Check current position - check both main perps and HIP-3 dexes
        dex = None
        if ':' in coin:
            dex = coin.split(':')[0]

        if dex:
            user_state = info.user_state(config['account_address'], dex=dex)
        else:
            user_state = info.user_state(config['account_address'])
        positions = user_state.get('assetPositions', [])

        position = None
        for pos in positions:
            if pos['position']['coin'] == coin:
                position = pos['position']
                break

        if not position or float(position['szi']) == 0:
            print(f"{Colors.YELLOW}No open position for {coin}{Colors.END}")
            return 0

        size = float(position['szi'])
        entry_px = float(position['entryPx'])
        unrealized_pnl = float(position['unrealizedPnl'])

        print(f"Current position: {abs(size):.4f} {'LONG' if size > 0 else 'SHORT'}")
        print(f"Entry: {format_price(entry_px)}")
        print(f"Unrealized PnL: {format_pnl(unrealized_pnl)}")

        # Close position
        result = exchange.market_close(coin)

        had_error = False
        if result.get('status') == 'ok':
            _invalidate_proxy_cache(config)
            statuses = result.get('response', {}).get('data', {}).get('statuses', [])
            for status in statuses:
                if 'filled' in status:
                    filled = status['filled']
                    print(f"\n{Colors.GREEN}Position closed!{Colors.END}")
                    print(f"  Size: {filled.get('totalSz')}")
                    print(f"  Avg Price: {format_price(float(filled.get('avgPx', 0)))}")
                elif 'error' in status:
                    print(f"\n{Colors.RED}Error: {_humanize_error(status['error'], info)}{Colors.END}")
                    had_error = True
        else:
            print(f"\n{Colors.RED}Close failed: {result}{Colors.END}")
            had_error = True

        return 1 if had_error else 0
    except Exception as e:
        print(f"{Colors.RED}Error closing position: {e}{Colors.END}")
        return 1


def cmd_cancel(args):
    """Cancel a specific order."""
    exchange, info, config = setup_exchange()
    oid = args.oid

    # Need to find the coin for this order
    try:
        # Search across native + all HIP-3 dexes
        open_orders = _get_all_open_orders(info, config['account_address'])

        order = None
        for o in open_orders:
            if str(o.get('oid')) == str(oid):
                order = o
                break

        if not order:
            print(f"{Colors.YELLOW}Order {oid} not found in open orders{Colors.END}")
            return 1

        coin = order.get('coin')
        print(f"\n{Colors.BOLD}Canceling order {oid} ({coin}){Colors.END}")

        result = exchange.cancel(coin, int(oid))

        if result.get('status') == 'ok':
            _invalidate_proxy_cache(config)
            print(f"{Colors.GREEN}Order canceled!{Colors.END}")
            return 0
        else:
            print(f"{Colors.RED}Cancel failed: {result}{Colors.END}")
            return 1

    except Exception as e:
        print(f"{Colors.RED}Error canceling order: {e}{Colors.END}")
        return 1


def cmd_cancel_all(args):
    """Cancel all open orders in a single bulk request."""
    exchange, info, config = setup_exchange()

    print(f"\n{Colors.BOLD}Canceling all open orders{Colors.END}")

    try:
        # Collect open orders across native + all HIP-3 dexes
        open_orders = _get_all_open_orders(info, config['account_address'])

        cancel_requests = []
        seen = set()
        for order in open_orders:
            coin = order.get('coin')
            oid = order.get('oid')
            if not coin or oid is None:
                continue
            key = (coin, str(oid))
            if key in seen:
                continue
            seen.add(key)
            try:
                cancel_requests.append({"coin": coin, "oid": int(oid)})
            except (TypeError, ValueError):
                continue

        if not cancel_requests:
            print(f"{Colors.DIM}No open orders to cancel{Colors.END}")
            return 0

        print(f"Found {len(cancel_requests)} open orders")

        result = exchange.bulk_cancel(cancel_requests)

        if result.get('status') == 'ok':
            _invalidate_proxy_cache(config)
            statuses = result.get('response', {}).get('data', {}).get('statuses', [])
            had_error = False
            for i, status in enumerate(statuses):
                coin = cancel_requests[i]['coin'] if i < len(cancel_requests) else '?'
                oid = cancel_requests[i]['oid'] if i < len(cancel_requests) else '?'
                if status == 'success':
                    print(f"  {Colors.GREEN}Canceled {coin} order {oid}{Colors.END}")
                elif isinstance(status, dict) and 'error' in status:
                    print(f"  {Colors.RED}Failed {coin} order {oid}: {_humanize_error(status['error'], info)}{Colors.END}")
                    had_error = True
                else:
                    print(f"  {Colors.GREEN}Canceled {coin} order {oid}{Colors.END}")
            print(f"\n{Colors.GREEN}Done!{Colors.END}")
            return 1 if had_error else 0
        else:
            print(f"{Colors.RED}Bulk cancel failed: {result}{Colors.END}")
            return 1

    except Exception as e:
        print(f"{Colors.RED}Error canceling orders: {e}{Colors.END}")
        return 1


def cmd_modify_order(args):
    """Modify an existing order's price and/or size."""
    exchange, info, config = setup_exchange()
    oid = int(args.oid)
    new_price = args.price
    new_size = getattr(args, 'size', None)

    try:
        # Find the existing order to get coin and side
        open_orders = _get_all_open_orders(info, config['account_address'])

        order = None
        for o in open_orders:
            if str(o.get('oid')) == str(oid):
                order = o
                break

        if not order:
            print(f"{Colors.YELLOW}Order {oid} not found in open orders{Colors.END}")
            return 1

        coin = order['coin']
        is_buy = order['side'] == 'B'
        side_label = "Buy" if is_buy else "Sell"
        current_sz = float(order['sz'])
        current_px = float(order['limitPx'])
        sz = new_size if new_size else current_sz

        print(f"\n{Colors.BOLD}Modifying order {oid} ({coin}){Colors.END}")
        print(f"  {side_label}: {current_sz} @ {format_price(current_px)} -> {sz} @ {format_price(new_price)}")

        result = exchange.modify_order(
            oid,
            coin,
            is_buy,
            sz,
            new_price,
            {"limit": {"tif": "Gtc"}},
        )

        had_error = False
        if result.get('status') == 'ok':
            _invalidate_proxy_cache(config)
            statuses = result.get('response', {}).get('data', {}).get('statuses', [])
            for status in statuses:
                if 'resting' in status:
                    print(f"\n{Colors.GREEN}Order modified!{Colors.END}")
                    print(f"  OID: {status['resting'].get('oid')}")
                elif 'filled' in status:
                    filled = status['filled']
                    print(f"\n{Colors.GREEN}Modified order filled immediately!{Colors.END}")
                    print(f"  Size: {filled.get('totalSz')}")
                    print(f"  Avg Price: {format_price(float(filled.get('avgPx', 0)))}")
                elif 'error' in status:
                    print(f"\n{Colors.RED}Error: {_humanize_error(status['error'], info)}{Colors.END}")
                    had_error = True
        else:
            print(f"\n{Colors.RED}Modify failed: {result}{Colors.END}")
            had_error = True

        return 1 if had_error else 0
    except Exception as e:
        print(f"{Colors.RED}Error modifying order: {e}{Colors.END}")
        return 1


def cmd_analyze(args):
    """Comprehensive market analysis with raw data for AI agent processing."""
    info, config = setup_info(require_credentials=False)

    # Assets to analyze
    default_assets = ['BTC', 'ETH', 'SOL', 'DOGE', 'HYPE']
    xyz_assets = ['xyz:TSLA', 'xyz:NVDA', 'xyz:AAPL']
    coins = args.coins if args.coins else default_assets

    print(f"\n{Colors.BOLD}{Colors.CYAN}COMPREHENSIVE MARKET ANALYSIS{Colors.END}")
    print(f"Timestamp: {datetime.now().isoformat()}")
    if config['is_testnet']:
        print(f"{Colors.YELLOW}[TESTNET]{Colors.END}")
    print("=" * 80)

    try:
        # 1. Account State (if credentials configured)
        print(f"\n{Colors.BOLD}=== ACCOUNT STATE ==={Colors.END}")
        if config['account_address']:
            summary = get_account_summary(info, config['account_address'])
            user_state = summary['perp_state']

            print(f"Portfolio Value: ${summary['portfolio_value']:,.2f} {summary['mode_label']}")
            print(f"Total Margin Used: ${summary['margin_used']:,.2f}")
            print(f"Withdrawable: ${summary['withdrawable']:,.2f}")

            positions = user_state.get('assetPositions', [])
            open_positions = [p for p in positions if float(p['position']['szi']) != 0]

            if open_positions:
                print(f"\nOpen Positions ({len(open_positions)}):")
                for pos in open_positions:
                    p = pos['position']
                    size = float(p['szi'])
                    entry = float(p['entryPx'])
                    pnl = float(p['unrealizedPnl'])
                    lev = p.get('leverage', {})
                    print(f"  {p['coin']}: {size:+.4f} @ ${entry:,.2f} | PnL: ${pnl:+,.2f} | Leverage: {lev}")
            else:
                print("\nNo open positions")
        else:
            print(f"{Colors.DIM}No credentials configured - skipping account state{Colors.END}")
            print(f"Add HL_ACCOUNT_ADDRESS and HL_SECRET_KEY to .env to see positions")

        # 2. All Prices
        print(f"\n{Colors.BOLD}=== CURRENT PRICES ==={Colors.END}")
        all_mids = info.all_mids()
        for coin in coins:
            if coin in all_mids:
                print(f"{coin}: ${float(all_mids[coin]):,.2f}")

        # 3. Funding Rates & Market Context
        print(f"\n{Colors.BOLD}=== FUNDING RATES & MARKET CONTEXT ==={Colors.END}")
        meta = info.meta_and_asset_ctxs()
        universe = meta[0]['universe']
        asset_ctxs = meta[1]
        name_to_idx = {asset['name']: i for i, asset in enumerate(universe)}

        print(f"{'Asset':<10} {'Price':>12} {'Funding/hr':>12} {'Funding APR':>12} {'Open Interest':>15} {'24h Volume':>15}")
        print("-" * 80)

        for coin in coins:
            if coin in name_to_idx:
                idx = name_to_idx[coin]
                ctx = asset_ctxs[idx]
                price = float(ctx.get('markPx', 0))
                funding = float(ctx.get('funding', 0))
                oi = float(ctx.get('openInterest', 0))
                vol = float(ctx.get('dayNtlVlm', 0))

                funding_pct = funding * 100
                funding_apr = funding * 24 * 365 * 100

                print(f"{coin:<10} ${price:>10,.2f} {funding_pct:>11.4f}% {funding_apr:>11.1f}% ${oi:>13,.0f} ${vol:>13,.0f}")

        # 4. HIP-3 Equity Perps
        print(f"\n{Colors.BOLD}=== HIP-3 EQUITY PERPS (trade.xyz) ==={Colors.END}")
        import requests
        for xyz_coin in xyz_assets:
            try:
                # Get funding
                resp = requests.post(
                    config['api_url'] + "/info",
                    json={"type": "fundingHistory", "coin": xyz_coin, "startTime": 0},
                    timeout=10
                )
                if resp.status_code == 200:
                    data = resp.json()
                    if data:
                        latest = data[-1]
                        funding = float(latest.get('fundingRate', 0))
                        funding_pct = funding * 100
                        funding_apr = funding * 24 * 365 * 100

                        # Get price from L2 book
                        book_resp = requests.post(
                            config['api_url'] + "/info",
                            json={"type": "l2Book", "coin": xyz_coin},
                            timeout=10
                        )
                        price = 0
                        if book_resp.status_code == 200:
                            book = book_resp.json()
                            levels = book.get('levels', [])
                            if len(levels) >= 2 and levels[0] and levels[1]:
                                mid = (float(levels[0][0]['px']) + float(levels[1][0]['px'])) / 2
                                price = mid

                        print(f"{xyz_coin:<12} ${price:>10,.2f} | Funding: {funding_pct:.4f}%/hr ({funding_apr:.1f}% APR)")
            except Exception as e:
                print(f"{xyz_coin:<12} Error: {e}")

        # 5. Order Book Depth (for major assets)
        print(f"\n{Colors.BOLD}=== ORDER BOOK SUMMARY ==={Colors.END}")
        for coin in ['BTC', 'ETH', 'SOL']:
            if coin in coins or True:  # Always show major assets
                try:
                    book = info.l2_snapshot(coin)
                    bids = book.get('levels', [[]])[0]
                    asks = book.get('levels', [[], []])[1]

                    if bids and asks:
                        best_bid = float(bids[0]['px'])
                        best_ask = float(asks[0]['px'])
                        mid = (best_bid + best_ask) / 2
                        spread = best_ask - best_bid
                        spread_bps = (spread / mid) * 10000

                        # Sum depth
                        bid_depth = sum(float(b['sz']) for b in bids[:10])
                        ask_depth = sum(float(a['sz']) for a in asks[:10])
                        imbalance = (bid_depth - ask_depth) / (bid_depth + ask_depth) if (bid_depth + ask_depth) > 0 else 0

                        print(f"{coin}: Spread {spread_bps:.1f}bps | Bid depth: {bid_depth:.2f} | Ask depth: {ask_depth:.2f} | Imbalance: {imbalance:+.2%}")
                except:
                    pass

        # 6. Recent Price Changes (from candles if available)
        print(f"\n{Colors.BOLD}=== NOTES FOR ANALYSIS ==={Colors.END}")
        print("""
Key signals to consider:
- Negative funding = shorts paying longs = potential squeeze opportunity (contrarian long)
- Positive funding > 0.01%/hr = longs crowded = potential long squeeze (caution)
- Order book imbalance > ±20% = directional pressure
- Open interest spike = new positions being built

For full technical analysis (RSI, SMA, ATH distance):
  python market_analyzer.py --skip-sentiment

For sentiment analysis (slower, uses Grok):
  python market_analyzer.py
""")

        return 0
    except Exception as e:
        print(f"{Colors.RED}Error during analysis: {e}{Colors.END}")
        import traceback
        traceback.print_exc()
        return 1


def cmd_raw(args):
    """Dump raw JSON data for specified asset - for AI processing."""
    info, config = setup_info()
    coin = args.coin

    print(f"\n{Colors.BOLD}Raw Data Dump: {coin}{Colors.END}")
    print("=" * 60)

    try:
        # Price
        all_mids = info.all_mids()
        if coin in all_mids:
            print(f"\n--- Price ---")
            print(f"mid_price: {all_mids[coin]}")

        # Meta and context
        meta = info.meta_and_asset_ctxs()
        universe = meta[0]['universe']
        asset_ctxs = meta[1]
        name_to_idx = {asset['name']: i for i, asset in enumerate(universe)}

        if coin in name_to_idx:
            idx = name_to_idx[coin]
            print(f"\n--- Asset Metadata ---")
            print(json.dumps(universe[idx], indent=2))
            print(f"\n--- Asset Context ---")
            print(json.dumps(asset_ctxs[idx], indent=2))

        # Order book
        print(f"\n--- L2 Book (Top 5) ---")
        book = info.l2_snapshot(coin)
        print(json.dumps({
            'bids': book.get('levels', [[]])[0][:5],
            'asks': book.get('levels', [[], []])[1][:5]
        }, indent=2))

        # Recent trades
        print(f"\n--- Recent Trades (Last 10) ---")
        # Note: SDK might not have this, using requests
        import requests
        resp = requests.post(
            config['api_url'] + "/info",
            json={"type": "recentTrades", "coin": coin},
            timeout=10
        )
        if resp.status_code == 200:
            trades = resp.json()[-10:]
            print(json.dumps(trades, indent=2))

        return 0
    except Exception as e:
        print(f"{Colors.RED}Error: {e}{Colors.END}")
        return 1


def cmd_candles(args):
    """Get OHLCV candlestick data for technical analysis."""
    info, config = setup_info()
    coin = args.coin
    interval = args.interval
    lookback = args.lookback

    # Parse lookback to milliseconds
    now_ms = int(datetime.now().timestamp() * 1000)
    unit = lookback[-1].lower()
    amount = int(lookback[:-1])
    if unit == 'h':
        start_ms = now_ms - (amount * 3600 * 1000)
    elif unit == 'd':
        start_ms = now_ms - (amount * 86400 * 1000)
    elif unit == 'w':
        start_ms = now_ms - (amount * 7 * 86400 * 1000)
    else:
        print(f"{Colors.RED}Invalid lookback format. Use e.g., 24h, 7d, 2w{Colors.END}")
        return 1

    print(f"\n{Colors.BOLD}{coin} Candles ({interval}, last {lookback}){Colors.END}")
    print("=" * 80)

    try:
        candles = info.candles_snapshot(coin, interval, start_ms, now_ms)

        if not candles:
            print(f"{Colors.DIM}No candle data{Colors.END}")
            return 0

        # Print table
        print(f"  {'Time':<18} {'Open':>12} {'High':>12} {'Low':>12} {'Close':>12} {'Volume':>14}")
        print("  " + "-" * 82)

        closes = []
        for c in candles:
            t = datetime.fromtimestamp(c['t'] / 1000).strftime('%Y-%m-%d %H:%M')
            o = float(c['o'])
            h = float(c['h'])
            l = float(c['l'])
            cl = float(c['c'])
            v = float(c['v'])
            closes.append(cl)

            # Color: green if close > open, red if close < open
            color = Colors.GREEN if cl >= o else Colors.RED
            print(f"  {t:<18} {color}{format_price(o):>12} {format_price(h):>12} {format_price(l):>12} {format_price(cl):>12}{Colors.END} {v:>14.2f}")

        # Summary stats
        if len(closes) >= 2:
            print(f"\n{Colors.BOLD}Summary:{Colors.END}")
            first = closes[0]
            last = closes[-1]
            high = max(float(c['h']) for c in candles)
            low = min(float(c['l']) for c in candles)
            change = ((last - first) / first) * 100
            change_color = Colors.GREEN if change >= 0 else Colors.RED

            print(f"  Period change: {change_color}{change:+.2f}%{Colors.END} ({format_price(first)} -> {format_price(last)})")
            print(f"  Period high:   {format_price(high)}")
            print(f"  Period low:    {format_price(low)}")
            print(f"  Candles:       {len(candles)}")

            # Simple moving averages if enough data
            if len(closes) >= 20:
                sma20 = sum(closes[-20:]) / 20
                print(f"  SMA(20):       {format_price(sma20)}")
                pos = "above" if last > sma20 else "below"
                print(f"  Price vs SMA:  {pos} ({((last - sma20) / sma20 * 100):+.2f}%)")

            if len(closes) >= 50:
                sma50 = sum(closes[-50:]) / 50
                print(f"  SMA(50):       {format_price(sma50)}")

        return 0
    except Exception as e:
        print(f"{Colors.RED}Error fetching candles: {e}{Colors.END}")
        return 1


def cmd_funding_history(args):
    """Show historical funding rates for a coin."""
    info, config = setup_info()
    coin = args.coin
    lookback = getattr(args, 'lookback', '7d')

    # Parse lookback to ms
    now_ms = int(datetime.now().timestamp() * 1000)
    unit = lookback[-1].lower()
    amount = int(lookback[:-1])
    if unit == 'h':
        start_ms = now_ms - (amount * 3600 * 1000)
    elif unit == 'd':
        start_ms = now_ms - (amount * 86400 * 1000)
    elif unit == 'w':
        start_ms = now_ms - (amount * 7 * 86400 * 1000)
    else:
        start_ms = now_ms - (7 * 86400 * 1000)

    try:
        data = info.funding_history(coin, start_ms, now_ms)
        if not data:
            print(f"No funding history for {coin}")
            return 0

        print(f"\n{Colors.BOLD}{coin} Funding History (last {lookback}){Colors.END}")
        print("=" * 70)
        print(f"  {'Time':<22} {'Rate':>12} {'Annualized':>14} {'Premium':>12}")
        print(f"  {'-'*22} {'-'*12} {'-'*14} {'-'*12}")

        rates = []
        for entry in data:
            ts = datetime.fromtimestamp(entry['time'] / 1000).strftime('%Y-%m-%d %H:%M')
            rate = float(entry['fundingRate'])
            premium = float(entry['premium'])
            annual = rate * 8760 * 100  # hourly rate * hours/year * 100 for %
            rates.append(rate)

            color = Colors.GREEN if rate >= 0 else Colors.RED
            print(f"  {ts:<22} {color}{rate*100:>+11.6f}%{Colors.END} {color}{annual:>+13.2f}%{Colors.END} {premium*100:>+11.6f}%")

        # Summary
        avg_rate = sum(rates) / len(rates) if rates else 0
        avg_annual = avg_rate * 8760 * 100
        max_rate = max(rates) if rates else 0
        min_rate = min(rates) if rates else 0
        color = Colors.GREEN if avg_rate >= 0 else Colors.RED
        print(f"\n{Colors.BOLD}Summary:{Colors.END}")
        print(f"  Samples:        {len(rates)}")
        print(f"  Avg rate:       {color}{avg_rate*100:+.6f}% ({avg_annual:+.2f}% annualized){Colors.END}")
        print(f"  Max rate:       {max_rate*100:+.6f}%")
        print(f"  Min rate:       {min_rate*100:+.6f}%")
        print()

        return 0
    except Exception as e:
        print(f"{Colors.RED}Error fetching funding history: {e}{Colors.END}")
        return 1


def cmd_trades(args):
    """Show recent trades for a coin."""
    info, config = setup_info()
    coin = args.coin
    limit = getattr(args, 'limit', 20)

    try:
        # SDK doesn't wrap recentTrades, use raw post
        data = info.post("/info", {"type": "recentTrades", "coin": coin})
        if not data:
            print(f"No recent trades for {coin}")
            return 0

        # Take last N trades
        trades = data[-limit:] if len(data) > limit else data

        print(f"\n{Colors.BOLD}{coin} Recent Trades (last {len(trades)}){Colors.END}")
        print("=" * 75)
        print(f"  {'Time':<22} {'Side':<6} {'Price':>14} {'Size':>12} {'Value':>14}")
        print(f"  {'-'*22} {'-'*6} {'-'*14} {'-'*12} {'-'*14}")

        total_buy_vol = 0
        total_sell_vol = 0
        for t in trades:
            ts = datetime.fromtimestamp(t['time'] / 1000).strftime('%Y-%m-%d %H:%M:%S')
            side = t['side']
            px = float(t['px'])
            sz = float(t['sz'])
            value = px * sz

            if side == 'B':
                color = Colors.GREEN
                side_label = "BUY"
                total_buy_vol += value
            else:
                color = Colors.RED
                side_label = "SELL"
                total_sell_vol += value

            print(f"  {ts:<22} {color}{side_label:<6}{Colors.END} ${px:>13,.2f} {sz:>12} ${value:>13,.2f}")

        # Summary
        total_vol = total_buy_vol + total_sell_vol
        buy_pct = (total_buy_vol / total_vol * 100) if total_vol > 0 else 50
        print(f"\n{Colors.BOLD}Summary:{Colors.END}")
        print(f"  Buy volume:     ${total_buy_vol:>14,.2f} ({buy_pct:.1f}%)")
        print(f"  Sell volume:    ${total_sell_vol:>14,.2f} ({100-buy_pct:.1f}%)")
        print(f"  Total volume:   ${total_vol:>14,.2f}")
        bias_color = Colors.GREEN if buy_pct > 50 else Colors.RED if buy_pct < 50 else Colors.END
        bias = "BUY BIAS" if buy_pct > 55 else "SELL BIAS" if buy_pct < 45 else "NEUTRAL"
        print(f"  Bias:           {bias_color}{bias}{Colors.END}")
        print()

        return 0
    except Exception as e:
        print(f"{Colors.RED}Error fetching recent trades: {e}{Colors.END}")
        return 1


def cmd_user_funding(args):
    """Show personal funding payments received/paid on positions."""
    info, config = setup_info(require_credentials=True)
    lookback = getattr(args, 'lookback', '7d')

    # Parse lookback to ms
    now_ms = int(datetime.now().timestamp() * 1000)
    unit = lookback[-1].lower()
    amount = int(lookback[:-1])
    if unit == 'h':
        start_ms = now_ms - (amount * 3600 * 1000)
    elif unit == 'd':
        start_ms = now_ms - (amount * 86400 * 1000)
    elif unit == 'w':
        start_ms = now_ms - (amount * 7 * 86400 * 1000)
    else:
        start_ms = now_ms - (7 * 86400 * 1000)

    try:
        data = info.user_funding_history(config['account_address'], start_ms, now_ms)
        if not data:
            print(f"No funding payments in the last {lookback}")
            return 0

        print(f"\n{Colors.BOLD}Your Funding Payments (last {lookback}){Colors.END}")
        print("=" * 80)
        print(f"  {'Time':<22} {'Coin':<12} {'Payment':>14} {'Position Size':>14}")
        print(f"  {'-'*22} {'-'*12} {'-'*14} {'-'*14}")

        total_funding = 0
        by_coin = {}
        for entry in data:
            ts = datetime.fromtimestamp(entry['time'] / 1000).strftime('%Y-%m-%d %H:%M')
            coin = entry.get('coin', entry.get('delta', {}).get('coin', '?'))
            delta = entry.get('delta', {})
            funding_delta = float(delta.get('usdc', 0))
            szi = delta.get('szi', '?')
            total_funding += funding_delta

            if coin not in by_coin:
                by_coin[coin] = 0
            by_coin[coin] += funding_delta

            color = Colors.GREEN if funding_delta >= 0 else Colors.RED
            print(f"  {ts:<22} {coin:<12} {color}${funding_delta:>+13,.4f}{Colors.END} {szi:>14}")

        # Summary
        color = Colors.GREEN if total_funding >= 0 else Colors.RED
        print(f"\n{Colors.BOLD}Summary:{Colors.END}")
        print(f"  Total funding:  {color}${total_funding:>+,.4f}{Colors.END}")
        print(f"  Payments:       {len(data)}")
        if by_coin:
            print(f"\n  {Colors.BOLD}By coin:{Colors.END}")
            for coin, amt in sorted(by_coin.items(), key=lambda x: abs(x[1]), reverse=True):
                c = Colors.GREEN if amt >= 0 else Colors.RED
                print(f"    {coin:<12} {c}${amt:>+,.4f}{Colors.END}")
        print()

        return 0
    except Exception as e:
        print(f"{Colors.RED}Error fetching funding payments: {e}{Colors.END}")
        return 1


def cmd_portfolio(args):
    """Show portfolio performance overview."""
    info, config = setup_info(require_credentials=False)

    address = args.address if hasattr(args, 'address') and args.address else config.get('account_address', '')
    if not address:
        print(f"{Colors.RED}Error: No account address. Set HL_ACCOUNT_ADDRESS or use --address.{Colors.END}")
        return 1

    try:
        # Show current portfolio value as header
        try:
            summary = get_account_summary(info, address)
            pv = summary['portfolio_value']
            mode_label = summary['mode_label']
            print(f"\n{Colors.BOLD}Portfolio Performance{Colors.END} {mode_label}")
            print("=" * 60)
            print(f"  Current Value: ${pv:>,.2f}")
        except Exception:
            print(f"\n{Colors.BOLD}Portfolio Performance{Colors.END}")
            print("=" * 60)

        data = info.portfolio(address)
        if not data:
            print("No portfolio data available")
            return 0

        # API returns [["day", {data}], ["week", {data}], ...] or dict
        periods = {}
        if isinstance(data, list):
            for item in data:
                if isinstance(item, list) and len(item) == 2:
                    periods[item[0]] = item[1]
        elif isinstance(data, dict):
            periods = data

        labels = {'day': '24h', 'week': '7d', 'month': '30d', 'allTime': 'All Time'}
        for period_key in ['day', 'week', 'month', 'allTime']:
            period_data = periods.get(period_key)
            if not period_data:
                continue
            label = labels.get(period_key, period_key)
            vlm = float(period_data.get('vlm', 0))

            # Extract PnL from pnlHistory
            pnl_history = period_data.get('pnlHistory', [])
            pnl = float(pnl_history[-1][1]) if pnl_history else 0

            # Extract account value from history
            acct_history = period_data.get('accountValueHistory', [])
            acct_val = float(acct_history[-1][1]) if acct_history else 0
            start_val = float(acct_history[0][1]) if acct_history else 0

            pnl_color = Colors.GREEN if pnl >= 0 else Colors.RED
            print(f"\n  {Colors.BOLD}{label}:{Colors.END}")
            print(f"    Account:  ${acct_val:>,.2f}")
            print(f"    PnL:      {pnl_color}${pnl:>+,.4f}{Colors.END}")
            if start_val > 0:
                pct = (pnl / start_val) * 100
                print(f"    Return:   {pnl_color}{pct:>+.4f}%{Colors.END}")
            print(f"    Volume:   ${vlm:>,.2f}")

        print()

        return 0
    except Exception as e:
        print(f"{Colors.RED}Error fetching portfolio: {e}{Colors.END}")
        return 1


def _cmd_scan_sorted(assets, hip3_data, sort_key, reverse, top_n, min_volume):
    """Render a single flat sorted table for scan --sort mode."""
    # Merge native + HIP-3 into one list
    merged = list(assets)
    for h in hip3_data:
        if h.get('volume', 0) >= min_volume:
            merged.append(h)

    # Sort key mapping with default directions
    sort_cfg = {
        'funding':      (lambda x: x['funding_apr'], False),   # ascending (most negative first)
        'volume':       (lambda x: x['volume'], True),          # descending
        'oi':           (lambda x: x.get('oi_ntl', 0), True),    # descending (notional)
        'price-change': (lambda x: x['pct_change'], True),     # descending
    }
    key_fn, default_desc = sort_cfg[sort_key]
    descending = not default_desc if reverse else default_desc

    merged.sort(key=key_fn, reverse=descending)
    rows = merged[:top_n]

    label = sort_key.upper().replace('-', ' ')
    direction = "descending" if descending else "ascending"
    print(f"\n{Colors.BOLD}Sorted by {label} ({direction}) — top {top_n}:{Colors.END}")
    print(f"{'Asset':<14} {'Price':>12} {'Funding APR':>12} {'OI':>14} {'Volume':>14} {'24h Chg':>9}")
    print("-" * 79)

    for a in rows:
        funding_color = Colors.GREEN if a['funding_apr'] < -10 else Colors.RED if a['funding_apr'] > 10 else Colors.YELLOW
        chg_color = Colors.GREEN if a['pct_change'] > 0 else Colors.RED if a['pct_change'] < 0 else Colors.END
        print(f"{a['name']:<14} ${a['price']:>10,.2f} {funding_color}{a['funding_apr']:>11.1f}%{Colors.END} ${a.get('oi_ntl', 0):>12,.0f} ${a.get('volume', 0):>12,.0f} {chg_color}{a['pct_change']:>+8.2f}%{Colors.END}")

    return 0


def cmd_scan(args):
    """Scan all assets for trading opportunities based on funding rates."""
    info, config = setup_info()

    min_volume = args.min_volume if hasattr(args, 'min_volume') and args.min_volume else 100000
    top_n = args.top if hasattr(args, 'top') and args.top else 20

    print(f"\n{Colors.BOLD}{Colors.CYAN}MARKET SCANNER - ALL HYPERLIQUID PERPS{Colors.END}")
    print(f"Timestamp: {datetime.now().isoformat()}")
    print(f"Filter: Min 24h volume > ${min_volume:,}")
    print("=" * 90)

    try:
        meta = info.meta_and_asset_ctxs()
        universe = meta[0]['universe']
        contexts = meta[1]

        assets = []
        for i, asset in enumerate(universe):
            ctx = contexts[i]
            name = asset['name']
            funding = float(ctx.get('funding', 0))
            mark_px = float(ctx.get('markPx', 0))
            oi = float(ctx.get('openInterest', 0))
            volume = float(ctx.get('dayNtlVlm', 0))
            prev_px = float(ctx.get('prevDayPx', 0))
            pct_change = ((mark_px - prev_px) / prev_px * 100) if prev_px else 0.0

            if volume >= min_volume:
                assets.append({
                    'name': name,
                    'price': mark_px,
                    'funding_hr': funding * 100,
                    'funding_apr': funding * 24 * 365 * 100,
                    'oi': oi,
                    'oi_ntl': oi * mark_px,
                    'volume': volume,
                    'pct_change': pct_change,
                })

        print(f"\nTotal perps: {len(universe)} | With sufficient volume: {len(assets)}")

        # HIP-3 Perps (all dexes) — bulk fetch via metaAndAssetCtxs
        import requests as req

        hip3_data = []
        try:
            all_dexes = info.perp_dexs()
            dex_names = [d.get('name') for d in all_dexes if d is not None and d.get('name')]
        except Exception:
            dex_names = ['xyz']

        for dex in dex_names:
            try:
                resp = req.post(
                    config['api_url'] + "/info",
                    json={"type": "metaAndAssetCtxs", "dex": dex},
                    timeout=10
                )
                if resp.status_code != 200:
                    continue
                dex_meta = resp.json()
                dex_universe = dex_meta[0]['universe']
                dex_ctxs = dex_meta[1]

                for i, asset in enumerate(dex_universe):
                    coin = asset.get('name', '')
                    if not coin:
                        continue
                    ctx = dex_ctxs[i]
                    funding = float(ctx.get('funding', 0))
                    price = float(ctx.get('markPx', 0))
                    h3_oi = float(ctx.get('openInterest', 0))
                    h3_volume = float(ctx.get('dayNtlVlm', 0))
                    h3_prev_px = float(ctx.get('prevDayPx', 0))
                    h3_pct_change = ((price - h3_prev_px) / h3_prev_px * 100) if h3_prev_px else 0.0
                    funding_hr = funding * 100
                    funding_apr = funding * 24 * 365 * 100

                    hip3_data.append({
                        'name': coin,
                        'price': price,
                        'funding_hr': funding_hr,
                        'funding_apr': funding_apr,
                        'oi': h3_oi,
                        'oi_ntl': h3_oi * price,
                        'volume': h3_volume,
                        'pct_change': h3_pct_change,
                    })
            except Exception:
                pass

        # --sort mode: flat sorted table
        sort_key = getattr(args, 'sort', None)
        if sort_key:
            reverse = getattr(args, 'reverse', False)
            return _cmd_scan_sorted(assets, hip3_data, sort_key, reverse, top_n, min_volume)

        # Default multi-section output
        # Sort by funding rate (most negative first)
        assets_by_funding = sorted(assets, key=lambda x: x['funding_apr'])

        print(f"\n{Colors.BOLD}{Colors.GREEN}TOP {top_n} NEGATIVE FUNDING (shorts paying longs - LONG opportunities):{Colors.END}")
        print(f"{'Asset':<12} {'Price':>12} {'Funding/hr':>12} {'APR':>10} {'24h Chg':>9} {'Open Interest':>15} {'24h Volume':>15}")
        print("-" * 89)

        for a in assets_by_funding[:top_n]:
            funding_color = Colors.GREEN if a['funding_apr'] < -50 else Colors.YELLOW if a['funding_apr'] < 0 else Colors.END
            chg_color = Colors.GREEN if a['pct_change'] > 0 else Colors.RED if a['pct_change'] < 0 else Colors.END
            print(f"{a['name']:<12} ${a['price']:>10,.2f} {funding_color}{a['funding_hr']:>11.4f}%{Colors.END} {a['funding_apr']:>9.1f}% {chg_color}{a['pct_change']:>+8.2f}%{Colors.END} ${a['oi']:>13,.0f} ${a['volume']:>13,.0f}")

        print(f"\n{Colors.BOLD}{Colors.RED}TOP {top_n} POSITIVE FUNDING (longs paying shorts - SHORT opportunities or avoid):{Colors.END}")
        print(f"{'Asset':<12} {'Price':>12} {'Funding/hr':>12} {'APR':>10} {'24h Chg':>9} {'Open Interest':>15} {'24h Volume':>15}")
        print("-" * 89)

        for a in assets_by_funding[-top_n:][::-1]:
            funding_color = Colors.RED if a['funding_apr'] > 50 else Colors.YELLOW if a['funding_apr'] > 0 else Colors.END
            chg_color = Colors.GREEN if a['pct_change'] > 0 else Colors.RED if a['pct_change'] < 0 else Colors.END
            print(f"{a['name']:<12} ${a['price']:>10,.2f} {funding_color}{a['funding_hr']:>11.4f}%{Colors.END} {a['funding_apr']:>9.1f}% {chg_color}{a['pct_change']:>+8.2f}%{Colors.END} ${a['oi']:>13,.0f} ${a['volume']:>13,.0f}")

        # High volume movers
        assets_by_volume = sorted(assets, key=lambda x: x['volume'], reverse=True)[:10]
        print(f"\n{Colors.BOLD}{Colors.BLUE}TOP 10 BY VOLUME (most liquid):{Colors.END}")
        print(f"{'Asset':<12} {'Price':>12} {'Funding APR':>12} {'24h Chg':>9} {'24h Volume':>15}")
        print("-" * 64)
        for a in assets_by_volume:
            funding_color = Colors.GREEN if a['funding_apr'] < -10 else Colors.RED if a['funding_apr'] > 10 else Colors.YELLOW
            chg_color = Colors.GREEN if a['pct_change'] > 0 else Colors.RED if a['pct_change'] < 0 else Colors.END
            print(f"{a['name']:<12} ${a['price']:>10,.2f} {funding_color}{a['funding_apr']:>11.1f}%{Colors.END} {chg_color}{a['pct_change']:>+8.2f}%{Colors.END} ${a['volume']:>13,.0f}")

        # HIP-3 section display
        print(f"\n{Colors.BOLD}{Colors.MAGENTA}HIP-3 PERPS:{Colors.END}")
        print(f"{'Asset':<14} {'Price':>12} {'Funding/hr':>12} {'APR':>10} {'24h Chg':>9}")
        print("-" * 59)

        for h in hip3_data:
            funding_color = Colors.GREEN if h['funding_apr'] < -10 else Colors.RED if h['funding_apr'] > 10 else Colors.YELLOW
            chg_color = Colors.GREEN if h['pct_change'] > 0 else Colors.RED if h['pct_change'] < 0 else Colors.END
            print(f"{h['name']:<14} ${h['price']:>10,.2f} {funding_color}{h['funding_hr']:>11.4f}%{Colors.END} {h['funding_apr']:>9.1f}% {chg_color}{h['pct_change']:>+8.2f}%{Colors.END}")

        print(f"\n{Colors.BOLD}Summary:{Colors.END}")
        negative_funding = [a for a in assets if a['funding_apr'] < -20]
        print(f"  Native perps with funding < -20% APR: {len(negative_funding)}")
        if negative_funding:
            best = min(negative_funding, key=lambda x: x['funding_apr'])
            print(f"  Best native opportunity: {best['name']} at {best['funding_apr']:.1f}% APR (${best['volume']:,.0f} vol)")

        if hip3_data:
            best_hip3 = min(hip3_data, key=lambda x: x['funding_apr'])
            print(f"  Best HIP-3 opportunity: {best_hip3['name']} at {best_hip3['funding_apr']:.1f}% APR")

        return 0
    except Exception as e:
        print(f"{Colors.RED}Error scanning: {e}{Colors.END}")
        import traceback
        traceback.print_exc()
        return 1


def cmd_hip3(args):
    """Get detailed data for HIP-3 perps (trade.xyz assets - equities, commodities, forex)."""
    info, config = setup_info()
    import requests as req

    # If no specific asset, fetch all available from API
    if not args.coin:
        try:
            # Fetch all HIP-3 assets dynamically from xyz dex
            meta = info.meta(dex='xyz')
            universe = meta.get('universe', [])
            assets = [a.get('name', '') for a in universe]
            # Filter out empty and sort
            assets = sorted([a for a in assets if a])
        except Exception as e:
            print(f"{Colors.YELLOW}Warning: Could not fetch HIP-3 assets dynamically, using fallback list{Colors.END}")
            assets = [
                'xyz:TSLA', 'xyz:NVDA', 'xyz:AAPL', 'xyz:GOOGL', 'xyz:AMZN',
                'xyz:META', 'xyz:MSFT', 'xyz:HOOD', 'xyz:PLTR', 'xyz:MSTR',
                'xyz:AMD', 'xyz:NFLX', 'xyz:COIN', 'xyz:XYZ100',
                'xyz:GOLD', 'xyz:SILVER', 'xyz:COPPER', 'xyz:NATGAS',
            ]
    else:
        coin = args.coin if args.coin.startswith('xyz:') else f'xyz:{args.coin}'
        assets = [coin]

    print(f"\n{Colors.BOLD}{Colors.MAGENTA}HIP-3 EQUITY PERPS DATA{Colors.END}")
    print("=" * 80)

    had_error = False
    for coin in assets:
        try:
            print(f"\n{Colors.BOLD}{coin}{Colors.END}")

            # Get L2 Book (price + liquidity)
            book_resp = req.post(
                config['api_url'] + "/info",
                json={"type": "l2Book", "coin": coin},
                timeout=10
            )

            if book_resp.status_code == 200:
                book = book_resp.json()
                levels = book.get('levels', [])

                if len(levels) >= 2 and levels[0] and levels[1]:
                    best_bid = float(levels[0][0]['px'])
                    best_ask = float(levels[1][0]['px'])
                    mid = (best_bid + best_ask) / 2
                    spread = best_ask - best_bid
                    spread_bps = (spread / mid) * 10000

                    # Calculate depth
                    bid_depth = sum(float(b['sz']) * float(b['px']) for b in levels[0][:5])
                    ask_depth = sum(float(a['sz']) * float(a['px']) for a in levels[1][:5])

                    print(f"  Price:       ${mid:,.2f}")
                    print(f"  Bid:         ${best_bid:,.2f}")
                    print(f"  Ask:         ${best_ask:,.2f}")
                    print(f"  Spread:      {spread_bps:.1f} bps (${spread:.2f})")
                    print(f"  Bid Depth:   ${bid_depth:,.0f} (top 5 levels)")
                    print(f"  Ask Depth:   ${ask_depth:,.0f} (top 5 levels)")

            # Get Funding Rate
            funding_resp = req.post(
                config['api_url'] + "/info",
                json={"type": "fundingHistory", "coin": coin, "startTime": 0},
                timeout=10
            )

            if funding_resp.status_code == 200:
                data = funding_resp.json()
                if data:
                    latest = data[-1]
                    funding = float(latest.get('fundingRate', 0))
                    funding_hr = funding * 100
                    funding_apr = funding * 24 * 365 * 100

                    funding_color = Colors.GREEN if funding < 0 else Colors.RED if funding > 0.0001 else Colors.YELLOW
                    signal = "shorts paying longs" if funding < 0 else "longs paying shorts" if funding > 0 else "neutral"

                    print(f"  Funding:     {funding_color}{funding_hr:.4f}%/hr ({funding_apr:.1f}% APR){Colors.END}")
                    print(f"  Signal:      {signal}")

            # Get Meta info (if available)
            meta_resp = req.post(
                config['api_url'] + "/info",
                json={"type": "perpsAtTime", "req": {"user": config['account_address'], "time": 0}},
                timeout=10
            )

        except Exception as e:
            print(f"  {Colors.RED}Error: {e}{Colors.END}")
            had_error = True

    return 1 if had_error else 0

def _grok_call(prompt: str, tools: list[str] | None = None, timeout: int = 60,
               max_chars: int = 0) -> tuple[bool, str]:
    """Shared Grok API helper. Sends a single call with specified tools.

    Args:
        prompt: The query to send to Grok.
        tools: List of tool types (e.g., ["web_search", "x_search"]).
               If None, uses both web_search and x_search.
        timeout: Request timeout in seconds.
        max_chars: If > 0, truncate output text to this many characters.

    Returns:
        (success: bool, text: str)
    """
    import requests as req

    grok_api_key = os.getenv('XAI_API_KEY')
    if not grok_api_key:
        return False, "XAI_API_KEY not set in .env"

    if tools is None:
        tools = ["web_search", "x_search"]

    tool_specs = [{"type": t} for t in tools]

    try:
        response = req.post(
            "https://api.x.ai/v1/responses",
            headers={
                "Authorization": f"Bearer {grok_api_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": "grok-4-1-fast",
                "tools": tool_specs,
                "input": [{"role": "user", "content": prompt}]
            },
            timeout=timeout
        )
        if response.status_code == 200:
            data = response.json()
            texts = []
            for item in data.get('output', []):
                if item.get('type') == 'message':
                    for content in item.get('content', []):
                        if content.get('type') in ('text', 'output_text'):
                            texts.append(content.get('text', ''))
            result = "\n".join(texts)
            if max_chars > 0 and len(result) > max_chars:
                result = result[:max_chars]
            return True, result
        else:
            return False, f"HTTP {response.status_code}"
    except Exception as e:
        return False, str(e)


def cmd_ask(args):
    """Ask Grok anything — it picks the right tools (web, X) automatically."""
    query = args.query
    web_only = args.web
    x_only = args.x

    grok_api_key = os.getenv('XAI_API_KEY')
    if not grok_api_key:
        print(f"{Colors.RED}Error: XAI_API_KEY not set in .env{Colors.END}")
        print("Add your Grok API key: XAI_API_KEY=...")
        return 1

    print(f"\n{Colors.BOLD}{Colors.CYAN}ASK GROK:{Colors.END} {query}")
    print("=" * 60)

    # Determine tools
    if web_only:
        tools = ["web_search"]
    elif x_only:
        tools = ["x_search"]
    else:
        tools = ["web_search", "x_search"]

    ok, text = _grok_call(query, tools=tools)
    if ok:
        print(f"{Colors.DIM}{text}{Colors.END}")
        return 0
    else:
        print(f"{Colors.RED}Error: {text}{Colors.END}")
        return 1


def cmd_sentiment(args):
    """Get sentiment analysis for an asset using Grok API."""
    coin = args.coin

    grok_api_key = os.getenv('XAI_API_KEY')
    if not grok_api_key:
        print(f"{Colors.RED}Error: XAI_API_KEY not set in .env{Colors.END}")
        print("Add your Grok API key to use sentiment analysis")
        return 1

    print(f"\n{Colors.BOLD}{Colors.CYAN}SENTIMENT ANALYSIS: {coin}{Colors.END}")
    print("=" * 60)

    had_error = False

    # Web search for news & analysis
    print(f"\n{Colors.BOLD}Web Search (News & Analysis):{Colors.END}")
    web_query = f"What is the current market sentiment and recent news for {coin} cryptocurrency? Focus on price action, major developments, and whether traders are bullish or bearish. Be concise."
    ok, text = _grok_call(web_query, tools=["web_search"], max_chars=800)
    if ok:
        print(f"{Colors.DIM}{text}{Colors.END}")
    else:
        print(f"{Colors.RED}Web search error: {text}{Colors.END}")
        had_error = True

    # X/Twitter sentiment
    print(f"\n{Colors.BOLD}X/Twitter Sentiment:{Colors.END}")
    x_query = f"What is the sentiment on X/Twitter about ${coin} in the last 24-48 hours? Are traders bullish or bearish? What are the key opinions? Be concise."
    ok, text = _grok_call(x_query, tools=["x_search"], max_chars=800)
    if ok:
        print(f"{Colors.DIM}{text}{Colors.END}")
    else:
        print(f"{Colors.RED}X search error: {text}{Colors.END}")
        had_error = True

    return 1 if had_error else 0


def cmd_search(args):
    """General-purpose search using Grok's web and X/Twitter search."""
    query = args.query
    web_only = args.web
    x_only = args.x

    grok_api_key = os.getenv('XAI_API_KEY')
    if not grok_api_key:
        print(f"{Colors.RED}Error: XAI_API_KEY not set in .env{Colors.END}")
        print("Add your Grok API key to use search")
        return 1

    print(f"\n{Colors.BOLD}{Colors.CYAN}SEARCH: \"{query}\"{Colors.END}")
    print("=" * 60)

    had_error = False

    if not x_only:
        print(f"\n{Colors.BOLD}Web:{Colors.END}")
        ok, text = _grok_call(query, tools=["web_search"])
        if ok:
            print(f"{Colors.DIM}{text}{Colors.END}")
        else:
            print(f"{Colors.RED}Error: {text}{Colors.END}")
            had_error = True

    if not web_only:
        print(f"\n{Colors.BOLD}X/Twitter:{Colors.END}")
        ok, text = _grok_call(query, tools=["x_search"])
        if ok:
            print(f"{Colors.DIM}{text}{Colors.END}")
        else:
            print(f"{Colors.RED}Error: {text}{Colors.END}")
            had_error = True

    return 1 if had_error else 0


def cmd_unlocks(args):
    """Check token unlock schedules using Grok search."""
    import requests as req

    grok_api_key = os.getenv('XAI_API_KEY')
    if not grok_api_key:
        print(f"{Colors.RED}Error: XAI_API_KEY not set in .env{Colors.END}")
        return 1

    # If no coin specified, check current positions
    if not args.coins:
        info, config = setup_info(require_credentials=True)
        try:
            user_state = info.user_state(config['account_address'])
            positions = user_state.get('assetPositions', [])
            coins = []
            for pos in positions:
                position = pos.get('position', {})
                if float(position.get('szi', 0)) != 0:
                    coin = position.get('coin', '')
                    # Skip HIP-3 perps (equities don't have token unlocks)
                    if ':' not in coin:
                        coins.append(coin)
            if not coins:
                print("No native token positions found.")
                return 0
        except Exception as e:
            print(f"{Colors.RED}Error getting positions: {e}{Colors.END}")
            return 1
    else:
        coins = args.coins

    print(f"\n{Colors.BOLD}{Colors.CYAN}TOKEN UNLOCK CHECK{Colors.END}")
    print("=" * 70)

    had_error = False
    for coin in coins:
        print(f"\n{Colors.BOLD}{coin}:{Colors.END}")

        query = f"What are the upcoming token unlocks or vesting events for {coin} cryptocurrency in the next 30 days? Include dates, amounts, and percentage of supply if available. Be specific and concise. If no unlocks found, say so."
        ok, text = _grok_call(query, tools=["web_search"], max_chars=600)
        if ok:
            print(f"{Colors.DIM}{text}{Colors.END}")
        else:
            print(f"{Colors.RED}Search error: {text}{Colors.END}")
            had_error = True
            had_error = True

    print()
    return 1 if had_error else 0


def cmd_devcheck(args):
    """Check for developer sentiment, complaints, and exodus signals."""
    import requests as req

    coin = args.coin

    grok_api_key = os.getenv('XAI_API_KEY')
    if not grok_api_key:
        print(f"{Colors.RED}Error: XAI_API_KEY not set in .env{Colors.END}")
        return 1

    print(f"\n{Colors.BOLD}{Colors.CYAN}DEVELOPER CHECK: {coin}{Colors.END}")
    print("=" * 70)

    had_error = False

    # Search for developer issues/complaints
    print(f"\n{Colors.BOLD}Developer Sentiment & Issues:{Colors.END}")
    dev_query = f"""Search for developer complaints, issues, or concerns about {coin} blockchain/protocol:
1. Are developers leaving or switching to other chains?
2. Any complaints about costs, centralization, or technical issues?
3. Any apps or projects that abandoned {coin} for competitors?
4. What are devs saying in forums, Discord, or X?
Be specific with examples and sources."""

    ok, text = _grok_call(dev_query, tools=["web_search"], max_chars=1200)
    if ok:
        print(f"{Colors.DIM}{text}{Colors.END}")
    else:
        print(f"{Colors.RED}Search error: {text}{Colors.END}")
        had_error = True

    # X/Twitter dev sentiment
    print(f"\n{Colors.BOLD}X/Twitter Dev Chatter:{Colors.END}")
    x_query = f"What are developers saying about {coin} on X/Twitter? Look for: complaints, frustrations, projects leaving, technical issues, cost concerns. Not price speculation - developer experience only."
    ok, text = _grok_call(x_query, tools=["x_search"], max_chars=800)
    if ok:
        print(f"{Colors.DIM}{text}{Colors.END}")
    else:
        print(f"{Colors.RED}X search error: {text}{Colors.END}")
        had_error = True

    print()
    return 1 if had_error else 0


def cmd_polymarket(args):
    """Get Polymarket prediction market data for trading signals."""
    import httpx
    import json

    category = args.category.lower() if args.category else 'crypto'

    # Map categories to API tags and client-side filters
    TAG_MAP = {
        'crypto': 'crypto',
        'btc': 'crypto',
        'eth': 'crypto',
        'trending': None,  # No tag — just top by volume
        'macro': 'politics',
    }

    TITLE_FILTER = {
        'btc': lambda t: 'bitcoin' in t.lower() or 'btc' in t.lower(),
        'eth': lambda t: 'ethereum' in t.lower() or 'eth' in t.lower(),
    }

    tag = TAG_MAP.get(category, 'crypto')
    title_filter = TITLE_FILTER.get(category)

    print(f"\n{Colors.BOLD}{Colors.CYAN}POLYMARKET PREDICTIONS: {category.upper()}{Colors.END}")
    print("=" * 70)

    try:
        url = 'https://gamma-api.polymarket.com/events?limit=20&active=true&closed=false'
        if tag:
            url += f'&tag={tag}'

        r = httpx.get(url, timeout=15)
        if r.status_code != 200:
            print(f"{Colors.RED}API error: {r.status_code}{Colors.END}")
            return 1

        events = r.json()
        if not events:
            print(f"{Colors.DIM}No active events found for '{category}'.{Colors.END}")
            return 0

        # Client-side title filter for btc/eth
        if title_filter:
            events = [e for e in events if title_filter(e.get('title', ''))]

        # Sort by volume descending
        events.sort(key=lambda x: float(x.get('volume', 0) or 0), reverse=True)

        if not events:
            print(f"{Colors.DIM}No matching events found for '{category}'.{Colors.END}")
            return 0

        for event in events[:10]:
            title = event.get('title', 'Unknown')
            volume = float(event.get('volume', 0) or 0)

            print(f"\n{Colors.BOLD}{title}{Colors.END}")
            print(f"  Volume: ${volume:,.0f}")

            markets = event.get('markets', [])
            markets.sort(key=lambda x: float(x.get('volume', 0) or 0), reverse=True)

            for m in markets[:8]:
                question = m.get('question', '')
                prices = m.get('outcomePrices', '[]')
                try:
                    p = json.loads(prices) if isinstance(prices, str) else prices
                    yes_prob = float(p[0]) * 100 if p and len(p) > 0 else 0
                except:
                    yes_prob = 0
                vol = float(m.get('volume', 0) or 0)

                # Color code by probability
                if yes_prob > 70:
                    prob_color = Colors.GREEN
                elif yes_prob < 30:
                    prob_color = Colors.RED
                else:
                    prob_color = Colors.YELLOW

                print(f"    {question}: {prob_color}{yes_prob:5.1f}%{Colors.END} (${vol:,.0f})")

        print()

        return 0
    except Exception as e:
        print(f"{Colors.RED}Error: {e}{Colors.END}")
        return 1


def cmd_dexes(args):
    """List all HIP-3 dexes and their assets (fetched dynamically from API)."""
    # Get base info client
    base_info, config = setup_info(require_credentials=False, include_hip3=False)

    print(f"\n{Colors.BOLD}{Colors.CYAN}HIP-3 DEXES{Colors.END}")
    print("=" * 80)

    try:
        # Fetch all dexes from API
        all_dexes = base_info.perp_dexs()

        for dex_info in all_dexes:
            if dex_info is None:
                # Native perps (BTC, ETH, SOL, etc.)
                continue

            dex_name = dex_info.get('name', 'unknown')
            full_name = dex_info.get('fullName', dex_name)

            # Get assets from meta
            try:
                meta = base_info.meta(dex=dex_name)
                universe = meta.get('universe', [])
                assets = sorted([a.get('name', '').replace(f'{dex_name}:', '') for a in universe if a.get('name')])
                leverages = [a.get('maxLeverage', 0) for a in universe]
            except:
                # Fallback to assetToStreamingOiCap from dex info
                oi_caps = dex_info.get('assetToStreamingOiCap', [])
                assets = sorted([a[0].split(':')[1] for a in oi_caps if a[0]])
                leverages = []

            print(f"\n{Colors.BOLD}{dex_name.upper()}{Colors.END} ({full_name})")

            if assets:
                print(f"Assets ({len(assets)}): {', '.join(assets)}")
            else:
                print(f"{Colors.DIM}No assets yet{Colors.END}")

            if leverages:
                print(f"Leverage: {min(leverages)}-{max(leverages)}x")

        print()
        return 0
    except Exception as e:
        print(f"{Colors.RED}Error fetching dexes: {e}{Colors.END}")
        return 1


def cmd_history(args):
    """Show trade history from Hyperliquid API."""
    from datetime import datetime

    info, config = setup_info(require_credentials=True)

    print(f"\n{Colors.BOLD}{Colors.CYAN}TRADE HISTORY{Colors.END}")
    print("=" * 80)

    try:
        fills = info.user_fills(config['account_address'])

        if not fills:
            print("No trades found.")
            return 0

        # Limit results
        limit = args.limit if hasattr(args, 'limit') and args.limit else 20
        recent = fills[-limit:]

        print(f"{'Time':<18} {'Side':<6} {'Asset':<14} {'Size':>12} {'Price':>14} {'Value':>12}")
        print("-" * 80)

        for fill in reversed(recent):  # Most recent first
            ts = fill.get('time', 0)
            dt = datetime.fromtimestamp(ts/1000).strftime('%Y-%m-%d %H:%M')
            coin = fill.get('coin', '?')
            side = fill.get('side', '?')
            side_str = f"{Colors.GREEN}BUY{Colors.END}" if side == 'B' else f"{Colors.RED}SELL{Colors.END}"
            sz = float(fill.get('sz', 0))
            px = float(fill.get('px', 0))
            value = sz * px

            print(f"{dt:<18} {side_str:<15} {coin:<14} {sz:>12.4f} ${px:>13.4f} ${value:>11.2f}")

        print(f"\n{Colors.DIM}Showing last {len(recent)} trades. Use --limit N for more.{Colors.END}")

        return 0
    except Exception as e:
        print(f"{Colors.RED}Error: {e}{Colors.END}")
        return 1


# ============================================================================
# MAIN
# ============================================================================

def main():
    parser = argparse.ArgumentParser(
        description='Hyperliquid Trading Toolkit',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )

    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # Status commands
    subparsers.add_parser('status', help='Account status and positions summary')
    check_parser = subparsers.add_parser('check', help='Position health check (book ratio, funding, warnings)')
    check_parser.add_argument('--address', help='Account address (overrides HL_ACCOUNT_ADDRESS)')
    subparsers.add_parser('positions', help='Detailed position information')
    subparsers.add_parser('orders', help='List open orders')

    # Price/data commands
    price_parser = subparsers.add_parser('price', help='Get current prices')
    price_parser.add_argument('coins', nargs='*', help='Assets to get prices for')

    funding_parser = subparsers.add_parser('funding', help='Get funding rates')
    funding_parser.add_argument('coins', nargs='*', help='Assets to get funding for')
    funding_parser.add_argument('--predicted', action='store_true', help='Show predicted rates with cross-exchange comparison')

    book_parser = subparsers.add_parser('book', help='Get order book')
    book_parser.add_argument('coin', help='Asset to get order book for')

    candles_parser = subparsers.add_parser('candles', help='Get OHLCV candlestick data')
    candles_parser.add_argument('coin', help='Asset to get candles for')
    candles_parser.add_argument('--interval', default='1h', help='Candle interval: 1m, 5m, 15m, 1h, 4h, 1d (default: 1h)')
    candles_parser.add_argument('--lookback', default='7d', help='Lookback period: e.g., 24h, 7d, 2w (default: 7d)')

    fh_parser = subparsers.add_parser('funding-history', help='Historical funding rates for a coin')
    fh_parser.add_argument('coin', help='Asset to get funding history for')
    fh_parser.add_argument('--lookback', default='7d', help='Lookback period: e.g., 24h, 7d, 2w (default: 7d)')

    trades_parser = subparsers.add_parser('trades', help='Recent trades for a coin')
    trades_parser.add_argument('coin', help='Asset to get recent trades for')
    trades_parser.add_argument('--limit', type=int, default=20, help='Number of trades to show (default: 20)')

    uf_parser = subparsers.add_parser('user-funding', help='Your funding payments received/paid')
    uf_parser.add_argument('--lookback', default='7d', help='Lookback period: e.g., 24h, 7d, 2w (default: 7d)')

    portfolio_parser = subparsers.add_parser('portfolio', help='Portfolio performance overview')
    portfolio_parser.add_argument('--address', help='Account address (overrides HL_ACCOUNT_ADDRESS)')

    # Trading commands
    leverage_parser = subparsers.add_parser('leverage', help='Set leverage for an asset')
    leverage_parser.add_argument('coin', help='Asset to set leverage for')
    leverage_parser.add_argument('leverage', type=int, help='Leverage multiplier (e.g., 5 for 5x)')
    leverage_parser.add_argument('--isolated', action='store_true', help='Use isolated margin (default: cross)')

    swap_parser = subparsers.add_parser('swap', help='Swap USDC to HIP-3 dex collateral (USDH, USDe, USDT0, USDXL)')
    swap_parser.add_argument('amount', type=float, help='Amount to swap')
    swap_parser.add_argument('--token', default=None, help='Collateral token (default: USDH). Options: USDH, USDe, USDT0, USDXL')
    swap_parser.add_argument('--to-usdc', action='store_true', help='Reverse: sell collateral back to USDC')

    buy_parser = subparsers.add_parser('buy', help='Market buy')
    buy_parser.add_argument('coin', help='Asset to buy')
    buy_parser.add_argument('size', type=float, help='Size to buy')
    buy_parser.add_argument('--leverage', type=int, help='Set leverage before order (e.g., 5 for 5x)')
    buy_parser.add_argument('--isolated', action='store_true', help='Use isolated margin (default: cross)')

    sell_parser = subparsers.add_parser('sell', help='Market sell')
    sell_parser.add_argument('coin', help='Asset to sell')
    sell_parser.add_argument('size', type=float, help='Size to sell')
    sell_parser.add_argument('--leverage', type=int, help='Set leverage before order (e.g., 5 for 5x)')
    sell_parser.add_argument('--isolated', action='store_true', help='Use isolated margin (default: cross)')

    limit_buy_parser = subparsers.add_parser('limit-buy', help='Limit buy order')
    limit_buy_parser.add_argument('coin', help='Asset to buy')
    limit_buy_parser.add_argument('size', type=float, help='Size to buy')
    limit_buy_parser.add_argument('price', type=float, help='Limit price')

    limit_sell_parser = subparsers.add_parser('limit-sell', help='Limit sell order')
    limit_sell_parser.add_argument('coin', help='Asset to sell')
    limit_sell_parser.add_argument('size', type=float, help='Size to sell')
    limit_sell_parser.add_argument('price', type=float, help='Limit price')

    sl_parser = subparsers.add_parser('stop-loss', help='Place stop-loss trigger order')
    sl_parser.add_argument('coin', help='Asset')
    sl_parser.add_argument('size', type=float, help='Size to close')
    sl_parser.add_argument('trigger_price', type=float, help='Trigger price (market order fires when hit)')
    sl_parser.add_argument('--buy', action='store_true', help='Force buy side (for closing shorts)')

    tp_parser = subparsers.add_parser('take-profit', help='Place take-profit trigger order')
    tp_parser.add_argument('coin', help='Asset')
    tp_parser.add_argument('size', type=float, help='Size to close')
    tp_parser.add_argument('trigger_price', type=float, help='Trigger price (market order fires when hit)')
    tp_parser.add_argument('--buy', action='store_true', help='Force buy side (for closing shorts)')

    close_parser = subparsers.add_parser('close', help='Close position')
    close_parser.add_argument('coin', help='Asset to close')

    cancel_parser = subparsers.add_parser('cancel', help='Cancel order')
    cancel_parser.add_argument('oid', help='Order ID to cancel')

    subparsers.add_parser('cancel-all', help='Cancel all open orders')

    modify_parser = subparsers.add_parser('modify-order', help='Modify existing order price/size')
    modify_parser.add_argument('oid', help='Order ID to modify')
    modify_parser.add_argument('price', type=float, help='New price')
    modify_parser.add_argument('--size', type=float, help='New size (default: keep current)')

    # Analysis commands
    analyze_parser = subparsers.add_parser('analyze', help='Comprehensive analysis with raw data')
    analyze_parser.add_argument('coins', nargs='*', help='Assets to analyze (default: BTC ETH SOL DOGE HYPE)')

    raw_parser = subparsers.add_parser('raw', help='Dump raw JSON data for an asset')
    raw_parser.add_argument('coin', help='Asset to dump data for')

    scan_parser = subparsers.add_parser('scan', help='Scan ALL assets for funding opportunities')
    scan_parser.add_argument('--min-volume', type=float, default=100000, help='Minimum 24h volume filter (default: 100000)')
    scan_parser.add_argument('--top', type=int, default=20, help='Number of top results to show (default: 20)')
    scan_parser.add_argument('--sort', choices=['funding', 'volume', 'oi', 'price-change'],
                             help='Sort by single metric (outputs flat table instead of sections)')
    scan_parser.add_argument('--reverse', action='store_true',
                             help='Reverse sort direction')

    sentiment_parser = subparsers.add_parser('sentiment', help='Get Grok sentiment analysis for an asset')
    sentiment_parser.add_argument('coin', help='Asset to analyze sentiment for')

    ask_parser = subparsers.add_parser('ask', help='Ask Grok anything (auto-picks web/X tools)')
    ask_parser.add_argument('query', help='Question for Grok')
    ask_parser.add_argument('--web', action='store_true', help='Web search only')
    ask_parser.add_argument('--x', action='store_true', help='X/Twitter search only')

    search_parser = subparsers.add_parser('search', help='Search web and X/Twitter via Grok')
    search_parser.add_argument('query', help='Search query (any topic)')
    search_parser.add_argument('--web', action='store_true', help='Web search only')
    search_parser.add_argument('--x', action='store_true', help='X/Twitter search only')

    hip3_parser = subparsers.add_parser('hip3', help='Get HIP-3 equity perp data (trade.xyz)')
    hip3_parser.add_argument('coin', nargs='?', help='HIP-3 asset (e.g., META, TSLA) - leave empty for all')

    polymarket_parser = subparsers.add_parser('polymarket', help='Get active Polymarket prediction markets')
    polymarket_parser.add_argument('category', nargs='?', default='crypto',
                                   help='crypto | btc | eth | trending | macro (default: crypto)')

    subparsers.add_parser('dexes', help='List all HIP-3 dexes and their assets')

    history_parser = subparsers.add_parser('history', help='Show trade history from API')
    history_parser.add_argument('--limit', type=int, default=20, help='Number of trades to show (default: 20)')

    unlocks_parser = subparsers.add_parser('unlocks', help='Check token unlock schedules')
    unlocks_parser.add_argument('coins', nargs='*', help='Tokens to check (default: current positions)')

    devcheck_parser = subparsers.add_parser('devcheck', help='Check developer sentiment and exodus signals')
    devcheck_parser.add_argument('coin', help='Protocol to check developer sentiment for')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 0

    # Route to command handlers
    commands = {
        'status': cmd_status,
        'check': cmd_check,
        'positions': cmd_positions,
        'orders': cmd_orders,
        'price': cmd_price,
        'funding': cmd_funding,
        'book': cmd_book,
        'candles': cmd_candles,
        'funding-history': cmd_funding_history,
        'trades': cmd_trades,
        'user-funding': cmd_user_funding,
        'portfolio': cmd_portfolio,
        'leverage': cmd_leverage,
        'swap': cmd_transfer,
        'buy': cmd_buy,
        'sell': cmd_sell,
        'limit-buy': cmd_limit_buy,
        'limit-sell': cmd_limit_sell,
        'stop-loss': cmd_stop_loss,
        'take-profit': cmd_take_profit,
        'close': cmd_close,
        'cancel': cmd_cancel,
        'cancel-all': cmd_cancel_all,
        'modify-order': cmd_modify_order,
        'analyze': cmd_analyze,
        'raw': cmd_raw,
        'scan': cmd_scan,
        'sentiment': cmd_sentiment,
        'search': cmd_search,
        'ask': cmd_ask,
        'hip3': cmd_hip3,
        'polymarket': cmd_polymarket,
        'dexes': cmd_dexes,
        'history': cmd_history,
        'unlocks': cmd_unlocks,
        'devcheck': cmd_devcheck,
    }

    if args.command in commands:
        result = commands[args.command](args)
        if isinstance(result, bool):
            return 0 if result else 1
        if isinstance(result, int):
            return result
        return 0
    else:
        parser.print_help()
        return 1


if __name__ == '__main__':
    sys.exit(main())
