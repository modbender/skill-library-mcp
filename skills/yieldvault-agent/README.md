# Autonomous Yield Farming Agent Skill

**Status:** ✅ Production Ready | **Chain:** BNB Testnet (97) / Mainnet (56) | **Model:** Deterministic Decision Engine

## Quick Start

### Installation

```bash
npm install
# or link as OpenClaw skill
ln -s /home/ubuntu/.openclaw/workspace/skills/yield-farming-agent /path/to/openclaw/skills/
```

### Basic Usage

```javascript
const YieldFarmingAgent = require('./index.js');
const mockdata = require('./mockdata.json');

const agent = new YieldFarmingAgent({
  chainId: 97,
  harvest_threshold_usd: 25,
  rebalance_apr_delta: 0.02,
  max_allocation_percent: 0.35
});

// Your current position state
const allocation = {
  vault_bnb_lp_001: {
    shares: "1000",
    amount_usd: "50000",
    pending_rewards_usd: "1200"
  }
};

// Get deterministic decision
const decision = agent.decide(mockdata.vaults, allocation);
console.log(JSON.stringify(decision, null, 2));
```

### CLI Execution

```bash
# Run with default example
node index.js

# Run with hash verification
node index.js --verify
```

## Decision Flow

```
┌─────────────────────────────────────────────────┐
│  1. Load Vaults & Filter by Risk (score ≤ 0.5)  │
└────────────────────┬────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────┐
│  2. Calculate NET_APR = apr - fees - risk_penalty │
│     (risk_penalty = risk_score × 0.10)           │
└────────────────────┬────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────┐
│  3. Rank by NET_APR (descending)                │
│     → Select best_vault                         │
└────────────────────┬────────────────────────────┘
                     │
          ┌──────────┴──────────┐
          │                     │
    ┌─────▼─────┐        ┌─────▼──────┐
    │ HARVEST?  │        │ COMPOUND?  │
    │ rewards   │        │ net_apr >=  │
    │ >= $25    │        │ threshold   │
    └─────┬─────┘        └─────┬──────┘
          │ YES                │ YES
          ├─────────┬──────────┤
          │         │          │
    ┌─────▼──┐  ┌──▼─┐  ┌─────▼──┐
    │HARVEST │  │YES │  │COMPOUND│
    └────────┘  │    │  └────────┘
                │    │
              NO│    │NO
                │    │
          ┌─────▼────▼─────┐
          │  REBALANCE?    │
          │  better vault  │
          │  exists?       │
          └────────┬───────┘
                   │
           ┌───────┴────────┐
           │ YES            │ NO
       ┌───▼──┐        ┌────▼──┐
       │REBALNCE│       │ NOOP  │
       └────────┘       └───────┘
```

## Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `chainId` | 97 | BNB Testnet ID (mainnet: 56) |
| `harvest_threshold_usd` | 25 | Minimum pending rewards to trigger harvest |
| `rebalance_apr_delta` | 0.02 | Minimum APR delta (2%) to trigger rebalance |
| `max_allocation_percent` | 0.35 | Maximum 35% allocation to single vault |

## Vault States (in execution output)

```json
{
  "id": "vault_bnb_lp_001",
  "name": "BNB-BUSD LP Yield",
  "net_apr": "0.375000",
  "allocation_percent": "41.67",
  "pending_rewards_usd": "1200.00",
  "risk_score": "0.25"
}
```

- **net_apr**: Effective APR after fees and risk penalty
- **allocation_percent**: Current $ allocation / total portfolio
- **pending_rewards_usd**: Harvestable rewards value
- **risk_score**: 0-1 scale (vaults > 0.5 filtered out)

## Action Types

### DEPOSIT
```json
{
  "action": "DEPOSIT",
  "vault_id": "vault_bnb_lp_001",
  "token": "BNB-BUSD",
  "amount": "10000.00"
}
```
*Deposit funds into a vault.*

### WITHDRAW
```json
{
  "action": "WITHDRAW",
  "vault_id": "vault_bnb_lp_001",
  "token": "LP-SHARES",
  "amount": "500.00"
}
```
*Exit position by withdrawing LP shares.*

### HARVEST
```json
{
  "action": "HARVEST",
  "vault_id": "vault_bnb_lp_001",
  "token": "CAKE",
  "amount": "1200.00"
}
```
*Claim accumulated rewards when >= threshold.*

### COMPOUND
```json
{
  "action": "COMPOUND",
  "vault_id": "vault_cake_farm_001",
  "token": "CAKE",
  "amount": "2525.00"
}
```
*Reinvest rewards back into vault when APR high.*

### REBALANCE
```json
{
  "action": "REBALANCE",
  "from_vault_id": "vault_bnb_lp_001",
  "to_vault_id": "vault_link_oracle_001",
  "token": "BNB-BUSD",
  "amount": "25000.00"
}
```
*Move allocation from lower to higher APR vault.*

### NOOP
```json
{
  "action": "NOOP",
  "vault_id": "vault_cake_farm_001",
  "reason": "all_optimized"
}
```
*No action needed - portfolio already optimized.*

## Hash Verification

Every execution record includes cryptographic audit trail:

```javascript
const agent = new YieldFarmingAgent();
const execution = agent.decide(vaults, allocation);

// Verify hashes
const verification = agent.verifyRecord(execution);
if (verification.valid) {
  console.log('✅ Record integrity verified');
} else {
  console.log('❌ Hash mismatch detected:', verification.errors);
}
```

**Hashes Included:**
- `decision_hash` - SHA256 of decision object
- `execution_hash` - SHA256 of full record (excluding execution_hash itself)

## Risk Score & Net APR Calculation

### Net APR Formula

```
risk_penalty = risk_score × 0.10
net_apr = apr - fees - risk_penalty

Example:
  vault_cake_farm_001:
  apr = 0.65 (65%)
  fees = 0.10 (10%)
  risk_score = 0.45 (45% risk)
  risk_penalty = 0.45 × 0.10 = 0.045
  net_apr = 0.65 - 0.10 - 0.045 = 0.505 (50.5%)
```

### Risk Filter

Only vaults with `risk_score ≤ 0.5` are considered.

**Filtered OUT:**
- `vault_high_risk_001` (risk_score: 0.80)

**Included:**
- All other vaults with risk_score ≤ 0.5

## Example: Execution Record

See `execution.example.json` for complete output structure.

**Key insight:** The engine selected **COMPOUND** action for the CAKE vault because:
- Best vault (highest NET_APR): `vault_cake_farm_001` with 50.5% NET APR
- No pending rewards to harvest
- Net APR (50.5%) exceeds compound threshold (2%)
- Decision: Reinvest gains back into vault

## Next Steps: On-Chain Integration

### 1. Smart Contract Adapter
```solidity
// Pseudo-code
contract YieldFarmingAutomation {
  bytes32 public lastDecisionHash;
  
  function executeDecision(ExecutionRecord calldata record) external onlyKeeper {
    require(record.decision_hash == computeHash(record.decision), "Hash mismatch");
    
    // Route to appropriate action handler
    if (record.decision.action == "HARVEST") {
      _harvest(record.decision.vault_id);
    } else if (record.decision.action == "REBALANCE") {
      _rebalance(record.decision.from_vault_id, record.decision.to_vault_id);
    }
    // ...
    
    lastDecisionHash = record.execution_hash;
    emit ExecutionRecorded(record.cycle_num, record.decision_hash);
  }
}
```

### 2. Keeper Integration
- Deploy keeper contract (Chainlink Automation, Gelato, etc.)
- Keeper polls `decide()` off-chain
- If action needed, calls `executeDecision()` on-chain
- Emit event for indexing

### 3. State Tracking
- Maintain vault TVL & APR on-chain (oracle feed)
- Store execution hashes for audit trail
- Monitor for decision divergence (off-chain vs on-chain)

### 4. Governance
- Consider multi-sig approval for large rebalances
- Time-lock for parameter updates
- Pause mechanism for emergency

## File Structure

```
yield-farming-agent/
├── index.js                 # Main decision engine
├── mockdata.json           # Sample vault data
├── config.default.json     # Default parameters
├── execution.example.json  # Example output
├── SKILL.md               # Specification
├── README.md              # This file
└── package.json           # (optional) Dependencies
```

## Performance

- **Decision time:** < 5ms (Node.js on standard hardware)
- **Vault states:** 8 vaults in example
- **Scalability:** Linear O(n) where n = number of vaults
- **Determinism:** 100% - Same input → Same output, same hashes

## License

MIT
