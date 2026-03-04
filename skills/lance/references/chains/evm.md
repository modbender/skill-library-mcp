# EVM Chain Guide

## Intake

Capture:
- chain id
- RPC endpoint quality
- target addresses and labels
- proxy implementation resolution
- verified source availability

## EVM Focus Areas

- external call ordering (reentrancy windows)
- authorization boundary enforcement
- signature domain/nonce/deadline handling
- oracle source quality (spot vs TWAP)
- upgradeability and storage layout safety
- cross-contract state assumptions

## Evidence Sources

- source code + ABI
- bytecode disassembly
- function selector mapping
- event/state transition traces

## Common Traps

- flagging centralization without exploit path
- ignoring proxy admin protections
- overclaiming oracle attacks without liquidity math
