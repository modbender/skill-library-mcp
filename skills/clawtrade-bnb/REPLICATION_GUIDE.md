# Complete Replication Guide - YieldVault Agent v1.1.0

This guide shows **exactly** how to replicate the entire yield farming agent from scratch.

## Prerequisites

- **Node.js** ≥ 16.0.0
- **npm** ≥ 8.0.0
- **Git** (to clone repo)
- **BNB testnet wallet** with tBNB (free from faucet)
- **Text editor** (VS Code recommended)

## Step-by-Step Installation

### Phase 1: Get the Code

**Option A: From ClawHub (Recommended)**
```bash
clawhub install clawtrade-bnb
cd ~/.openclaw/workspace/skills/clawtrade-bnb
npm install
```

**Option B: From GitHub**
```bash
git clone https://github.com/open-web-academy/clawtrade-bnb-bnb.git
cd clawtrade-bnb-bnb
npm install
```

### Phase 2: Configure Environment

#### Step 1: Get testnet RPC
Need a BNB testnet RPC endpoint. Choose one:
- `https://bsc-testnet.publicnode.com` (recommended - free, reliable)
- `https://data-seed-prebsc-2-b.binance.org:8545`

#### Step 2: Get testnet wallet
Create a new wallet for testing:
```bash
# Using ethers.js
node -e "
const ethers = require('ethers');
const wallet = ethers.Wallet.createRandom();
console.log('Address:', wallet.address);
console.log('Private Key:', wallet.privateKey);
"
```

**Save this private key securely!**

#### Step 3: Get testnet BNB
Get free testnet BNB from faucet:
- https://testnet.binance.org/faucet
- Paste your wallet address → Claim tBNB

Verify balance:
```bash
node -e "
const ethers = require('ethers');
const provider = new ethers.providers.JsonRpcProvider('https://bsc-testnet.publicnode.com');
provider.getBalance('YOUR_ADDRESS_HERE').then(b => 
  console.log(ethers.utils.formatEther(b), 'BNB')
);
"
```

#### Step 4: Set up environment file
```bash
# Create .env (git-ignored automatically)
echo "PRIVATE_KEY=YOUR_TESTNET_PRIVATE_KEY" > .env
echo "RPC_URL=https://bsc-testnet.publicnode.com" >> .env

# Verify (should show your address)
node -e "require('dotenv').config(); const ethers = require('ethers'); const w = new ethers.Wallet(process.env.PRIVATE_KEY); console.log('Wallet:', w.address)"
```

### Phase 3: Deploy Smart Contracts (Optional)

If you want to use your own vault contracts:

```bash
cd contracts
npm install

# Deploy to testnet
npm run deploy:testnet

# Save the addresses printed in console
# Update ../config.deployed.json with new addresses
```

**OR use existing test vaults:**
```bash
# Contracts already deployed on testnet:
# vault_eth_staking_001: 0x588eD88A145144F1E368D624EeFC336577a4276b
# vault_high_risk_001: 0x6E05a63550200e20c9C4F112E337913c32FEBdf0
# vault_link_oracle_001: 0x0C035842471340599966AA5A3573AC7dB34D14E4
```

### Phase 4: Verify Setup

```bash
# Test everything works
node agent-cli.js network status

# Should print:
# ╔════════════════════════════════════════════╗
# ║ Network:  BNB Testnet
# ║ RPC:      https://bsc-testnet.publicnode.com
# ║ Wallet:   YOUR_WALLET_ADDRESS
# ╚════════════════════════════════════════════╝
```

## Phase 5: Run the Agent

### Terminal 1: Strategy Engine
```bash
node strategy-scheduler.js

# Output:
# ╔═══════════════════════════════════════════╗
# ║  DeFi Strategy Scheduler - LIVE           ║
# ╠═══════════════════════════════════════════╣
# ║  Engine: BNB Testnet
# ║  Wallet: 0xBA2aCD05...
# ║  Strategies: Compound, Rebalance, Harvest
# ║  Cycle Interval: 60s
# ╚═══════════════════════════════════════════╝
#
# 📊 Execution Cycle #1 @ 2026-02-18T18:00:00Z
# ✓ vault_eth_staking_001: COMPOUND ($45.50)
# ✓ vault_high_risk_001: REBALANCE (2.1% delta)
# ✓ vault_link_oracle_001: HARVEST ($12.30)
# ✅ Cycle #1 completed
```

### Terminal 2: Dashboard
```bash
npm run dev:dashboard

# Output:
# ➜  Local:  http://localhost:5173/
# ➜  press h to show help

# Open browser: http://localhost:5173
# See real-time performance metrics
```

### Terminal 3: Control Panel
```bash
node agent-cli.js

# Interactive mode - try these commands:
help                    # Show all commands
network status          # View current network
perf summary            # Quick metrics
perf report             # Detailed analysis
learn now               # Optimize parameters
learn report            # View improvements

# Or run directly:
node agent-cli.js network testnet
node agent-cli.js perf summary
node agent-cli.js learn now
```

## File Structure After Setup

```
clawtrade-bnb/
├── .env                              # Your secrets (git-ignored)
├── .network.json                     # Network preference (auto-created)
├── execution-log.jsonl               # Action history (auto-created)
├── performance-metrics.json           # Metrics (auto-created)
├── learning-state.json                # Learning progress (auto-created)
│
├── Core Engine Files
├── defi-strategy-engine.js            # 3 autonomous strategies
├── on-chain-logger.js                 # Event logging
├── strategy-scheduler.js              # Main loop (60s cycles)
├── network-switcher.js                # Testnet ↔ mainnet toggle
├── performance-analytics.js           # Real APR calculations
├── reinforced-learning.js             # Self-improving system
├── agent-cli.js                       # Control panel
│
├── Configuration
├── config.deployed.json               # Contract addresses & ABIs
├── config.scheduler.json              # Strategy parameters
├── package.json                       # Dependencies
│
├── Dashboard
├── dashboard/src/App.tsx              # React frontend
├── dashboard/src/index.css            # Styling
├── dashboard/package.json             # Frontend deps
├── dashboard/dist/                    # Built assets
│
├── Smart Contracts
├── contracts/YieldVault.sol           # Core vault contract
├── contracts/package.json             # Hardhat config
├── contracts/deployments/             # Deployed addresses
│
├── Documentation
├── README.md                          # User guide
├── README_STRATEGY.md                 # Strategy details
├── README_ADVANCED.md                 # Networking & learning
├── SKILL.md                           # Installation guide
├── REPLICATION_GUIDE.md               # This file
│
└── Testing
    ├── test.js                        # Unit tests
    └── test.live.js                   # Live testnet tests
```

## Verification Checklist

- [ ] Node.js v16+ installed (`node --version`)
- [ ] npm v8+ installed (`npm --version`)
- [ ] `.env` file created with PRIVATE_KEY
- [ ] Testnet wallet has > 0.1 BNB
- [ ] RPC endpoint accessible
- [ ] `npm install` completed without errors
- [ ] `node agent-cli.js network status` shows testnet
- [ ] Strategy scheduler starts (`node strategy-scheduler.js`)
- [ ] Dashboard runs (`npm run dev:dashboard`)
- [ ] CLI interactive mode works (`node agent-cli.js`)

## Common Issues & Solutions

### Issue: "PRIVATE_KEY is not defined"
**Solution:** Create `.env` file with `PRIVATE_KEY=your_key`
```bash
echo "PRIVATE_KEY=0x..." > .env
```

### Issue: "Cannot find module 'ethers'"
**Solution:** Install dependencies
```bash
npm install
```

### Issue: "Connection refused" (RPC error)
**Solution:** RPC endpoint down - try alternative
```bash
# Edit config.deployed.json or set env:
export RPC_URL=https://bsc-dataseed1.defibit.io
```

### Issue: "Insufficient balance" (testnet)
**Solution:** Get more tBNB from faucet
- https://testnet.binance.org/faucet
- Paste address → Claim

### Issue: "Contract not found" (0x0000...)
**Solution:** Verify contract address in config.deployed.json
```bash
node -e "const c = require('./config.deployed.json'); console.log(JSON.stringify(c.contracts, null, 2))"
```

## Customization

### Change Network to Mainnet

```bash
# After everything works on testnet:
node agent-cli.js network mainnet

# Add real contracts to config.deployed.json
# Add real private key to .env (mainnet key)
# Run with caution - this is real money!
```

### Add Custom Vault

Edit `config.deployed.json`:
```json
{
  "vaultId": "my_vault",
  "name": "My Custom Vault",
  "address": "0x...",
  "underlying": "0x...",
  "strategy": "My Strategy",
  "risk_score": 0.4
}
```

### Adjust Strategy Parameters

Edit `config.scheduler.json`:
```json
{
  "agent": {
    "harvest_threshold_usd": 50,      // Was 25 - harvest larger amounts
    "rebalance_apr_delta": 3.0,       // Was 2.0 - be more conservative
    "dynamic_harvest_gas_ratio": 3.0  // Was 2.0 - higher gas threshold
  }
}
```

Then optimize with learning:
```bash
node agent-cli.js learn now
```

## Performance Optimization

### For Testnet (Development)
```bash
# Fast iterations, low costs
node agent-cli.js network testnet
# Harvest threshold: $25 (low)
# Gas multiplier: 1.2x (lenient)
```

### For Mainnet (Production)
```bash
# Higher safety, more conservative
node agent-cli.js network mainnet
# Harvest threshold: $100 (higher)
# Gas multiplier: 1.5x (safer)
```

### Use Reinforced Learning
```bash
# After 100 cycles, optimize automatically
node agent-cli.js learn now

# This adjusts:
# - Harvest thresholds (based on success)
# - Rebalance delta (based on failures)
# - Gas ratio (based on estimates)
```

## Monitoring & Debugging

### View Live Logs
```bash
# Real-time action log
tail -f execution-log.jsonl | jq

# Pretty print latest action
tail -1 execution-log.jsonl | jq
```

### Check Performance
```bash
# Generate report
node agent-cli.js perf report

# Per-vault breakdown
node agent-cli.js perf vaults

# Strategy analysis
node agent-cli.js perf strategies
```

### View Learning Progress
```bash
# See improvements
node agent-cli.js learn report

# View raw learning state
cat learning-state.json | jq
```

## Troubleshooting with Logs

All actions logged to `execution-log.jsonl` (one JSON per line):

```json
{
  "timestamp": 1708308000,
  "cycle": 42,
  "action": "COMPOUND_YIELD",
  "vault": "vault_eth_staking_001",
  "rewards_usd": 45.50,
  "harvest_tx": "0x...",
  "compound_tx": "0x...",
  "confidence": 0.95
}
```

Analyze errors:
```bash
# Find failures
grep ERROR execution-log.jsonl | jq

# Count by type
grep -o '"action":"[^"]*"' execution-log.jsonl | sort | uniq -c
```

## Next Steps After Setup

1. **Let it run for 24 hours**
   - Collect real performance data
   - System learns optimal parameters

2. **Check performance**
   ```bash
   node agent-cli.js perf report
   ```

3. **Optimize with learning**
   ```bash
   node agent-cli.js learn now
   ```

4. **Monitor dashboard**
   - http://localhost:5173
   - Real-time metrics, action history

5. **When confident, go mainnet**
   ```bash
   node agent-cli.js network mainnet
   ```

## Getting Help

- **Documentation:** `README.md`, `README_ADVANCED.md`
- **GitHub Issues:** https://github.com/open-web-academy/clawtrade-bnb-bnb/issues
- **CLI Help:** `node agent-cli.js help`
- **Live Logs:** `tail -f execution-log.jsonl`

## Summary

You now have:
- ✅ Production-ready DeFi agent
- ✅ 3 autonomous strategies (self-optimizing)
- ✅ Real-time dashboard
- ✅ CLI control panel
- ✅ On-chain event logging
- ✅ Performance analytics
- ✅ Network switching (testnet ↔ mainnet)
- ✅ Reinforced learning (auto-improvements)

**Total setup time: 15 minutes**
**Time to first autonomous cycle: 30 seconds**

Happy yield farming! 🚀

---

**Last Updated:** 2026-02-18  
**Version:** 1.1.0  
**Status:** Ready for Production
