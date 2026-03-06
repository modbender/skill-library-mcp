---
name: polymarket-whale-copier
version: 1.0.0
description: Copy trade winning Polymarket wallets automatically. Track whale wallets, mirror their bets at configurable percentages, with built-in risk management. No API keys needed.
author: nix
tags: [polymarket, trading, copy-trading, whale, prediction-markets, automation]
---

# 🐋 Polymarket Whale Copier

**Automatically copy trade winning Polymarket wallets.**

Track any wallet, mirror their bets, profit from their alpha.

## Features

- 🎯 **Copy Any Wallet** — Just paste their address
- 📊 **Configurable Size** — Copy 1-100% of their position
- 🛡️ **Risk Controls** — Min/max trade limits, BUY-only mode
- 📝 **Full Logging** — Every trade documented
- 🔄 **Auto-Redemption** — Claims winning positions automatically
- 💰 **No API Keys** — Uses public Polymarket APIs

## Quick Start

```bash
# 1. Set your Polymarket private key
export POLYMARKET_KEY="0xYourPrivateKey"

# 2. Run the copier
python3 scripts/copy_trader.py --target 0xWhaleWallet --percent 10
```

## Configuration

Edit `config.json`:

```json
{
  "target_wallet": "0x...",
  "copy_percent": 10,
  "min_trade_usd": 5,
  "max_trade_usd": 50,
  "buy_only": true,
  "check_interval_sec": 60,
  "dry_run": false
}
```

## Commands

```bash
# Start copy trading (background)
./scripts/start.sh

# Check status
./scripts/status.sh

# Stop trading
./scripts/stop.sh

# View recent trades
./scripts/logs.sh

# Auto-redeem winning positions
python3 scripts/auto_redeem.py
```

## Finding Whale Wallets

1. Go to [Polymarket Leaderboard](https://polymarket.com/leaderboard)
2. Click on top traders
3. Copy their wallet address from the URL
4. Paste into config or `--target` flag

## Risk Management

| Setting | Default | Description |
|---------|---------|-------------|
| `copy_percent` | 10% | % of whale's position to copy |
| `min_trade_usd` | $5 | Skip trades smaller than this |
| `max_trade_usd` | $50 | Cap maximum trade size |
| `buy_only` | true | Only copy BUYs (safer) |

## How It Works

1. **Monitor** — Polls target wallet every 60 seconds
2. **Detect** — Identifies new trades via Polymarket API
3. **Filter** — Applies your risk settings
4. **Execute** — Places matching orders on your account
5. **Log** — Records everything for analysis

## Example Output

```
🚀 POLYMARKET COPY TRADER STARTING
🎯 Target: 0x4ffe49ba...609f71
📊 Copy: 10% | Limits: $5-$50

🔄 Monitoring cycle #42
📈 New trade detected!
   Whale: BUY 500 shares @ $0.35 = $175
   Copying: BUY 50 shares @ $0.35 = $17.50
✅ Order placed: #123456789
```

## Requirements

- Python 3.8+
- Polymarket account with USDC
- Private key (for signing trades)

## Safety Notes

⚠️ **Never share your private key**
⚠️ **Start with small amounts**
⚠️ **Use dry_run mode first**
⚠️ **Past performance ≠ future results**

## Support

Issues? Questions? Open a GitHub issue or find us on Discord.

---

*Built by Nix 🔥 | Not financial advice*
