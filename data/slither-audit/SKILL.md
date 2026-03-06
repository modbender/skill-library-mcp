---
name: slither-audit
description: Run slither static analysis on Solidity contracts. Fast, lightweight security scanner for EVM smart contracts.
env:
  required: []
  optional: []
---

# Slither Audit

Run Slither static analysis on local Solidity contracts.

## What It Does

- Runs Slither static analysis on local `.sol` files
- Parses output for vulnerabilities
- Generates Markdown report with findings and severity

## What It Does NOT Do

- ❌ Fetch contracts from block explorers (use local files)
- ❌ AI-powered analysis (see evmbench for that)
- ❌ Require API keys

## Quick Start

```bash
# Install dependencies
pip install slither-analyzer

# Run audit
python3 slither-audit.py /path/to/contracts/
```

## Usage

```bash
python3 slither-audit.py ./contracts/
python3 slither-audit.py contract.sol
```

## Output Example

```
# Audit Report: Vulnerable.sol
**Chain:** local

## Vulnerabilities Found
- reentrancy-eth (High)
  Reentrancy in Bank.withdraw()...

Found 3 issues
```

## What Slither Detects

- Reentrancy
- Access control
- Integer overflow
- Unchecked external calls
- 100+ detectors

See: https://github.com/crytic/slither

## Limitations

- Local files only
- No AI analysis (see evmbench)
- Requires valid Solidity code
