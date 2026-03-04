---
name: nautilus-trader
description: >
  NautilusTrader algorithmic trading platform for strategy development and live trading.
  Use when building trading strategies, backtesting, or deploying to Hyperliquid.
version: "2.0.0"
allowed-tools: Read, Write, Edit, Bash, Glob, Grep
---

# Nautilus Trader Skill

Comprehensive assistance with NautilusTrader development. Includes complete Hyperliquid mainnet integration with SDK patch for live trading.

---

## Overview

This skill covers:

- Strategy development with NautilusTrader
- Backtesting using the Parquet data catalog
- Live trading deployment on Hyperliquid mainnet
- SDK patch for Hyperliquid price precision requirements

### When to Use

- Building trading strategies with NautilusTrader
- Running backtests with historical data
- Deploying strategies to Hyperliquid mainnet
- Debugging NautilusTrader adapter issues
- Working with multi-timeframe (MTF) indicators

---

## Prerequisites

### Core Dependencies

```bash
# NautilusTrader (backtesting + live trading framework)
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

### Environment Variables

Create a `.env` file for Hyperliquid credentials:

```bash
HYPERLIQUID_PK=your_private_key_without_0x_prefix
HYPERLIQUID_VAULT=0xYourVaultAddressHere
```

---

## Quick Start

### 1. Apply the Hyperliquid Patch (for live trading)

```python
# CRITICAL: Import patch BEFORE Nautilus Trader
import hyperliquid_patch

# Then import Nautilus normally
from nautilus_trader.adapters.hyperliquid import HYPERLIQUID
from nautilus_trader.live.node import TradingNode
```

### 2. Basic Strategy Template

```python
from nautilus_trader.trading.strategy import Strategy
from nautilus_trader.config import StrategyConfig
from nautilus_trader.model.data import Bar, BarType
from nautilus_trader.model.enums import OrderSide, TimeInForce
from nautilus_trader.model.identifiers import InstrumentId
from decimal import Decimal

class MyStrategyConfig(StrategyConfig):
    instrument_id: str
    bar_type: str
    trade_size: Decimal = Decimal("0.1")

class MyStrategy(Strategy):
    def __init__(self, config: MyStrategyConfig):
        super().__init__(config)
        self.instrument_id = InstrumentId.from_str(config.instrument_id)
        self.bar_type = BarType.from_str(config.bar_type)
        self.trade_size = config.trade_size

    def on_start(self):
        self.instrument = self.cache.instrument(self.instrument_id)
        self.subscribe_bars(self.bar_type)

    def on_bar(self, bar: Bar):
        # Your strategy logic here
        pass

    def on_stop(self):
        self.close_all_positions(self.instrument_id)
```

---

## Strategy Development

### Heiken Ashi Indicator

```python
from nautilus_trader.indicators.base.indicator import Indicator
from nautilus_trader.model.data import Bar

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
        o, h, l, c = float(bar.open), float(bar.high), float(bar.low), float(bar.close)

        self.ha_close = (o + h + l + c) / 4

        if self._prev_ha_open is None:
            self.ha_open = (o + c) / 2
        else:
            self.ha_open = (self._prev_ha_open + self._prev_ha_close) / 2

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

See `references/hyperliquid.md` for complete MTF EMA + Heiken Ashi strategy implementation.

Key concepts:

- HTF (Higher Timeframe): Determines trend direction via EMA crossover
- LTF (Lower Timeframe): Entry timing via Heiken Ashi confirmation
- Entry: HA color change in trend direction
- Exit: HA color reversal

---

## Backtesting

### Engine Setup

```python
from nautilus_trader.backtest.engine import BacktestEngine, BacktestEngineConfig
from nautilus_trader.model.currencies import USD
from nautilus_trader.model.enums import AccountType, OmsType
from nautilus_trader.model.identifiers import Venue
from nautilus_trader.model.objects import Money
from nautilus_trader.persistence.catalog import ParquetDataCatalog
from decimal import Decimal

def run_backtest():
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

    instruments = catalog.instruments()
    for instrument in instruments:
        engine.add_instrument(instrument)

    bars = catalog.bars()
    engine.add_data(bars)

    # Add strategy
    strategy = MyStrategy(config=MyStrategyConfig(
        instrument_id="SOL-USD.HYPERLIQUID",
        bar_type="SOL-USD.HYPERLIQUID-5-MINUTE-LAST-EXTERNAL",
        trade_size=Decimal("1.0"),
    ))
    engine.add_strategy(strategy)

    # Run
    engine.run()

    # Results
    print(engine.trader.generate_account_report(Venue("HYPERLIQUID")))
    print(engine.trader.generate_order_fills_report())
    print(engine.trader.generate_positions_report())

    engine.dispose()
```

### Data Catalog

See `references/backtesting.md` and `references/data.md` for detailed catalog operations:

- `ParquetDataCatalog` - Query and manage Parquet data files
- `BarDataWrangler` - Convert pandas DataFrames to Nautilus Bar objects
- `write_data()` - Persist data to catalog
- `query()` - Retrieve data with time filters

---

## Live Trading on Hyperliquid

### Node Configuration

```python
import os
from dotenv import load_dotenv

load_dotenv()

# CRITICAL: Apply patch BEFORE Nautilus imports
import hyperliquid_patch

from nautilus_trader.adapters.hyperliquid import (
    HYPERLIQUID,
    HyperliquidDataClientConfig,
    HyperliquidExecClientConfig,
)
from nautilus_trader.live.node import TradingNode, TradingNodeConfig
from nautilus_trader.config import LiveDataEngineConfig, LiveExecEngineConfig

def main():
    node_config = TradingNodeConfig(
        trader_id="LIVE-001",
        data_engine=LiveDataEngineConfig(),
        exec_engine=LiveExecEngineConfig(),
    )

    node = TradingNode(config=node_config)

    data_config = HyperliquidDataClientConfig(
        wallet_address=os.getenv("HYPERLIQUID_VAULT"),
        is_testnet=False,
    )

    exec_config = HyperliquidExecClientConfig(
        wallet_address=os.getenv("HYPERLIQUID_VAULT"),
        private_key=os.getenv("HYPERLIQUID_PK"),
        is_testnet=False,
    )

    node.build()

    # Add your strategy
    strategy = MyStrategy(config=my_config)
    node.trader.add_strategy(strategy)

    node.run()

if __name__ == "__main__":
    main()
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

### Network Latency

For best performance, deploy on AWS ap-northeast-1 (Tokyo):

- Ping to Hyperliquid CloudFront: ~1ms
- API latency: ~28ms

---

## Hyperliquid SDK Patch

### The Problem

Nautilus Trader v1.222.0 has bugs in the Hyperliquid adapter:

1. Rust HTTP client serialization causes type mismatches
2. Price precision exceeds Hyperliquid's 5 significant figure limit

### The Solution

Bypass the buggy adapter using the official Hyperliquid Python SDK. The patch file is located at `references/hyperliquid_patch.py`.

### Price Precision Rules

Hyperliquid requires maximum 5 significant figures for all prices:

| Price     | Valid? | Sig Figs |
|-----------|--------|----------|
| $139.05   | Yes    | 5        |
| $139.054  | No     | 6        |
| $1.2345   | Yes    | 5        |
| $1.23456  | No     | 6        |
| $12345    | Yes    | 5        |
| $123456   | No     | 6        |

### Usage

```python
# CRITICAL: Import patch BEFORE any Nautilus imports
import hyperliquid_patch

# Then import Nautilus normally
from nautilus_trader.adapters.hyperliquid import HYPERLIQUID
```

The patch auto-applies on import and handles:

- Price formatting to 5 significant figures
- Rounding up for buys, down for sells (ensures fills)
- SDK-based order submission bypassing Rust client

### Verified Working

Tested on Hyperliquid Mainnet 2025-01-12:

```
SELL 0.72 SOL @ $143.38 - FILLED
BUY 0.71 SOL @ $143.39 - FILLED
```

---

## Configuration

### File Structure

```
your_trading_project/
├── .env                        # Credentials (gitignored)
├── hyperliquid_patch.py        # SDK patch for live trading
├── heiken_ashi.py              # Heiken Ashi indicator
├── my_strategy.py              # Strategy implementation
├── backtest.py                 # Backtest runner
├── live.py                     # Live trading runner
└── data_catalog/               # Parquet data for backtesting
```

### Bar Type Format

```
{symbol}.{venue}-{step}-{aggregation}-{price_type}-{source}

Examples:
SOL-USD.HYPERLIQUID-1-HOUR-LAST-EXTERNAL
SOL-USD.HYPERLIQUID-5-MINUTE-LAST-EXTERNAL
BTC-USD.HYPERLIQUID-15-MINUTE-LAST-EXTERNAL
```

---

## Troubleshooting

### Order Rejected: Invalid Price

Ensure prices have max 5 significant figures. Use the `format_price_5_sigfigs()` function from the patch.

### Connection Error

1. Check `.env` has correct `HYPERLIQUID_PK` and `HYPERLIQUID_VAULT`
2. Verify private key format (with or without `0x` prefix)
3. Confirm vault address is correct

### Patch Not Applied

Ensure `import hyperliquid_patch` comes BEFORE any Nautilus imports.

### Missing Data in Backtest

1. Verify data catalog path exists
2. Check instrument IDs match between data and strategy config
3. Ensure bar types are correctly formatted

### Position Not Closing

Check that `reduce_only=True` is set on exit orders for netting accounts.

---

## Reference Files

Detailed documentation is available in `references/`:

| File | Description |
|------|-------------|
| `hyperliquid.md` | Complete Hyperliquid integration guide |
| `hyperliquid_patch.py` | SDK patch source code |
| `strategies.md` | Strategy patterns and examples |
| `backtesting.md` | Data catalog and backtest API |
| `data.md` | Data handling and wrangling |
| `getting_started.md` | NautilusTrader fundamentals |
| `concepts.md` | Core concepts and architecture |
| `api.md` | Full API reference |

Use `view` to read specific reference files when detailed information is needed.
