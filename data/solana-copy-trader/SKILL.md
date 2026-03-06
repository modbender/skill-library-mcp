---
name: solana-copy-trader
description: >
  Solana whale copy trading bot. Track any wallet, copy trades in real-time via Jupiter + Pump.fun APIs,
  with paper trading simulation and live execution. Use when user wants to copy trade a Solana wallet,
  track whale transactions, scan for arbitrage opportunities, monitor pump.fun token launches,
  or set up an autonomous Solana trading bot.
---

# Solana Copy Trader

Real-time Solana whale copy trader using Helius WebSocket + Jupiter API + Pump.fun.

## Quick Start

```bash
cd solana-bot
npm install
cp .env.example .env  # fill in keys
node index.js copy    # paper mode (safe)
node index.js watch   # whale tracker only
node index.js scan    # arb scanner
```

## Modes

| Mode | Command | Description |
|------|---------|-------------|
| `copy` | `node index.js copy 0.01` | Copy whale trades (paper by default) |
| `watch` | `node index.js watch` | Watch whale txs live |
| `scan` | `node index.js scan` | Scan arb opportunities |
| `paper` | `node index.js paper` | Full paper trading sim |
| `analyze` | `node index.js analyze` | Wallet pattern analysis |
| `safety` | `node index.js safety <mint>` | Token rug check |

## .env Setup

```env
PRIVATE_KEY=your_base58_private_key   # leave blank for watch-only
RPC_URL=https://mainnet.helius-rpc.com/?api-key=YOUR_KEY
HELIUS_API_KEY=your_helius_key        # free at dev.helius.xyz
BOT_TOKEN=telegram_bot_token          # for alerts
CHAT_ID=your_telegram_chat_id
MAX_TRADE_SOL=0.01                    # safety limit per trade
MIN_PROFIT_PCT=0.5
```

## Architecture

```
Helius WebSocket → whale tx detected
        ↓
parseTransaction() → decode token changes
        ↓
Jupiter quote → can we route? 
        ↓ (if no route)
Pump.fun DAS check → bonding curve token?
        ↓
safety check → price impact < 50%?
        ↓
paper: log trade | live: executeRealSwap()
        ↓
Telegram alert sent
```

## Key Files

- `src/copy_trade.js` — Core copy trader engine
- `src/wallet_tracker.js` — Helius WebSocket + tx parsing
- `src/arbitrage.js` — Jupiter arb scanner
- `src/pumpfun.js` — Pump.fun token metadata via Helius DAS
- `src/sniper.js` — New token sniper (paper mode)
- `src/config.js` — Wallet + connection setup
- `src/alerts.js` — Telegram notifications

## Live → Paper Switch

In `copy_trade.js` `startCopyTrader()`:
```js
paper: true   // paper mode (safe, no real money)
paper: false  // LIVE mode — real trades
```

Or use `index.js` mode `copy` (always paper) vs direct `startCopyTrader({ paper: false })`.

## Safety Limits

- `MAX_TRADE_SOL` — max SOL per trade (default 0.01)
- `maxPositions: 3` — max open positions at once
- `priceImpact > 50%` → skip (rug protection)
- Pump safety score < 40 → skip

## Whale to Copy

Default whale: `AgmLJBMDCqWynYnQiPCuj9ewsNNsBJXyzoUhD9LJzN51`
- Confirmed MEV bot: 477 SOL, 172K txs/day, $40K/day
- Change in `src/copy_trade.js` → `WHALE` constant

## Requirements

- Node.js 18+
- Free Helius API key (1000 req/day free tier)
- Solana wallet (optional — watch-only without)
- Telegram bot (optional — for alerts)

See `references/api-setup.md` for getting free API keys.
See `references/trading-concepts.md` for how Solana MEV/arb works.
