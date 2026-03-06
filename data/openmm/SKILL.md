---
name: openmm
version: 0.1.0
description: "Open-source market making for AI agents. Multi-exchange trading, grid strategies, and real-time market data. CLI + MCP + Skills."
tags: [trading, market-making, defi, crypto, exchanges, mcp, grid-trading]
metadata:
  openclaw:
    emoji: "📈"
    homepage: https://github.com/3rd-Eye-Labs/OpenMM
    docs: https://deepwiki.com/3rd-Eye-Labs/OpenMM
    requires:
      bins: [openmm]
    install:
      - kind: node
        package: "@3rd-eye-labs/openmm"
        bins: [openmm]
---

# OpenMM — Open-Source Market Making for AI Agents

OpenMM is an open-source market making framework — multi-exchange support, grid strategies, real-time market data, and automated trading. One CLI for everything.

**GitHub:** https://github.com/3rd-Eye-Labs/OpenMM
**MCP Server:** https://github.com/QBT-Labs/OpenMM-MCP
**Docs:** https://deepwiki.com/3rd-Eye-Labs/OpenMM

## What is OpenMM?

- **Multi-Exchange** — MEXC, Gate.io, Kraken, Bitget
- **Grid Trading** — Automated grid strategies with dynamic spacing, sizing, and volatility adjustment
- **Market Data** — Tickers, orderbooks, recent trades across all exchanges
- **Order Management** — Limit/market orders, cancel, list open orders
- **Cardano DEX** — Pool discovery, aggregated prices via Iris Protocol
- **CLI + MCP** — Use via command line or as MCP server for AI agents
- **Open Source** — MIT licensed, fully customizable

## Quick Start

### Option A: CLI

```bash
# Install
npm install -g @3rd-eye-labs/openmm

# Set exchange credentials as environment variables
export MEXC_API_KEY="your_api_key"
export MEXC_SECRET="your_secret_key"

# Check balances
openmm balance --exchange mexc

# Get ticker price
openmm ticker --exchange mexc --symbol BTC/USDT

# Start grid trading (dry run first)
openmm trade --strategy grid --exchange mexc --symbol INDY/USDT --dry-run
```

### Option B: MCP Server

Run `npx @qbtlabs/openmm-mcp` to start a local MCP server over stdio. This exposes all 13 tools to any MCP-compatible client.

```json
{
  "mcpServers": {
    "openmm": {
      "command": "npx",
      "args": ["@qbtlabs/openmm-mcp"],
      "env": {
        "MEXC_API_KEY": "your_key",
        "MEXC_SECRET": "your_secret"
      }
    }
  }
}
```

Only include env vars for exchanges you want to use.

### Option C: As Library

```typescript
import { OpenMM } from '@3rd-eye-labs/openmm';

const mm = new OpenMM({
  exchange: 'mexc',
  apiKey: process.env.MEXC_API_KEY,
  secret: process.env.MEXC_SECRET
});

const orderbook = await mm.getOrderbook('BTC/USDT');
```

---

## Environment Setup

Exchange credentials are configured via environment variables — keys are stored locally and never sent to the server. Add them to your `.env` file or export them in your shell:

```env
# MEXC (API key + secret)
MEXC_API_KEY=your_mexc_api_key
MEXC_SECRET=your_mexc_secret_key

# Gate.io (API key + secret)
GATEIO_API_KEY=your_gateio_api_key
GATEIO_SECRET=your_gateio_secret_key

# Bitget (API key + secret + passphrase set when creating the API key)
BITGET_API_KEY=your_bitget_api_key
BITGET_SECRET=your_bitget_secret_key
BITGET_PASSPHRASE=your_bitget_passphrase

# Kraken (API key + secret)
KRAKEN_API_KEY=your_kraken_api_key
KRAKEN_SECRET=your_kraken_secret_key
```

### Symbol Format
- Use standard format: `BTC/USDT`, `ETH/USDT`, `INDY/USDT`, `ADA/EUR`, `BTC/USD`
- The CLI automatically converts to exchange-specific format
- Kraken supports both USD/EUR fiat pairs and USDT pairs

---

## Core Tools

### Balance & Portfolio

Check account balances on any connected exchange. Query each exchange separately — there is no cross-exchange aggregate command.

```bash
# Get all balances
openmm balance --exchange mexc
openmm balance --exchange gateio
openmm balance --exchange bitget
openmm balance --exchange kraken

# Get specific asset balance
openmm balance --exchange mexc --asset BTC
openmm balance --exchange mexc --asset USDT
openmm balance --exchange kraken --asset ADA
openmm balance --exchange kraken --asset EUR

# JSON output (useful for scripting)
openmm balance --exchange mexc --json
openmm balance --exchange bitget --json
```

**Options:**
- `-e, --exchange <exchange>` — Exchange to query (required)
- `-a, --asset <asset>` — Specific asset to query (optional)
- `--json` — Output in JSON format

### Market Data

Real-time prices, orderbooks, and trade history. Use `--symbol` with the standard `BASE/QUOTE` format. Kraken uses fiat pairs like `ADA/EUR` and `BTC/USD` alongside crypto pairs.

**Ticker — current price, bid/ask, spread, volume:**

```bash
# MEXC
openmm ticker --exchange mexc --symbol BTC/USDT
openmm ticker --exchange mexc --symbol ETH/USDT --json

# Bitget (Cardano tokens)
openmm ticker --exchange bitget --symbol SNEK/USDT
openmm ticker --exchange bitget --symbol BTC/USDT --json

# Kraken (fiat pairs)
openmm ticker --exchange kraken --symbol ADA/EUR
openmm ticker --exchange kraken --symbol BTC/USD --json
```

**Order Book — bid/ask depth:**

```bash
# MEXC - BTC/USDT with default 10 levels
openmm orderbook --exchange mexc --symbol BTC/USDT

# Bitget - top 5 levels for SNEK
openmm orderbook --exchange bitget --symbol SNEK/USDT --limit 5

# Kraken - ADA/EUR with 10 levels
openmm orderbook --exchange kraken --symbol ADA/EUR --limit 10

# Gate.io - JSON output
openmm orderbook --exchange gateio --symbol BTC/USDT --json
```

**Recent Trades — latest executions with buy/sell breakdown:**

```bash
# MEXC - default 20 trades
openmm trades --exchange mexc --symbol BTC/USDT

# Bitget - 50 trades for SNEK
openmm trades --exchange bitget --symbol SNEK/USDT --limit 50

# Kraken - ADA/EUR trades
openmm trades --exchange kraken --symbol ADA/EUR

# Gate.io - JSON output
openmm trades --exchange gateio --symbol ETH/USDT --json
```

**Options (shared across ticker, orderbook, trades):**
- `-e, --exchange <exchange>` — Exchange to query (required)
- `-s, --symbol <symbol>` — Trading pair symbol (required)
- `-l, --limit <limit>` — Number of levels/trades (orderbook default: 10, trades default: 20)
- `--json` — Output in JSON format

### Order Management

Place and manage orders on any supported exchange. Orders use your exchange API credentials configured via environment variables.

```bash
# List all open orders
openmm orders list --exchange mexc
openmm orders list --exchange gateio
openmm orders list --exchange bitget

# List open orders for a specific pair
openmm orders list --exchange bitget --symbol SNEK/USDT
openmm orders list --exchange kraken --symbol ADA/EUR --limit 5

# Get specific order by ID
openmm orders get --exchange mexc --id 123456 --symbol BTC/USDT
openmm orders get --exchange bitget --id 1385288398060044291 --symbol SNEK/USDT
openmm orders get --exchange kraken --id OQN3UE-LRH6U-MPLZ5I --symbol ADA/EUR

# Create limit buy order
openmm orders create --exchange mexc --symbol BTC/USDT --side buy --type limit --amount 0.001 --price 50000
openmm orders create --exchange bitget --symbol SNEK/USDT --side buy --type limit --amount 10000 --price 0.00001
openmm orders create --exchange kraken --symbol ADA/EUR --side buy --type limit --amount 50 --price 0.45

# Create market sell order
openmm orders create --exchange mexc --symbol BTC/USDT --side sell --type market --amount 0.001
openmm orders create --exchange bitget --symbol SNEK/USDT --side sell --type market --amount 5000

# Cancel order by ID (symbol is required)
openmm orders cancel --exchange mexc --id C02__626091255599874048060 --symbol INDY/USDT
openmm orders cancel --exchange bitget --id 1385288398060044291 --symbol SNEK/USDT
openmm orders cancel --exchange kraken --id OQN3UE-LRH6U-MPLZ5I --symbol ADA/EUR
```

**Create Options:**
- `-e, --exchange <exchange>` — Exchange to use (required)
- `-s, --symbol <symbol>` — Trading pair (required)
- `--side <side>` — Order side: buy/sell (required)
- `--type <type>` — Order type: market/limit (required)
- `--amount <amount>` — Order amount in base currency (required)
- `--price <price>` — Order price (required for limit orders, ignored for market)
- `--json` — Output in JSON format

**Exchange notes:**
- **Bitget** — 6 decimal price precision for SNEK/NIGHT pairs, 2 decimal quantity precision. Requires passphrase.
- **Kraken** — Minimum order value 5 EUR/USD. Supports major fiat pairs (EUR, USD, GBP).
- **MEXC/Gate.io** — Minimum order value 1 USDT per order.

### Grid Trading

The grid strategy places buy and sell orders at intervals around the current center price. As price oscillates, orders fill and the grid automatically recreates — capturing the spread on each cycle. Total orders = levels x 2.

```bash
# Start grid with defaults (5 levels, 2% spacing, $50 per order)
openmm trade --strategy grid --exchange mexc --symbol INDY/USDT

# Dry run — preview the grid without placing real orders
openmm trade --strategy grid --exchange bitget --symbol SNEK/USDT --dry-run

# Custom grid configuration
openmm trade --strategy grid --exchange mexc --symbol INDY/USDT \
  --levels 5 \
  --spacing 0.02 \
  --size 50 \
  --max-position 0.6 \
  --safety-reserve 0.3

# Geometric spacing — tighter near center, wider at edges
openmm trade --strategy grid --exchange kraken --symbol BTC/USD \
  --levels 10 \
  --spacing 0.005 \
  --spacing-model geometric \
  --spacing-factor 1.5 \
  --size-model pyramidal \
  --size 50

# Volatility-based spread adjustment — grid widens in volatile markets
openmm trade --strategy grid --exchange mexc --symbol INDY/USDT \
  --levels 10 \
  --spacing 0.005 \
  --spacing-model geometric \
  --spacing-factor 1.3 \
  --size-model pyramidal \
  --size 5 \
  --volatility

# Volatility with custom thresholds (tighter sensitivity)
openmm trade --strategy grid --exchange kraken --symbol SNEK/EUR \
  --levels 5 \
  --spacing 0.01 \
  --size 5 \
  --volatility \
  --volatility-low 0.01 \
  --volatility-high 0.03

# Load configuration from a JSON profile
openmm trade --strategy grid --exchange gateio --symbol SNEK/USDT \
  --grid-profile ./profiles/balanced-geometric.json
```

**Strategy output on startup:**
```
Starting Trading Strategy
Strategy: GRID
Exchange: KRAKEN
Symbol: BTC/USD
Grid Levels: 10 per side (20 total)
Grid Spacing: 0.3%
Spacing Model: geometric
Spacing Factor: 1.3
Size Model: pyramidal
Order Size: $50
Max Position: 80%
Safety Reserve: 20%

Strategy initialized successfully
Grid Configuration:
  Levels: 10 per side (20 total orders)
  Spacing Model: geometric
  Base Spacing: 0.30%
  Spacing Factor: 1.3
  Size Model: pyramidal
  Base Size: $50
Strategy is now running!
Press Ctrl+C to stop the strategy gracefully
```

**Graceful shutdown:** Press `Ctrl+C`. The system cancels all open orders, disconnects from the exchange, and displays final status.

**Required Parameters:**
- `--strategy grid` — Specifies grid trading strategy
- `--exchange <exchange>` — Exchange to trade on (mexc, bitget, gateio, kraken)
- `--symbol <symbol>` — Trading pair (e.g., INDY/USDT, SNEK/USDT, ADA/EUR)

**Grid Parameters:**
- `--levels <number>` — Grid levels each side (default: 5, max: 10, total orders = levels x 2)
- `--spacing <decimal>` — Base price spacing between levels (default: 0.02 = 2%)
- `--size <number>` — Base order size in quote currency (default: 50)
- `--confidence <decimal>` — Minimum price confidence to trade (default: 0.6)
- `--deviation <decimal>` — Price deviation to trigger grid recreation (default: 0.015)
- `--debounce <ms>` — Delay between grid adjustments (default: 2000ms)
- `--max-position <decimal>` — Maximum position size as % of balance (default: 0.8)
- `--safety-reserve <decimal>` — Safety reserve as % of balance (default: 0.2)
- `--dry-run` — Simulate trading without placing real orders

**Dynamic Grid Parameters:**
- `--spacing-model <model>` — linear, geometric, or custom (default: linear)
- `--spacing-factor <number>` — Geometric spacing multiplier per level (default: 1.3)
- `--size-model <model>` — flat, pyramidal, or custom (default: flat)
- `--grid-profile <path>` — Load complete grid configuration from a JSON profile

**Volatility Parameters:**
- `--volatility` — Enable volatility-based dynamic spread adjustment
- `--volatility-low <decimal>` — Low volatility threshold (default: 0.02). Below this, spacing stays normal.
- `--volatility-high <decimal>` — High volatility threshold (default: 0.05). Above this, spacing is widened maximally.

**Exchange notes for grid:**
- **MEXC/Gate.io** — Minimum 1 USDT per order. Ensure `--size` / `--levels` >= 1.
- **Bitget** — Minimum 1 USDT per order. Price precision: 6 decimals for SNEK/NIGHT. Requires passphrase.
- **Kraken** — Minimum 5 EUR/USD per order. Ensure `--size` / `--levels` >= 5.

### Cardano DEX Integration

OpenMM integrates with Cardano DEX liquidity pools via the Iris Protocol. Supported tokens: **INDY** (Indigo Protocol), **SNEK** (Snek Token), **NIGHT** (Midnight), **MIN** (Minswap).

Prices are calculated by fetching TOKEN/ADA from on-chain DEX pools (weighted by TVL), then multiplying by ADA/USDT from CEX price feeds (MEXC, Coingecko) to produce a TOKEN/USDT price.

**Discover liquidity pools:**

```bash
# Find all pools for a token
openmm pool-discovery discover INDY

# Top 5 pools for SNEK
openmm pool-discovery discover SNEK --limit 5

# Filter by minimum TVL
openmm pool-discovery discover INDY --min-liquidity 50000

# Show all pools (ignore limit)
openmm pool-discovery discover NIGHT --show-all
```

**Get live prices from pools:**

```bash
openmm pool-discovery prices NIGHT
openmm pool-discovery prices SNEK
openmm pool-discovery prices INDY
```

**List supported tokens:**

```bash
openmm pool-discovery supported
```

**Compare DEX vs CEX prices:**

```bash
openmm price-comparison --symbol SNEK
openmm price-comparison --symbol INDY
```

---

## Safety Rules

### Always dry-run first

Before executing any grid strategy, preview the grid to see what orders will be placed:

```bash
openmm trade --strategy grid --exchange mexc --symbol INDY/USDT --dry-run
```

### Confirm before execution

For AI agents using MCP:
1. **Always show the trade plan** — display what will be executed
2. **Get explicit confirmation** — never auto-execute without user approval
3. **Use `dryRun: true`** — the MCP `start_grid_strategy` tool defaults to dry-run mode

### Risk management

Grid strategy has built-in risk controls:
- `--max-position 0.6` — Use max 60% of balance for trading (default: 80%)
- `--safety-reserve 0.3` — Keep 30% as safety reserve (default: 20%)
- `--confidence 0.8` — Require 80% price confidence before trading (default: 60%)

Total allocation is automatically capped regardless of the size model used. The grid recreates when orders are filled and adjusts to significant price movements (configurable via `--deviation`).

---

## CLI Reference

### Balance & Market Data
| Command | Description |
|---------|-------------|
| `balance` | Get balances for an exchange |
| `ticker` | Get current price, bid/ask, spread, volume |
| `orderbook` | Get orderbook depth (bids/asks) |
| `trades` | Get recent trades |
| `price-comparison` | Compare DEX vs CEX prices for Cardano tokens |

### Orders
| Command | Description |
|---------|-------------|
| `orders list` | List open orders (all or by symbol) |
| `orders get` | Get specific order by ID |
| `orders create` | Place a limit or market order |
| `orders cancel` | Cancel an order by ID |

### Trading
| Command | Description |
|---------|-------------|
| `trade --strategy grid` | Start grid trading strategy |

### Cardano
| Command | Description |
|---------|-------------|
| `pool-discovery discover` | Discover DEX liquidity pools for a token |
| `pool-discovery supported` | List supported Cardano tokens (INDY, SNEK, NIGHT, MIN) |
| `pool-discovery prices` | Get live aggregated pool prices |

---

## Supported Exchanges

| Exchange | Trading | Grid | Market Data | Min Order | Notes |
|----------|---------|------|-------------|-----------|-------|
| MEXC | ✅ | ✅ | ✅ | 1 USDT | API key + secret |
| Gate.io | ✅ | ✅ | ✅ | 1 USDT | API key + secret |
| Bitget | ✅ | ✅ | ✅ | 1 USDT | API key + secret + passphrase |
| Kraken | ✅ | ✅ | ✅ | 5 EUR/USD | API key + secret, fiat pairs supported |
| Binance | 🔜 | 🔜 | 🔜 | — | Coming soon |
| Coinbase | 🔜 | 🔜 | 🔜 | — | Coming soon |
| OKX | 🔜 | 🔜 | 🔜 | — | Coming soon |

---

## Tips for Agents

- **Check balances first** — always run `openmm balance --exchange <ex>` before trading
- **Use `--dry-run`** — preview grid strategies before placing real orders
- **Use `BASE/QUOTE` format** — e.g. `BTC/USDT`, `ADA/EUR`, `SNEK/USDT`
- **Query each exchange separately** — there is no cross-exchange aggregate command
- **Handle rate limits** — exchanges have API limits, space out requests
- **Store credentials securely** — use environment variables, never commit `.env` files
- **Respect minimum order values** — MEXC/Gate.io/Bitget: 1 USDT, Kraken: 5 EUR/USD
- **Use `--max-position` and `--safety-reserve`** — built-in risk controls for grid strategies
- **Bitget requires passphrase** — set via `BITGET_PASSPHRASE` env var (created when generating the API key)
- **Use `--json` for parsing** — all commands support `--json` for structured output

---

## MCP Tools (via OpenMM-MCP)

When using OpenMM as an MCP server, these 13 tools are available:

### Market Data
| Tool | Description | Parameters |
|------|-------------|------------|
| `get_ticker` | Real-time price, bid/ask, spread, volume | `exchange`, `symbol` |
| `get_orderbook` | Order book depth (bids/asks) | `exchange`, `symbol`, `limit?` |
| `get_trades` | Recent trades with buy/sell summary | `exchange`, `symbol`, `limit?` |

### Account
| Tool | Description | Parameters |
|------|-------------|------------|
| `get_balance` | Account balances (all or filtered by asset) | `exchange`, `asset?` |
| `list_orders` | Open orders (all or by symbol) | `exchange`, `symbol?` |

### Trading
| Tool | Description | Parameters |
|------|-------------|------------|
| `create_order` | Place limit or market order | `exchange`, `symbol`, `type`, `side`, `amount`, `price?` |
| `cancel_order` | Cancel order by ID | `exchange`, `symbol`, `orderId` |
| `cancel_all_orders` | Cancel all open orders for a pair | `exchange`, `symbol` |

### Strategy
| Tool | Description | Parameters |
|------|-------------|------------|
| `start_grid_strategy` | Calculate and place grid orders (defaults to dry-run) | `exchange`, `symbol`, `levels?`, `spacing?`, `orderSize?`, `spacingModel?`, `sizeModel?`, `dryRun?` |
| `stop_strategy` | Cancel all orders for a pair, stopping the grid | `exchange`, `symbol` |
| `get_strategy_status` | Grid status with open orders, price, and spread | `exchange`, `symbol` |

### Cardano
| Tool | Description | Parameters |
|------|-------------|------------|
| `get_cardano_price` | Aggregated token price from DEX pools (TOKEN/USDT via ADA bridge) | `symbol` |
| `discover_pools` | Discover Cardano DEX liquidity pools for a token | `symbol` |

### MCP Resources
| URI | Description |
|-----|-------------|
| `exchanges://list` | Supported exchanges with credential requirements |
| `strategies://grid` | Grid trading strategy documentation |
| `strategies://grid/profiles` | Example grid profiles (conservative/moderate/aggressive) |

### MCP Prompts
| Prompt | Description |
|--------|-------------|
| `market_analysis` | Analyze ticker + orderbook + trades for a trading pair |
| `portfolio_overview` | Summarize balances and open orders across an exchange |
| `grid_setup_advisor` | Recommend grid config based on market analysis and balance |

---

## Sub-Skills

For specific workflows, load these sub-skills:

| Skill | Description |
|-------|-------------|
| `openmm-exchange-setup` | Configure exchange API credentials step-by-step |
| `openmm-grid-trading` | Grid strategy creation and management |
| `openmm-portfolio` | Balance tracking and order overview across exchanges |

---

## Links

- **GitHub:** https://github.com/3rd-Eye-Labs/OpenMM
- **MCP Server:** https://github.com/QBT-Labs/OpenMM-MCP
- **npm:** https://www.npmjs.com/package/@3rd-eye-labs/openmm
- **Documentation:** https://deepwiki.com/3rd-Eye-Labs/OpenMM
- **Discord:** https://discord.gg/qbtlabs

---

## About

OpenMM is built by [3rd Eye Labs](https://github.com/3rd-Eye-Labs) and [QBT Labs](https://qbtlabs.io).

**License:** MIT
