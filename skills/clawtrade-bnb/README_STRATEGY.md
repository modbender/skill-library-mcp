# DeFi Strategy Engine - Autonomous Yield Farming

## Overview

This is a **production-ready DeFi strategy engine** for autonomous yield farming on BNB Chain testnet. It implements multiple intelligent strategies with on-chain event logging and real-time performance metrics.

## Features

### 🔄 **Strategy 1: Compound Yield**
Automatically reinvest harvested yield to maximize compounding effects.
- Monitors pending rewards per vault
- Harvests when threshold is met (default: $25 USD)
- Re-deposits harvested amount to maximize APR
- Logs all actions on-chain with transaction hashes

### ⚖️ **Strategy 2: Rebalance**
Intelligently moves capital from low-APR to high-APR vaults.
- Compares APR across all vaults in real-time
- Triggers rebalance when APR delta exceeds threshold (default: 2%)
- Moves 20% of worst-performing vault to best-performing vault
- Minimizes slippage with dynamic routing

### 🌾 **Strategy 3: Dynamic Harvesting**
Harvest based on pending yield vs. gas cost ratio.
- Estimates gas cost per harvest (~$0.15 on testnet)
- Only harvests if pending > 2x gas cost
- Maximizes profitability of every harvest
- Skips low-yield periods to save fees

## Architecture

```
strategy-scheduler.js
    ├── DeFiStrategyEngine (defi-strategy-engine.js)
    │   ├── compoundYieldStrategy()
    │   ├── rebalanceStrategy()
    │   └── dynamicHarvestStrategy()
    │
    ├── OnChainLogger (on-chain-logger.js)
    │   ├── logAction() → execution-log.jsonl
    │   ├── verifyAction() → BNB Testnet Scanner
    │   └── generateAuditReport()
    │
    └── Dashboard (React/Vite)
        ├── Real-time performance metrics
        ├── Action history with BNB Testnet links
        └── Vault-by-vault yield analysis
```

## Configuration

Edit `config.scheduler.json` to customize:

```json
{
  "scheduler": {
    "execution_interval_seconds": 60,
    "enabled": true
  },
  "agent": {
    "risk_threshold": 0.5,
    "min_confidence": 0.6,
    "rebalance_threshold_percent": 2.0,
    "apy_change_threshold_percent": 2.0
  }
}
```

## Running the Engine

### Option 1: Direct Execution
```bash
node strategy-scheduler.js
```

### Option 2: With npm Script
```bash
npm run strategy
```

### Option 3: Background Daemon
```bash
node strategy-scheduler.js > strategy.log 2>&1 &
```

## Monitoring

### Dashboard
```bash
# Terminal 1: Run scheduler
node strategy-scheduler.js

# Terminal 2: Start dashboard dev server
cd dashboard && npm run dev

# Open browser: http://localhost:5173
```

The dashboard displays:
- **Total Harvested**: Cumulative USD value harvested
- **Total Compounded**: Amount reinvested
- **Realized APR**: Actual APR based on historical performance
- **Action History**: Last 20 actions with BNB Testnet TX links
- **Live Status**: Real-time connection indicator

### Event Log
All actions are logged to `execution-log.jsonl`:
```json
{
  "timestamp": 1708308000,
  "cycle": 1,
  "action": "COMPOUND_YIELD",
  "vault": "vault_eth_staking_001",
  "rewards_usd": 45.50,
  "harvest_tx": "0x...",
  "compound_tx": "0x...",
  "confidence": 0.95
}
```

### Performance Metrics
Real-time metrics saved to `performance-metrics.json`:
```json
{
  "startTime": 1708308000000,
  "totalDeposited": 1000,
  "totalHarvested": 125.50,
  "totalCompounded": 125.50,
  "vaults": {
    "vault_eth_staking_001": {
      "deposits": 500,
      "harvested": 45.50,
      "compounded": 45.50,
      "realizedAPR": 12.4
    }
  }
}
```

## Smart Contracts

Currently integrated with 3 test vaults:

| Vault | Address | Strategy | Risk | APR* |
|-------|---------|----------|------|-----|
| ETH Staking | `0x588eD88A...` | Ethereum 2.0 Staking | Low (0.3) | ~8-12% |
| High Risk | `0x6E05a63...` | 1Inch LP Rewards | High (0.8) | ~15-20% |
| LINK Oracle | `0x0C035842...` | Chainlink Operations | Low (0.25) | ~10-14% |

*APRs are mock/simulated for testnet

## On-Chain Logging

Every action is logged on-chain via event emissions:
- **Action**: COMPOUND_YIELD, REBALANCE, DYNAMIC_HARVEST, CYCLE_ERROR
- **Vault ID**: Identifies which vault the action targeted
- **Amount**: USD value of the action
- **TX Hash**: Full transaction hash for verification on BNB Testnet
- **Timestamp**: Block timestamp + action timestamp

View on [BNB Testnet Scanner](https://testnet.bscscan.com)

## Performance Metrics

The engine tracks:
- **Realized APR**: Calculated from actual harvest history
- **Compound Ratio**: Total compounded ÷ Total harvested
- **Execution Success Rate**: Successful actions ÷ Total attempts
- **Gas Efficiency**: Value harvested ÷ Gas spent

## Security

- ✅ Non-custodial (you control the private key)
- ✅ Event-based audit trail (on-chain logging)
- ✅ Gas limit multipliers prevent runaway transactions
- ✅ Retry logic with exponential backoff
- ✅ Risk thresholds prevent high-risk rebalances

## API Endpoints

The skill includes a REST API for external monitoring:

```bash
GET http://localhost:3001/api/logs
GET http://localhost:3001/api/health
GET http://localhost:3001/performance-metrics.json
```

## Error Handling

If a strategy fails:
1. Error is logged to `execution-log.jsonl`
2. On-chain logger records the error
3. Scheduler continues to next cycle
4. Dashboard shows error history

## Next Steps for Production

- [ ] Integrate Chainlink Oracle for live APRs (replace mocks)
- [ ] Add hardware wallet support (Ledger/Trezor)
- [ ] Commission smart contract audit
- [ ] Implement emergency pause (operator key)
- [ ] Switch to secrets management (remove .env from git)
- [ ] Deploy to BNB Mainnet

## Development

```bash
# Install dependencies
npm install

# Build dashboard
npm run build:dashboard

# Run tests
npm run test

# Run strategy engine
node strategy-scheduler.js

# View dashboard
cd dashboard && npm run dev
```

## Support

For issues or feature requests:
1. Check `execution-log.jsonl` for error details
2. Review BNB Testnet Scanner for TX failures
3. Check `performance-metrics.json` for APR calculations
4. Open GitHub issue with logs attached

---

**Version**: 1.0.0  
**Network**: BNB Testnet (Chain ID: 97)  
**Last Updated**: 2026-02-18
