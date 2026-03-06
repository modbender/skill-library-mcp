# Yield Farming Agent - Live Execution Guide

## Overview

The Yield Farming Agent has been integrated with deployed testnet contracts. This guide explains how to run the agent against live blockchain data and execute autonomous decisions.

**Network:** BNB Testnet (ChainID: 97)

**Deployed Contracts:**
- `vault_eth_staking_001`: 0x588eD88A145144F1E368D624EeFC336577a4276b
- `vault_high_risk_001`: 0x6E05a63550200e20c9C4F112E337913c32FEBdf0
- `vault_link_oracle_001`: 0x0C035842471340599966AA5A3573AC7dB34D14E4

---

## Architecture

### Component: BlockchainReader

**Purpose:** Reads live data from smart contracts on testnet

**Key Methods:**
- `initializeContracts(contracts)` - Connect to vault contracts
- `getVaultData(vaultId, userAddress)` - Fetch vault balances, shares, and yields
- `getAllVaultsData(userAddress)` - Fetch all vaults in parallel
- `simulateDeposit(vaultId, amount)` - Estimate shares from deposit
- `simulateHarvest(vaultId, userAddress)` - Get harvestable yield amount
- `onExecutionRecorded(vaultId, callback)` - Listen to ExecutionRecorded events
- `isConnected()` - Verify RPC connectivity
- `getNetworkInfo()` - Get chain details

**Location:** `blockchain-reader.js`

### Component: YieldFarmingAgent (Enhanced)

**Purpose:** Autonomous decision engine with deterministic output

**Flow:**
1. **Input:** Live vault data + current allocation state
2. **Processing:**
   - Calculate NET_APR (APR - fees - risk_penalty)
   - Filter vaults by risk threshold (≤0.5)
   - Sort by net APR descending
   - Evaluate conditions: HARVEST → COMPOUND → REBALANCE → NOOP
3. **Output:** ExecutionRecord with signed hashes

**Location:** `index.js` (existing, unchanged)

### Configuration Files

**config.deployed.json:**
- RPC endpoint: `https://data-seed-prebsc-1-b.binance.org:8545`
- Contract addresses and ABIs
- Risk scores and strategy info
- Agent thresholds (harvest, rebalance, allocation)

**Usage:**
```javascript
const config = require('./config.deployed.json');
```

---

## Running Live Tests

### 1. Install Dependencies

```bash
cd /home/ubuntu/.openclaw/workspace/skills/yield-farming-agent
npm install
```

Dependencies: `ethers@^5.7.2`

### 2. Run Integration Test

```bash
node test.live.js
```

**What It Tests:**
1. RPC connectivity to BNB Testnet
2. Contract initialization and ABI loading
3. Live vault data reading (total assets, shares)
4. Simulated DEPOSIT and HARVEST actions
5. Event listener configuration
6. Agent decision making with real vault data

**Expected Output:**
```
✓ [PASS] RPC Connection
✓ [PASS] Contract Initialization
✓ [PASS] Read Vault Data
✓ [PASS] Simulate Actions
✓ [PASS] Event Listener Setup
✓ [PASS] Agent Decision
```

### 3. Run Agent with Live Data

```javascript
const BlockchainReader = require('./blockchain-reader');
const YieldFarmingAgent = require('./index');
const config = require('./config.deployed.json');

// Initialize blockchain reader
const reader = new BlockchainReader(config.rpc);
const contractsWithABI = config.contracts.map(c => ({
  ...c,
  abi: config.abi
}));
await reader.initializeContracts(contractsWithABI);

// Fetch live vault data
const vaultData = await reader.getAllVaultsData();

// Transform to agent format
const vaults = vaultData.map(v => ({
  id: v.vault_id,
  apr: 0.04, // TODO: Fetch from oracle or contract
  fees: 0.001,
  risk_score: 0.3,
  tvl_usd: parseFloat(v.total_assets) * 1000, // Convert to USD
  underlying: '0x...',
  strategy: 'Strategy Name'
}));

// Get current allocation from blockchain or state
const currentAllocation = { /* ... */ };

// Run decision engine
const agent = new YieldFarmingAgent(config);
const execution = agent.decide(vaults, currentAllocation);

console.log(execution);
```

---

## Event Listening

### Listen to ExecutionRecorded Events

```javascript
const removeListener = reader.onExecutionRecorded(
  'vault_link_oracle_001',
  (event) => {
    console.log('Execution recorded:', event);
    // {
    //   vault_id: 'vault_link_oracle_001',
    //   action: 'DEPOSIT',
    //   user: '0x...',
    //   amount: '1000000000000000000',
    //   shares: '5000000000000000000',
    //   timestamp: 1708117200,
    //   event_timestamp: '2026-02-17T21:32:00Z'
    // }
  }
);

// Later: remove listener
removeListener();
```

---

## Decision Flow (Live)

```
┌─────────────────────────────────────────────────┐
│ 1. Fetch Live Vault Data (BlockchainReader)    │
│    - Total assets, shares, user yield           │
│    - Read from deployed contracts               │
└──────────────┬──────────────────────────────────┘
               │
┌──────────────▼──────────────────────────────────┐
│ 2. Transform to Agent Format                    │
│    - Calculate net APR per vault                 │
│    - Filter by risk threshold                   │
│    - Prepare allocation state                   │
└──────────────┬──────────────────────────────────┘
               │
┌──────────────▼──────────────────────────────────┐
│ 3. Run YieldFarmingAgent.decide()               │
│    - Evaluate conditions                        │
│    - Generate deterministic decision            │
│    - Compute cryptographic hashes               │
└──────────────┬──────────────────────────────────┘
               │
┌──────────────▼──────────────────────────────────┐
│ 4. ExecutionRecord Output                       │
│    {                                            │
│      "timestamp": "2026-02-17T21:32:00Z",      │
│      "cycle_num": 1708117200,                   │
│      "decision": {                              │
│        "action": "HARVEST|COMPOUND|...",        │
│        "vault_id": "...",                       │
│        "amount": "..."                          │
│      },                                         │
│      "decision_hash": "sha256(...)",            │
│      "execution_hash": "sha256(...)"            │
│    }                                            │
└──────────────┬──────────────────────────────────┘
               │
┌──────────────▼──────────────────────────────────┐
│ 5. Execute Action (Future Step)                 │
│    - Call contract method (DEPOSIT/HARVEST)     │
│    - Emit ExecutionRecorded event               │
│    - Verify hashes match                        │
└─────────────────────────────────────────────────┘
```

---

## Key Files

| File | Purpose | Status |
|------|---------|--------|
| `index.js` | YieldFarmingAgent core | ✓ Complete |
| `blockchain-reader.js` | Blockchain integration | ✓ New |
| `config.deployed.json` | Contract addresses & ABIs | ✓ New |
| `test.live.js` | Integration test suite | ✓ New |
| `LIVE_EXECUTION_GUIDE.md` | This document | ✓ New |

---

## Testing Checklist

- [x] RPC endpoint connectivity verified
- [x] Contract ABIs loaded and initialized
- [x] Live vault data readable from blockchain
- [x] Deposit and harvest simulations work
- [x] Event listener can be configured
- [x] Agent decision makes with real data
- [x] Hash verification passes
- [ ] **TODO:** Deploy transaction executor
- [ ] **TODO:** Integrate with Discord/Telegram for notifications
- [ ] **TODO:** Setup cron scheduler for autonomous execution
- [ ] **TODO:** Add oracle integration for live APR rates

---

## Next Steps for Full Automation

### 1. Transaction Executor Module

Create `tx-executor.js` to:
- Call contract methods (deposit, harvest, withdraw)
- Sign transactions with private key
- Broadcast to testnet RPC
- Monitor transaction status
- Emit ExecutionRecorded events

```javascript
class TransactionExecutor {
  async executeDeposit(vaultId, amount) { /* ... */ }
  async executeHarvest(vaultId) { /* ... */ }
  async executeCompound(vaultId) { /* ... */ }
}
```

### 2. Oracle Integration

For live APR rates:
- Fetch from Chainlink oracle contracts
- Store in contract state
- Update every 24 hours

### 3. Scheduler

Setup cron job or interval:
```javascript
setInterval(() => {
  const execution = agent.decide(vaults, allocation);
  executor.execute(execution.decision);
}, 3600000); // Every hour
```

### 4. Notifications

Post results to Telegram/Discord:
- Decision made
- Action executed
- Event confirmation
- Error alerts

---

## Troubleshooting

### RPC Connection Fails
```
Error: could not detect network
```
**Solution:** Check if BNB Testnet RPC is online
```bash
curl -X POST https://data-seed-prebsc-1-b.binance.org:8545 \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"eth_blockNumber","params":[],"id":1}'
```

### Contract Not Found
```
Error: call revert exception
```
**Solution:** Verify contract address exists on testnet
- Use [BNBScan Testnet](https://testnet.bscscan.com/) to check
- Ensure you're on ChainID 97

### Gas Estimation Fails
```
Error: insufficient funds for gas
```
**Solution:** Get test BNB from faucet
- [BNB Testnet Faucet](https://testnet.binance.org/faucet-smart)

---

## Files Manifest

```
/home/ubuntu/.openclaw/workspace/skills/yield-farming-agent/
├── index.js                      (Core agent, unchanged)
├── blockchain-reader.js          (NEW: Blockchain integration)
├── config.deployed.json          (NEW: Contract config)
├── test.live.js                  (NEW: Integration tests)
├── LIVE_EXECUTION_GUIDE.md       (NEW: This guide)
├── config.default.json           (Agent thresholds)
├── mockdata.json                 (Fallback test data)
├── package.json                  (+ ethers.js dependency)
├── contracts/
│   ├── abi/
│   │   ├── YieldVault.json       (Contract ABI)
│   │   └── YieldVault.js
│   ├── deployments.json          (Deployment info)
│   └── ...
└── README.md                     (Original docs)
```

---

## Success Criteria

✓ Agent reads live vault data from blockchain
✓ Decisions are deterministic and verifiable
✓ Test suite passes 100%
✓ Can simulate actions without submitting txs
✓ Ready for transaction executor integration

---

## Support

For issues or questions:
1. Check test output: `node test.live.js`
2. Verify RPC connectivity
3. Review contract ABI in `config.deployed.json`
4. Check BNBScan for contract deployment status
