---
name: polymarket-pro
description: Use the official Polymarket CLI to browse markets, trade on CLOB, manage positions, and analyze on-chain data. Features include market search, order book analysis, limit/market orders, position management, and advanced CTF operations.
version: 1.0.0
author: Liwa
requirements:
  - polymarket CLI (brew install or shell script)
  - jq (for JSON processing)
  - wallet (private key or created via CLI)
tags:
  - polymarket
  - prediction-markets
  - trading
  - cli
  - defi
  - crypto
---

# Polymarket CLI Skill

This skill enables you to interact with Polymarket prediction markets using the official `polymarket` CLI tool. Unlike Polyclaw (which manages autonomous trading), this skill gives you direct, granular control over trading, research, and portfolio management.

## Installation

### Quick Install (macOS/Linux)

```bash
brew tap Polymarket/polymarket-cli https://github.com/Polymarket/polymarket-cli
brew install polymarket
```

### Shell Script (All Platforms)

```bash
curl -sSL https://raw.githubusercontent.com/Polymarket/polymarket-cli/main/install.sh | sh
```

### Verify Installation

```bash
polymarket --version
polymarket --help
```

---

## Wallet Setup

### Three Ways to Provide Private Key

1. **CLI flag**: `--private-key 0xabc...`
2. **Environment variable**: `export POLYMARKET_PRIVATE_KEY=0xabc...`
3. **Config file**: `~/.config/polymarket/config.json`

### Create New Wallet

```bash
# Generate new wallet (saves to config)
polymarket wallet create

# Or force overwrite existing
polymarket wallet create --force

# Import existing private key
polymarket wallet import 0xabc123...

# Check wallet address
polymarket wallet address

# Full wallet info
polymarket wallet show
```

### Approvals (Required Before Trading)

```bash
# Check current approval status
polymarket approve check
polymarket approve check 0xYOUR_ADDRESS

# Set approvals (sends 6 on-chain txs, needs MATIC for gas)
polymarket approve set
```

---

## Output Formats

Every command supports `-o json` or `-o table` (default):

```bash
# Human-readable table
polymarket markets list --limit 3

# JSON for scripts/agents
polymarket -o json markets list --limit 3

# Pipe to jq for specific fields
polymarket -o json markets search "bitcoin" | jq '.[].question'
```

---

## Market Research

### Browse Markets

```bash
# List markets with filters
polymarket markets list --limit 10
polymarket markets list --active true --order volume_num
polymarket markets list --closed false --limit 50 --offset 25

# Get specific market by ID or slug
polymarket markets get 12345
polymarket markets get will-trump-win-the-2024-election

# Search markets
polymarket markets search "bitcoin" --limit 5
polymarket markets search "election" --limit 10
```

### Events (Grouped Markets)

```bash
# List events
polymarket events list --limit 10
polymarket events list --tag politics --active true

# Get specific event
polymarket events get 500

# Get tags for event
polymarket events tags 500
```

### Tags & Series

```bash
# Browse tags
polymarket tags list
polymarket tags get politics
polymarket tags related politics

# Series (recurring events)
polymarket series list --limit 10
polymarket series get 42
```

### Order Book Analysis (No Wallet Needed)

```bash
# Check price
polymarket clob price TOKEN_ID --side buy
polymarket clob midpoint TOKEN_ID
polymarket clob spread TOKEN_ID

# Batch prices
polymarket clob batch-prices "TOKEN1,TOKEN2" --side buy
polymarket clob midpoints "TOKEN1,TOKEN2"

# Order book
polymarket clob book TOKEN_ID

# Last trade
polymarket clob last-trade TOKEN_ID

# Price history
polymarket clob price-history TOKEN_ID --interval 1d --fidelity 30

# Market metadata
polymarket clob tick-size TOKEN_ID
polymarket clob fee-rate TOKEN_ID
polymarket clob neg-risk TOKEN_ID
```

**Price history intervals**: `1m`, `1h`, `6h`, `1d`, `1w`, `max`

---

## Trading (CLOB)

### Place Orders

```bash
# Limit order (buy 10 shares at $0.50)
polymarket clob create-order \
  --token TOKEN_ID \
  --side buy --price 0.50 --size 10

# Market order (buy $5 worth)
polymarket clob market-order \
  --token TOKEN_ID \
  --side buy --amount 5

# Post multiple orders at once
polymarket clob post-orders \
  --tokens "TOKEN1,TOKEN2" \
  --side buy \
  --prices "0.40,0.60" \
  --sizes "10,10"

# Order types: GTC (default), FOK, GTD, FAK
# Add --post-only for limit orders
```

### Manage Orders

```bash
# View your orders
polymarket clob orders
polymarket clob orders --market 0xCONDITION...

# Get specific order
polymarket clob order ORDER_ID

# Cancel orders
polymarket clob cancel ORDER_ID
polymarket clob cancel-orders "ORDER1,ORDER2"
polymarket clob cancel-market --market 0xCONDITION...
polymarket clob cancel-all
```

### Check Balance & Trades

```bash
# Collateral balance (USDC)
polymarket clob balance --asset-type collateral

# Conditional token balance
polymarket clob balance --asset-type conditional --token TOKEN_ID

# Update balance cache
polymarket clob update-balance --asset-type collateral

# Your trades
polymarket clob trades

# Order details with scoring
polymarket clob order-scoring ORDER_ID
```

---

## On-Chain Data

### Portfolio & Positions

```bash
# Current positions
polymarket data positions 0xWALLET_ADDRESS
polymarket data closed-positions 0xWALLET_ADDRESS

# Portfolio value
polymarket data value 0xWALLET_ADDRESS

# Trade history
polymarket data trades 0xWALLET_ADDRESS --limit 50

# Activity summary
polymarket data activity 0xWALLET_ADDRESS
```

### Market Data

```bash
# Token holders
polymarket data holders 0xCONDITION_ID

# Open interest
polymarket data open-interest 0xCONDITION_ID

# Volume by event
polymarket data volume EVENT_ID

# Leaderboards
polymarket data leaderboard --period month --order-by pnl --limit 10
polymarket data builder-leaderboard --period week
polymarket data builder-volume --period month
```

---

## CTF Operations

Conditional Token Framework operations for advanced users.

```bash
# Split USDC into YES/NO tokens
polymarket ctf split --condition 0xCONDITION... --amount 10

# Merge tokens back to USDC
polymarket ctf merge --condition 0xCONDITION... --amount 10

# Redeem winning tokens after resolution
polymarket ctf redeem --condition 0xCONDITION...

# Redeem neg-risk positions
polymarket ctf redeem-neg-risk --condition 0xCONDITION... --amounts "10,5"

# Calculate condition IDs (read-only)
polymarket ctf condition-id --oracle 0xORACLE... --question 0xQUESTION... --outcomes 2
polymarket ctf collection-id --condition 0xCONDITION... --index-set 1
polymarket ctf position-id --collection 0xCOLLECTION...
```

`--amount` is in USDC (e.g., `10` = $10). Default `--partition` is binary (`1,2`).

---

## Bridge (Deposit Funds)

```bash
# Get deposit addresses (EVM, Solana, Bitcoin)
polymarket bridge deposit 0xWALLET_ADDRESS

# Supported assets
polymarket bridge supported-assets

# Check deposit status
polymarket bridge status 0xDEPOSIT_ADDRESS
```

---

## Rewards & API

```bash
# Check rewards
polymarket clob rewards --date 2024-06-15
polymarket clob earnings --date 2024-06-15
polymarket clob reward-percentages
polymarket clob current-rewards
polymarket clob market-reward 0xCONDITION...

# API key management
polymarket clob api-keys
polymarket clob create-api-key
polymarket clob delete-api-key

# Account status
polymarket clob account-status
polymarket clob notifications
```

---

## Interactive Shell

```bash
# Enter interactive mode
polymarket shell

# Example session:
# polymarket> markets list --limit 3
# polymarket> clob book 48331043336612883...
# polymarket> exit
```

Supports command history - useful for exploratory analysis.

---

## Common Workflows

### Research → Trade Flow

```bash
# 1. Find interesting markets
polymarket markets search "bitcoin" --limit 5

# 2. Deep dive on a market
polymarket markets get bitcoin-above-100k

# 3. Check order book
polymarket clob book TOKEN_ID

# 4. Check price history
polymarket clob price-history TOKEN_ID --interval 1d

# 5. Place trade
polymarket clob market-order --token TOKEN_ID --side buy --amount 10
```

### Monitor Portfolio

```bash
# Check positions
polymarket data positions 0xYOUR_ADDRESS
polymarket data value 0xYOUR_ADDRESS

# Check open orders
polymarket clob orders

# Check recent trades
polymarket clob trades

# Check PnL via leaderboard
polymarket data leaderboard --period month --order-by pnl
```

### Arbitrage Detection

```bash
# Batch check prices across markets
polymarket -o json markets list --limit 50 | jq '.[] | select(.volumeNum > 10000) | {question: .question, prices: .outcomePrices}'

# Check spread
polymarket clob spread TOKEN_ID

# Check multiple midpoints
polymarket clob midpoints "TOKEN1,TOKEN2,TOKEN3"
```

---

## Error Handling

| Situation | Action |
|-----------|--------|
| API error | Check `polymarket status` for API health |
| Insufficient balance | Check `polymarket clob balance --asset-type collateral` |
| Approval needed | Run `polymarket approve set` (needs MATIC) |
| Order rejected | Check order parameters, slippage |
| Wallet not configured | Run `polymarket wallet create` or set private key |

---

## Quick Reference

```bash
# Help
polymarket --help
polymarket markets --help
polymarket clob --help

# Status
polymarket status
polymarket clob ok
polymarket wallet show

# Setup
polymarket setup              # Guided wizard
polymarket wallet create     # New wallet
polymarket approve set        # Approve contracts

# Markets
polymarket markets list --limit 10
polymarket markets search "keyword"
polymarket markets get MARKET_ID

# Trading
polymarket clob create-order --token ID --side buy --price 0.50 --size 10
polymarket clob market-order --token ID --side buy --amount 5
polymarket clob cancel-all

# Portfolio
polymarket clob balance --asset-type collateral
polymarket data positions 0xADDRESS
polymarket clob trades

# Data
polymarket clob price TOKEN_ID --side buy
polymarket clob book TOKEN_ID
polymarket data leaderboard --period month
```

---

## Advanced Tips

1. **Use JSON output for automation**: `-o json` enables scripting with `jq`
2. **Batch operations**: Use comma-separated lists for efficiency
3. **Price history for analysis**: Use `--interval 1d --fidelity 30` for daily candles
4. **Track maker rewards**: Check `clob order-scoring` for your orders
5. **CTF for larger trades**: Split/merge can be more capital efficient than CLOB for large sizes

---

## Differences from Polyclaw

| Feature | Polyclaw | Polymarket CLI |
|---------|----------|----------------|
| Trading mode | Autonomous agent | Manual/direct |
| Token creation | Yes (via Clanker) | No |
| Market discovery | AI-powered | Manual search |
| Social posting | Auto | Manual |
| Order book access | Limited | Full |
| CTF operations | No | Yes |
| Rewards tracking | Dashboard | Full API |
| Control level | High-level | Low-level |

**Use Polyclaw** when you want autonomous trading with a performance token.
**Use Polymarket CLI** when you want direct control, arbitrage, or custom strategies.
