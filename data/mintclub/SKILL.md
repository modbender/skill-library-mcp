---
name: Mint Club V2 — Agent Skill
description: Interact with Mint Club V2 bonding curve tokens on Base using the mc CLI.
---

# Mint Club V2 — Agent Skill

Interact with Mint Club V2 bonding curve tokens on Base using the `mc` CLI.

## Setup

```bash
npm install -g mint.club-cli
```

Set your private key:
```bash
mc wallet --set-private-key 0x...
# Or export PRIVATE_KEY=0x...
```

## Commands

### Read Operations (no key needed)

```bash
mc info <token>          # Token info (supply, reserve, price, curve)
mc price <token>         # Price in reserve + USD
mc wallet                # Wallet address and balances
```

### Trading

```bash
# Buy/sell via bonding curve (reserve token)
mc buy <token> -a <amount>                    # Buy tokens
mc sell <token> -a <amount>                   # Sell tokens

# Zap: buy/sell with any token (auto-routes via Uniswap)
mc zap-buy <token> -i ETH -a 0.01            # Buy with ETH
mc zap-sell <token> -a 100 -o USDC           # Sell for USDC

# Direct Uniswap swap (any pair, V3 + V4)
mc swap -i ETH -o HUNT -a 0.001              # Swap tokens
mc swap -i HUNT -o USDC -a 100 -s 0.5        # Custom slippage
```

### Create Token

```bash
mc create -n "My Token" -s MYT -r HUNT -x 1000000 \
  --curve exponential --initial-price 0.01 --final-price 100
```

Curve presets: `linear`, `exponential`, `logarithmic`, `flat`

### Transfer

```bash
mc send <address> -a 0.01                     # Send ETH
mc send <address> -a 100 -t HUNT              # Send ERC-20
```

## Token Resolution

Use addresses or known symbols: `ETH`, `WETH`, `USDC`, `HUNT`, `MT`

## Environment

| Variable | Description |
|----------|-------------|
| `PRIVATE_KEY` | Wallet private key (or use `~/.mintclub/.env`) |

## Notes

- All operations are on **Base** (chain 8453)
- Default slippage: 1%
- Default royalty on create: 1% mint + 1% burn
- Token addresses are auto-saved to `~/.mintclub/tokens.json`
- Community: https://onchat.sebayaki.com/mintclub
