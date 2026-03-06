"""
Polymarket Trading Functions
"""
import os
import sys
from typing import List, Optional, Dict, Union
from eth_account import Account
from py_clob_client.client import ClobClient
from py_clob_client.clob_types import BalanceAllowanceParams, AssetType, OrderArgs
from py_clob_client.order_builder.constants import BUY, SELL
from rich.console import Console

console = Console()

# Environment variable names
PRIVATE_KEY_ENV = "POLYMARKET_PRIVATE_KEY"
FUNDER_ADDRESS_ENV = "POLYMARKET_FUNDER_ADDRESS"

# Data API
DATA_API_BASE_URL = "https://data-api.polymarket.com"
POSITIONS_ENDPOINT = "/positions"
DEFAULT_POSITIONS_LIMIT = 50


def get_private_key() -> Optional[str]:
    """Get private key from environment"""
    key = os.getenv(PRIVATE_KEY_ENV)
    if not key:
        console.print(f"[red]Error: {PRIVATE_KEY_ENV} not set[/red]")
        console.print("Run: export POLYMARKET_PRIVATE_KEY=0x...")
        return None
    if not key.startswith("0x"):
        key = "0x" + key
    return key


def get_funder_address() -> Optional[str]:
    """Get funder address from environment"""
    return os.getenv(FUNDER_ADDRESS_ENV)


def get_wallet_address() -> Optional[str]:
    """Get wallet address from private key"""
    key = get_private_key()
    if not key:
        return None
    try:
        acct = Account.from_key(key)
        return acct.address
    except Exception as e:
        console.print(f"[red]Error deriving address: {e}[/red]")
        return None


def fetch_positions_from_data_api(user: str, limit: int = DEFAULT_POSITIONS_LIMIT) -> List[Dict]:
    """Fetch positions from Polymarket Data API"""
    import requests

    url = f"{DATA_API_BASE_URL}{POSITIONS_ENDPOINT}"
    params = {"user": user, "limit": limit}
    resp = requests.get(url, params=params, timeout=10)
    resp.raise_for_status()
    data = resp.json()
    if not isinstance(data, list):
        raise RuntimeError("Unexpected response from Polymarket data API")
    return data


def get_client() -> Optional[ClobClient]:
    """Get authenticated Polymarket client"""
    key = get_private_key()
    funder = get_funder_address()
    if not key:
        return None
    
    try:
        host = "https://clob.polymarket.com"
        chain_id = 137  # Polygon
        
        console.print(f"[cyan]Initializing ClobClient:[/cyan]")
        console.print(f"  - Host: {host}")
        console.print(f"  - Chain ID: {chain_id}")
        console.print(f"  - Key (first 10 chars): {key[:10]}...")
        console.print(f"  - Funder: {funder}")
        
        # Create client with key and optional funder address
        signature_type = int(os.environ.get("POLYMARKET_SIGNATURE_TYPE", "1"))
        client = ClobClient(
            host,
            key=key,
            chain_id=chain_id,
            funder=funder,
            signature_type=signature_type
        )

        try:
            creds = client.create_or_derive_api_creds()
            client.set_api_creds(creds)
            console.print("[green]  - API credentials: derived successfully[/green]")
        except Exception as e:
            console.print(f"[red]Failed to derive API credentials: {e}[/red]")
            raise
        
        return client
    except Exception as e:
        console.print(f"[red]Error creating client: {e}[/red]")
        return None


def _from_raw_units(raw_value: Union[str, int, float], decimals: int = 6) -> float:
    """Convert raw token units to float value."""
    try:
        val = float(raw_value)
        return val / (10 ** decimals)
    except (ValueError, TypeError):
        return 0.0


def get_balance() -> Optional[float]:
    """Get USDC balance via ClobClient"""
    client = get_client()
    if not client:
        return None

    try:
        params = BalanceAllowanceParams(asset_type=AssetType.COLLATERAL)
        resp = client.get_balance_allowance(params=params)
        raw_balance = resp.get("balance", 0)
        return _from_raw_units(raw_balance)
    except Exception as e:
        console.print(f"[red]Failed to get USDC balance: {e}[/red]")
        raise


def get_markets(limit: int = 10, search: str = None):
    """Get list of markets"""
    client = get_client()
    if not client:
        return None
    
    try:
        markets = client.get_markets(
            limit=limit,
            search=search,
        )
        return markets
    except Exception as e:
        console.print(f"[red]Error fetching markets: {e}[/red]")
        return None


def get_market(token_id: str):
    """Get specific market details"""
    client = get_client()
    if not client:
        return None
    
    try:
        market = client.get_market(token_id)
        return market
    except Exception as e:
        console.print(f"[red]Error fetching market: {e}[/red]")
        return None


def place_order(token_id: str, side: str, price: float, size: float):
    """Place a trade order"""
    client = get_client()
    if not client:
        return None
    
    order_side = BUY if side.upper() == "BUY" else SELL
    
    try:
        resp = client.create_and_post_order(OrderArgs(
            token_id=token_id,
            price=float(price),
            size=float(size),
            side=order_side
        ))
        return resp
    except Exception as e:
        console.print(f"[red]Trade failed: {e}[/red]")
        return None


def get_positions(include_closed: bool = False):
    """Get positions via Polymarket Data API"""
    funder = get_funder_address()
    if not funder:
        raise RuntimeError("POLYMARKET_FUNDER_ADDRESS is not set")

    positions = fetch_positions_from_data_api(funder)
    if not positions:
        raise RuntimeError("Polymarket Data API returned no positions")

    return positions


def get_order_book(token_id: str):
    """Get order book for a market"""
    client = get_client()
    if not client:
        return None
    
    try:
        order_book = client.get_order_book(token_id)
        return order_book
    except Exception as e:
        console.print(f"[red]Error fetching order book: {e}[/red]")
        return None


def get_price(token_id: str, side: str = "BUY") -> Optional[float]:
    """Get current price for a market"""
    client = get_client()
    if not client:
        return None
    
    try:
        price = client.get_price(token_id)
        return price
    except Exception as e:
        console.print(f"[red]Error fetching price: {e}[/red]")
        return None
