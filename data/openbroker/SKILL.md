---
name: openbroker
description: Hyperliquid trading plugin with background position monitoring. Execute market orders, limit orders, manage positions, view funding rates, and run trading strategies with automatic alerts for PnL changes and liquidation risk.
license: MIT
compatibility: Requires Node.js 22+, network access to api.hyperliquid.xyz
homepage: https://www.npmjs.com/package/openbroker
metadata: {"author": "monemetrics", "version": "1.0.45", "openclaw": {"requires": {"bins": ["openbroker"], "env": ["HYPERLIQUID_PRIVATE_KEY"]}, "primaryEnv": "HYPERLIQUID_PRIVATE_KEY", "install": [{"id": "node", "kind": "node", "package": "openbroker", "bins": ["openbroker"], "label": "Install openbroker (npm)"}]}}
allowed-tools: ob_account ob_positions ob_funding ob_markets ob_search ob_spot ob_fills ob_orders ob_order_status ob_fees ob_candles ob_funding_history ob_trades ob_rate_limit ob_buy ob_sell ob_limit ob_trigger ob_tpsl ob_cancel ob_twap ob_bracket ob_chase ob_watcher_status Bash(openbroker:*)
---

# Open Broker - Hyperliquid Trading CLI

Execute trading operations on Hyperliquid DEX with builder fee support.

## Installation

```bash
npm install -g openbroker
```

## Quick Start

```bash
# 1. Setup (generates wallet, creates config, approves builder fee)
openbroker setup

# 2. Fund your wallet with USDC on Arbitrum, then deposit at https://app.hyperliquid.xyz/

# 3. Start trading
openbroker account
openbroker buy --coin ETH --size 0.1
```

## Command Reference

### Setup
```bash
openbroker setup              # One-command setup (wallet + config + builder approval)
openbroker approve-builder --check  # Check builder fee status (for troubleshooting)
```

The `setup` command offers three modes:
1. **Import existing key** — use a private key you already have (master wallet)
2. **Generate new wallet** — create a fresh master wallet
3. **Generate API wallet** (recommended for agents) — creates a restricted wallet that can trade but cannot withdraw

For options 1 and 2, setup saves config and approves the builder fee automatically.
For option 3 (API wallet), see the API Wallet Setup section below.

### API Wallet Setup (Recommended for Agents)

API wallets can place trades on behalf of a master account but **cannot withdraw funds**. This is the safest option for automated agents.

**Flow:**
1. Run `openbroker setup` and choose option 3 ("Generate API wallet")
2. The CLI generates a keypair and prints an approval URL (e.g. `https://openbroker.dev/approve?agent=0xABC...`)
3. The agent owner opens the URL in a browser and connects their master wallet (MetaMask etc.)
4. The master wallet signs two transactions: `ApproveAgent` (authorizes the API wallet) and `ApproveBuilderFee` (approves the 1 bps fee)
5. The CLI detects the approval automatically and saves the config

**After setup, the config will contain:**
```
HYPERLIQUID_PRIVATE_KEY=0x...        # API wallet private key
HYPERLIQUID_ACCOUNT_ADDRESS=0x...    # Master account address
HYPERLIQUID_NETWORK=mainnet
```

**Important for agents:** When using an API wallet, pass the approval URL to the agent owner (the human who controls the master wallet). The owner must approve in a browser before the agent can trade. The CLI waits up to 10 minutes for the approval. If it times out, re-run `openbroker setup`.

### Account Info
```bash
openbroker account            # Balance, equity, margin
openbroker account --orders   # Include open orders
openbroker positions          # Open positions with PnL
openbroker positions --coin ETH  # Specific coin
```

### Funding Rates
```bash
openbroker funding --top 20   # Top 20 by funding rate
openbroker funding --coin ETH # Specific coin
```

### Markets
```bash
openbroker markets --top 30   # Top 30 main perps
openbroker markets --coin BTC # Specific coin
```

### All Markets (Perps + Spot + HIP-3)
```bash
openbroker all-markets                 # Show all markets
openbroker all-markets --type perp     # Main perps only
openbroker all-markets --type hip3     # HIP-3 perps only
openbroker all-markets --type spot     # Spot markets only
openbroker all-markets --top 20        # Top 20 by volume
```

### Search Markets (Find assets across providers)
```bash
openbroker search --query GOLD    # Find all GOLD markets
openbroker search --query BTC     # Find BTC across all providers
openbroker search --query ETH --type perp  # ETH perps only
```

### Spot Markets
```bash
openbroker spot                   # Show all spot markets
openbroker spot --coin PURR       # Show PURR market info
openbroker spot --balances        # Show your spot balances
openbroker spot --top 20          # Top 20 by volume
```

### Trade Fills
```bash
openbroker fills                          # Recent fills
openbroker fills --coin ETH               # ETH fills only
openbroker fills --coin BTC --side buy --top 50
```

### Order History
```bash
openbroker orders                         # Recent orders (all statuses)
openbroker orders --coin ETH --status filled
openbroker orders --top 50
```

### Order Status
```bash
openbroker order-status --oid 123456789   # Check specific order
openbroker order-status --oid 0x1234...   # By client order ID
```

### Fee Schedule
```bash
openbroker fees                           # Fee tier, rates, and volume
```

### Candle Data (OHLCV)
```bash
openbroker candles --coin ETH                           # 24 hourly candles
openbroker candles --coin BTC --interval 4h --bars 48   # 48 four-hour bars
openbroker candles --coin SOL --interval 1d --bars 30   # 30 daily bars
```

### Funding History
```bash
openbroker funding-history --coin ETH              # Last 24h
openbroker funding-history --coin BTC --hours 168  # Last 7 days
```

### Recent Trades (Tape)
```bash
openbroker trades --coin ETH              # Last 30 trades
openbroker trades --coin BTC --top 50     # Last 50 trades
```

### Rate Limit
```bash
openbroker rate-limit                     # API usage and capacity
```

## Trading Commands

### Market Orders (Quick)
```bash
openbroker buy --coin ETH --size 0.1
openbroker sell --coin BTC --size 0.01
openbroker buy --coin SOL --size 5 --slippage 100  # Custom slippage (bps)
```

### Market Orders (Full)
```bash
openbroker market --coin ETH --side buy --size 0.1
openbroker market --coin BTC --side sell --size 0.01 --slippage 100
```

### Limit Orders
```bash
openbroker limit --coin ETH --side buy --size 1 --price 3000
openbroker limit --coin SOL --side sell --size 10 --price 200 --tif ALO
```

### Set TP/SL on Existing Position
```bash
# Set take profit at $40, stop loss at $30
openbroker tpsl --coin HYPE --tp 40 --sl 30

# Set TP at +10% from entry, SL at entry (breakeven)
openbroker tpsl --coin HYPE --tp +10% --sl entry

# Set only stop loss at -5% from entry
openbroker tpsl --coin ETH --sl -5%

# Partial position TP/SL
openbroker tpsl --coin ETH --tp 4000 --sl 3500 --size 0.5
```

### Trigger Orders (Standalone TP/SL)
```bash
# Take profit: sell when price rises to $40
openbroker trigger --coin HYPE --side sell --size 0.5 --trigger 40 --type tp

# Stop loss: sell when price drops to $30
openbroker trigger --coin HYPE --side sell --size 0.5 --trigger 30 --type sl
```

### Cancel Orders
```bash
openbroker cancel --all           # Cancel all orders
openbroker cancel --coin ETH      # Cancel ETH orders only
openbroker cancel --oid 123456    # Cancel specific order
```

## Advanced Execution

### TWAP (Time-Weighted Average Price)
```bash
# Execute 1 ETH buy over 1 hour (auto-calculates slices)
openbroker twap --coin ETH --side buy --size 1 --duration 3600

# Custom intervals with randomization
openbroker twap --coin BTC --side sell --size 0.5 --duration 1800 --intervals 6 --randomize 20
```

### Scale In/Out (Grid Orders)
```bash
# Place 5 buy orders ranging 2% below current price
openbroker scale --coin ETH --side buy --size 1 --levels 5 --range 2

# Scale out with exponential distribution
openbroker scale --coin BTC --side sell --size 0.5 --levels 4 --range 3 --distribution exponential --reduce
```

### Bracket Order (Entry + TP + SL)
```bash
# Long ETH with 3% take profit and 1.5% stop loss
openbroker bracket --coin ETH --side buy --size 0.5 --tp 3 --sl 1.5

# Short with limit entry
openbroker bracket --coin BTC --side sell --size 0.1 --entry limit --price 100000 --tp 5 --sl 2
```

### Chase Order (Follow Price)
```bash
# Chase buy with ALO orders until filled
openbroker chase --coin ETH --side buy --size 0.5 --timeout 300

# Aggressive chase with tight offset
openbroker chase --coin SOL --side buy --size 10 --offset 2 --timeout 60
```

## Trading Strategies

### Funding Arbitrage
```bash
# Collect funding on ETH if rate > 25% annualized
openbroker funding-arb --coin ETH --size 5000 --min-funding 25

# Run for 24 hours, check every 30 minutes
openbroker funding-arb --coin BTC --size 10000 --duration 24 --check 30 --dry
```

### Grid Trading
```bash
# ETH grid from $3000-$4000 with 10 levels, 0.1 ETH per level
openbroker grid --coin ETH --lower 3000 --upper 4000 --grids 10 --size 0.1

# Accumulation grid (buys only)
openbroker grid --coin BTC --lower 90000 --upper 100000 --grids 5 --size 0.01 --mode long
```

### DCA (Dollar Cost Averaging)
```bash
# Buy $100 of ETH every hour for 24 hours
openbroker dca --coin ETH --amount 100 --interval 1h --count 24

# Invest $5000 in BTC over 30 days with daily purchases
openbroker dca --coin BTC --total 5000 --interval 1d --count 30
```

### Market Making Spread
```bash
# Market make ETH with 0.1 size, 10bps spread
openbroker mm-spread --coin ETH --size 0.1 --spread 10

# Tighter spread with position limit
openbroker mm-spread --coin BTC --size 0.01 --spread 5 --max-position 0.1
```

### Maker-Only MM (ALO orders)
```bash
# Market make using ALO (post-only) orders - guarantees maker rebates
openbroker mm-maker --coin HYPE --size 1 --offset 1

# Wider offset for volatile assets
openbroker mm-maker --coin ETH --size 0.1 --offset 2 --max-position 0.5
```

## Order Types

### Limit Orders vs Trigger Orders

**Limit Orders** (`openbroker limit`):
- Execute immediately if price is met
- Rest on the order book until filled or cancelled
- A limit sell BELOW current price fills immediately (taker)
- NOT suitable for stop losses

**Trigger Orders** (`openbroker trigger`, `openbroker tpsl`):
- Stay dormant until trigger price is reached
- Only activate when price hits the trigger level
- Proper way to set stop losses and take profits
- Won't fill prematurely

### When to Use Each

| Scenario | Command |
|----------|---------|
| Buy at specific price below market | `openbroker limit` |
| Sell at specific price above market | `openbroker limit` |
| Stop loss (exit if price drops) | `openbroker trigger --type sl` |
| Take profit (exit at target) | `openbroker trigger --type tp` |
| Add TP/SL to existing position | `openbroker tpsl` |

## Common Arguments

All commands support `--dry` for dry run (preview without executing).

| Argument | Description |
|----------|-------------|
| `--coin` | Asset symbol (ETH, BTC, SOL, HYPE, etc.) |
| `--side` | Order direction: `buy` or `sell` |
| `--size` | Order size in base asset |
| `--price` | Limit price |
| `--dry` | Preview without executing |
| `--help` | Show command help |

### Order Arguments
| Argument | Description |
|----------|-------------|
| `--trigger` | Trigger price (for trigger orders) |
| `--type` | Trigger type: `tp` or `sl` |
| `--slippage` | Slippage tolerance in bps (for market orders) |
| `--tif` | Time in force: GTC, IOC, ALO |
| `--reduce` | Reduce-only order |

### TP/SL Price Formats
| Format | Example | Description |
|--------|---------|-------------|
| Absolute | `--tp 40` | Price of $40 |
| Percentage up | `--tp +10%` | 10% above entry |
| Percentage down | `--sl -5%` | 5% below entry |
| Entry price | `--sl entry` | Breakeven stop |

## Configuration

Config is loaded from (in priority order):
1. Environment variables
2. `.env` in current directory
3. `~/.openbroker/.env` (global config)

Run `openbroker setup` to create the global config interactively.

| Variable | Required | Description |
|----------|----------|-------------|
| `HYPERLIQUID_PRIVATE_KEY` | Yes | Wallet private key (0x...) |
| `HYPERLIQUID_NETWORK` | No | `mainnet` (default) or `testnet` |
| `HYPERLIQUID_ACCOUNT_ADDRESS` | No | Master account address (required for API wallets) |

The builder fee (1 bps / 0.01%) is hardcoded and not configurable.

## OpenClaw Plugin (Optional)

This skill works standalone via Bash — every command above runs through the `openbroker` CLI. For enhanced features, the same `openbroker` npm package also ships as an **OpenClaw plugin** that you can enable alongside this skill.

### What the plugin adds

- **Structured agent tools** (`ob_account`, `ob_buy`, `ob_limit`, etc.) — typed tool calls with proper input schemas instead of Bash strings. The agent gets structured JSON responses.
- **Background position watcher** — polls your Hyperliquid account every 30s and sends webhook alerts when positions open/close, PnL moves significantly, or margin usage gets dangerous.
- **CLI commands** — `openclaw ob status` and `openclaw ob watch` for inspecting the watcher.

### Enable the plugin

The plugin is bundled in the same `openbroker` npm package. To enable it in your OpenClaw config:

```yaml
plugins:
  entries:
    openbroker:
      enabled: true
      config:
        hooksToken: "your-hooks-secret"   # Required for watcher alerts
        watcher:
          enabled: true
          pollIntervalMs: 30000
          pnlChangeThresholdPct: 5
          marginUsageWarningPct: 80
```

The plugin reads wallet credentials from `~/.openbroker/.env` (set up by `openbroker setup`), so you don't need to duplicate `privateKey` in the plugin config unless you want to override.

### Webhook setup for watcher alerts

For position alerts to reach the agent, enable hooks in your gateway config:

```yaml
hooks:
  enabled: true
  token: "your-hooks-secret"   # Must match hooksToken above
```

Without hooks, the watcher still runs and tracks state (accessible via `ob_watcher_status`), but it can't wake the agent.

### Using with or without the plugin

- **Skill only (no plugin):** Use Bash commands (`openbroker buy --coin ETH --size 0.1`). No background monitoring.
- **Skill + plugin:** The agent prefers the `ob_*` tools when available (structured data), falls back to Bash for commands not covered by tools (strategies, scale). Background watcher sends alerts automatically.

## Risk Warning

- Always use `--dry` first to preview orders
- Start with small sizes on testnet (`HYPERLIQUID_NETWORK=testnet`)
- Monitor positions and liquidation prices
- Use `--reduce` for closing positions only
