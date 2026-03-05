---
name: stakingverse-lukso
description: Stake LYX tokens on Stakingverse (LUKSO liquid staking). Use when the user wants to stake LYX, unstake LYX, claim rewards, or check sLYX balance on Stakingverse. Supports deposit, withdrawal requests, and oracle-claim pattern.
---

# Stakingverse LUKSO Staking Skill

Stake LYX on Stakingverse and receive sLYX (liquid staking token). Earn ~8% APY while keeping your assets liquid.

## What This Skill Does

- **Stake LYX** → Receive sLYX tokens immediately
- **Request unstake** → Initiate withdrawal (requires oracle processing)
- **Claim unstaked LYX** → After oracle processes withdrawal request
- **Check sLYX balance** → View your staked position
- **Check claimable LYX** → See if withdrawal is ready to claim

## Required Credentials

Set these environment variables or edit the scripts:

```bash
export STAKINGVERSE_VAULT="0x9F49a95b0c3c9e2A6c77a16C177928294c0F6F04"
export MY_UP="your_universal_profile_address"
export CONTROLLER="your_controller_address"
export PRIVATE_KEY="your_controller_private_key"
export RPC_URL="https://rpc.mainnet.lukso.network"
```

## Quick Start

```bash
# Stake 10 LYX
node scripts/stake.js 10

# Check sLYX balance
node scripts/balance.js

# Request unstake of 5 sLYX
node scripts/unstake-request.js 5

# Check if withdrawal is ready
node scripts/check-claim.js

# Claim unstaked LYX (after oracle processes)
node scripts/claim.js
```

## How It Works

### The Stakingverse Architecture

**Stakingverse** is a liquid staking protocol on LUKSO:

- **You stake LYX** → Get sLYX tokens (1:1 ratio)
- **sLYX appreciates** → As staking rewards accrue, 1 sLYX > 1 LYX
- **sLYX is liquid** → Trade, transfer, or use in DeFi while earning
- **Unstaking is 2-step** → Request → Wait for oracle → Claim

### Key Contracts

| Contract | Address | Purpose |
|----------|---------|---------|
| Vault | `0x9F49a95b0c3c9e2A6c77a16C177928294c0F6F04` | Staking/unstaking logic |
| sLYX Token | `0x8a3982f4abcdc30f777910e8b5b5d8242628290a` | Liquid staking token (LSP7) |
| Oracle | Multiple | Validates withdrawal requests |

### Staking Flow

```
You (Controller)
    ↓
KeyManager.execute()
    ↓
UP.execute(CALL, Vault, 10 LYX, deposit())
    ↓
Vault receives LYX
    ↓
Vault mints sLYX to your UP
    ↓
You hold sLYX (earning rewards)
```

### Unstaking Flow (Two-Step)

```
Step 1: Request Withdrawal
    You (Controller)
        ↓
    KeyManager.execute()
        ↓
    UP.execute(CALL, Vault, 0, withdraw(sLYX_amount))
        ↓
    Vault burns sLYX
        ↓
    Oracle queue: withdrawal request created

Step 2: Wait for Oracle
    ↓ (Time passes - oracle processes)

Step 3: Claim LYX
    You (Controller)
        ↓
    KeyManager.execute()
        ↓
    UP.execute(CALL, Vault, 0, claim())
        ↓
    Oracle approves
        ↓
    Vault sends LYX to your UP
```

## Detailed Usage

### Stake LYX

```javascript
const { ethers } = require('ethers');

// Setup
const provider = new ethers.JsonRpcProvider(process.env.RPC_URL);
const wallet = new ethers.Wallet(process.env.PRIVATE_KEY, provider);

// Vault ABI (minimal)
const VAULT_ABI = [
  'function deposit() external payable',
  'function balanceOf(address) view returns (uint256)'
];

const LSP0_ABI = [
  'function execute(uint256 operation, address target, uint256 value, bytes calldata data) external'
];

const LSP6_ABI = [
  'function execute(bytes calldata payload) external payable returns (bytes memory)'
];

// Amount to stake
const stakeAmount = ethers.parseEther('10'); // 10 LYX

// Encode deposit call on Vault
const vaultInterface = new ethers.Interface(VAULT_ABI);
const depositData = vaultInterface.encodeFunctionData('deposit');

// Encode execute call on UP
const upInterface = new ethers.Interface(LSP0_ABI);
const executeData = upInterface.encodeFunctionData('execute', [
  0,                      // operation: CALL
  process.env.STAKINGVERSE_VAULT,  // target: Vault
  stakeAmount,            // value: LYX to stake
  depositData             // data: deposit()
]);

// Send via KeyManager
const keyManager = new ethers.Contract(process.env.KEY_MANAGER, LSP6_ABI, wallet);
const tx = await keyManager.execute(executeData);
const receipt = await tx.wait();

console.log(`Staked ${ethers.formatEther(stakeAmount)} LYX`);
console.log(`Transaction: ${receipt.hash}`);
```

### Check sLYX Balance

```javascript
const SLYX_ABI = ['function balanceOf(address) view returns (uint256)'];

const slyx = new ethers.Contract(
  '0x8a3982f4abcdc30f777910e8b5b5d8242628290a',
  SLYX_ABI,
  provider
);

const balance = await slyx.balanceOf(process.env.MY_UP);
console.log(`sLYX Balance: ${ethers.formatEther(balance)}`);
```

### Request Unstake

```javascript
const amountToUnstake = ethers.parseEther('5'); // 5 sLYX

// Encode withdraw call on Vault
const withdrawData = vaultInterface.encodeFunctionData('withdraw', [amountToUnstake]);

// Encode execute call on UP
const executeData = upInterface.encodeFunctionData('execute', [
  0,                              // operation: CALL
  process.env.STAKINGVERSE_VAULT, // target: Vault
  0,                              // value: 0 (no ETH sent)
  withdrawData                    // data: withdraw(amount)
]);

// Send via KeyManager
const tx = await keyManager.execute(executeData);
await tx.wait();

console.log(`Unstake requested for ${ethers.formatEther(amountToUnstake)} sLYX`);
console.log('Wait for oracle processing, then run claim.js');
```

### Check Claimable LYX

```javascript
const VAULT_FULL_ABI = [
  'function getClaimableAmount(address) view returns (uint256)',
  'function getPendingWithdrawals(address) view returns (uint256)'
];

const vault = new ethers.Contract(
  process.env.STAKINGVERSE_VAULT,
  VAULT_FULL_ABI,
  provider
);

const claimable = await vault.getClaimableAmount(process.env.MY_UP);
const pending = await vault.getPendingWithdrawals(process.env.MY_UP);

console.log(`Claimable LYX: ${ethers.formatEther(claimable)}`);
console.log(`Pending withdrawals: ${ethers.formatEther(pending)}`);
```

### Claim Unstaked LYX

```javascript
// Encode claim call on Vault (no parameters)
const claimData = vaultInterface.encodeFunctionData('claim');

// Encode execute call on UP
const executeData = upInterface.encodeFunctionData('execute', [
  0,
  process.env.STAKINGVERSE_VAULT,
  0,
  claimData
]);

// Send via KeyManager
const tx = await keyManager.execute(executeData);
const receipt = await tx.wait();

console.log(`Claimed LYX to your UP`);
console.log(`Transaction: ${receipt.hash}`);
```

## Transaction Flow Reference

### Standard Pattern: KeyManager → UP → Target

All transactions must follow this flow:

```javascript
// 1. Encode the target contract call
const targetData = targetInterface.encodeFunctionData('functionName', [args]);

// 2. Encode UP.execute() wrapper
const upData = upInterface.encodeFunctionData('execute', [
  0,              // operation type (0 = CALL)
  targetAddress,  // target contract
  value,          // LYX to send (0 for most calls)
  targetData      // encoded function call
]);

// 3. Send via KeyManager
const tx = await keyManager.execute(upData);
```

## Common Issues

### "Insufficient permissions"
- Your controller needs `CALL` and `TRANSFERVALUE` permissions
- Check: `keyManager.getPermissions(controllerAddress)`

### "Withdrawal not ready"
- Oracle hasn't processed your request yet
- Check claimable amount before calling claim()
- Can take hours depending on oracle

### "Invalid amount"
- Trying to unstake more sLYX than you have
- Check balance first: `sLYX.balanceOf(UP_ADDRESS)`

## Important Notes

- **APY varies**: Currently ~8%, but changes based on network conditions
- **sLYX is LSP7**: Fungible token standard (like ERC20)
- **Rewards auto-compound**: sLYX value increases, no need to claim
- **Oracle dependency**: Unstaking requires oracle validation for security
- **Gas costs**: Controller pays gas for all transactions

## Resources

- Stakingverse App: https://app.stakingverse.io
- Stakingverse Docs: https://docs.stakingverse.io
- LUKSO Docs: https://docs.lukso.tech
- sLYX Token: `0x8a3982f4abcdc30f777910e8b5b5d8242628290a`
