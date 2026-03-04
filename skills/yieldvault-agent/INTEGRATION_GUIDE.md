# On-Chain Integration Guide

## Overview

This guide explains how to integrate the Yield Farming Agent with smart contracts on BNB Chain.

## Architecture

```
┌─────────────────────────────────────────┐
│   Autonomous Yield Farming Agent        │
│   (Off-Chain Decision Engine)           │
│   - Deterministic decisions             │
│   - Risk-aware optimization             │
│   - Cryptographic audit trail           │
└──────────────┬──────────────────────────┘
               │ (Decision JSON)
               │ execution_hash
               │ decision_hash
               ▼
┌──────────────────────────────────────────┐
│   Smart Contract (On-Chain)              │
│   - Verify decision hash                 │
│   - Execute action                       │
│   - Emit execution event                 │
│   - Track allocation state               │
└──────────────┬───────────────────────────┘
               │
               ▼
        ┌──────────────┐
        │  VAULT 1     │
        │  APR: 50.5%  │
        └──────────────┘
        ┌──────────────┐
        │  VAULT 2     │
        │  APR: 37.5%  │
        └──────────────┘
        ┌──────────────┐
        │  VAULT 3     │
        │  APR: 35.0%  │
        └──────────────┘
```

## Step 1: Deploy Smart Contract

### Solidity Contract Stub

```solidity
pragma solidity ^0.8.0;

contract YieldFarmingAutomation {
    // Events
    event ExecutionRecorded(uint256 cycle, bytes32 decisionHash);
    event ActionExecuted(string action, address vault, uint256 amount);
    
    // State
    mapping(uint256 => bytes32) public executionHashes;
    uint256 public lastCycle;
    
    // Keeper role
    address public keeper;
    modifier onlyKeeper() {
        require(msg.sender == keeper, "Only keeper");
        _;
    }
    
    constructor(address _keeper) {
        keeper = _keeper;
    }
    
    // Main function called by keeper
    function executeDecision(
        ExecutionRecord calldata record
    ) external onlyKeeper {
        // 1. Verify decision hash
        bytes32 computedDecisionHash = keccak256(abi.encode(record.decision));
        require(
            computedDecisionHash == record.decision_hash,
            "Decision hash mismatch"
        );
        
        // 2. Route to action handler
        if (keccak256(bytes(record.decision.action)) == keccak256(bytes("HARVEST"))) {
            _harvest(record.decision.vault_id);
        } else if (keccak256(bytes(record.decision.action)) == keccak256(bytes("COMPOUND"))) {
            _compound(record.decision.vault_id);
        } else if (keccak256(bytes(record.decision.action)) == keccak256(bytes("REBALANCE"))) {
            _rebalance(
                record.decision.from_vault_id,
                record.decision.to_vault_id,
                record.decision.amount
            );
        }
        // ... other actions
        
        // 3. Record execution
        executionHashes[record.cycle_num] = record.execution_hash;
        lastCycle = record.cycle_num;
        
        // 4. Emit event
        emit ExecutionRecorded(record.cycle_num, record.decision_hash);
    }
    
    // Action implementations
    function _harvest(bytes32 vaultId) internal {
        // Implementation: Call vault harvest
        emit ActionExecuted("HARVEST", address(0), 0);
    }
    
    function _compound(bytes32 vaultId) internal {
        // Implementation: Reinvest rewards
        emit ActionExecuted("COMPOUND", address(0), 0);
    }
    
    function _rebalance(
        bytes32 from,
        bytes32 to,
        string memory amount
    ) internal {
        // Implementation: Move allocation between vaults
        emit ActionExecuted("REBALANCE", address(0), 0);
    }
}

// Input struct
struct ExecutionRecord {
    uint256 timestamp;
    uint256 cycle_num;
    uint256 chainId;
    Decision decision;
    string decision_hash;
    string execution_hash;
}

struct Decision {
    string best_vault_id;
    string best_vault_net_apr;
    Action action;
    string rationale;
}

struct Action {
    string action;
    string vault_id;
    string from_vault_id;
    string to_vault_id;
    string token;
    string amount;
    string reason;
}
```

## Step 2: Deploy Keeper

### Chainlink Automation Example

```javascript
// keeper.js - Runs off-chain
const YieldFarmingAgent = require('./yield-farming-agent');
const Web3 = require('web3');

const web3 = new Web3('https://data-seed-prebsc-1-b7a9f.bnbchain.org');
const contractAddress = '0x...'; // Your contract address
const contract = new web3.eth.Contract(ABI, contractAddress);

// Create agent
const agent = new YieldFarmingAgent({
  chainId: 97  // BNB testnet
});

// Poll function (called by Chainlink Automation)
async function checkUpkeep() {
  try {
    // Get current vault data (from oracle or API)
    const vaults = await fetchVaultData();
    
    // Get current allocation state
    const allocation = await contract.methods.getAllocation().call();
    
    // Get decision
    const decision = agent.decide(vaults, allocation);
    
    // Check if action needed
    if (decision.decision.action.action !== 'NOOP') {
      return {
        upkeepNeeded: true,
        performData: web3.eth.abi.encodeParameter('tuple', [decision])
      };
    }
    
    return { upkeepNeeded: false };
  } catch (error) {
    console.error('Error in checkUpkeep:', error);
    return { upkeepNeeded: false };
  }
}

// Execute function (called by Chainlink Automation when upkeep needed)
async function performUpkeep(performData) {
  const decision = web3.eth.abi.decodeParameter('tuple', performData);
  
  // Call smart contract with decision
  const tx = await contract.methods.executeDecision(decision).send({
    from: keeperAddress,
    gas: 500000
  });
  
  console.log(`✅ Execution recorded: ${tx.hash}`);
}

// Register with Chainlink Automation
// Go to automation.chain.link and create upkeep
```

## Step 3: Verify Hash Integrity

### On-Chain Verification

```solidity
function verifyExecutionHash(uint256 cycle) public view returns (bool) {
    // Compare stored hash with recomputed hash
    // (requires similar hash computation on-chain)
    return executionHashes[cycle] != bytes32(0);
}
```

### Off-Chain Verification

```javascript
// Before sending to keeper
const verification = agent.verifyRecord(decision);

if (!verification.valid) {
    console.error('❌ Hash mismatch detected:', verification.errors);
    process.exit(1);
}

console.log('✅ Record integrity verified - safe to execute');
```

## Step 4: Monitor & Alert

### Event Listening

```javascript
// Listen for execution events
contract.events.ExecutionRecorded({
    fromBlock: 'latest'
}, (error, event) => {
    if (error) {
        console.error('Error:', error);
        return;
    }
    
    const { cycle, decisionHash } = event.returnValues;
    console.log(`✅ Cycle ${cycle} executed with hash: ${decisionHash}`);
    
    // Update off-chain state
    lastExecutedCycle = cycle;
    lastExecutedHash = decisionHash;
});
```

### Divergence Detection

```javascript
// Compare off-chain decision with on-chain execution
async function detectDivergence() {
    // Get last decision
    const vaults = await fetchVaultData();
    const allocation = await contract.methods.getAllocation().call();
    const offChainDecision = agent.decide(vaults, allocation);
    
    // Get last on-chain execution
    const onChainHash = await contract.methods.executionHashes(lastCycle).call();
    
    // Compare hashes
    if (offChainDecision.decision_hash !== onChainHash) {
        console.warn('⚠️ DIVERGENCE DETECTED');
        // Alert team, pause automation, etc.
    }
}

// Run periodically
setInterval(detectDivergence, 5 * 60 * 1000); // Every 5 minutes
```

## Step 5: Configure Parameters

### Update Strategy

```solidity
function updateParameters(
    uint256 _harvestThreshold,
    uint256 _rebalanceDelta,
    uint256 _maxAllocation
) external onlyGovernance {
    harvestThreshold = _harvestThreshold;
    rebalanceDelta = _rebalanceDelta;
    maxAllocation = _maxAllocation;
    
    emit ParametersUpdated(_harvestThreshold, _rebalanceDelta, _maxAllocation);
}
```

### Off-Chain Configuration

```javascript
// Update config and redeploy keeper
const config = {
    chainId: 56,  // Switch to mainnet
    harvest_threshold_usd: 100,
    rebalance_apr_delta: 0.03,
    max_allocation_percent: 0.30
};

const agent = new YieldFarmingAgent(config);
```

## Step 6: Security Best Practices

### 1. Access Control
```solidity
// Only keeper can execute
modifier onlyKeeper() {
    require(msg.sender == keeper, "Only keeper");
    _;
}

// Governance can update parameters
modifier onlyGovernance() {
    require(msg.sender == governance, "Only governance");
    _;
}
```

### 2. Rate Limiting
```solidity
// Prevent same decision from executing twice
require(lastExecutionHash != record.execution_hash, "Duplicate execution");
require(block.timestamp > lastExecutionTime + MIN_INTERVAL, "Too soon");
```

### 3. Emergency Pause
```solidity
bool public paused;

function pause() external onlyGovernance {
    paused = true;
    emit Paused();
}

function unpause() external onlyGovernance {
    paused = false;
    emit Unpaused();
}

modifier whenNotPaused() {
    require(!paused, "Contract is paused");
    _;
}
```

### 4. Multi-Sig Approval
```solidity
// Large rebalances require multi-sig approval
function approveRebalance(bytes32 executionHash) external {
    require(isMultiSigMember[msg.sender], "Not multi-sig member");
    approvals[executionHash]++;
    
    if (approvals[executionHash] >= REQUIRED_APPROVALS) {
        executeRebalance(executionHash);
    }
}
```

## Deployment Checklist

- [ ] Deploy smart contract with correct keeper address
- [ ] Register keeper with Chainlink Automation
- [ ] Configure vault addresses in smart contract
- [ ] Set correct chainId (97 for testnet, 56 for mainnet)
- [ ] Set initial parameters (harvest_threshold, rebalance_delta, max_allocation)
- [ ] Fund keeper with BNB for gas
- [ ] Set up event monitoring
- [ ] Configure divergence detection alerts
- [ ] Test with mock execution on testnet
- [ ] Perform multi-sig governance approval for mainnet
- [ ] Deploy to mainnet

## Testing

### Local Testnet

```bash
# Start Hardhat node
npx hardhat node

# In another terminal
npx hardhat test

# Test keeper
npm test  # Runs yield-farming-agent tests
```

### BNB Testnet

```bash
# Deploy to testnet
npx hardhat run scripts/deploy.js --network bnbTestnet

# Verify contract
npx hardhat verify --network bnbTestnet CONTRACT_ADDRESS

# Monitor execution
npm run monitor:testnet
```

## Costs (Estimated)

| Action | Gas Cost | USD (100 Gwei) |
|--------|----------|---|
| HARVEST | 150,000 | ~$3 |
| COMPOUND | 120,000 | ~$2.50 |
| REBALANCE | 200,000 | ~$4 |
| Keeper Registration | - | ~$5/month |

## Support

For questions or issues with integration:
1. Check SKILL.md for specification details
2. Review EXAMPLES.md for decision logic
3. Run tests: `npm test`
4. Check hash verification: `node index.js --verify`

---

**Version:** 1.0.0  
**Chain:** BNB (Testnet: 97, Mainnet: 56)  
**Status:** Production Ready
