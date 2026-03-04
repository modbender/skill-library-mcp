# CCXT (Centralized Exchanges)

## Overview

The SDK includes a `ccxt_adapter` that acts as a **multi-exchange factory** for centralized exchanges (CEXes). Each configured exchange becomes a property on the adapter (e.g. `adapter.aster`, `adapter.binance`), and you call the CCXT unified API on that exchange object.

- **Type**: `CCXT`
- **Module**: `wayfinder_paths.adapters.ccxt_adapter.adapter.CCXTAdapter`
- **Capabilities**: `exchange.factory`

## When to use (and when not to)

- Use for CEX workflows (Aster, Binance, etc.) **when the user has API credentials** and explicitly wants centralized exchange data or trading.
- Do **not** use CCXT for Hyperliquid by default. Prefer the native Wayfinder Hyperliquid surfaces (`hyperliquid` resources + `hyperliquid_execute`) unless the user explicitly asks for CCXT/Hyperliquid.

## Config (`config.json`)

Add a `ccxt` section with exchange IDs and credentials (exchange IDs must match CCXT exchange ids):

```json
{
  "ccxt": {
    "aster": { "apiKey": "…", "secret": "…" },
    "binance": { "apiKey": "…", "secret": "…" }
  }
}
```

## Script pattern

CCXT is not exposed as an MCP tool in this skill. Use a one-off script via `run_script`.

```python
import asyncio
from wayfinder_paths.mcp.scripting import get_adapter
from wayfinder_paths.adapters.ccxt_adapter import CCXTAdapter

async def main():
    adapter = get_adapter(CCXTAdapter)
    try:
        ticker = await adapter.aster.fetch_ticker("ETH/USDT")
        print(ticker.get("last"))
    finally:
        await adapter.close()

if __name__ == "__main__":
    asyncio.run(main())
```

Run it:

```bash
poetry run wayfinder run_script --script_path .wayfinder_runs/ccxt_ticker.py --wallet_label main
```

## Common CCXT calls

- `fetch_ticker(symbol)` / `fetch_order_book(symbol)`
- `fetch_balance()`
- `create_order(symbol, "market"|"limit", "buy"|"sell", amount, price?)`
- `cancel_order(id, symbol?)`
- `fetch_open_orders(symbol?)`

Always `await adapter.close()` to avoid leaking sessions.
