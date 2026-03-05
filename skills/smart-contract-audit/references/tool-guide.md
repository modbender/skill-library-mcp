# Static Analysis Tool Guide — Reference for Agents

## Tool Overview

| Tool | Type | Install | Speed | Strengths |
|------|------|---------|-------|-----------|
| Slither | Static analysis | pip | Fast (~seconds) | Broad detector coverage, low false positive |
| Aderyn | Static analysis | cargo | Fast (~seconds) | Cyfrin detectors, gas optimization |
| 4naly3er | Static analysis | npx | Fast | Gas optimization, QA findings |

---

## 1. Slither (Trail of Bits)

### Install
```bash
pip3 install slither-analyzer
# Requires solc: pip3 install solc-select && solc-select install 0.8.20 && solc-select use 0.8.20
```

### Run
```bash
# Basic analysis
slither . --json slither-output.json

# On specific file
slither contract.sol --json slither-output.json

# With specific solc version
slither . --solc-remaps "@openzeppelin=node_modules/@openzeppelin" --json slither-output.json

# Human-readable summary
slither . --print human-summary
slither . --print contract-summary
```

### Key Detectors (by severity)
**High:**
- `reentrancy-eth` — Reentrancy with ETH transfer
- `suicidal` — Functions allowing anyone to destruct contract
- `uninitialized-state` — Uninitialized state variables
- `arbitrary-send-eth` — Functions sending ETH to arbitrary address
- `controlled-delegatecall` — Delegatecall with user-controlled input

**Medium:**
- `reentrancy-no-eth` — Reentrancy without ETH (state manipulation)
- `locked-ether` — Contract locks ETH with no withdrawal
- `tx-origin` — Dangerous use of tx.origin
- `unchecked-lowlevel` — Unchecked low-level calls
- `missing-zero-check` — Missing zero-address validation

**Low/Informational:**
- `naming-convention` — Non-standard naming
- `solc-version` — Problematic Solidity version
- `unused-state` — Unused state variables

### Interpreting Output
- Focus on High and Medium severity first
- Cross-reference with code to eliminate false positives
- Slither's `reentrancy-eth` is very reliable — almost always true positive
- `arbitrary-send-eth` may have false positives if access control exists but Slither can't determine it

---

## 2. Aderyn (Cyfrin)

### Install
```bash
# Via cargo
cargo install aderyn

# Or via npm
npm install -g aderyn
```

### Run
```bash
# Basic analysis
aderyn . --output aderyn-output.json

# On specific path
aderyn ./src --output aderyn-output.json

# Markdown report
aderyn . --output aderyn-report.md
```

### Key Detectors
**High:**
- Unprotected initializer
- Arbitrary `delegatecall`
- Uninitialized state variables
- Weak randomness from chain attributes
- `selfdestruct` usage

**Low:**
- Centralization risk (single owner)
- Floating pragma
- Missing events on state changes
- `abi.encodePacked` with multiple dynamic types (collision risk)
- Unused imports/variables
- Gas optimizations (storage reads in loops, etc.)

### Interpreting Output
- Aderyn produces fewer false positives than most tools
- Focus on High findings first
- "Centralization risk" findings are always worth flagging to protocol
- Gas findings are informational but valuable for comprehensive reports

---

## 3. 4naly3er

### Run
```bash
# Clone and run
npx @4naly3er/cli . --output 4naly3er-report.md
```

### What It Finds
- Gas optimization opportunities
- QA issues (missing events, naming, visibility)
- Non-critical findings
- Mostly Low/Informational severity

### Interpreting Output
- Useful for comprehensive reports
- Gas findings help demonstrate thoroughness
- QA findings often valid but low priority
- Good complement to the deeper analysis tools

---

## Running All Tools Together

Run tools in parallel since they're independent:
```bash
# Install all tools first
./scripts/install-tools.sh

# Run in parallel
./scripts/run-slither.sh <target> &
./scripts/run-aderyn.sh <target> &
wait

# Outputs will be in:
# - audit-output/slither-output.json
# - audit-output/aderyn-output.json
```

## Severity Mapping
| Tool Severity | Report Severity |
|--------------|-----------------|
| Slither High | Critical/High |
| Slither Medium | Medium |
| Slither Low/Info | Low/Informational |
| Aderyn High | High/Medium |
| Aderyn Low | Low/Informational |
| 4naly3er | Low/Informational |

Always validate tool findings manually before including in final report.
