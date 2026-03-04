# Agent Wallet Security Audit — Round 2

**Date:** 2026-02-15
**Auditor:** Max (Internal AI-Assisted Review, adversarial red-team mode — NOT a third-party audit)
**Contracts:** AgentAccountV2.sol, AgentAccountV2_4337.sol

## Findings & Fixes

### 🔴 Critical

| ID | Finding | Root Cause | Fix |
|----|---------|------------|-----|
| C2-1 | Flash-loan NFT hijack: temp NFT holder installs permanent backdoor operator | `_isOwner()` checked live but `setOperator` persists forever | **Operator epoch** — all operators invalidated on ownership change |
| C2-2 | Stale operators after NFT transfer: old operators drain new owner's funds | Same as C2-1 | **Same epoch mechanism** + `_syncOwnership()` on every mutating call |

### 🟠 High

| ID | Finding | Fix |
|----|---------|-----|
| H2-1 | 4337 pending queue bricks after 50 lifetime txs (pendingNonce never decreases) | Changed to `_countActivePending()` — counts only non-executed/non-cancelled/non-expired |
| H2-2 | validateUserOp pays EntryPoint prefund even for invalid signatures | Prefund only sent when `valid == true` |

### 🟡 Medium

| ID | Finding | Fix |
|----|---------|-----|
| M2-1 | NFT burn locks funds forever (`ownerOf` reverts) | `_tryGetOwner()` with try/catch, `_isOwner` requires non-zero owner |
| M2-2 | Period boundary double-spend (2x limit in ~1 second) | Fixed period windows using floor division instead of rolling start |

## Architecture Changes

### Operator Epoch Pattern
- New state: `operatorEpoch` (uint256), `_cachedOwner` (address)
- `OperatorInfo` struct replaces `bool`: stores `{authorized, epoch}`
- `_syncOwnership()` called on every state-mutating function — detects NFT transfers and bumps epoch
- `_isActiveOperator()` requires `info.epoch == operatorEpoch`
- `invalidateAllOperators()` — owner can manually bump epoch
- `isOperatorActive()` — public view function

### Fixed Period Windows
- `_currentPeriodStart()` uses floor division: `periodStart + (elapsed / periodLength * periodLength)`
- Eliminates the edge case where spending at period boundary resets the window

### NFT Burn Protection  
- `_tryGetOwner()` wraps `ownerOf` in try/catch, returns `address(0)` on revert
- `_isOwner()` requires non-zero owner (explicit revert message)
- `isValidSignature` gracefully returns invalid for burned NFTs

## Status: ALL FIXES APPLIED ✅
