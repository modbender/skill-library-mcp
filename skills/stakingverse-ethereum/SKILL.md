---
name: stakingverse-ethereum
description: Stake ETH on StakeWise (Ethereum liquid staking). Use when the user wants to stake ETH, unstake ETH, or check staked positions on StakeWise V3 vaults. Supports state updates via keeper and harvest proofs from subgraph.
---

# StakeWise Ethereum Staking Skill

Stake ETH on StakeWise V3 and receive osETH (liquid staking token). Earn staking rewards while keeping your ETH liquid.

## What This Skill Does

- **Stake ETH** → Receive osETH tokens (handles state updates automatically)
- **Unstake ETH** → Burn osETH for ETH
- **Check staked position** → View vault shares and earned rewards
- **Monitor vault state** → Check if keeper state update is required
- **Query harvest proofs** → Get Merkle proofs from subgraph for deposits

## Required Credentials

Set these environment variables or edit the scripts:

```bash
export STAKEWISE_VAULT="0x8A93A876912c9F03F88Bc9114847cf5b63c89f56"
export KEEPER="0x6B5815467da09DaA7DC83Db21c9239d98Bb487b5"
export PRIVATE_KEY="your_private_key"
export MY_ADDRESS="your_address"
export RPC_URL="https://ethereum-rpc.publicnode.com"
```

## Quick Start

```bash
# Stake 0.1 ETH (auto-handles state updates)
node scripts/stake.mjs 0.1

# Check staked position
node scripts/position.js

# Unstake 0.05 osETH
node scripts/unstake.js 0.05

# Check if state update required
node scripts/check-state.js
```

## How StakeWise V3 Works

### Architecture Overview

StakeWise V3 uses a **keeper-oracle pattern** for state updates:

```
User (EOA/UP)
    ↓
Vault Contract
    ↓
Keeper (Oracle) - Validates and processes rewards
    ↓
osETH Token - Liquid staking token
```

### Key Components

| Component | Address | Purpose |
|-----------|---------|---------|
| Vault | `0x8A93A876912c9F03F88Bc9114847cf5b63c89f56` | Staking/unstaking logic |
| Keeper | `0x6B5815467da09DaA7DC83Db21c9239d98Bb487b5` | Oracle for state updates |
| osETH Token | Dynamic per vault | Liquid staking token |
| Subgraph | `https://graphs.stakewise.io/mainnet-a/subgraphs/name/stakewise/prod` | Harvest proofs and data |

### The State Update Mechanism

**Why state updates?**
- StakeWise accumulates rewards off-chain via validators
- Keeper periodically "harvests" and posts state on-chain
- Users can only deposit when state is current

**When is state update required?**
```javascript
const vault = new ethers.Contract(vaultAddress, vaultAbi, provider);
const needsUpdate = await vault.isStateUpdateRequired();
// true = must update state before depositing
```

### Staking Flow (With State Update)

```
Step 1: Check State
    User
      ↓
    vault.isStateUpdateRequired()
      ↓
    Returns: true (update needed)

Step 2: Query Subgraph for Harvest Params
    User
      ↓
    POST to StakeWise subgraph
      ↓
    Returns: rewardsRoot, reward, unlockedMevReward, proof[]

Step 3: Update State and Deposit
    User
      ↓
    vault.updateStateAndDeposit(harvestParams, receiver, referrer)
      ↓
    Keeper validates harvest
      ↓
    Vault mints osETH to receiver
      ↓
    User receives osETH
```

## Detailed Usage

### Stake ETH (Full Flow with State Update)

```javascript
import { ethers } from 'ethers';
import fetch from 'node-fetch';

// Setup
const provider = new ethers.JsonRpcProvider(process.env.RPC_URL);
const wallet = new ethers.Wallet(process.env.PRIVATE_KEY, provider);

// Vault ABI (minimal)
const VAULT_ABI = [
  'function isStateUpdateRequired() view returns (bool)',
  'function updateStateAndDeposit(tuple(bytes32 rewardsRoot, uint256 reward, uint256 unlockedMevReward, bytes32[] proof) harvestParams, address receiver, address referrer) external payable',
  'function deposit(address receiver, address referrer) external payable'
];

const vault = new ethers.Contract(
  process.env.STAKEWISE_VAULT,
  VAULT_ABI,
  wallet
);

// Amount to stake
const stakeAmount = ethers.parseEther('0.1'); // 0.1 ETH

// Step 1: Check if state update required
const needsUpdate = await vault.isStateUpdateRequired();
console.log('State update required:', needsUpdate);

if (needsUpdate) {
  // Step 2: Query subgraph for harvest params
  const subgraphQuery = {
    query: `
      query getHarvestProofs($vault: String!) {
        harvestProofs(
          where: { vault: $vault }
          orderBy: blockNumber
          orderDirection: desc
          first: 1
        ) {
          rewardsRoot
          reward
          unlockedMevReward
          proof
        }
      }
    `,
    variables: {
      vault: process.env.STAKEWISE_VAULT.toLowerCase()
    }
  };

  const response = await fetch('https://graphs.stakewise.io/mainnet-a/subgraphs/name/stakewise/prod', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(subgraphQuery)
  });

  const data = await response.json();
  const harvestProof = data.data.harvestProofs[0];

  // Step 3: Call updateStateAndDeposit
  const harvestParams = {
    rewardsRoot: harvestProof.rewardsRoot,
    reward: BigInt(harvestProof.reward),
    unlockedMevReward: BigInt(harvestProof.unlockedMevReward),
    proof: harvestProof.proof
  };

  const tx = await vault.updateStateAndDeposit(
    harvestParams,
    process.env.MY_ADDRESS,  // receiver
    ethers.ZeroAddress,       // referrer (optional)
    { value: stakeAmount }
  );

  const receipt = await tx.wait();
  console.log(`Staked ${ethers.formatEther(stakeAmount)} ETH with state update`);
  console.log(`Transaction: ${receipt.hash}`);
} else {
  // Simple deposit (no state update needed)
  const tx = await vault.deposit(
    process.env.MY_ADDRESS,
    ethers.ZeroAddress,
    { value: stakeAmount }
  );

  const receipt = await tx.wait();
  console.log(`Staked ${ethers.formatEther(stakeAmount)} ETH`);
  console.log(`Transaction: ${receipt.hash}`);
}
```

### Check Staked Position

```javascript
const OSETH_ABI = [
  'function balanceOf(address) view returns (uint256)',
  'function convertToAssets(uint256 shares) view returns (uint256)'
];

// Get osETH token address from vault
const osEthAddress = await vault.osToken();
const osEth = new ethers.Contract(osEthAddress, OSETH_ABI, provider);

const osEthBalance = await osEth.balanceOf(process.env.MY_ADDRESS);
const underlyingEth = await osEth.convertToAssets(osEthBalance);

console.log(`osETH Balance: ${ethers.formatEther(osEthBalance)}`);
console.log(`Equivalent ETH: ${ethers.formatEther(underlyingEth)}`);
```

### Unstake ETH

```javascript
const VAULT_FULL_ABI = [
  'function redeem(uint256 shares, address receiver, address owner) returns (uint256 assets)',
  'function maxRedeem(address owner) view returns (uint256)'
];

const vaultFull = new ethers.Contract(
  process.env.STAKEWISE_VAULT,
  VAULT_FULL_ABI,
  wallet
);

// Check max redeemable
const maxShares = await vaultFull.maxRedeem(process.env.MY_ADDRESS);
console.log(`Max redeemable: ${ethers.formatEther(maxShares)} osETH`);

// Redeem shares for ETH
const sharesToRedeem = ethers.parseEther('0.05');
const tx = await vaultFull.redeem(
  sharesToRedeem,
  process.env.MY_ADDRESS,  // receiver
  process.env.MY_ADDRESS   // owner
);

const receipt = await tx.wait();
console.log(`Redeemed ${ethers.formatEther(sharesToRedeem)} osETH for ETH`);
console.log(`Transaction: ${receipt.hash}`);
```

## Subgraph Queries

### Get Latest Harvest Proof

```javascript
const query = {
  query: `
    query {
      harvestProofs(
        orderBy: blockNumber
        orderDirection: desc
        first: 1
      ) {
        id
        vault
        rewardsRoot
        reward
        unlockedMevReward
        proof
        blockNumber
      }
    }
  `
};

const response = await fetch('https://graphs.stakewise.io/mainnet-a/subgraphs/name/stakewise/prod', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify(query)
});

const data = await response.json();
console.log(data.data.harvestProofs[0]);
```

### Get Vault State

```javascript
const query = {
  query: `
    query {
      vaults(first: 1) {
        id
        address
        totalAssets
        totalShares
        apr
      }
    }
  `
};
```

## Common Issues

### "State update required"
- The keeper hasn't posted recent rewards
- Query subgraph for latest harvest proof
- Use `updateStateAndDeposit()` instead of `deposit()`

### "Invalid harvest proof"
- Proof may be outdated
- Always query subgraph immediately before depositing
- Proofs are block-specific

### "Insufficient shares"
- Trying to redeem more osETH than you have
- Check balance: `osETH.balanceOf(yourAddress)`

### "Vault is paused"
- Emergency pause may be active
- Check: `vault.paused()`
- Wait for StakeWise team to unpause

## Important Notes

- **APY varies**: Based on Ethereum validator rewards, typically 3-5%
- **osETH is rebasing**: Balance increases automatically as rewards accrue
- **Keeper dependency**: Deposits require valid state (keeper must be active)
- **Gas costs**: State updates cost more gas than simple deposits
- **MEV rewards**: Part of harvest includes MEV extraction rewards

## Resources

- StakeWise App: https://app.stakewise.io
- StakeWise Docs: https://docs.stakewise.io
- Subgraph: https://graphs.stakewise.io/mainnet-a/subgraphs/name/stakewise/prod
- Vault: `0x8A93A876912c9F03F88Bc9114847cf5b63c89f56`
- Keeper: `0x6B5815467da09DaA7DC83Db21c9239d98Bb487b5`
