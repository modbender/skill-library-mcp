---
name: Polymarket Trade Agent Skill
description: A fully functional Polymarket trading agent that can research
  markets, analyze opportunities, and execute trades.
---

# Polymarket Trade Agent Skill

## Overview
A fully functional Polymarket trading agent that can research markets, analyze opportunities, and execute trades.

## Configuration Required
- **POLYMARKET_PRIVATE_KEY**: Your Polygon wallet private key (starts with 0x...)
- **POLYMARKET_FUNDER_ADDRESS**: Optional funder address for transfers (starts with 0x...)
- This key controls your Polymarket account and must have USDC balance

## Setup

### Step 1: Get Your Private Key
1. Go to [polymarket.com](https://polymarket.com)
2. Connect your wallet (MetaMask)
3. Go to Settings → API Keys or find your wallet address
4. Get the private key for the wallet that has USDC on Polymarket

### Step 2: Configure
```bash
export POLYMARKET_PRIVATE_KEY=0xYOUR_PRIVATE_KEY_HERE
```

### Step 3: Check Balance
```bash
polymarket balance
```

## Commands

### Research & Analysis
- `polymarket markets` - List top markets
- `polymarket search <query>` - Search markets
- `polymarket analyze <market_id>` - Get AI analysis

### Trading
- `polymarket balance` - Check USDC balance
- `polymarket buy <token_id> <price> <size>` - Place buy order
- `polymarket sell <token_id> <price> <size>` - Place sell order
- `polymarket positions` - View open positions

### Utility
- `polymarket doctor` - Health check
- `polymarket address` - Show your wallet address

## Trading Strategy

### Finding Opportunities
1. Run `polymarket markets` to see trending markets
2. Research the underlying events via web search
3. Compare market odds to your own probability estimate
4. Calculate edge: `Edge = Your_Probability - Market_Probability`

### Example Analysis
```
Market: "Will Iran regime fall by June 30?"
Current Price: Yes = $0.42 (42% implied)
My Research: Given Khamenei killed, power vacuum exists
My Estimate: 60% probability
Edge: +18% → BUY YES
```

### Position Sizing
- Never risk more than 5% of bankroll on single trade
- Recommended: 2-5% per trade
- Diversify across uncorrelated events

## Risk Rules
1. Always verify balance before trading
2. Start with small positions (test the waters)
3. Don't bet more than you can afford to lose
4. Set mental stop-loss at 50% of position

## Notes
- All trades are on Polygon network
- Minimum trade size typically $1
- Fees are small but apply to each trade
