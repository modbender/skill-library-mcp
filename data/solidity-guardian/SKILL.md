---
name: solidity-guardian
version: 1.0.0
description: Smart contract security analysis skill. Detect vulnerabilities, suggest fixes, generate audit reports. Supports Hardhat/Foundry projects. Uses pattern matching + best practices from Trail of Bits, OpenZeppelin, and Consensys.
author: aviclaw
tags:
  - solidity
  - security
  - audit
  - smart-contracts
  - ethereum
  - vulnerability
  - scanner
---

# Solidity Guardian 🛡️

Security analysis for Solidity smart contracts. Find vulnerabilities, get fix suggestions, follow best practices.

## Quick Start

```bash
# Analyze a single contract
node skills/solidity-guardian/analyze.js contracts/MyContract.sol

# Analyze entire project
node skills/solidity-guardian/analyze.js ./contracts/

# Generate markdown report
node skills/solidity-guardian/analyze.js ./contracts/ --format markdown > AUDIT.md
```

## What It Detects (40+ Patterns)

### Critical (Must Fix)
| ID | Vulnerability | Description |
|----|--------------|-------------|
| SG-001 | Reentrancy | External calls before state updates |
| SG-002 | Unprotected selfdestruct | Missing access control on selfdestruct |
| SG-003 | Delegatecall to untrusted | Delegatecall with user-controlled address |
| SG-004 | Uninitialized storage pointer | Storage pointer overwrites slots |
| SG-005 | Signature replay | ecrecover without nonce/chainId |
| SG-006 | Arbitrary jump | Function type from user input |

### High (Should Fix)
| ID | Vulnerability | Description |
|----|--------------|-------------|
| SG-010 | Missing access control | Public functions that should be restricted |
| SG-011 | Unchecked transfer | ERC20 transfer without return check |
| SG-012 | Integer overflow | Arithmetic without SafeMath (pre-0.8) |
| SG-013 | tx.origin auth | Using tx.origin for authentication |
| SG-014 | Weak randomness | block.timestamp/blockhash for randomness |
| SG-015 | Unprotected withdrawal | Withdrawal without ownership check |
| SG-016 | Unchecked low-level call | .call() without success check |
| SG-017 | Dangerous equality | Strict balance check (manipulable) |
| SG-018 | Deprecated functions | suicide, sha3, throw, callcode |
| SG-019 | Wrong constructor | Function name matches contract |

### Medium (Consider Fixing)
| ID | Vulnerability | Description |
|----|--------------|-------------|
| SG-020 | Floating pragma | Non-pinned Solidity version |
| SG-021 | Missing zero check | No validation for zero address |
| SG-022 | Timestamp dependence | Logic depends on block.timestamp |
| SG-023 | DoS with revert | Loop with external call can revert |
| SG-024 | Front-running risk | Predictable state changes |

### Low (Best Practice)
| ID | Vulnerability | Description |
|----|--------------|-------------|
| SG-030 | Missing events | State changes without events |
| SG-031 | Magic numbers | Hardcoded values without constants |
| SG-032 | Implicit visibility | Functions without explicit visibility |
| SG-033 | Large contract | Contract exceeds size recommendations |
| SG-034 | Missing NatSpec | Public functions without documentation |

## Usage Examples

### Basic Analysis
```javascript
const { analyzeContract } = require('./analyzer');

const results = await analyzeContract('contracts/Token.sol');
console.log(results.findings);
```

### With Fix Suggestions
```javascript
const results = await analyzeContract('contracts/Vault.sol', {
  includeFixes: true,
  severity: ['critical', 'high']
});

for (const finding of results.findings) {
  console.log(`[${finding.severity}] ${finding.title}`);
  console.log(`  Line ${finding.line}: ${finding.description}`);
  console.log(`  Fix: ${finding.suggestion}`);
}
```

### Generate Report
```javascript
const { generateReport } = require('./reporter');

const report = await generateReport('./contracts/', {
  format: 'markdown',
  includeGas: true,
  includeBestPractices: true
});

fs.writeFileSync('SECURITY_AUDIT.md', report);
```

## Best Practices Checklist

When writing secure contracts, follow these guidelines:

### Access Control
- [ ] Use OpenZeppelin's `Ownable` or `AccessControl`
- [ ] Apply `onlyOwner` or role checks to sensitive functions
- [ ] Implement two-step ownership transfer
- [ ] Consider timelocks for critical operations

### Reentrancy Prevention
- [ ] Use `ReentrancyGuard` on all external-facing functions
- [ ] Follow checks-effects-interactions pattern
- [ ] Update state BEFORE external calls
- [ ] Use pull over push for payments

### Input Validation
- [ ] Validate all external inputs
- [ ] Check for zero addresses
- [ ] Validate array lengths match
- [ ] Use SafeERC20 for token transfers

### Arithmetic Safety
- [ ] Use Solidity 0.8+ or SafeMath
- [ ] Check for division by zero
- [ ] Validate percentage calculations (≤100)
- [ ] Be careful with token decimals

### Upgradeability (if applicable)
- [ ] Use initializer instead of constructor
- [ ] Protect initialize from re-initialization
- [ ] Follow storage layout rules
- [ ] Test upgrade paths

## Slither Integration

Guardian can run alongside Slither for comprehensive analysis:

```bash
# Combined analysis (auto-installs Slither if missing)
node skills/solidity-guardian/slither-integration.js ./contracts/ --install-slither

# Generate combined report
node skills/solidity-guardian/slither-integration.js . --format markdown --output AUDIT.md

# Guardian only (faster, no Slither dependency)
node skills/solidity-guardian/slither-integration.js ./contracts/ --guardian-only

# Slither only
node skills/solidity-guardian/slither-integration.js ./contracts/ --slither-only
```

**Why both?**
- Guardian: Fast pattern matching, custom rules, no compilation needed
- Slither: Deep dataflow analysis, CFG-based detection, more comprehensive

## Integration with Other Tools

### Hardhat
```javascript
// hardhat.config.js
require('./skills/solidity-guardian/hardhat-plugin');

// Run: npx hardhat guardian
```

### Foundry
```bash
# Add to CI
forge build
node skills/solidity-guardian/analyze.js ./src/
```

## References

- [Trail of Bits - Building Secure Contracts](https://github.com/crytic/building-secure-contracts)
- [OpenZeppelin - Security Best Practices](https://docs.openzeppelin.com/learn/preparing-for-mainnet)
- [Consensys - Smart Contract Best Practices](https://consensys.github.io/smart-contract-best-practices/)
- [SWC Registry](https://swcregistry.io/)

---

Built by Avi 🔐 | Security-first, ship always.
