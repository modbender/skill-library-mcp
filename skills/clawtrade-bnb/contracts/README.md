# YieldVault Smart Contract

Stub implementation of a yield farming vault contract compatible with the BNB Testnet (chainId: 97) yield farming agent skill.

---

## 📋 Overview

**Network:** BNB Testnet  
**Chain ID:** 97  
**Solidity Version:** 0.8.24  
**Status:** ✅ Ready for Deployment  

### Key Features

✅ **Core Functions**
- `deposit(amount)` - Deposit tokens and receive shares
- `withdraw(shares)` - Burn shares and withdraw tokens
- `harvest()` - Claim yields without reinvesting
- `compound()` - Reinvest yields as new shares

✅ **Agent Events** (required by yield farming agent)
- `ExecutionRecorded` - Tracks all vault actions with vault_id, action, user, amount, shares
- `ActionExecuted` - Records success/failure status of actions

✅ **Data Compatibility**
- Compatible with `mockdata.json` vault structure
- Supports vault_id, token addresses, shares, and amounts
- Integrates with 8 predefined vault configurations

✅ **Admin Functions**
- Pause/unpause vault (emergency)
- Fee management (5% default, adjustable)
- Ownership transfer

---

## 🚀 Quick Start

### 1. Install Dependencies

```bash
cd contracts
npm install
```

### 2. Configure Environment

```bash
cp .env.example .env
# Edit .env with your values:
# - DEPLOYER_ADDRESS (your wallet address)
# - PRIVATE_KEY (your private key, no 0x prefix)
# - RPC_URL (optional, defaults to public testnet RPC)
```

### 3. Check Balance

```bash
npm run check-balance
```

If balance is 0, get testnet BNB from:
https://testnet.binance.org/faucet-smart-chain

### 4. Compile Contract

```bash
npm run compile
```

### 5. Deploy to BNB Testnet

```bash
npm run deploy:testnet
```

**Output:**
```
🚀 YieldVault Multi-Vault Deployment
====================================
Deployer: 0x...

📝 Deploying vault_bnb_lp_001...
   ✅ Deployed to: 0x1234567890123456789012345678901234567890
```

### 6. Verify on BscScan (Optional)

```bash
npm run verify 0x1234567890123456789012345678901234567890
```

---

## 📁 Project Structure

```
contracts/
├── YieldVault.sol              # Main contract (Solidity 0.8.24)
├── deploy.js                   # Viem deployment script (reference)
├── hardhat.config.js           # Hardhat configuration
├── package.json                # Dependencies and scripts
├── .env.example                # Environment template (copy to .env)
├── .gitignore                  # Git ignore rules
│
├── scripts/
│   ├── deploy.js              # Hardhat deployment script
│   ├── check-balance.js       # Check deployer balance
│   └── generate-abi.js        # Generate ABI files
│
├── abi/
│   ├── YieldVault.json        # Contract ABI (JSON)
│   ├── YieldVault.js          # Contract ABI (JS export)
│   └── YieldVault.d.ts        # TypeScript declaration
│
├── DEPLOYMENT.md              # Step-by-step deployment guide
├── ABI_USAGE.md              # ABI integration guide
├── README.md                  # This file
└── deployments.json          # Deployment history (generated)
```

---

## 🛠️ Available Commands

| Command | Description |
|---------|-------------|
| `npm run compile` | Compile Solidity contract |
| `npm run deploy:testnet` | Deploy to BNB Testnet |
| `npm run verify <ADDRESS>` | Verify contract on BscScan |
| `npm run check-balance` | Check deployer account balance |
| `npm run test` | Run contract tests (if available) |
| `npm run clean` | Clean artifacts and cache |
| `npm run flatten` | Flatten contract for verification |
| `npm run generate-abi` | Generate ABI files |

---

## 📝 Contract Details

### Constructor

```solidity
constructor(string memory _vaultId, address _underlying)
```

**Parameters:**
- `_vaultId`: Vault identifier (e.g., "vault_bnb_lp_001")
- `_underlying`: ERC20 token address

**Example:**
```javascript
const vault = await YieldVault.deploy(
  "vault_bnb_lp_001",
  "0xB4FBF271143F901BF5EE8b0E99033aBEA4912312" // USDC testnet
);
```

### Core Functions

#### deposit()
```solidity
function deposit(uint256 amount) 
  external 
  returns (uint256 sharesIssued)
```

- Transfers tokens from user to vault
- Issues shares (initially 1:1, then based on vault price)
- Emits: `Deposit`, `ExecutionRecorded`, `ActionExecuted`

#### withdraw()
```solidity
function withdraw(uint256 shares) 
  external 
  returns (uint256 amountRedeemed)
```

- Burns user's shares
- Returns underlying tokens (minus 5% fee)
- Emits: `Withdraw`, `FeeDeducted`, `ExecutionRecorded`, `ActionExecuted`

#### harvest()
```solidity
function harvest() 
  external 
  returns (uint256 yieldAmount)
```

- Claims accrued yield without reinvesting
- Transfers yield to user
- Emits: `Harvest`, `ExecutionRecorded`, `ActionExecuted`

#### compound()
```solidity
function compound() 
  external 
  returns (uint256 newShares)
```

- Reinvests yield as new shares
- Increases user's vault position
- Emits: `Compound`, `ExecutionRecorded`, `ActionExecuted`

### View Functions

| Function | Returns | Purpose |
|----------|---------|---------|
| `getShareBalance(address user)` | uint256 | Get user's share balance |
| `getTotalAssets()` | uint256 | Get total vault TVL |
| `getTotalShares()` | uint256 | Get total shares issued |
| `getVaultInfo()` | (id, token, assets, shares) | Get vault metadata (mockdata.json compatible) |
| `calculateSharesFromAssets(uint256)` | uint256 | Convert assets to shares |
| `calculateAssetsFromShares(uint256)` | uint256 | Convert shares to assets |
| `calculateUserYield(address user)` | uint256 | Estimate user's pending yield |

---

## 📡 Events

### ExecutionRecorded

Emitted on every vault action (deposit, withdraw, harvest, compound).

```solidity
event ExecutionRecorded(
    string indexed vaultId,
    string action,
    address indexed user,
    uint256 amount,
    uint256 shares,
    uint256 timestamp
);
```

**Example Usage (Agent):**
```javascript
contract.on('ExecutionRecorded', (vaultId, action, user, amount, shares, timestamp) => {
  console.log(`[${vaultId}] ${action} by ${user}`);
  console.log(`  Amount: ${amount}, Shares: ${shares}`);
  console.log(`  Time: ${new Date(timestamp * 1000)}`);
});
```

### ActionExecuted

Emitted with execution status and message.

```solidity
event ActionExecuted(
    string indexed vaultId,
    string action,
    address indexed user,
    uint256 indexed amount,
    bool success,
    string message
);
```

---

## 🔌 Integration with Yield Farming Agent

### 1. Import ABI

```javascript
const YieldVaultABI = require('./abi/YieldVault.json');
```

### 2. Create Contract Instance

```javascript
const contract = new ethers.Contract(
  deployedAddress,
  YieldVaultABI,
  provider
);
```

### 3. Call Functions

```javascript
// Deposit
const depositTx = await contract.deposit(ethers.parseUnits('100', 18));
await depositTx.wait();

// Get user info
const shares = await contract.getShareBalance(userAddress);
const yield = await contract.calculateUserYield(userAddress);

// Get vault info (mockdata.json compatible)
const [vaultId, token, totalAssets, totalShares] = await contract.getVaultInfo();

// Harvest
const harvestTx = await contract.harvest();
await harvestTx.wait();

// Compound
const compoundTx = await contract.compound();
await compoundTx.wait();
```

### 4. Listen to Events

```javascript
contract.on('ExecutionRecorded', (vaultId, action, user, amount, shares, timestamp) => {
  // Update agent skill with execution record
  agentSkill.recordExecution({
    vaultId,
    action,
    user,
    amount: amount.toString(),
    shares: shares.toString(),
    timestamp: timestamp.toNumber()
  });
});
```

---

## 🔗 Vault Configurations (from mockdata.json)

The contract is preconfigured with 8 vault types:

| Vault ID | Name | Token | APR | Strategy |
|----------|------|-------|-----|----------|
| vault_bnb_lp_001 | BNB-BUSD LP Yield | USDC | 45% | Liquidity Mining |
| vault_eth_staking_001 | ETH Staking | WETH | 8% | Staking |
| vault_cake_farm_001 | CAKE Farming | CAKE | 65% | Auto-Compound |
| vault_usdc_stable_001 | USDC Stable | USDC | 12% | Lending |
| vault_btc_hodl_001 | BTC Wrapper | WBTC | 35% | Liquidity Mining |
| vault_high_risk_001 | Exotic Yield | EXOTIC | 250% | Leveraged (HIGH RISK) |
| vault_bnb_native_001 | BNB Staking | BNB | 6% | Staking |
| vault_link_oracle_001 | LINK Rewards | LINK | 42% | Oracle Participation |

Deploy multiple vault instances, one per vault type.

---

## 🧪 Testing

### Run Tests

```bash
npm run test
```

### Create a Test File

```javascript
// test/YieldVault.test.js
const { expect } = require("chai");

describe("YieldVault", function () {
  let vault;
  let owner, user;

  beforeEach(async function () {
    [owner, user] = await ethers.getSigners();
    
    const YieldVault = await ethers.getContractFactory("YieldVault");
    vault = await YieldVault.deploy(
      "test_vault",
      "0xB4FBF271143F901BF5EE8b0E99033aBEA4912312"
    );
  });

  it("Should initialize with correct vault ID", async function () {
    expect(await vault.vaultId()).to.equal("test_vault");
  });

  it("Should calculate shares correctly on empty vault", async function () {
    const shares = await vault.calculateSharesFromAssets(100);
    expect(shares).to.equal(100); // 1:1 on empty vault
  });
});
```

---

## 🌐 BNB Testnet Resources

**Faucet:** https://testnet.binance.org/faucet-smart-chain  
**Explorer:** https://testnet.bscscan.com  
**RPC:** https://data-seed-prebsc-1-b7a35f9.binance.org:8545  
**Chain ID:** 97  

---

## 📊 Gas Estimates

| Function | Gas (approx) | Cost @ 10 Gwei (tBNB) |
|----------|--------------|----------------------|
| Deploy | 2,500,000 | 0.025 |
| Deposit | 150,000 | 0.0015 |
| Withdraw | 200,000 | 0.002 |
| Harvest | 180,000 | 0.0018 |
| Compound | 220,000 | 0.0022 |

---

## 🔒 Security Notes

⚠️ **This is a stub implementation for agent integration testing.**

- NOT audited for production use
- Limited error handling
- Simplified yield calculation (stub: 10% APY)
- No reentrancy guards (add for production)
- No access control beyond owner modifier

**For Production:**
1. Add OpenZeppelin contracts (SafeERC20, ReentrancyGuard, Ownable)
2. Implement proper yield calculation
3. Add comprehensive tests
4. Security audit
5. Gradual rollout with limits

---

## 📖 Documentation

- **DEPLOYMENT.md** - Step-by-step deployment guide
- **ABI_USAGE.md** - API reference and integration examples
- **YieldVault.sol** - Contract source with detailed comments

---

## 🤝 Support

For questions or issues:

1. Check **DEPLOYMENT.md** for deployment help
2. Review **ABI_USAGE.md** for integration questions
3. Check BNB Chain documentation: https://docs.bnbchain.org/
4. BscScan Help: https://docs.bscscan.com/

---

## ✨ Deployment Checklist

- [ ] Copy `.env.example` to `.env`
- [ ] Fill in `DEPLOYER_ADDRESS` and `PRIVATE_KEY`
- [ ] Run `npm install`
- [ ] Run `npm run check-balance` (ensure you have testnet BNB)
- [ ] Run `npm run compile`
- [ ] Run `npm run deploy:testnet`
- [ ] Save contract addresses from `deployments.json`
- [ ] (Optional) Run `npm run verify <ADDRESS>` to verify on BscScan
- [ ] Copy ABI from `abi/YieldVault.json` to agent skill
- [ ] Test contract interactions

---

**Created:** 2026-02-17  
**Status:** ✅ Ready for Agent Integration  
**Network:** BNB Testnet (chainId: 97)
