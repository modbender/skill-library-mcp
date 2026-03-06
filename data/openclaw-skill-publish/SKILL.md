---
name: probtrade
version: 2.0.4
description: "Polymarket prediction markets: analytics, trading, hot markets, price movements, top traders, and market search. Powered by prob.trade."
homepage: https://app.prob.trade
user-invocable: true
metadata: {"openclaw":{"requires":{"bins":["python3"],"env":["PROBTRADE_API_KEY","PROBTRADE_API_SECRET"],"config":["~/.openclaw/skills/probtrade/config.yaml"]},"emoji":"📊","install":[{"id":"python3","kind":"brew","formula":"python@3","bins":["python3"],"label":"Install Python 3","os":["darwin","linux"]}]}}
---

# prob.trade — Polymarket Analytics & Trading

Get real-time prediction market intelligence and trade on Polymarket from [prob.trade](https://app.prob.trade). Browse trending markets, discover price movements, see what top traders are doing, and place orders.

## Setup (required for all commands)

All commands require a prob.trade API key. Configure it in `~/.openclaw/skills/probtrade/config.yaml`:
```yaml
api_key: "ptk_live_..."
api_secret: "pts_..."
```
Generate keys at https://app.prob.trade (Settings → API Keys). Free account required.

## Analytics Commands

Use the scripts below to query the prob.trade Public API.

### Market Overview
Get a quick snapshot of the prediction market landscape:
```bash
python3 {baseDir}/scripts/probtrade.py overview
```
Returns: market stats, top 10 hot markets, breaking price movements, and newest markets.

### Hot Markets
See the most actively traded markets right now:
```bash
python3 {baseDir}/scripts/probtrade.py hot [--limit N]
```

### Breaking Markets
Markets with the biggest price movements in the last 24 hours:
```bash
python3 {baseDir}/scripts/probtrade.py breaking [--limit N]
```

### New Markets
Recently created prediction markets:
```bash
python3 {baseDir}/scripts/probtrade.py new [--limit N] [--days N]
```

### Search Markets
Find markets about a specific topic:
```bash
python3 {baseDir}/scripts/probtrade.py search "Trump" [--limit N]
```

### Market Details
Get detailed information about a specific market by its condition ID:
```bash
python3 {baseDir}/scripts/probtrade.py market <condition_id>
```

### Market Statistics
Category breakdown and overall market counts:
```bash
python3 {baseDir}/scripts/probtrade.py stats
```

### Top Traders
See the most profitable prediction market traders:
```bash
python3 {baseDir}/scripts/probtrade.py traders [--limit N] [--sort pnl|roi|volume|winRate] [--period all|30d|7d|24h]
```

## Trading Commands

Trade on Polymarket using the same API key configured above.

### Place Order
```bash
python3 {baseDir}/scripts/probtrade.py order --market <condition_id> --side BUY --outcome Yes --type LIMIT --price 0.55 --amount 10
```

### Cancel Order
```bash
python3 {baseDir}/scripts/probtrade.py cancel --order-id <orderId>
```

### View Positions
```bash
python3 {baseDir}/scripts/probtrade.py positions
```

### View Balance
```bash
python3 {baseDir}/scripts/probtrade.py balance
```

### View Open Orders
```bash
python3 {baseDir}/scripts/probtrade.py orders
```

Security: API secret never leaves your machine. Only HMAC signatures are sent. No withdraw/transfer endpoints exist.

## Output Format

All commands output structured JSON for easy parsing by AI agents. Key fields:

- **condition_id**: Unique market identifier (use for trading on Polymarket)
- **question**: The prediction market question
- **tokens**: Current prices for Yes/No outcomes
- **volume_24hr**: Trading volume in last 24 hours
- **liquidity**: Available liquidity for trading
- **end_date_iso**: When the market resolves

## Links

- Dashboard: https://app.prob.trade
- Market page: `https://app.prob.trade/markets/{condition_id}`
- Trader profile: `https://app.prob.trade/traders/{address}`
- Public API: https://api.prob.trade/api/public/overview
- Trading API docs: https://prob.trade/docs/public-api
- ClawHub: https://clawhub.ai/vlprosvirkin/prob-trade-polymarket-analytics
