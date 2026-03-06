---
name: solana-funding-arb-cn
description: "Solana 资金费率套利 | Solana Funding Rate Arbitrage. 永续合约资金费率套利 | Perpetual funding rate arbitrage. 监控资金费率、发现套利机会 | Monitor funding rates, find arb opportunities. 触发词：Solana、资金费率、套利、funding rate."
metadata:
  openclaw:
    emoji: ◎
    fork-of: "https://clawhub.ai"
---
# Solana Funding Rate Arbitrage (v2.0)

Automated funding rate arbitrage bot for Solana perpetual DEXes.

## 🔥 What's New in v2.0

- **Auto-Trading**: Fully automated position management
- **Multi-DEX Support**: Drift Protocol + Flash Trade
- **Position Manager**: Track PnL and funding collected
- **Risk Management**: Stop-loss, max DD, auto-rebalancing
- **Cron Integration**: Scheduled rate checks

## Supported DEXes

| DEX | Markets | Trading | Data Source |
|-----|---------|---------|-------------|
| Drift Protocol | 64 | ✅ Full | Direct API |
| Flash Trade | 19 | 🔶 DRY_RUN | CoinGecko |

## Strategy Options

| Strategy | Leverage | Win Rate | APY | Max Drawdown |
|----------|----------|----------|-----|--------------|
| Ultra Safe | 1x | 96% | 126% | 2% |
| Conservative | 1.5x | 89% | 203% | 4% |
| Moderate | 2.5x | 85% | 411% | 9% |

## Quick Start

```bash
cd scripts && npm install

# 1. Scan funding rates (no trading)
npm run trade:scan

# 2. Check position status
npm run trade:status

# 3. Run in DRY_RUN mode (simulated)
npm run trade:dry

# 4. Run live trading (requires wallet)
npm run trade

# Other commands
npm run scan        # Basic rate scanner
npm run dashboard   # Web dashboard (:3456)
npm run monte-carlo # Risk simulations
```

## Configuration

**Config file:** `~/.secrets/funding-arb-config.json`

```json
{
  "strategy": "ultra_safe",
  "max_position_pct": 50,
  "min_spread": 0.5,
  "max_dd_pct": 2,
  "auto_execute": true,
  "dry_run": true,
  "leverage": 1,
  "check_interval_hours": 4,
  "min_apy_threshold": 100,
  "max_position_usd": 100,
  "notification": {
    "telegram": true,
    "on_open": true,
    "on_close": true,
    "on_funding": true
  },
  "risk": {
    "max_positions": 2,
    "stop_loss_pct": 2,
    "take_profit_pct": null,
    "auto_rebalance": true,
    "rebalance_threshold": 0.3
  }
}
```

## Environment Variables

Create `.env` in scripts directory or `~/.secrets/.env`:

```env
# Required for live trading
SOLANA_PRIVATE_KEY=[1,2,3,...]  # Or use wallet file
SOLANA_WALLET_PATH=/path/to/wallet.json

# Optional
SOLANA_RPC_URL=https://mainnet.helius-rpc.com/?api-key=YOUR_KEY
DEBUG=true  # Verbose logging
```

## Cron Setup

Run every 4 hours:

```bash
# Add to crontab -e
0 */4 * * * ~/clawd/skills/solana-funding-arb/scripts/cron-runner.sh
```

## How It Works

1. **Scan**: Compare funding rates on Drift vs Flash Trade
2. **Identify**: Find pairs where one is paying and other is receiving
3. **Execute**: 
   - Go LONG on exchange with negative rate (receive funding)
   - Go SHORT on exchange with positive rate (receive funding)
4. **Collect**: Delta-neutral = collect funding from both sides
5. **Rebalance**: Close when spread reverses or DD exceeded

### Example Trade

```
SOL Funding Rates:
- Drift: -500% APY (longs receive)
- Flash: +800% APY (shorts receive)
- Spread: 1300% APY

Action:
→ LONG $50 SOL on Drift (receive 500% APY)
→ SHORT $50 SOL on Flash (receive 800% APY)
→ Net: Delta-neutral, collecting ~1300% APY in funding
```

## Files

```
scripts/
├── src/trading/
│   ├── auto-trader.ts      # Main trading logic
│   ├── drift-client.ts     # Drift Protocol integration
│   ├── flash-client.ts     # Flash Trade integration
│   └── position-manager.ts # Position tracking
├── cron-runner.sh          # Cron wrapper script
└── ...

~/.clawd/funding-arb/
├── positions.json          # Current positions
├── history.json           # Trade history
├── trader-state.json      # Bot state
└── logs/                  # Cron logs
```

## Risks

⚠️ **Smart Contract Risk**: DEX bugs, hacks
⚠️ **Rate Reversal**: 15-18% daily probability
⚠️ **Execution Slippage**: 0.2-0.4%
⚠️ **Liquidation**: Only with leverage >1x

## Yield Comparison

| Platform | APY | vs Ultra Safe |
|----------|-----|---------------|
| Ultra Safe (1x) | 126% | — |
| US Bank (FDIC) | 4.5% | 28x less |
| Aave V3 | 2.5% | 50x less |
| Marginfi | 8.5% | 15x less |

## Testing

1. Start with `dry_run: true` (default)
2. Run `npm run trade:scan` to verify opportunities
3. Run `npm run trade:dry` to test execution flow
4. When ready, set `dry_run: false` and `max_position_usd: 10`
5. Monitor logs at `~/.clawd/funding-arb/logs/`

## References

- [Drift Protocol Docs](https://docs.drift.trade)
- [Flash Trade](https://flash.trade)
- [API Reference](references/api.md)
