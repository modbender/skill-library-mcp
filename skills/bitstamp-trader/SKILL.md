---
name: bitstamp-trader
description: Safety-first Bitcoin and crypto trading on Bitstamp via CLI. Use when the user wants to check crypto prices, view account balance, place buy/sell orders, manage open orders, check trade history, or monitor the market on Bitstamp. Supports BTC/USD, ETH/USD, and other pairs. All trades are dry-run by default — live execution requires explicit --live flag. Safety guardrails include max order size, daily volume limits, price deviation checks, and a kill switch.
---

# Bitstamp Trader

Safety-first crypto trading CLI powered by CCXT.

## Quick Reference

All commands use the script at `scripts/bitstamp.py`. Run via:

```bash
python3 scripts/bitstamp.py <command> [options]
```

### Market Data (no auth needed)

```bash
python3 scripts/bitstamp.py ticker                    # BTC/USD price
python3 scripts/bitstamp.py ticker -m ETH/USD         # ETH price
python3 scripts/bitstamp.py orderbook -m BTC/USD -d 5 # Top 5 order book
python3 scripts/bitstamp.py markets --all              # All available pairs
```

### Account (requires API keys)

```bash
python3 scripts/bitstamp.py balance           # Account balances
python3 scripts/bitstamp.py orders            # Open orders
python3 scripts/bitstamp.py trades --limit 10 # Recent trade history
```

### Trading (dry-run by default)

```bash
# Dry-run (simulation)
python3 scripts/bitstamp.py buy 0.001 -m BTC/USD              # Market buy
python3 scripts/bitstamp.py buy 0.001 -m BTC/USD -p 50000     # Limit buy
python3 scripts/bitstamp.py sell 0.5 -m ETH/USD               # Market sell

# Live execution (add --live)
python3 scripts/bitstamp.py buy 0.001 -m BTC/USD --live       # REAL market buy
python3 scripts/bitstamp.py sell 0.5 -m ETH/USD -p 4000 --live
```

### Order Management

```bash
python3 scripts/bitstamp.py cancel --order-id 12345 -m BTC/USD
python3 scripts/bitstamp.py cancel --all   # Cancel all open orders
```

### Safety Controls

```bash
python3 scripts/bitstamp.py kill-switch                         # EMERGENCY STOP
python3 scripts/bitstamp.py kill-switch --status                # Check status
python3 scripts/bitstamp.py kill-switch --deactivate            # Resume trading
python3 scripts/bitstamp.py config                              # View safety limits
python3 scripts/bitstamp.py config --set max_order_size_usd=200 # Adjust limits
python3 scripts/bitstamp.py audit --limit 30                    # View audit log
```

## Setup

1. Set API keys as environment variables:
   ```bash
   export BITSTAMP_API_KEY="your-key"
   export BITSTAMP_API_SECRET="your-secret"
   ```

2. On Bitstamp, create an API key with **Orders** permission only (NO Withdrawals). Enable **IP whitelisting**.

3. Test with: `python3 scripts/bitstamp.py ticker`

## Safety Details

See [references/safety.md](references/safety.md) for full safety architecture:
- Dry-run default, kill switch, max order size, daily limits, price sanity checks

## API Details

See [references/api-reference.md](references/api-reference.md) for Bitstamp API specifics, permissions, and rate limits.

## Important Rules

- **NEVER place live orders without explicit user confirmation.** Always dry-run first.
- **NEVER store API keys in files.** Use environment variables only.
- **When user says "buy" or "sell" without --live, always run as dry-run** and show what WOULD happen.
- **For live trades, always show the dry-run result first**, then ask for confirmation before adding --live.
- **If anything seems wrong** (price spike, unusual volume, API errors), activate the kill switch.
- **Log everything.** Check audit log when debugging issues.
