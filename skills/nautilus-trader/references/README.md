# nautilus_trader_hyperfix

Fix for Nautilus Trader's Hyperliquid adapter enabling live mainnet trading.

**Status:** Beta - Verified working on mainnet (Jan 2025)

## The Problem

Nautilus Trader v1.222.0's Hyperliquid adapter has bugs ([Issue #3152](https://github.com/nautechsystems/nautilus_trader/issues/3152)):

1. `rust_decimal` serialization causes L1 signature verification failures
2. Prices exceed Hyperliquid's 5 significant figure limit

## The Solution

Bypass the Rust HTTP client using the official Hyperliquid Python SDK.

## Quick Start

### 1. Install

```bash
pip install nautilus_trader hyperliquid-python-sdk eth-account python-dotenv
```

### 2. Set Environment

```bash
export HYPERLIQUID_PK=your_private_key_without_0x
export HYPERLIQUID_VAULT=0xYourVaultAddress
```

Or create `.env`:
```
HYPERLIQUID_PK=abc123...
HYPERLIQUID_VAULT=0x...
```

### 3. Import Before Nautilus

```python
# CRITICAL: Import patch FIRST
import hyperliquid_patch

# Then import Nautilus
from nautilus_trader.adapters.hyperliquid import HYPERLIQUID
```

### 4. Set Leverage (Once)

```python
from hyperliquid.exchange import Exchange
from hyperliquid.utils import constants
from eth_account import Account
import os

pk = os.getenv("HYPERLIQUID_PK")
if not pk.startswith("0x"):
    pk = "0x" + pk

account = Account.from_key(pk)
exchange = Exchange(account, constants.MAINNET_API_URL)
exchange.update_leverage(10, "SOL", is_cross=True)
```

## Price Precision

Hyperliquid requires max 5 significant figures:

| Price | Valid? | Sig Figs |
|-------|--------|----------|
| 139.05 | ✓ | 5 |
| 139.054 | ✗ | 6 |
| 1.2345 | ✓ | 5 |
| 12345 | ✓ | 5 |

The patch handles this automatically.

## Verified Working

Tested on Hyperliquid Mainnet:
```
SELL 0.72 SOL @ $143.38 - FILLED
BUY 0.71 SOL @ $143.39 - FILLED
```

## Network Latency

Best performance from AWS ap-northeast-1 (Tokyo):
- Ping to Hyperliquid: ~1ms
- API latency: ~28ms

## Files

```
nautilus_trader_hyperfix/
├── hyperliquid_patch.py    # The fix - import this
├── examples/
│   ├── live_trading.py     # Live trading example
│   └── set_leverage.py     # One-time leverage setup
├── requirements.txt
├── LICENSE
└── README.md
```

## Compatibility

- Nautilus Trader: v1.222.0
- Python: 3.11+
- Hyperliquid SDK: 0.10+

## Limitations

- Only supports Market and Limit orders (no Stop/MIT/LIT)
- No cancel order support (use SDK directly)
- No position sync on reconnect

## Contributing

Issues and PRs welcome. Test on testnet first.

## License

MIT
