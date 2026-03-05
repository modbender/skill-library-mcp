---
name: clawtrade-bnb
version: 1.1.0
description: Autonomous DeFi trading agent for BNB Chain with multi-strategy engine, network switching, and reinforced learning.
keywords: trading, defi, autonomous-agent, multi-strategy, reinforced-learning, bnb-chain
---

# CawTrade BNB - Autonomous DeFi Trading Agent v1.1.0

**Production-ready autonomous trading agent** for BNB Chain testnet & mainnet. Features 3 intelligent strategies, real-time performance analytics, on-chain event logging, and self-improving reinforced learning.

## Core Features

### 🤖 Three Autonomous Strategies
1. **Compound Yield** - Auto-reinvest harvested rewards for exponential growth
2. **Rebalance** - Move capital from low-APR to high-APR vaults automatically
3. **Dynamic Harvest** - Intelligent harvesting based on gas cost optimization

### 🌐 Network Switching
- Instant testnet ↔ mainnet toggle (no restart)
- Separate configs per network (gas, thresholds, RPCs)
- Contract address mapping per chain
- Persistent network preferences

### 📊 Real-Time Analytics
- Realized APR (actual, based on historical yields)
- Per-vault performance breakdown
- Strategy effectiveness scoring
- Success rate tracking (target: >90%)
- Failure pattern detection

### 🧠 Reinforced Learning
- Auto-learns from past failures
- Dynamically optimizes strategy parameters
- Adjusts thresholds based on success rates
- Confidence scoring per strategy
- Self-improving over time

### ⛓️ On-Chain Event Logging
- All actions logged with TX hashes
- Auditable blockchain trail
- BNB Testnet Scanner links
- Complete execution history

### 🎮 Control Panel CLI
- Interactive command-line interface
- Network management commands
- Performance metrics dashboard
- Learning progress tracking
- Real-time optimization

## Installation & Setup

### 1. Install Skill
```bash
clawhub install clawtrade-bnb
cd ~/.openclaw/workspace/skills/clawtrade-bnb
npm install
```

### 2. Configure Environment
```bash
# Copy example config
cp config.deployed.json config.live.json

# Edit with your settings
nano config.live.json
# Set RPC endpoint, contract addresses, wallet
```

### 3. Set Private Key (Secure)
```bash
# Option A: Environment variable (recommended)
export PRIVATE_KEY="your_testnet_private_key"

# Option B: .env file (git-ignored)
echo "PRIVATE_KEY=your_key" >> .env

# NOTE: Never commit private keys!
```

### 4. Verify Setup
```bash
# Test connection and contracts
node agent-cli.js network status

# Check wallet balance
npm run verify
```

## Quick Start - 3 Commands

```bash
# Terminal 1: Run strategy engine (60-second cycles)
node strategy-scheduler.js

# Terminal 2: Real-time dashboard
npm run dev:dashboard
# → Open http://localhost:5173

# Terminal 3: Control panel
node agent-cli.js

# Example commands:
node agent-cli.js network testnet        # Switch network
node agent-cli.js perf summary           # See performance
node agent-cli.js learn now              # Optimize strategies
```

## Architecture

```
DeFi Strategy Engine
├─ Compound Yield Strategy
│  └─ Harvest when pending > $25 → Re-deposit
├─ Rebalance Strategy
│  └─ Move 20% from low-APR to high-APR vault
└─ Dynamic Harvest Strategy
   └─ Harvest only if pending > 2x gas cost

         ↓ (runs every 60 seconds)

Strategy Scheduler
├─ Read vault APRs & pending rewards
├─ Execute all 3 strategies
└─ Log actions + TX hashes

         ↓ (logs to blockchain)

On-Chain Logger
├─ execution-log.jsonl (append-only)
├─ performance-metrics.json (cumulative)
└─ learning-state.json (optimization history)

         ↓ (analyzes continuously)

Reinforced Learning System
├─ Tracks success rates per strategy
├─ Detects failure patterns
├─ Auto-adjusts thresholds
└─ Generates improvement reports

         ↓ (displays real-time)

Dashboard + Control Panel
├─ React dashboard (http://localhost:5173)
├─ Agent CLI (network, perf, learn commands)
└─ Performance API (/api/logs, /api/health)
```

## Configuration Files

**config.deployed.json** - Contract addresses & ABIs
```json
{
  "chainId": 97,
  "network": "BNB Testnet",
  "contracts": [
    {
      "vaultId": "vault_eth_staking_001",
      "address": "0x588eD88A145144F1E368D624EeFC336577a4276b",
      "strategy": "Ethereum 2.0 Staking",
      "risk_score": 0.3
    }
  ]
}
```

**config.scheduler.json** - Strategy thresholds
```json
{
  "scheduler": {
    "execution_interval_seconds": 60,
    "enabled": true
  },
  "agent": {
    "harvest_threshold_usd": 25,
    "rebalance_apr_delta": 2.0,
    "max_allocation_percent": 0.35,
    "min_confidence": 0.6
  }
}
```

## Strategy Decision Logic

Each 60-second cycle:

1. **COMPOUND YIELD**
   - Check pending rewards per vault
   - If pending ≥ $25 → Harvest + Re-deposit
   - Log action with TX hash

2. **REBALANCE**
   - Compare APRs across all vaults
   - If top APR > bottom APR by ≥ 2% → Rebalance
   - Move 20% from worst to best vault
   - Log action with TX hash

3. **DYNAMIC HARVEST**
   - Estimate gas cost per harvest
   - Only harvest if pending > 2x gas cost
   - Maximize profitability per action
   - Log action with TX hash

**Example Output:**
```
Cycle #42 @ 2026-02-18T18:00:00Z
✓ vault_eth_staking_001: COMPOUND ($45.50 harvested)
✓ vault_high_risk_001: REBALANCE (2.1% APR delta)
✓ vault_link_oracle_001: HARVEST ($12.30 pending)
✅ Total Rewards: $57.80 | Compounded: $45.50
```

## CLI Commands

### Network Management
```bash
node agent-cli.js network status      # Current network config
node agent-cli.js network testnet     # Switch to testnet
node agent-cli.js network mainnet     # Switch to mainnet (⚠️ production)
```

### Performance Monitoring
```bash
node agent-cli.js perf summary        # Quick stats
node agent-cli.js perf report         # Detailed analysis
node agent-cli.js perf vaults         # Per-vault breakdown
node agent-cli.js perf strategies     # Strategy effectiveness
```

### Reinforced Learning
```bash
node agent-cli.js learn now           # Analyze & optimize
node agent-cli.js learn report        # View improvements
node agent-cli.js learn reset         # Reset learning state
```

## Supported Networks

| Network | Chain ID | Use Case | Harvest Min | Gas Multiplier |
|---------|----------|----------|-------------|----------------|
| BNB Testnet | 97 | Development | $25 | 1.2x |
| BNB Mainnet | 56 | Production | $100 | 1.5x |

## Network Switching

Switch instantly without restarting:
```bash
# Current config
node agent-cli.js network status
# → BNB Testnet

# Switch to production
node agent-cli.js network mainnet
# → Updated RPC, contract addresses, and thresholds

# All settings updated automatically
```

## Security & Safety

### On-Chain Auditing
- ✅ Every action logged with transaction hash
- ✅ Blockchain verification via BNB Testnet/Mainnet Scanner
- ✅ Append-only execution log (execution-log.jsonl)
- ✅ Complete audit trail for compliance

### Risk Management
- ✅ Deterministic decision logic (reproducible, auditable)
- ✅ Success rate monitoring (>90% target)
- ✅ Confidence thresholds per strategy
- ✅ Graceful error handling & recovery
- ✅ Automatic parameter optimization via learning

### Private Key Security
- ✅ Never hardcoded - use environment variables only
- ✅ .env file git-ignored
- ✅ Testnet for development, mainnet when ready
- ✅ For production: use hardware wallet support (future)

## File Structure

```
clawtrade-bnb/
├── defi-strategy-engine.js          # 3 strategies (compound, rebalance, harvest)
├── on-chain-logger.js                # Event logging with TX hashes
├── strategy-scheduler.js              # Main loop (60s cycles)
├── network-switcher.js                # Testnet ↔ mainnet toggle
├── performance-analytics.js           # Real APR & metrics
├── reinforced-learning.js             # Self-improving parameters
├── agent-cli.js                       # Control panel
├── dashboard/                         # React frontend (real-time)
├── contracts/                         # Vault smart contracts
├── config.deployed.json               # Contract addresses & ABIs
├── config.scheduler.json              # Strategy thresholds
├── execution-log.jsonl                # Action history (generated)
├── performance-metrics.json           # Metrics (generated)
├── learning-state.json                # Learning progress (generated)
├── README.md                          # User guide
├── README_STRATEGY.md                 # Strategy details
├── README_ADVANCED.md                 # Network switching & learning
├── SKILL.md                           # This file
└── package.json                       # Dependencies
```

## Integration with Other Skills

This is a **standalone, complete skill**. It can also integrate with:

- **Telegram Notifications** - Send alerts to OpenClaw users
- **Email Reports** - Daily performance summaries
- **Database Logging** - Store metrics in persistent DB
- **Webhook Integrations** - Trigger external services

## Documentation

| File | Purpose |
|------|---------|
| `README.md` | Complete user guide |
| `README_STRATEGY.md` | Strategy details & examples |
| `README_ADVANCED.md` | Network switching & reinforced learning |
| `SKILL.md` | This installation & architecture guide |

## What You Get

✅ **Production-ready code** (tested, documented, error-handling)
✅ **3 profitable strategies** (auto-optimizing, self-learning)
✅ **Real-time dashboard** (React, live updates)
✅ **CLI control panel** (manage from terminal)
✅ **On-chain logging** (auditable, transparent)
✅ **Network switching** (testnet → mainnet in seconds)
✅ **Self-improvement** (learns from failures automatically)
✅ **Complete documentation** (guides, examples, FAQ)

## Replicating This Skill

For someone else to replicate:

1. **Install**
   ```bash
   clawhub install clawtrade-bnb
   npm install
   ```

2. **Configure**
   ```bash
   # Edit config files with your contracts & RPC
   nano config.deployed.json
   ```

3. **Deploy Contracts** (if using new vaults)
   ```bash
   cd contracts && npm run deploy:testnet
   ```

4. **Run**
   ```bash
   node strategy-scheduler.js      # Main engine
   npm run dev:dashboard           # Dashboard
   node agent-cli.js               # Control panel
   ```

5. **Monitor**
   - Dashboard: http://localhost:5173
   - Logs: execution-log.jsonl
   - Analytics: node agent-cli.js perf report

**Total setup time: ~15 minutes**

## Support & Community

- GitHub Issues: https://github.com/open-web-academy/clawtrade-bnb-bnb
- ClawHub: https://clawhub.com (search: clawtrade-bnb)
- Discord: https://discord.com/invite/clawd

## Version History

- **v1.1.0** (2026-02-18) - Network switcher, analytics, reinforced learning, CLI
- **v1.0.0** (2026-02-17) - Initial release, 3 strategies, on-chain logging

## License

MIT - Free to use, modify, and distribute
