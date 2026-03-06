# Trail of Bits Methodology — Condensed Reference

Source: https://github.com/crytic/building-secure-contracts

## Design Review Checklist

### Documentation
- [ ] Plain English system description exists with assumptions documented
- [ ] Architecture diagrams showing contract interactions and state machine
- [ ] Natspec comments on all public/external functions
- [ ] Invariants explicitly stated

### Upgradeability
- [ ] Prefer contract migration over delegatecall proxy
- [ ] If using proxy: storage layout identical between proxy and implementation
- [ ] Inheritance order consistent (affects storage layout)
- [ ] Implementation initialized immediately (prevent takeover)
- [ ] Factory pattern used for safe deployment + initialization
- [ ] No function shadowing between proxy and implementation
- [ ] Implementation disabled for direct use (flag in constructor)
- [ ] Immutable/constant vars synced between proxy and implementation
- [ ] Contract existence checks on all low-level calls
- [ ] Migration/upgrade procedure documented before deployment

### On-chain vs Off-chain
- [ ] Minimize on-chain computation; verify off-chain results on-chain
- [ ] Sort/compute off-chain, validate on-chain

## Implementation Review Checklist

### Function Composition
- [ ] Small functions with clear single purpose
- [ ] Logic divided into separate contracts or grouped by function type
- [ ] Authentication, arithmetic, state changes clearly separated

### Inheritance
- [ ] Inheritance depth/width manageable
- [ ] Use `slither --print inheritance-graph` to visualize
- [ ] All parent public functions accounted for

### Events
- [ ] All critical operations emit events
- [ ] Events facilitate debugging and post-deployment monitoring

### Known Pitfalls
- [ ] Check against Ethernaut CTF, Capture the Ether, Not So Smart Contracts
- [ ] Review Solidity documentation warnings sections

### Dependencies
- [ ] Using well-tested libraries (OpenZeppelin)
- [ ] Dependencies managed via package manager (not copy-paste)
- [ ] Dependencies up to date

### Testing
- [ ] Thorough unit tests
- [ ] Custom Slither detectors for project-specific issues
- [ ] Echidna/Medusa fuzz testing with property checks
- [ ] Invariant testing

### Solidity Best Practices
- [ ] Stable compiler version (not bleeding edge)
- [ ] No inline assembly unless absolutely necessary
- [ ] Check latest compiler for warnings even if deploying older version

## Token Integration Checklist (When interacting with arbitrary tokens)

### General
- [ ] Token contract has been audited
- [ ] Security contact exists
- [ ] Contract avoids unnecessary complexity

### ERC20 Conformity
- [ ] `transfer`/`transferFrom` return boolean
- [ ] `name`, `decimals`, `symbol` presence checked if used
- [ ] `decimals` returns `uint8`
- [ ] ERC20 approve race condition mitigated

### ERC20 Risks
- [ ] Not ERC777 (no external calls in transfer)
- [ ] No fee-on-transfer behavior
- [ ] No rebasing behavior (interest-bearing tokens)
- [ ] No flash minting capability

### Token Scarcity
- [ ] Supply not concentrated in few addresses
- [ ] Total supply sufficient (not easily manipulable)
- [ ] Flash loan risks accounted for

### Non-standard Tokens to Watch
- USDT: no return value on transfer
- BNB: returns true but short-returns (only 1 byte)
- Multiple-address tokens (SNX/sBTC double-entry)
- Pausable tokens (can trap funds)
- Blacklistable tokens (USDC, USDT)
- Upgradeable tokens (rules can change)
- Tokens with callbacks (ERC777)

## Deployment Checklist
- [ ] Monitor contracts post-deployment (logs, alerts)
- [ ] Security contact registered on blockchain-security-contacts
- [ ] Privileged wallet keys secured (hardware wallets)
- [ ] Incident response plan documented
- [ ] Post-deployment verification script run

## Key Slither Commands for Audit
```bash
# Overview
slither . --print human-summary
slither . --print contract-summary
slither . --print inheritance-graph

# Detectors (automatic vulnerability detection)
slither . --detect all

# ERC conformance
slither-check-erc <address> <ContractName> --erc erc20

# Upgradeability checks
slither-check-upgradeability <proxy> <implementation>

# Property generation for fuzzing
slither-prop . --contract <ContractName>
```
