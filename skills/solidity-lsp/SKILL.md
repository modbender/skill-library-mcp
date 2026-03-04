---
name: solidity-lsp
description: Solidity language server providing smart contract development support including compilation, linting, security analysis, and code intelligence for .sol files. Use when working with Ethereum smart contracts, Substrate pallets, or any Solidity code that needs compilation, security checks, gas optimization, or code navigation. Essential for ClawChain pallet development.
---

# Solidity LSP

Solidity language server integration providing comprehensive smart contract development support through solc (Solidity compiler) and solhint (linter).

## Capabilities

- **Compilation**: Compile Solidity smart contracts with solc
- **Linting**: Static analysis with solhint for best practices and security
- **Security**: Detect common vulnerabilities (reentrancy, overflow, etc.)
- **Gas optimization**: Identify expensive operations
- **Code intelligence**: Syntax highlighting, error detection
- **Supported extensions**: `.sol`

## Installation

Install Solidity compiler and linter:

```bash
# Solidity compiler
npm install -g solc

# Solidity linter
npm install -g solhint
```

Verify installation:
```bash
solcjs --version
solhint --version
```

## Usage

### Compile Solidity Contract

```bash
solcjs --bin --abi contract.sol
```

Compile with optimization:
```bash
solcjs --optimize --bin --abi contract.sol
```

### Lint Contract

Run solhint on a file:
```bash
solhint contracts/MyContract.sol
```

Run on entire project:
```bash
solhint 'contracts/**/*.sol'
```

### Security Analysis

solhint includes security rules by default. For advanced security analysis, consider:

```bash
# Install slither (requires Python)
pip3 install slither-analyzer

# Run security analysis
slither contracts/
```

## Configuration

### solhint Configuration

Create `.solhint.json` in project root:

```json
{
  "extends": "solhint:recommended",
  "rules": {
    "compiler-version": ["error", "^0.8.0"],
    "func-visibility": ["warn", {"ignoreConstructors": true}],
    "max-line-length": ["warn", 120],
    "not-rely-on-time": "warn",
    "avoid-low-level-calls": "warn",
    "no-inline-assembly": "warn"
  }
}
```

### Hardhat/Foundry Integration

For full development environments, see `references/frameworks.md`.

## Integration Pattern

When developing smart contracts:

1. **Write**: Edit Solidity code
2. **Lint**: Run `solhint` to catch issues early
3. **Compile**: Use `solcjs` to verify compilation
4. **Analyze**: Run security tools before deployment
5. **Test**: Write comprehensive unit tests

## Common Issues

- **Compiler version mismatch**: Specify pragma version in contract
- **Gas optimization**: Use `view`/`pure` where possible
- **Security**: Never use `tx.origin` for authentication
- **Best practices**: Follow Checks-Effects-Interactions pattern

## More Information

- [Solidity Documentation](https://docs.soliditylang.org/)
- [Solhint GitHub](https://github.com/protofire/solhint)
- [Solidity Security Best Practices](https://consensys.github.io/smart-contract-best-practices/)
- See `references/frameworks.md` for Hardhat/Foundry setup
