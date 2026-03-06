---
name: nofx
description: NOFX AI Trading OS integration - crypto market data, AI trading signals, strategy management, trader control, and automated reporting. Use when working with NOFX platform (nofxai.com, nofxos.ai) for crypto trading, market analysis, AI500/AI300 signals, fund flow tracking, OI monitoring, strategy creation, trader management, backtesting, or AI debate arena.
---

# NOFX AI Trading Skill

Integrate with NOFX - the open-source AI-powered crypto trading operating system.

## Quick Reference

| Resource | URL |
|----------|-----|
| Web Dashboard | https://nofxai.com |
| Data API | https://nofxos.ai |
| API Docs | https://nofxos.ai/api-docs |
| GitHub | https://github.com/NoFxAiOS/nofx |

## Deployment

For installation and deployment instructions, see `references/deployment.md`:
- One-click install (Linux/macOS/Docker)
- Windows installation (Docker Desktop / WSL2)
- Railway cloud deployment
- Manual installation for developers
- Server deployment with HTTPS

## Supported Exchanges

For exchange registration links (with fee discounts) and API setup, see `references/exchanges.md`:

**CEX**: Binance, Bybit, OKX, Bitget, KuCoin, Gate.io
**DEX**: Hyperliquid, Aster DEX, Lighter

**AI Models**: DeepSeek, Qwen, OpenAI, Claude, Gemini, Grok, Kimi

## Configuration

Store credentials in workspace `skills/nofx/config.json`:

```json
{
  "api_key": "cm_xxxxxx",
  "web_email": "user@example.com",
  "browser_profile": "clawd"
}
```

## 1. Market Data (API)

Base URL: `https://nofxos.ai`
Auth: `?auth=API_KEY` or `Authorization: Bearer API_KEY`

### AI Signals

```bash
# AI500 - High potential coins (score > 70)
curl "https://nofxos.ai/api/ai500/list?auth=$KEY"

# AI300 - Quantitative flow signals (S/A/B levels)
curl "https://nofxos.ai/api/ai300/list?auth=$KEY&limit=10"

# Single coin AI analysis
curl "https://nofxos.ai/api/ai500/{symbol}?auth=$KEY"
```

### Fund Flow

```bash
# Institution inflow ranking
curl "https://nofxos.ai/api/netflow/top-ranking?auth=$KEY&limit=10&duration=1h&type=institution"

# Outflow ranking
curl "https://nofxos.ai/api/netflow/low-ranking?auth=$KEY&limit=10&duration=1h&type=institution"
```

### Open Interest

```bash
# OI increase ranking
curl "https://nofxos.ai/api/oi/top-ranking?auth=$KEY&limit=10&duration=1h"

# OI decrease ranking
curl "https://nofxos.ai/api/oi/low-ranking?auth=$KEY&limit=10&duration=1h"

# OI market cap ranking
curl "https://nofxos.ai/api/oi-cap/ranking?auth=$KEY&limit=10"
```

### Price & Rates

```bash
# Price ranking (gainers/losers)
curl "https://nofxos.ai/api/price/ranking?auth=$KEY&duration=1h"

# Funding rate top (crowded longs)
curl "https://nofxos.ai/api/funding-rate/top?auth=$KEY&limit=10"

# Funding rate low (crowded shorts)
curl "https://nofxos.ai/api/funding-rate/low?auth=$KEY&limit=10"

# Long-short ratio anomalies
curl "https://nofxos.ai/api/long-short/list?auth=$KEY&limit=10"
```

### Single Coin Data

```bash
# Comprehensive coin data
curl "https://nofxos.ai/api/coin/{symbol}?auth=$KEY&include=all"

# Order book heatmap
curl "https://nofxos.ai/api/heatmap/future/{symbol}?auth=$KEY"
```

Duration options: `1m, 5m, 15m, 30m, 1h, 4h, 8h, 12h, 24h, 2d, 3d, 5d, 7d`

## 2. Strategy Management (Browser)

Use browser automation on https://nofxai.com/strategy

### Strategy Structure

```json
{
  "strategy_type": "ai_trading",
  "language": "en",
  "coin_source": {
    "source_type": "ai500|static|oi_top|oi_low|mixed",
    "static_coins": ["BTC", "ETH"],
    "use_ai500": true,
    "ai500_limit": 10
  },
  "indicators": {
    "enable_ema": true,
    "enable_rsi": true,
    "enable_atr": true,
    "enable_boll": true,
    "enable_oi": true,
    "enable_funding_rate": true,
    "enable_quant_data": true,
    "nofxos_api_key": "cm_xxx"
  },
  "risk_control": {
    "max_position_pct": 10,
    "stop_loss_pct": 3,
    "take_profit_pct": 5
  },
  "prompt_sections": {
    "role_definition": "...",
    "entry_standards": "...",
    "decision_process": "..."
  }
}
```

### Natural Language Strategy Creation

When user describes a strategy in natural language:
1. Parse requirements (coins, indicators, entry/exit rules, risk)
2. Generate StrategyConfig JSON
3. Navigate to Strategy Studio
4. Create new strategy and fill in fields
5. Save and activate

## 3. Trader Management (Browser)

Use browser automation on https://nofxai.com/traders

### Actions

- **List**: Navigate to /traders, parse trader list
- **Create**: Click "Create Trader", select model/exchange/strategy
- **Start/Stop**: Click Start/Stop button on trader card
- **View**: Click "View" for details and logs

### Trader Config

```
Model: claude|deepseek|gpt|gemini|grok|kimi|qwen
Exchange: binance|bybit|okx|bitget|kucoin|gate|hyperliquid|aster|lighter
Strategy: Select from strategy list
```

## 4. Dashboard (Browser)

Navigate to https://nofxai.com/dashboard

### Available Data

- Account equity and balance
- Total P/L (absolute and percentage)
- Current positions
- Equity curve chart
- Trade history
- AI decision logs

## 5. Arena - AI Debate (Browser)

Navigate to https://nofxai.com/debate

### Create Debate

1. Click "New Debate"
2. Select symbol
3. Select AI models and roles:
   - Bull: Finds long opportunities
   - Bear: Finds short opportunities  
   - Analyst: Neutral analysis
4. Run debate rounds
5. Get consensus recommendation

## 6. Backtest (Browser)

Navigate to https://nofxai.com/backtest

### Run Backtest

1. Select AI model
2. Select strategy (optional)
3. Enter symbols (comma-separated)
4. Set time range
5. Run and analyze results

## 7. Monitoring & Alerts

### Cron Job for Market Reports

```json
{
  "name": "NOFX Market Report",
  "schedule": {"kind": "cron", "expr": "*/30 * * * *"},
  "sessionTarget": "isolated",
  "payload": {
    "kind": "agentTurn",
    "message": "Fetch NOFX data and generate market report...",
    "deliver": true,
    "channel": "telegram",
    "to": "USER_ID"
  }
}
```

### Report Contents

- 🤖 AI500 signals (coin + score + gain)
- 💰 Institution flow TOP10
- 🚀 Price gainers TOP10
- 📈 OI increase TOP10
- 📉 OI decrease TOP10
- ⚠️ Drop alerts

## 8. Common Workflows

### Daily Market Check

1. Fetch AI500/AI300 signals
2. Check institution fund flow
3. Monitor OI changes
4. Identify opportunities

### Strategy Development

1. Analyze market data
2. Define entry/exit rules
3. Create strategy in Studio
4. Backtest with historical data
5. Create trader and start

### Risk Monitoring

1. Check dashboard P/L
2. Review positions
3. Monitor drawdown
4. Adjust or stop traders if needed

## API Response Examples

See `references/api-examples.md` for detailed response structures.

## Additional References

| Reference | Description |
|-----------|-------------|
| `references/grid-trading.md` | Grid trading detailed guide with examples |
| `references/market-charts.md` | Market page and chart analysis |
| `references/multi-account.md` | Multi-account management |
| `references/webhooks.md` | Telegram/Discord/Slack notifications |
| `references/faq.md` | Frequently asked questions |
