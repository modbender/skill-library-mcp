# YieldVault Smart Contract Deployment Guide

**Network:** BNB Testnet (chainId: 97)  
**Contract:** YieldVault.sol (Solidity 0.8.24)  
**Status:** Stub implementation ready for agent integration

---

## 📋 Table of Contents

1. [Prerequisites](#prerequisites)
2. [Setup](#setup)
3. [Configuration](#configuration)
4. [Compilation](#compilation)
5. [Deployment](#deployment)
6. [Verification](#verification)
7. [Integration](#integration)
8. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Required Software

- **Node.js** >= 18.0
- **npm** or **yarn**
- **Hardhat** (recommended) or **Foundry** (alternative)
- **Git**

### Required Accounts

- **BNB Testnet Account** with private key
- **BNB Testnet Tokens** for gas fees (get from faucet)
- **(Optional) BscScan Account** for contract verification

### Installation

```bash
# Install Node.js dependencies
npm install

# Install Hardhat (if not already done)
npm install --save-dev hardhat

# Initialize Hardhat (if needed)
npx hardhat
```

---

## Setup

### 1. Create a BNB Testnet Account

If you don't have one:

```bash
# Generate a new private key (using OpenSSL or online tools)
openssl rand -hex 32

# Or use Hardhat to generate an account
npx hardhat account
```

**Never share your private key!**

### 2. Get Testnet BNB

Visit the official BNB Testnet Faucet:

- **URL:** https://testnet.binance.org/faucet-smart-chain
- **Amount:** 2-5 tBNB per request
- **Wait Time:** 24 hours between requests
- **Fund Wallet:** Use your account address (0x...)

Verify you have funds:

```bash
npm run check-balance
```

---

## Configuration

### 1. Copy Environment File

```bash
cd contracts
cp .env.example .env
```

### 2. Edit `.env` with Your Values

```bash
nano .env
# or
vim .env
```

**Fill in:**

```env
# Your deployer wallet address
DEPLOYER_ADDRESS=0x1234567890123456789012345678901234567890

# Your private key (NO 0x prefix)
PRIVATE_KEY=1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef

# BNB Testnet RPC (default works, or use your own)
RPC_URL=https://data-seed-prebsc-1-b7a35f9.binance.org:8545
```

### 3. Verify Configuration

```bash
npm run verify-env
```

Expected output:
```
✅ DEPLOYER_ADDRESS is set
✅ PRIVATE_KEY is set
✅ RPC_URL is accessible
✅ Wallet has sufficient balance
```

---

## Compilation

### Using Hardhat

#### 1. Create `hardhat.config.js`

```javascript
require("@nomicfoundation/hardhat-toolbox");
require("dotenv").config();

module.exports = {
  solidity: "0.8.24",
  networks: {
    bnbTestnet: {
      url: process.env.RPC_URL || "https://data-seed-prebsc-1-b7a35f9.binance.org:8545",
      accounts: process.env.PRIVATE_KEY ? [process.env.PRIVATE_KEY] : [],
      chainId: 97,
    },
  },
  etherscan: {
    apiKey: {
      bscTestnet: process.env.BSCSCAN_API_KEY || "",
    },
  },
};
```

#### 2. Compile the Contract

```bash
npx hardhat compile
```

**Output:**
```
Compiling 1 file with 0.8.24
YieldVault compiled successfully
```

Compiled artifacts are saved to: `artifacts/contracts/`

---

## Deployment

### Option A: Using Hardhat Deploy Script

#### 1. Create `scripts/deploy.js`

```javascript
const hre = require("hardhat");

async function main() {
  console.log("🚀 Deploying YieldVault...");

  const YieldVault = await hre.ethers.getContractFactory("YieldVault");

  const vaultId = "vault_bnb_lp_001";
  const underlyingToken = "0xB4FBF271143F901BF5EE8b0E99033aBEA4912312"; // USDC testnet

  const vault = await YieldVault.deploy(vaultId, underlyingToken);
  await vault.deployed();

  console.log("✅ YieldVault deployed to:", vault.address);
  console.log("   Vault ID:", vaultId);
  console.log("   Underlying Token:", underlyingToken);

  return vault.address;
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error(error);
    process.exit(1);
  });
```

#### 2. Deploy to BNB Testnet

```bash
npx hardhat run scripts/deploy.js --network bnbTestnet
```

**Expected Output:**
```
🚀 Deploying YieldVault...
✅ YieldVault deployed to: 0x1234...
   Vault ID: vault_bnb_lp_001
   Underlying Token: 0xB4FB...
```

### Option B: Using web3.js Deployment

```javascript
// deploy-web3.js
const Web3 = require('web3');
const fs = require('fs');
require('dotenv').config();

const web3 = new Web3(process.env.RPC_URL);

async function deploy() {
  const account = web3.eth.accounts.privateKeyToAccount('0x' + process.env.PRIVATE_KEY);
  web3.eth.accounts.wallet.add(account);

  const contract = new web3.eth.Contract(ABI); // Load ABI
  const bytecode = fs.readFileSync('./contracts/YieldVault.json').bytecode;

  const tx = contract.deploy({
    data: bytecode,
    arguments: ['vault_bnb_lp_001', '0xB4FBF271143F901BF5EE8b0E99033aBEA4912312']
  });

  const receipt = await tx.send({
    from: account.address,
    gas: 3000000,
    gasPrice: web3.utils.toWei('10', 'gwei')
  });

  console.log('✅ Deployed to:', receipt.contractAddress);
  return receipt.contractAddress;
}

deploy().catch(console.error);
```

---

## Verification

### Using BscScan (Public Explorer)

#### 1. Get BscScan API Key

- Visit: https://bscscan.com/apis
- Create a free account
- Generate an API key
- Add to `.env`: `BSCSCAN_API_KEY=...`

#### 2. Verify Contract

```bash
npx hardhat verify --network bnbTestnet <CONTRACT_ADDRESS> "vault_bnb_lp_001" "0xB4FBF271143F901BF5EE8b0E99033aBEA4912312"
```

**Expected Output:**
```
✅ Contract verified successfully
View at: https://testnet.bscscan.com/address/<CONTRACT_ADDRESS>
```

### Manual Verification

1. Go to: https://testnet.bscscan.com
2. Search for your contract address
3. Click "Contract" tab
4. Upload `YieldVault.sol` and constructor arguments
5. Mark as verified ✅

---

## Integration

### 1. Contract ABI Export

The contract ABI is automatically generated during compilation:

```
artifacts/contracts/YieldVault.sol/YieldVault.json
```

Use in your agent skill:

```javascript
const YieldVaultABI = require('./artifacts/contracts/YieldVault.sol/YieldVault.json').abi;

const contract = new ethers.Contract(
  deployedAddress,
  YieldVaultABI,
  provider
);
```

### 2. Compatible Events

The contract emits two event types required by the agent:

```solidity
event ExecutionRecorded(
    string indexed vaultId,
    string action,
    address indexed user,
    uint256 amount,
    uint256 shares,
    uint256 timestamp
);

event ActionExecuted(
    string indexed vaultId,
    string action,
    address indexed user,
    uint256 indexed amount,
    bool success,
    string message
);
```

Listen for events:

```javascript
contract.on('ExecutionRecorded', (vaultId, action, user, amount, shares, timestamp) => {
  console.log(`[${vaultId}] ${action} executed by ${user}`);
});
```

### 3. Data Structure Compatibility

The contract is compatible with `mockdata.json`:

```json
{
  "vault_id": "vault_bnb_lp_001",
  "token": "0xB4FBF271143F901BF5EE8b0E99033aBEA4912312",
  "shares": 1000000000000000000,
  "amount": 500000000000000000
}
```

Interact with the contract:

```javascript
// Deposit
const tx = await vault.deposit(ethers.parseUnits('100', 18));

// Get user shares
const shares = await vault.getShareBalance(userAddress);

// Get vault info (compatible with mockdata structure)
const [vaultId, token, totalAssets, totalShares] = await vault.getVaultInfo();
```

---

## Troubleshooting

### Common Issues

#### 1. **"PRIVATE_KEY is not set"**

```bash
# Ensure .env file exists and has PRIVATE_KEY
cat .env | grep PRIVATE_KEY

# Should output: PRIVATE_KEY=1234567890...
```

#### 2. **"Insufficient Funds"**

```bash
# Request more testnet BNB from faucet
# https://testnet.binance.org/faucet-smart-chain

# Check balance
npx hardhat run --network bnbTestnet scripts/check-balance.js
```

#### 3. **"RPC Connection Failed"**

```bash
# Test RPC endpoint
curl https://data-seed-prebsc-1-b7a35f9.binance.org:8545 \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"eth_blockNumber","params":[],"id":1}'

# Try alternate RPC endpoint
# https://data-seed-prebsc-2-b7a35f9.binance.org:8545
```

#### 4. **"Compilation Error: Unknown pragma"**

```bash
# Update Hardhat version
npm install --save-dev @nomicfoundation/hardhat-toolbox@latest

# Ensure Solidity 0.8.24 is supported
npx hardhat compile --version
```

#### 5. **"Gas Limit Exceeded"**

```javascript
// Increase gas limit in hardhat.config.js
networks: {
  bnbTestnet: {
    gas: 5000000,  // Increase from default
    gasPrice: "auto"
  }
}
```

### Getting Help

- **Hardhat Docs:** https://hardhat.org/
- **BNB Chain Docs:** https://docs.bnbchain.org/
- **BscScan API:** https://docs.bscscan.com/
- **Solidity Docs:** https://docs.soliditylang.org/

---

## Quick Reference Commands

```bash
# Check balance
npm run balance

# Compile contracts
npm run compile

# Deploy to testnet
npm run deploy:testnet

# Verify contract
npm run verify <ADDRESS>

# View deployment artifacts
ls artifacts/contracts/

# Reset compilation cache
rm -rf artifacts cache
npm run compile
```

---

## Security Notes

⚠️ **IMPORTANT**

1. **Never commit `.env` to version control** - Add to `.gitignore`:
   ```
   .env
   .env.local
   *.key
   private_key*
   ```

2. **Keep private keys secret** - If compromised:
   - Create a new wallet immediately
   - Move all funds
   - Never reuse the compromised key

3. **Use testnet for development** - Always test before mainnet

4. **Verify contract source** - Check BscScan before interacting

---

## Next Steps

After successful deployment:

1. ✅ Save contract address and ABI
2. ✅ Verify on BscScan
3. ✅ Update agent skill configuration
4. ✅ Test basic functions (deposit, withdraw, harvest)
5. ✅ Monitor contract activity on BscScan

---

**Last Updated:** 2026-02-17  
**Solidity Version:** 0.8.24  
**Network:** BNB Testnet (97)
