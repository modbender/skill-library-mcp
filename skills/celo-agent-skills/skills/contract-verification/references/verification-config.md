# Contract Verification Configuration

## Complete Hardhat Configuration

```javascript
// hardhat.config.js
require("dotenv").config();
require("@nomicfoundation/hardhat-toolbox");
require("@nomicfoundation/hardhat-verify");

module.exports = {
  solidity: {
    version: "0.8.28",
    settings: {
      optimizer: {
        enabled: true,
        runs: 200,
      },
      viaIR: true,
    },
  },
  networks: {
    celo: {
      url: "https://forno.celo.org",
      accounts: [process.env.PRIVATE_KEY],
      chainId: 42220,
    },
    celoSepolia: {
      url: "https://forno.celo-sepolia.celo-testnet.org",
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
  sourcify: {
    enabled: true,
  },
};
```

## Complete Foundry Configuration

```toml
# foundry.toml
[profile.default]
src = "src"
out = "out"
libs = ["lib"]
solc_version = "0.8.28"
optimizer = true
optimizer_runs = 200
via_ir = true

[rpc_endpoints]
celo = "https://forno.celo.org"
celoSepolia = "https://forno.celo-sepolia.celo-testnet.org"

[etherscan]
celo = { key = "${ETHERSCAN_API_KEY}", chain_id = 42220 }
celoSepolia = { key = "${ETHERSCAN_API_KEY}", chain_id = 11142220 }
```

## Environment Variables Template

```bash
# .env
PRIVATE_KEY=0xYOUR_PRIVATE_KEY
ETHERSCAN_API_KEY=your_celoscan_api_key
```

Source: https://docs.celo.org/developer/verify/hardhat

## Verification Scripts

### Hardhat Deploy and Verify Script

```javascript
// scripts/deploy-and-verify.js
const hre = require("hardhat");

async function main() {
  const [deployer] = await hre.ethers.getSigners();
  console.log("Deploying with:", deployer.address);

  // Deploy
  const MyContract = await hre.ethers.getContractFactory("MyContract");
  const contract = await MyContract.deploy("MyToken", 1000000);
  await contract.waitForDeployment();

  const address = await contract.getAddress();
  console.log("Deployed to:", address);

  // Wait for block confirmations
  console.log("Waiting for confirmations...");
  await contract.deploymentTransaction().wait(5);

  // Verify
  console.log("Verifying...");
  await hre.run("verify:verify", {
    address: address,
    constructorArguments: ["MyToken", 1000000],
  });

  console.log("Verified!");
}

main().catch(console.error);
```

### Foundry Deploy and Verify Script

```solidity
// script/Deploy.s.sol
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.28;

import "forge-std/Script.sol";
import "../src/MyContract.sol";

contract DeployScript is Script {
    function run() external {
        uint256 deployerPrivateKey = vm.envUint("PRIVATE_KEY");

        vm.startBroadcast(deployerPrivateKey);

        MyContract myContract = new MyContract("MyToken", 1000000);

        vm.stopBroadcast();

        console.log("Deployed to:", address(myContract));
    }
}
```

Run with verification:
```bash
forge script script/Deploy.s.sol \
  --rpc-url https://forno.celo.org \
  --broadcast \
  --verify \
  --etherscan-api-key $ETHERSCAN_API_KEY
```

## Constructor Arguments Encoding

### Using cast (Foundry)

```bash
# String and uint256
cast abi-encode "constructor(string,uint256)" "MyToken" 1000000

# Address and uint256
cast abi-encode "constructor(address,uint256)" "0x1234...5678" 1000000

# Array of addresses
cast abi-encode "constructor(address[])" "[0x1234...5678,0xabcd...ef01]"
```

### Using ethers.js

```javascript
const { ethers } = require("ethers");

const args = ethers.AbiCoder.defaultAbiCoder().encode(
  ["string", "uint256"],
  ["MyToken", 1000000]
);

console.log(args); // Use this in verification
```

## Network Information

| Network | Chain ID | RPC URL | Celoscan | Blockscout |
|---------|----------|---------|----------|------------|
| Mainnet | 42220 | https://forno.celo.org | https://celoscan.io | https://celo.blockscout.com |
| Sepolia | 11142220 | https://forno.celo-sepolia.celo-testnet.org | https://sepolia.celoscan.io | https://celo-sepolia.blockscout.com |

Source: https://docs.celo.org/developer/verify/hardhat

## Blockscout API Verification

### JavaScript Example

```javascript
// blockscout-verify.js
async function verifyOnBlockscout(address, sourceCode, compilerVersion, contractName) {
  const baseUrl = "https://celo.blockscout.com/api/v2";

  const response = await fetch(
    `${baseUrl}/smart-contracts/${address}/verification/via/flattened-code`,
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        compiler_version: compilerVersion, // e.g., "v0.8.28+commit.7893614a"
        source_code: sourceCode,
        is_optimization_enabled: true,
        optimization_runs: 200,
        contract_name: contractName,
        evm_version: "paris",
        license_type: "mit",
        autodetect_constructor_args: true,
      }),
    }
  );

  const result = await response.json();
  console.log("Verification result:", result);
  return result;
}
```

### cURL Examples

**Flattened Source:**
```bash
curl -X POST "https://celo.blockscout.com/api/v2/smart-contracts/0xYOUR_ADDRESS/verification/via/flattened-code" \
  -H "Content-Type: application/json" \
  -d '{
    "compiler_version": "v0.8.28+commit.7893614a",
    "source_code": "// SPDX-License-Identifier: MIT\npragma solidity ^0.8.28;\ncontract MyContract { ... }",
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
  -F "autodetect_constructor_args=true" \
  -F "files[0]=@standard-input.json"
```

### License Types

| ID | String | License |
|----|--------|---------|
| 1 | none | No License |
| 2 | unlicense | The Unlicense |
| 3 | mit | MIT License |
| 4 | gnu_gpl_v2 | GNU GPLv2 |
| 5 | gnu_gpl_v3 | GNU GPLv3 |
| 12 | apache_2_0 | Apache 2.0 |

Source: https://docs.blockscout.com/devs/verification

## Common Issues

### Optimizer Mismatch

Ensure your verification uses the same optimizer settings as deployment:
- `enabled`: true/false
- `runs`: number (commonly 200)
- `viaIR`: true/false

### Compiler Version

Use the exact same compiler version. Check with:
```bash
# Hardhat
npx hardhat compile --show-stack-traces

# Foundry
forge build --force
```

### Libraries

If your contract uses external libraries:

```bash
# Hardhat
npx hardhat verify --network celo <ADDRESS> \
  --libraries contracts/MyLib.sol:MyLib:<LIB_ADDRESS>

# Foundry
forge verify-contract --chain-id 42220 <ADDRESS> src/MyContract.sol:MyContract \
  --libraries src/MyLib.sol:MyLib:<LIB_ADDRESS>
```
