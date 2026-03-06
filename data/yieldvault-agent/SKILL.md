---
name: yieldvault-agent
description: Autonomous yield farming agent for BNB Chain with deterministic execution, smart contract integration, and automated decision-making.
---

# YieldVault Agent

Autonomous yield farming agent for BNB Chain with deterministic execution, smart contract integration, and automated decision-making.

## Features

- **Deterministic Decision Engine** - Same input always produces same output (auditable)
- **Smart Contract Integration** - Interact with YieldVault contracts on BNB testnet/mainnet
- **Autonomous Scheduler** - Run farming decisions hourly without manual intervention
- **Transaction Executor** - Automatic DEPOSIT, WITHDRAW, HARVEST, COMPOUND, REBALANCE actions
- **Telegram Alerts** - Real-time notifications for executions, APR changes, and errors
- **Risk Management** - Conservative risk filtering (only vaults with risk_score ≤ 0.5)
- **Yield Optimization** - Net APR calculation (apr - fees - risk_penalty)

## Installation

```bash
clawhub install yieldvault-agent
```

## Quick Start

### 1. Configure

```bash
cp config.deployed.json .env.local
# Edit with your contract addresses and RPC endpoint
```

### 2. Deploy Contracts (if needed)

```bash
cd contracts
npm install
npm run deploy:testnet
```

### 3. Run Tests

```bash
npm test                    # Unit tests
node test.live.mock.js      # Integration tests (offline)
node test.live.js           # Live testnet tests
```

### 4. Start Scheduler

```bash
node scheduler.js
# Runs decision cycle every hour against testnet
```

### 5. Monitor Alerts

Telegram notifications sent automatically for:
- Execution started (vault_id, action, amount)
- APR changes (>1% delta)
- Errors (with severity level)
- Cycle completion (stats summary)

## Architecture

```
Smart Contracts (BNB Testnet/Mainnet)
    ↓
BlockchainReader (live vault data)
    ↓
YieldFarmingAgent (deterministic decisions)
    ↓
TransactionExecutor (sign & broadcast)
    ↓
Scheduler (hourly automation)
    ↓
Notifications (Telegram alerts)
```

## Configuration

Edit `config.scheduler.json`:

```json
{
  "chainId": 97,
  "interval_minutes": 60,
  "harvest_threshold_usd": 25,
  "rebalance_apr_delta": 0.02,
  "max_allocation_percent": 0.35,
  "risk_score_threshold": 0.5
}
```

## Decision Logic

1. **Read** current vault state (APR, TVL, user balance)
2. **Calculate** Net APR = apr - fees - (risk_score × 0.10)
3. **Filter** vaults with risk_score ≤ 0.5
4. **Select** vault with highest Net APR
5. **Decide** action:
   - HARVEST if pending_rewards ≥ $25 USD
   - COMPOUND if net_apr ≥ 2% delta
   - REBALANCE if another vault beats current by ≥ 2%
   - NOOP if already optimized

6. **Execute** transaction (with retry logic)
7. **Log** execution record (SHA256 auditable)

## Supported Networks

- **Testnet:** BNB Chain Testnet (chainId: 97)
- **Mainnet:** BNB Chain Mainnet (chainId: 56)

## Security

- ✅ Deterministic execution (reproducible, auditable)
- ✅ SHA256 audit trail for every decision
- ✅ Risk filtering (conservative)
- ✅ Constraint enforcement (max 35% per vault)
- ✅ Retry logic with exponential backoff
- ✅ No hardcoded private keys (use environment variables)

## Production Readiness

For mainnet deployment, add:

1. **Chainlink Oracle** - Live APR feeds
2. **Hardware Wallet Support** - Ledger/Trezor signing
3. **Smart Contract Audit** - Professional security review
4. **Emergency Pause** - Multi-sig pause mechanism

See `FINAL_CHECKLIST.md` for complete production requirements.

## Documentation

- `README.md` - Full user guide
- `SKILL.md` - This file
- `FINAL_CHECKLIST.md` - Production requirements
- `INTEGRATION_GUIDE.md` - Smart contract integration
- `EXAMPLES.md` - Usage examples
- `RESPUESTAS_PREGUNTAS.md` - FAQ & architecture

## Support

Issues & PRs welcome: https://github.com/open-web-academy/yieldvault-agent-bnb

## License

MIT
