---
name: prediction-bridge
description: Query live prediction market data from the Prediction Bridge API. Use when the user asks about prediction markets, event odds, market prices, whale trades, trader analytics, or news related to prediction markets. Provides semantic search across 9+ platforms (Polymarket, Kalshi, Limitless, Probable, PredictFun, SxBet, Myriad, PancakeSwap), on-chain whale trade monitoring, Smart PnL analytics, and trader leaderboards. Run the bundled Python script to fetch real-time data.
---

# Prediction Bridge

Query live prediction market data across 9+ platforms via the Prediction Bridge API.

## How to Use

Run the script at `scripts/prediction_bridge.py` with the appropriate command. It uses only Python stdlib — no pip install needed.

```bash
python scripts/prediction_bridge.py <command> [args] [options]
```

## Commands

### Search events by meaning

```bash
python scripts/prediction_bridge.py search "trump tariff" --limit 5
python scripts/prediction_bridge.py search "will bitcoin hit 100k"
python scripts/prediction_bridge.py search "2028 election" --include-inactive
```

### Browse events

```bash
python scripts/prediction_bridge.py events --limit 10
python scripts/prediction_bridge.py events --source polymarket --limit 5
python scripts/prediction_bridge.py events --status active --category "Crypto"
python scripts/prediction_bridge.py event 1839                          # detail by ID
```

### News matched to events

```bash
python scripts/prediction_bridge.py news --limit 10
```

### Platform statistics

```bash
python scripts/prediction_bridge.py stats
```

### Whale trades (on-chain large trades)

```bash
python scripts/prediction_bridge.py whale-trades --limit 10
python scripts/prediction_bridge.py whale-trades --address 0x1234...    # by wallet
python scripts/prediction_bridge.py whale-trades --min-value 50000      # min USD
python scripts/prediction_bridge.py whale-trades --only-alerts          # above alert threshold
python scripts/prediction_bridge.py whale-trades --event-slug "us-election"
```

### Market price data

```bash
python scripts/prediction_bridge.py market-history polymarket 18454
python scripts/prediction_bridge.py market-candles polymarket 18454 --interval 1h
```

### Analytics

```bash
python scripts/prediction_bridge.py smart-pnl 18454                    # market Smart PnL
python scripts/prediction_bridge.py top-holders 18454                   # top holders breakdown
python scripts/prediction_bridge.py leaderboard --limit 20              # top traders
python scripts/prediction_bridge.py user-summary 0x1234...              # wallet portfolio
python scripts/prediction_bridge.py user-pnl 0x1234...                  # realized PnL
```

### Other

```bash
python scripts/prediction_bridge.py languages                           # supported languages
python scripts/prediction_bridge.py --help                              # full help
```

## Typical Workflows

**"What are the hottest prediction markets right now?"**
→ `events --limit 10` (sorted by volume)

**"Find markets about AI regulation"**
→ `search "AI regulation"` (semantic search)

**"Show me recent whale trades on Polymarket"**
→ `whale-trades --limit 10`

**"Who are the top traders and what are they betting on?"**
→ `leaderboard --limit 10`, then `user-summary <address>` for details

**"What's the Smart PnL signal for a specific market?"**
→ Get market ID from `event <id>`, then `smart-pnl <market_id>`

**"Any news moving prediction markets today?"**
→ `news --limit 10`

## Environment

Set `PREDICTION_BRIDGE_URL` to override the default API base URL:

```bash
export PREDICTION_BRIDGE_URL=https://prediction-bridge.onrender.com
```
