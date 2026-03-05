---
name: contract-verification
description: Verify smart contracts on Celo. Use when publishing contract source code to Celoscan or Blockscout.
license: Apache-2.0
metadata:
  author: celo-org
  version: "1.0.0"
---

# Contract Verification on Celo

This skill covers verifying smart contracts on Celo block explorers, making source code publicly readable.

## When to Use

- After deploying a contract to Celo
- Publishing open-source contracts
- Enabling contract interaction via explorer UI
- Building trust with users

## Verification Methods

| Method | Best For |
|--------|----------|
| Hardhat | Automated deployment workflows |
| Foundry | Foundry-based projects |
| Celoscan UI | Quick manual verification |
| Blockscout UI | Alternative explorer UI |
| Blockscout API | Programmatic verification |
| Sourcify | Decentralized verification |
| Remix | Browser-based verification |

## Hardhat Verification

### Configuration

Source: https://docs.celo.org/developer/verify/hardhat

```javascript
// hardhat.config.js
require("dotenv").config();
require("@nomicfoundation/hardhat-verify");

module.exports = {
  solidity: "0.8.28",
  networks: {
    celo: {
      url: "https://forno.celo.org",
      accounts: [process.env.PRIVATE_KEY],
      chainId: 42220,
    },
    celoSepolia: {
      url: "https://forno.celo-sepolia.celo-testnet.org/",
      accounts: [process.env.PRIVATE_KEY],
      chainId: 11142220,
    },
  },
  etherscan: {
    apiKey: process.env.ETHERSCAN_API_KEY,
    customChains: [
      {
        network: "celo",
        chainId: 42220,
        urls: {
          apiURL: "https://api.etherscan.io/v2/api",
          browserURL: "https://celoscan.io/",
        },
      },
      {
        network: "celoSepolia",
        chainId: 11142220,
        urls: {
          apiURL: "https://api.etherscan.io/v2/api",
          browserURL: "https://sepolia.celoscan.io",
        },
      },
    ],
  },
};
```

### Environment Variables

```bash
# .env
PRIVATE_KEY=0xYOUR_PRIVATE_KEY
ETHERSCAN_API_KEY=your_celoscan_api_key
```

Get an API key from [Etherscan](https://etherscan.io/myapikey) or [Celoscan](https://celoscan.io/myapikey).

### Verify Commands

**Mainnet:**
```bash
npx hardhat verify --network celo <CONTRACT_ADDRESS> <CONSTRUCTOR_ARGS>
```

**Testnet:**
```bash
npx hardhat verify --network celoSepolia <CONTRACT_ADDRESS> <CONSTRUCTOR_ARGS>
```

### Example with Constructor Arguments

```bash
# Contract with constructor: constructor(string memory name, uint256 value)
npx hardhat verify --network celo 0x1234...5678 "MyToken" 1000000
```

### Complex Constructor Arguments

For complex arguments, create a file:

```javascript
// arguments.js
module.exports = [
  "MyToken",
  "MTK",
  1000000,
  "0x1234567890123456789012345678901234567890",
];
```

```bash
npx hardhat verify --network celo 0x1234...5678 --constructor-args arguments.js
```

## Foundry Verification

Source: https://docs.celo.org/developer/verify/foundry

### Configuration

```toml
# foundry.toml
[profile.default]
src = "src"
out = "out"
libs = ["lib"]
solc_version = "0.8.28"

[rpc_endpoints]
celo = "https://forno.celo.org"
celoSepolia = "https://forno.celo-sepolia.celo-testnet.org"
```

### Environment Setup

```bash
export ETHERSCAN_API_KEY=<your_etherscan_api_key>
```

### Verify Commands

**Mainnet (Chain ID 42220):**
```bash
forge verify-contract \
  --chain-id 42220 \
  <CONTRACT_ADDRESS> \
  src/MyContract.sol:MyContract \
  --etherscan-api-key $ETHERSCAN_API_KEY \
  --watch
```

**Testnet (Chain ID 11142220):**
```bash
forge verify-contract \
  --chain-id 11142220 \
  <CONTRACT_ADDRESS> \
  src/MyContract.sol:MyContract \
  --etherscan-api-key $ETHERSCAN_API_KEY \
  --watch
```

### With Constructor Arguments

```bash
forge verify-contract \
  --chain-id 42220 \
  --etherscan-api-key $ETHERSCAN_API_KEY \
  <CONTRACT_ADDRESS> \
  src/MyContract.sol:MyContract \
  --constructor-args $(cast abi-encode "constructor(string,uint256)" "MyToken" 1000000) \
  --watch
```

### Deploy and Verify in One Command

```bash
forge create \
  --rpc-url https://forno.celo.org \
  --private-key $PRIVATE_KEY \
  --etherscan-api-key $ETHERSCAN_API_KEY \
  --verify \
  src/MyContract.sol:MyContract \
  --constructor-args "MyToken" 1000000
```

## Celoscan UI Verification

1. Go to your contract on [Celoscan](https://celoscan.io)
2. Click the **Contract** tab
3. Click **Verify & Publish**
4. Select compiler settings:
   - Compiler Type (Solidity Single/Multi-file)
   - Compiler Version
   - License Type
5. Paste your source code
6. Add constructor arguments (ABI-encoded)
7. Complete CAPTCHA
8. Click **Verify and Publish**

## Blockscout Verification

Celo has a Blockscout explorer at [celo.blockscout.com](https://celo.blockscout.com) that supports contract verification.

### Blockscout URLs

| Network | Explorer URL | API Base |
|---------|--------------|----------|
| Mainnet | https://celo.blockscout.com | https://celo.blockscout.com/api/v2 |
| Sepolia | https://celo-sepolia.blockscout.com | https://celo-sepolia.blockscout.com/api/v2 |

### UI Verification

1. Go to [celo.blockscout.com](https://celo.blockscout.com) (or [celo-sepolia.blockscout.com](https://celo-sepolia.blockscout.com) for testnet)
2. Search for your contract address
3. Click **Code** tab
4. Click **Verify & Publish**
5. Select verification method:
   - **Via flattened source code** - Single file with all imports inlined
   - **Via standard input JSON** - Compiler standard JSON input
   - **Via Sourcify** - Decentralized verification
6. Fill in compiler settings (version, optimization, EVM version)
7. Submit verification

### API Verification

Blockscout provides a REST API for programmatic verification.

**Flattened Source Code:**
```bash
curl -X POST "https://celo.blockscout.com/api/v2/smart-contracts/0xYOUR_ADDRESS/verification/via/flattened-code" \
  -H "Content-Type: application/json" \
  -d '{
    "compiler_version": "v0.8.28+commit.7893614a",
    "source_code": "// SPDX-License-Identifier: MIT\npragma solidity ^0.8.28;\n...",
    "is_optimization_enabled": true,
    "optimization_runs": 200,
    "contract_name": "MyContract",
    "evm_version": "paris",
    "license_type": "mit"
  }'
```

**Standard JSON Input:**
```bash
curl -X POST "https://celo.blockscout.com/api/v2/smart-contracts/0xYOUR_ADDRESS/verification/via/standard-input" \
  -F "compiler_version=v0.8.28+commit.7893614a" \
  -F "contract_name=MyContract" \
  -F "license_type=mit" \
  -F "files[0]=@standard-input.json"
```

**API Endpoints:**
- Flattened: `POST /api/v2/smart-contracts/{address}/verification/via/flattened-code`
- Standard JSON: `POST /api/v2/smart-contracts/{address}/verification/via/standard-input`
- Multi-part: `POST /api/v2/smart-contracts/{address}/verification/via/multi-part`
- Sourcify: `POST /api/v2/smart-contracts/{address}/verification/via/sourcify`

Source: https://docs.blockscout.com/devs/verification

## Sourcify Verification

Sourcify provides decentralized contract verification that works across multiple explorers.

Source: https://docs.celo.org/developer/verify/remix

### Benefits

- Decentralized storage of verified source code
- Works with Blockscout and other explorers
- Metadata hash verification ensures exact source match

### Using Remix Sourcify Plugin

1. Open [Remix IDE](https://remix.ethereum.org)
2. Go to **Plugin Manager** (plug icon)
3. Search for "Sourcify" and activate it
4. Deploy your contract to Celo
5. In the Sourcify plugin:
   - Select the deployed contract
   - Choose the network (Celo Mainnet: 42220, Sepolia: 11142220)
   - Click **Verify**
6. Contract will be verified on Sourcify and visible in Blockscout

### Programmatic Sourcify Verification

```bash
curl -X POST "https://sourcify.dev/server/verify" \
  -F "address=0xYOUR_ADDRESS" \
  -F "chain=42220" \
  -F "files[0]=@MyContract.sol" \
  -F "files[1]=@metadata.json"
```

## Remix Verification

Verify contracts directly from Remix IDE using the Etherscan plugin.

Source: https://docs.celo.org/developer/verify/remix

### Setup

1. Open [Remix IDE](https://remix.ethereum.org)
2. Go to **Plugin Manager**
3. Activate **Etherscan - Contract Verification** plugin

### Verification Steps

1. Deploy your contract to Celo via Remix
2. Open the Etherscan plugin (checkmark icon)
3. Enter your Celoscan API key
4. Select the contract to verify
5. Choose network:
   - Celo Mainnet (Chain ID: 42220)
   - Celo Sepolia (Chain ID: 11142220)
6. Click **Verify**

### Configuration for Celo

In Remix settings, add custom network:
- Network Name: Celo Mainnet
- Chain ID: 42220
- API URL: https://api.celoscan.io/api
- Browser URL: https://celoscan.io

## Troubleshooting

### "Unable to verify"

**Causes:**
- Compiler version mismatch
- Optimizer settings mismatch
- Wrong constructor arguments

**Solutions:**
- Match exact compiler version used in deployment
- Match optimizer settings (enabled, runs)
- Verify constructor args are ABI-encoded correctly

### "Already verified"

Contract is already verified. Check the explorer to see the source code.

### "Contract not found"

**Causes:**
- Wrong contract address
- Contract not yet indexed

**Solutions:**
- Double-check the address
- Wait a few minutes for indexing

### Proxy Contracts

For proxy contracts, verify both:
1. The implementation contract
2. The proxy contract

Then link them on Celoscan:
1. Go to proxy contract
2. Click "More Options"
3. Select "Is this a proxy?"
4. Follow verification steps

## API Endpoints

| Network | API URL |
|---------|---------|
| Mainnet | https://api.celoscan.io/api |
| Sepolia | https://api-sepolia.celoscan.io/api |

## Dependencies

For Hardhat:
```json
{
  "devDependencies": {
    "@nomicfoundation/hardhat-verify": "^2.0.0",
    "hardhat": "^2.19.0"
  }
}
```

## Additional Resources

- [verification-config.md](references/verification-config.md) - Complete configuration examples
