# Solidity Development Frameworks

## Hardhat

Full-featured Ethereum development environment.

### Installation

```bash
npm install --save-dev hardhat
npx hardhat
```

### Configuration

`hardhat.config.js`:
```javascript
module.exports = {
  solidity: "0.8.19",
  networks: {
    hardhat: {},
    sepolia: {
      url: process.env.SEPOLIA_URL,
      accounts: [process.env.PRIVATE_KEY]
    }
  }
};
```

### Commands

```bash
npx hardhat compile       # Compile contracts
npx hardhat test          # Run tests
npx hardhat node          # Start local node
npx hardhat run scripts/deploy.js --network sepolia
```

---

## Foundry

Fast Rust-based toolkit for Ethereum development.

### Installation

```bash
curl -L https://foundry.paradigm.xyz | bash
foundryup
```

### Project Structure

```
project/
├── src/          # Solidity contracts
├── test/         # Solidity tests
├── script/       # Deployment scripts
└── foundry.toml  # Configuration
```

### Commands

```bash
forge build           # Compile
forge test            # Run tests
forge test -vvv       # Verbose test output
forge coverage        # Code coverage
forge script script/Deploy.s.sol --broadcast
```

### Configuration

`foundry.toml`:
```toml
[profile.default]
src = "src"
out = "out"
libs = ["lib"]
solc_version = "0.8.19"
optimizer = true
optimizer_runs = 200
```

---

## Substrate/Ink! (for ClawChain)

Smart contracts on Substrate-based chains use ink!.

### Installation

```bash
cargo install cargo-contract --force
```

### Create Contract

```bash
cargo contract new my_contract
cd my_contract
cargo contract build
```

### Test

```bash
cargo test
```

### Deploy

```bash
cargo contract instantiate --constructor new \
  --args "initial_value" \
  --suri //Alice
```

---

## Comparison

| Framework | Language | Speed | Use Case |
|-----------|----------|-------|----------|
| Hardhat | JS/TS | Medium | Full-featured, plugins |
| Foundry | Rust | Fast | Testing, gas optimization |
| Ink! | Rust | Fast | Substrate/Polkadot chains |

**For ClawChain development**: Use ink! for on-chain pallets, Foundry for gas analysis of equivalent EVM logic.
