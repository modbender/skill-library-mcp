"""
Hyperliquid Patch for Nautilus Trader
=====================================
Bypasses buggy Rust HTTP client using official Hyperliquid Python SDK.
Formats prices to max 5 significant figures per Hyperliquid requirements.

Usage:
    import hyperliquid_patch  # BEFORE any nautilus imports
    from nautilus_trader.adapters.hyperliquid import HYPERLIQUID
"""

import math
import os
from decimal import Decimal
from eth_account import Account
from hyperliquid.exchange import Exchange
from hyperliquid.utils import constants
from hyperliquid.info import Info

DEFAULT_SLIPPAGE = Decimal("0.03")
_EXCHANGE = None
_INFO = None


def get_exchange():
    """Initialize Hyperliquid SDK connection."""
    global _EXCHANGE, _INFO
    if _EXCHANGE is None:
        private_key = os.getenv("HYPERLIQUID_PK")
        vault_address = os.getenv("HYPERLIQUID_VAULT")
        if not private_key:
            raise ValueError("HYPERLIQUID_PK not set")
        if not private_key.startswith("0x"):
            private_key = "0x" + private_key
        account = Account.from_key(private_key)
        _INFO = Info(constants.MAINNET_API_URL, skip_ws=True)
        _EXCHANGE = Exchange(account, constants.MAINNET_API_URL, vault_address=vault_address)
    return _EXCHANGE, _INFO


def get_mid_price(symbol: str) -> Decimal:
    """Get current mid price."""
    _, info = get_exchange()
    mids = info.all_mids()
    if symbol in mids:
        return Decimal(str(mids[symbol]))
    raise ValueError(f"No mid price for {symbol}")


def format_price_5_sigfigs(price: float, is_buy: bool) -> str:
    """
    Format price to max 5 significant figures.

    Hyperliquid requirement: "Prices can have up to 5 significant figures"
    - 139.05 valid (5 sig figs)
    - 139.054 invalid (6 sig figs)

    Rounds up for buys, down for sells to ensure fills.
    """
    if price == 0:
        return "0"
    abs_price = abs(price)
    int_digits = len(str(int(abs_price))) if abs_price >= 1 else 0
    decimal_places = max(0, 5 - int_digits)
    factor = 10 ** decimal_places
    if is_buy:
        rounded = math.ceil(price * factor) / factor
    else:
        rounded = math.floor(price * factor) / factor
    if decimal_places > 0:
        return f"{rounded:.{decimal_places}f}"
    return str(int(rounded))


def apply_hyperliquid_patch():
    """Monkey-patch Nautilus Hyperliquid adapter to use SDK."""
    try:
        from nautilus_trader.adapters.hyperliquid.execution import HyperliquidExecutionClient
        from nautilus_trader.model.enums import OrderType, OrderSide
        from nautilus_trader.model.identifiers import VenueOrderId
        from functools import wraps

        original = HyperliquidExecutionClient._submit_order

        @wraps(original)
        async def patched_submit_order(self, command):
            order = command.order
            if order.is_closed:
                return

            self.generate_order_submitted(
                strategy_id=order.strategy_id,
                instrument_id=order.instrument_id,
                client_order_id=order.client_order_id,
                ts_event=self._clock.timestamp_ns(),
            )

            try:
                exchange, _ = get_exchange()
                symbol = str(order.instrument_id).split("-")[0]
                is_buy = order.side == OrderSide.BUY
                is_market = order.order_type == OrderType.MARKET
                size = float(order.quantity)

                if order.has_price and order.price is not None:
                    limit_price = format_price_5_sigfigs(float(order.price), is_buy)
                elif is_market:
                    mid = get_mid_price(symbol)
                    slippage_price = float(mid) * (1.03 if is_buy else 0.97)
                    limit_price = format_price_5_sigfigs(slippage_price, is_buy)
                else:
                    raise ValueError(f"Unsupported: {order.order_type}")

                order_type = {"limit": {"tif": "Ioc"}} if is_market else {"limit": {"tif": "Gtc"}}

                result = exchange.order(
                    name=symbol,
                    is_buy=is_buy,
                    sz=size,
                    limit_px=float(limit_price),
                    order_type=order_type,
                    reduce_only=order.is_reduce_only,
                )

                if result.get("status") == "ok":
                    statuses = result.get("response", {}).get("data", {}).get("statuses", [])
                    if statuses:
                        s = statuses[0]
                        if "error" in s:
                            raise ValueError(s["error"])
                        venue_id = str(s.get("resting", s.get("filled", {})).get("oid", order.client_order_id))
                    else:
                        venue_id = str(order.client_order_id)

                    self.generate_order_accepted(
                        strategy_id=order.strategy_id,
                        instrument_id=order.instrument_id,
                        client_order_id=order.client_order_id,
                        venue_order_id=VenueOrderId(venue_id),
                        ts_event=self._clock.timestamp_ns(),
                    )
                else:
                    raise ValueError(str(result))

            except Exception as e:
                self.generate_order_rejected(
                    strategy_id=order.strategy_id,
                    instrument_id=order.instrument_id,
                    client_order_id=order.client_order_id,
                    reason=str(e),
                    ts_event=self._clock.timestamp_ns(),
                )

        HyperliquidExecutionClient._submit_order = patched_submit_order
        print("[PATCH] Hyperliquid SDK patch applied (5 sig fig prices)")
        return True

    except Exception as e:
        print(f"[PATCH] Failed: {e}")
        return False


apply_hyperliquid_patch()
