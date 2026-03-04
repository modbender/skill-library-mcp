# Nautilus Trader + Hyperliquid Complete Guide

This reference covers end-to-end setup for backtesting strategies with Nautilus Trader and deploying them live on Hyperliquid mainnet.

## Table of Contents

1. [Installation](#installation)
2. [Environment Setup](#environment-setup)
3. [Backtesting with MTF EMA + Heiken Ashi](#backtesting-with-mtf-ema--heiken-ashi)
4. [Hyperliquid Live Trading Patch](#hyperliquid-live-trading-patch)
5. [Price Precision Rules](#price-precision-rules)
6. [Complete Strategy Example](#complete-strategy-example)

---

## Installation

### Core Dependencies

```bash
# Nautilus Trader (backtesting + live trading framework)
pip install nautilus_trader

# Hyperliquid SDK (for live trading patch)
pip install hyperliquid-python-sdk eth-account python-dotenv

# Data handling
pip install pandas numpy
```

### Verify Installation

```python
import nautilus_trader
print(f"Nautilus Trader: {nautilus_trader.__version__}")
# Tested with v1.222.0
```

---

## Environment Setup

### Create `.env` File

```bash
# Hyperliquid credentials for live trading
HYPERLIQUID_PK=your_private_key_without_0x_prefix
HYPERLIQUID_VAULT=0xYourVaultAddressHere
```

### Load Environment

```python
from dotenv import load_dotenv
load_dotenv()
```

---

## Backtesting with MTF EMA + Heiken Ashi

### Heiken Ashi Indicator

```python
from nautilus_trader.indicators.base.indicator import Indicator
from nautilus_trader.model.data import Bar
import numpy as np

class HeikenAshi(Indicator):
    """Heiken Ashi candle smoothing indicator."""

    def __init__(self):
        super().__init__([])
        self.ha_open = 0.0
        self.ha_close = 0.0
        self.ha_high = 0.0
        self.ha_low = 0.0
        self._prev_ha_open = None
        self._prev_ha_close = None
        self.initialized = False

    def handle_bar(self, bar: Bar) -> None:
        o = float(bar.open)
        h = float(bar.high)
        l = float(bar.low)
        c = float(bar.close)

        # HA Close = (O + H + L + C) / 4
        self.ha_close = (o + h + l + c) / 4

        # HA Open = (prev_HA_Open + prev_HA_Close) / 2
        if self._prev_ha_open is None:
            self.ha_open = (o + c) / 2
        else:
            self.ha_open = (self._prev_ha_open + self._prev_ha_close) / 2

        # HA High/Low
        self.ha_high = max(h, self.ha_open, self.ha_close)
        self.ha_low = min(l, self.ha_open, self.ha_close)

        self._prev_ha_open = self.ha_open
        self._prev_ha_close = self.ha_close
        self.initialized = True

    @property
    def is_bullish(self) -> bool:
        return self.ha_close > self.ha_open

    @property
    def is_bearish(self) -> bool:
        return self.ha_close < self.ha_open

    def reset(self) -> None:
        self._prev_ha_open = None
        self._prev_ha_close = None
        self.initialized = False
```

### Multi-Timeframe EMA Strategy

```python
from nautilus_trader.trading.strategy import Strategy
from nautilus_trader.config import StrategyConfig
from nautilus_trader.indicators.average.ema import ExponentialMovingAverage
from nautilus_trader.model.data import Bar, BarType
from nautilus_trader.model.enums import OrderSide, TimeInForce
from nautilus_trader.model.identifiers import InstrumentId
from nautilus_trader.model.instruments import Instrument
from nautilus_trader.model.orders import MarketOrder
from decimal import Decimal

class MTFEmaHeikenAshiConfig(StrategyConfig):
    instrument_id: str
    htf_bar_type: str  # Higher timeframe (e.g., 1H)
    ltf_bar_type: str  # Lower timeframe (e.g., 5m)
    ema_fast: int = 9
    ema_slow: int = 21
    trade_size: Decimal = Decimal("0.1")

class MTFEmaHeikenAshiStrategy(Strategy):
    """
    Multi-Timeframe EMA Crossover with Heiken Ashi confirmation.

    Entry Logic:
    - HTF: EMA9 > EMA21 (bullish trend) or EMA9 < EMA21 (bearish trend)
    - LTF: Wait for Heiken Ashi color change in trend direction
    - Enter on HA confirmation

    Exit Logic:
    - HA color reversal on LTF
    """

    def __init__(self, config: MTFEmaHeikenAshiConfig):
        super().__init__(config)
        self.instrument_id = InstrumentId.from_str(config.instrument_id)
        self.htf_bar_type = BarType.from_str(config.htf_bar_type)
        self.ltf_bar_type = BarType.from_str(config.ltf_bar_type)
        self.trade_size = config.trade_size

        # HTF indicators
        self.ema_fast = ExponentialMovingAverage(config.ema_fast)
        self.ema_slow = ExponentialMovingAverage(config.ema_slow)

        # LTF indicator
        self.heiken_ashi = HeikenAshi()

        # State
        self.htf_trend = 0  # 1=bullish, -1=bearish, 0=neutral
        self.prev_ha_bullish = None
        self.position_side = None

    def on_start(self):
        self.instrument = self.cache.instrument(self.instrument_id)
        self.subscribe_bars(self.htf_bar_type)
        self.subscribe_bars(self.ltf_bar_type)

    def on_bar(self, bar: Bar):
        if bar.bar_type == self.htf_bar_type:
            self._handle_htf_bar(bar)
        elif bar.bar_type == self.ltf_bar_type:
            self._handle_ltf_bar(bar)

    def _handle_htf_bar(self, bar: Bar):
        """Update HTF EMAs and determine trend."""
        self.ema_fast.handle_bar(bar)
        self.ema_slow.handle_bar(bar)

        if not self.ema_slow.initialized:
            return

        if self.ema_fast.value > self.ema_slow.value:
            self.htf_trend = 1  # Bullish
        elif self.ema_fast.value < self.ema_slow.value:
            self.htf_trend = -1  # Bearish
        else:
            self.htf_trend = 0

    def _handle_ltf_bar(self, bar: Bar):
        """Check for HA confirmation and manage entries/exits."""
        self.heiken_ashi.handle_bar(bar)

        if not self.heiken_ashi.initialized:
            return

        ha_bullish = self.heiken_ashi.is_bullish
        ha_changed = self.prev_ha_bullish is not None and ha_bullish != self.prev_ha_bullish
        self.prev_ha_bullish = ha_bullish

        if not ha_changed:
            return

        # Entry signals
        if self.position_side is None:
            if self.htf_trend == 1 and ha_bullish:
                self._enter_long()
            elif self.htf_trend == -1 and not ha_bullish:
                self._enter_short()

        # Exit signals (HA reversal)
        elif self.position_side == OrderSide.BUY and not ha_bullish:
            self._exit_position()
        elif self.position_side == OrderSide.SELL and ha_bullish:
            self._exit_position()

    def _enter_long(self):
        order = self.order_factory.market(
            instrument_id=self.instrument_id,
            order_side=OrderSide.BUY,
            quantity=self.instrument.make_qty(self.trade_size),
            time_in_force=TimeInForce.IOC,
        )
        self.submit_order(order)
        self.position_side = OrderSide.BUY

    def _enter_short(self):
        order = self.order_factory.market(
            instrument_id=self.instrument_id,
            order_side=OrderSide.SELL,
            quantity=self.instrument.make_qty(self.trade_size),
            time_in_force=TimeInForce.IOC,
        )
        self.submit_order(order)
        self.position_side = OrderSide.SELL

    def _exit_position(self):
        exit_side = OrderSide.SELL if self.position_side == OrderSide.BUY else OrderSide.BUY
        order = self.order_factory.market(
            instrument_id=self.instrument_id,
            order_side=exit_side,
            quantity=self.instrument.make_qty(self.trade_size),
            time_in_force=TimeInForce.IOC,
            reduce_only=True,
        )
        self.submit_order(order)
        self.position_side = None

    def on_stop(self):
        self.close_all_positions(self.instrument_id)
```

### Backtest Engine Setup

```python
from nautilus_trader.backtest.engine import BacktestEngine, BacktestEngineConfig
from nautilus_trader.model.currencies import USD
from nautilus_trader.model.enums import AccountType, OmsType
from nautilus_trader.model.identifiers import Venue
from nautilus_trader.model.objects import Money
from nautilus_trader.persistence.catalog import ParquetDataCatalog
from decimal import Decimal

def run_backtest():
    # Engine config
    config = BacktestEngineConfig(
        trader_id="BACKTESTER-001",
        logging_level="INFO",
    )
    engine = BacktestEngine(config=config)

    # Add venue
    engine.add_venue(
        venue=Venue("HYPERLIQUID"),
        oms_type=OmsType.NETTING,
        account_type=AccountType.MARGIN,
        base_currency=USD,
        starting_balances=[Money(100_000, USD)],
    )

    # Load data from catalog
    catalog = ParquetDataCatalog("./data_catalog")

    # Add instruments and bars
    instruments = catalog.instruments()
    for instrument in instruments:
        engine.add_instrument(instrument)

    bars = catalog.bars()  # Load your bar data
    engine.add_data(bars)

    # Configure strategy
    strategy_config = MTFEmaHeikenAshiConfig(
        instrument_id="SOL-USD.HYPERLIQUID",
        htf_bar_type="SOL-USD.HYPERLIQUID-1-HOUR-LAST-EXTERNAL",
        ltf_bar_type="SOL-USD.HYPERLIQUID-5-MINUTE-LAST-EXTERNAL",
        ema_fast=9,
        ema_slow=21,
        trade_size=Decimal("1.0"),
    )
    strategy = MTFEmaHeikenAshiStrategy(config=strategy_config)
    engine.add_strategy(strategy)

    # Run backtest
    engine.run()

    # Results
    print(engine.trader.generate_account_report(Venue("HYPERLIQUID")))
    print(engine.trader.generate_order_fills_report())
    print(engine.trader.generate_positions_report())

    engine.dispose()

if __name__ == "__main__":
    run_backtest()
```

---

## Hyperliquid Live Trading Patch

### The Problem

Nautilus Trader v1.222.0 has bugs in the Hyperliquid adapter:
1. Rust HTTP client serialization causes type mismatches
2. Price precision exceeds Hyperliquid's 5 significant figure limit

### The Solution

Bypass the buggy adapter using the official Hyperliquid Python SDK.

### Create `hyperliquid_patch.py`

```python
import os
import math
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
        if not private_key.startswith("0x"):
            private_key = "0x" + private_key
        account = Account.from_key(private_key)
        _INFO = Info(constants.MAINNET_API_URL, skip_ws=True)
        _EXCHANGE = Exchange(account, constants.MAINNET_API_URL, vault_address=vault_address)
    return _EXCHANGE, _INFO

def get_mid_price(symbol: str) -> Decimal:
    """Get current mid price for symbol."""
    _, info = get_exchange()
    return Decimal(str(info.all_mids()[symbol]))

def format_price_5_sigfigs(price: float, is_buy: bool) -> str:
    """
    Format price to max 5 significant figures (Hyperliquid requirement).

    Rounds up for buys (ceiling) and down for sells (floor) to ensure fills.
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
    return f"{rounded:.{decimal_places}f}" if decimal_places > 0 else str(int(rounded))

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

                if order.has_price and order.price:
                    limit_price = format_price_5_sigfigs(float(order.price), is_buy)
                elif is_market:
                    mid = get_mid_price(symbol)
                    slippage_price = float(mid) * (1.03 if is_buy else 0.97)
                    limit_price = format_price_5_sigfigs(slippage_price, is_buy)
                else:
                    raise ValueError(f"Unsupported order type: {order.order_type}")

                order_type = {"limit": {"tif": "Ioc"}} if is_market else {"limit": {"tif": "Gtc"}}
                result = exchange.order(
                    name=symbol, is_buy=is_buy, sz=size,
                    limit_px=float(limit_price), order_type=order_type,
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
        print("HYPERLIQUID PATCH APPLIED - Using SDK with 5 sig fig prices")
        return True
    except Exception as e:
        print(f"PATCH FAILED: {e}")
        return False

# Auto-apply on import
apply_hyperliquid_patch()
```

### Usage: Import BEFORE Nautilus

```python
# CRITICAL: Import patch BEFORE Nautilus Trader
import hyperliquid_patch

# Then import Nautilus normally
from nautilus_trader.adapters.hyperliquid import HYPERLIQUID
from nautilus_trader.live.node import TradingNode
```

### Set Leverage (One-Time Setup)

```python
from hyperliquid.exchange import Exchange
from hyperliquid.utils import constants
from eth_account import Account
import os

private_key = os.getenv("HYPERLIQUID_PK")
if not private_key.startswith("0x"):
    private_key = "0x" + private_key

account = Account.from_key(private_key)
exchange = Exchange(account, constants.MAINNET_API_URL)

# Set 10x leverage for SOL (cross margin)
exchange.update_leverage(10, "SOL", is_cross=True)
```

---

## Price Precision Rules

Hyperliquid requires maximum 5 significant figures for all prices:

| Price | Valid? | Sig Figs |
|-------|--------|----------|
| $139.05 | Yes | 5 |
| $139.054 | No | 6 |
| $1.2345 | Yes | 5 |
| $1.23456 | No | 6 |
| $12345 | Yes | 5 |
| $123456 | No | 6 |

The `format_price_5_sigfigs()` function handles this automatically.

---

## Complete Strategy Example

### Live Trading Setup

```python
#!/usr/bin/env python3
"""
MTF EMA + Heiken Ashi Strategy - Live on Hyperliquid
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# CRITICAL: Apply patch BEFORE Nautilus imports
import hyperliquid_patch

from nautilus_trader.adapters.hyperliquid import HYPERLIQUID, HyperliquidDataClientConfig, HyperliquidExecClientConfig
from nautilus_trader.live.node import TradingNode, TradingNodeConfig
from nautilus_trader.config import LiveDataEngineConfig, LiveExecEngineConfig
from decimal import Decimal

# Import your strategy
from mtf_ema_ha_strategy import MTFEmaHeikenAshiStrategy, MTFEmaHeikenAshiConfig

def main():
    # Node configuration
    node_config = TradingNodeConfig(
        trader_id="LIVE-001",
        data_engine=LiveDataEngineConfig(),
        exec_engine=LiveExecEngineConfig(),
    )

    node = TradingNode(config=node_config)

    # Hyperliquid configuration
    data_config = HyperliquidDataClientConfig(
        wallet_address=os.getenv("HYPERLIQUID_VAULT"),
        is_testnet=False,  # Mainnet
    )

    exec_config = HyperliquidExecClientConfig(
        wallet_address=os.getenv("HYPERLIQUID_VAULT"),
        private_key=os.getenv("HYPERLIQUID_PK"),
        is_testnet=False,  # Mainnet
    )

    # Add Hyperliquid venue
    node.add_data_client_factory(HYPERLIQUID, HyperliquidLiveDataClientFactory)
    node.add_exec_client_factory(HYPERLIQUID, HyperliquidLiveExecClientFactory)

    node.build()

    # Strategy configuration
    strategy_config = MTFEmaHeikenAshiConfig(
        instrument_id="SOL-USD.HYPERLIQUID",
        htf_bar_type="SOL-USD.HYPERLIQUID-1-HOUR-LAST-EXTERNAL",
        ltf_bar_type="SOL-USD.HYPERLIQUID-5-MINUTE-LAST-EXTERNAL",
        ema_fast=9,
        ema_slow=21,
        trade_size=Decimal("0.5"),  # 0.5 SOL per trade
    )

    strategy = MTFEmaHeikenAshiStrategy(config=strategy_config)
    node.trader.add_strategy(strategy)

    # Start trading
    node.run()

if __name__ == "__main__":
    main()
```

---

## Network Latency Optimization

For best performance, deploy on AWS ap-northeast-1 (Tokyo):
- Ping to Hyperliquid CloudFront (nrt12): ~1ms
- API latency: ~28ms

---

## Verified Working

Tested on Hyperliquid Mainnet 2025-01-12:
```
SELL 0.72 SOL @ $143.38 - FILLED
BUY 0.71 SOL @ $143.39 - FILLED
```

---

## Troubleshooting

### Order Rejected: Invalid Price

Ensure prices have max 5 significant figures. Use `format_price_5_sigfigs()`.

### Connection Error

1. Check `.env` has correct `HYPERLIQUID_PK` and `HYPERLIQUID_VAULT`
2. Verify private key starts with `0x` (or SDK adds it)
3. Confirm vault address is correct

### Patch Not Applied

Ensure `import hyperliquid_patch` comes BEFORE any Nautilus imports.

---

## File Structure

```
your_trading_project/
├── .env                        # Credentials (gitignored)
├── hyperliquid_patch.py        # SDK patch for live trading
├── heiken_ashi.py              # Heiken Ashi indicator
├── mtf_ema_ha_strategy.py      # Strategy implementation
├── backtest.py                 # Backtest runner
├── live.py                     # Live trading runner
└── data_catalog/               # Parquet data for backtesting
```
