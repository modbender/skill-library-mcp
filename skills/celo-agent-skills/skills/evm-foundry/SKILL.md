---
name: evm-foundry
description: Foundry development for EVM chains including Celo. Use when working with forge, cast, anvil, writing Solidity contracts, testing, deploying, or verifying contracts with Foundry.
license: Apache-2.0
metadata:
  author: celo-org
  version: "1.0.0"
---

# Foundry Development for EVM Chains

This skill covers Foundry setup and development for EVM-compatible chains with emphasis on Celo.

## When to Use

- Setting up a new Foundry project
- Writing and compiling Solidity smart contracts with forge
- Testing contracts with forge test
- Deploying contracts to Celo or other EVM chains
- Verifying contracts on block explorers
- Interacting with contracts using cast

## Foundry Tools

| Tool | Purpose |
|------|---------|
| forge | Build, test, debug, deploy, and verify smart contracts |
| cast | Interact with contracts and retrieve chain data from CLI |
| anvil | Run a local Ethereum development node with forking support |
| chisel | Fast Solidity REPL for interactive development |

## Installation

```bash
# Install Foundryup (the Foundry installer)
curl -L https://foundry.paradigm.xyz | bash

# Install Foundry tools
foundryup
```

For Windows, use Git BASH or WSL (Foundryup doesn't support PowerShell or Command Prompt).

## Quick Start

### Initialize Project

```bash
forge init my-project
cd my-project
```

### Project Structure

```
my-project/
├── foundry.toml      # Configuration
├── src/              # Contract source files
│   └── Counter.sol
├── test/             # Test files
│   └── Counter.t.sol
├── script/           # Deployment scripts
│   └── Counter.s.sol
└── lib/              # Dependencies
```

## Celo Network Information

| Network | Chain ID | RPC Endpoint |
|---------|----------|--------------|
| Celo Mainnet | 42220 | https://forno.celo.org |
| Celo Sepolia | 11142220 | https://forno.celo-sepolia.celo-testnet.org |


## Configuration

### foundry.toml for Celo

```toml
[profile.default]
src = "src"
out = "out"
libs = ["lib"]
solc = "0.8.28"
optimizer = true
optimizer_runs = 200

[rpc_endpoints]
celo = "https://forno.celo.org"
celo_sepolia = "https://forno.celo-sepolia.celo-testnet.org"
localhost = "http://127.0.0.1:8545"

[etherscan]
celo = { key = "${CELOSCAN_API_KEY}", chain = 42220, url = "https://api.celoscan.io/api" }
celo_sepolia = { key = "${CELOSCAN_API_KEY}", chain = 11142220, url = "https://api.etherscan.io/v2/api" }
```

### Environment Variables (.env)

```bash
PRIVATE_KEY=your_private_key_here
CELOSCAN_API_KEY=your_celoscan_api_key_here
```

Load environment variables:

```bash
source .env
```

## Writing Contracts

### Basic Contract

```solidity
// src/MyContract.sol
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.28;

contract MyContract {
    string public name;
    address public owner;

    event NameChanged(string oldName, string newName);

    modifier onlyOwner() {
        require(msg.sender == owner, "Not owner");
        _;
    }

    constructor(string memory _name) {
        name = _name;
        owner = msg.sender;
    }

    function setName(string memory _newName) external onlyOwner {
        string memory oldName = name;
        name = _newName;
        emit NameChanged(oldName, _newName);
    }
}
```

### Using OpenZeppelin

```bash
forge install OpenZeppelin/openzeppelin-contracts
```

Add to `remappings.txt`:

```
@openzeppelin/contracts/=lib/openzeppelin-contracts/contracts/
```

```solidity
// src/MyToken.sol
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.28;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

contract MyToken is ERC20, Ownable {
    constructor() ERC20("MyToken", "MTK") Ownable(msg.sender) {
        _mint(msg.sender, 1000000 * 10 ** decimals());
    }

    function mint(address to, uint256 amount) external onlyOwner {
        _mint(to, amount);
    }
}
```

## Compilation

```bash
# Compile all contracts
forge build

# Clean and rebuild
forge clean && forge build

# Check contract sizes
forge build --sizes
```

## Testing

### Test File Structure

```solidity
// test/MyContract.t.sol
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.28;

import {Test, console} from "forge-std/Test.sol";
import {MyContract} from "../src/MyContract.sol";

contract MyContractTest is Test {
    MyContract public myContract;
    address public owner;
    address public user;

    function setUp() public {
        owner = address(this);
        user = makeAddr("user");
        myContract = new MyContract("Initial Name");
    }

    function test_InitialName() public view {
        assertEq(myContract.name(), "Initial Name");
    }

    function test_Owner() public view {
        assertEq(myContract.owner(), owner);
    }

    function test_SetName() public {
        myContract.setName("New Name");
        assertEq(myContract.name(), "New Name");
    }

    function test_SetNameEmitsEvent() public {
        vm.expectEmit(true, true, true, true);
        emit MyContract.NameChanged("Initial Name", "New Name");
        myContract.setName("New Name");
    }

    function test_RevertWhen_NonOwnerSetsName() public {
        vm.prank(user);
        vm.expectRevert("Not owner");
        myContract.setName("Hacked");
    }

    function testFuzz_SetName(string memory newName) public {
        myContract.setName(newName);
        assertEq(myContract.name(), newName);
    }
}
```

### Running Tests

```bash
# Run all tests
forge test

# Run with verbosity (show logs)
forge test -vvv

# Run specific test
forge test --match-test test_SetName

# Run specific contract
forge test --match-contract MyContractTest

# Run with gas reporting
forge test --gas-report

# Run with coverage
forge coverage

# Fork testing against Celo mainnet
forge test --fork-url https://forno.celo.org
```

## Deployment

### Deployment Script

```solidity
// script/Deploy.s.sol
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.28;

import {Script, console} from "forge-std/Script.sol";
import {MyContract} from "../src/MyContract.sol";

contract DeployScript is Script {
    function setUp() public {}

    function run() public {
        uint256 deployerPrivateKey = vm.envUint("PRIVATE_KEY");

        vm.startBroadcast(deployerPrivateKey);

        MyContract myContract = new MyContract("My Contract Name");
        console.log("Contract deployed to:", address(myContract));

        vm.stopBroadcast();
    }
}
```

### Deploy Commands

```bash
# Deploy to local Anvil
forge script script/Deploy.s.sol --rpc-url http://127.0.0.1:8545 --broadcast

# Deploy to Celo Sepolia
forge script script/Deploy.s.sol --rpc-url https://forno.celo-sepolia.celo-testnet.org --broadcast --private-key $PRIVATE_KEY

# Deploy to Celo Mainnet
forge script script/Deploy.s.sol --rpc-url https://forno.celo.org --broadcast --private-key $PRIVATE_KEY

# Deploy with verification
forge script script/Deploy.s.sol --rpc-url https://forno.celo-sepolia.celo-testnet.org --broadcast --verify --private-key $PRIVATE_KEY
```

### Quick Deploy with forge create

```bash
# Deploy to Celo Sepolia
forge create src/MyContract.sol:MyContract \
  --rpc-url https://forno.celo-sepolia.celo-testnet.org \
  --private-key $PRIVATE_KEY \
  --constructor-args "My Contract Name"

# Deploy with verification
forge create src/MyContract.sol:MyContract \
  --rpc-url https://forno.celo-sepolia.celo-testnet.org \
  --private-key $PRIVATE_KEY \
  --constructor-args "My Contract Name" \
  --verify \
  --etherscan-api-key $CELOSCAN_API_KEY
```

## Verification

### Verify Existing Contract

```bash
# Verify on Celo Sepolia
forge verify-contract \
  --chain-id 11142220 \
  <CONTRACT_ADDRESS> \
  src/MyContract.sol:MyContract \
  --etherscan-api-key $CELOSCAN_API_KEY \
  --watch

# Verify on Celo Mainnet
forge verify-contract \
  --chain-id 42220 \
  <CONTRACT_ADDRESS> \
  src/MyContract.sol:MyContract \
  --etherscan-api-key $CELOSCAN_API_KEY \
  --watch

# With constructor arguments
forge verify-contract \
  --chain-id 11142220 \
  <CONTRACT_ADDRESS> \
  src/MyContract.sol:MyContract \
  --etherscan-api-key $CELOSCAN_API_KEY \
  --constructor-args $(cast abi-encode "constructor(string)" "My Contract Name") \
  --watch
```

## Cast Commands

### Reading Data

```bash
# Get balance
cast balance <ADDRESS> --rpc-url https://forno.celo.org

# Call view function
cast call <CONTRACT_ADDRESS> "name()(string)" --rpc-url https://forno.celo.org

# Get storage slot
cast storage <CONTRACT_ADDRESS> 0 --rpc-url https://forno.celo.org

# Get block number
cast block-number --rpc-url https://forno.celo.org
```

### Writing Data

```bash
# Send transaction
cast send <CONTRACT_ADDRESS> "setName(string)" "New Name" \
  --rpc-url https://forno.celo.org \
  --private-key $PRIVATE_KEY

# Transfer CELO
cast send <TO_ADDRESS> --value 1ether \
  --rpc-url https://forno.celo.org \
  --private-key $PRIVATE_KEY
```

### Utility Commands

```bash
# Encode function call
cast calldata "setName(string)" "New Name"

# Decode function call
cast 4byte-decode <CALLDATA>

# Convert units
cast to-wei 1 ether
cast from-wei 1000000000000000000

# Get ABI-encoded constructor args
cast abi-encode "constructor(string)" "My Contract Name"
```

## Anvil (Local Node)

```bash
# Start local node
anvil

# Start with fork of Celo mainnet
anvil --fork-url https://forno.celo.org

# Start with specific block
anvil --fork-url https://forno.celo.org --fork-block-number 12345678
```

## Block Explorers

- **Celo Mainnet:** https://celoscan.io
- **Celo Sepolia:** https://sepolia.celoscan.io

## Additional Resources

- [foundry-config.md](references/foundry-config.md) - Detailed configuration options
- [testing-patterns.md](references/testing-patterns.md) - Advanced testing patterns
- [security-checklist.md](rules/security-checklist.md) - Security best practices
