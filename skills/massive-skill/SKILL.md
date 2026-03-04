---
name: massive-api
description: Access Massive(Polygon) stock, crypto, forex, options, indices, futures, market data, and news APIs via CLI.
metadata:
  openclaw:
    requires:
      bins: ["npx"]
      env: ["MASSIVE_API_KEY"]
    primaryEnv: "MASSIVE_API_KEY"
---

# Massive(Polygon) Market Data Skill

A CLI tool and JS client wrapper for the [Massive(Polygon)](https://massive.com) financial data APIs. Covers stocks, crypto, forex, options, indices, futures, market status, news, and reference data.

## CLI Usage

```bash
npx --yes massive <command> [options]
```

All commands output JSON to stdout. Use `--help` for a list of commands or `<command> --help` for command-specific options.

### Stocks

See [Stocks Commands Reference](references/stocks_commands.md) for full details on all stock commands and parameters.

### Crypto

See [Crypto Commands Reference](references/crypto_commands.md) for full details on all crypto commands and parameters.

### Forex

See [Forex Commands Reference](references/forex_commands.md) for full details on all forex commands and parameters.

### Options

See [Options Commands Reference](references/options_commands.md) for full details on all options commands and parameters.

### Indices

See [Indices Commands Reference](references/indices_commands.md) for full details on all indices commands and parameters.

### Reference Data

See [Reference Data Commands Reference](references/reference_commands.md) for full details on all reference data commands and parameters.

### Market

See [Market Commands Reference](references/market_commands.md) for full details on all market commands and parameters.

### News

See [News Commands Reference](references/news_commands.md) for full details on all news commands and parameters.