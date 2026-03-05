# Agent Wallet V2 — Security Audit Report

**Date:** 2026-02-14  
**Auditor:** Max (Internal AI-Assisted Review — NOT a third-party audit)  
**Contracts:** AgentAccountV2.sol, AgentAccountV2_4337.sol, AgentAccountFactoryV2.sol  
**Solidity:** ^0.8.19  

---

## Executive Summary

**Result: CONDITIONAL PASS — Deploy with Fixes**

| Severity | Count |
|----------|-------|
| Critical | 2 |
| High | 4 |
| Medium | 5 |
| Low | 3 |

The core spend-limit architecture is sound, but there are critical reentrancy and spend-limit bypass vectors that must be fixed before mainnet.

---

## Critical Findings

### C-1: Reentrancy in `agentExecute` — Spend Recorded Before Execution, But Call Can Manipulate State

**Severity:** Critical  
**Contract:** AgentAccountV2.sol, AgentAccountV2_4337.sol

**Description:** In `agentExecute`, spend is recorded via `_checkAndRecordSpend` *before* the external call, which is good. However, the external call `to.call{value: value}(data)` can call back into the contract. While the spend tracking itself is safe (checks-effects-interactions pattern for the spend), the callback could invoke `agentExecute` with a *different* token policy (e.g., an ERC20 policy) or call `agentTransferToken` — creating cross-function reentrancy.

More critically: **`agentExecute` tracks spend against `address(0)` (ETH) but the `data` payload can encode arbitrary calls** — including ERC20 `transfer()` calls. An operator can call `agentExecute(tokenAddress, 0, transfer(attacker, 1000000))` with `value=0`, which passes the ETH spend check (0 ≤ any limit) but executes an ERC20 transfer with no token spend tracking.

**Impact:** Complete bypass of ERC20 spend limits. An operator can drain all ERC20 tokens by routing transfers through `agentExecute` instead of `agentTransferToken`.

**Proof of Concept:**
1. Owner sets USDC spend policy: 100 USDC per tx, 500 USDC per day
2. Operator calls `agentExecute(usdcAddress, 0, abi.encodeWithSelector(IERC20.transfer.selector, attacker, 1_000_000e6))`
3. ETH spend check: amount=0, passes trivially (if ETH policy exists) or queues (if no ETH policy — but operator can set up to exploit)
4. Actually — if no ETH policy, it queues. But if owner set ANY ETH policy (even 1 wei), value=0 passes.
5. The USDC transfer executes with zero spend tracking against the USDC policy.

**Recommended Fix:** `agentExecute` should either:
- Only allow calls to non-token addresses (whitelist/blacklist approach), OR
- Parse calldata for known transfer selectors and enforce token limits, OR  
- Restrict `agentExecute` to ETH-only transfers (no arbitrary calldata for operators)

### C-2: `approvePending` Reentrancy — State Update After External Call

**Severity:** Critical  
**Contract:** AgentAccountV2.sol, AgentAccountV2_4337.sol

**Description:** In `approvePending`, `ptx.executed = true` is set before the external call — good. However, `_recordSpend` is called *after* the external call. If the called contract calls back into `approvePending` (or any function that reads spend tracking), the spend state is stale.

More importantly: the external call in `approvePending` uses `ptx.to.call{value: ptx.value}(ptx.data)`. For a pending ERC20 transfer, `ptx.to` is the **token contract address** and `ptx.data` is `transfer(to, amount)`. If the token contract has a callback mechanism (e.g., ERC-777 tokens with `tokensReceived` hooks), the recipient could reenter before `_recordSpend` updates the period tracking.

**Impact:** Spend tracking becomes inaccurate. While the `ptx.executed = true` prevents double-execution of the same pending tx, the spend counter may not reflect the approved amount, allowing more autonomous spending than intended.

**Recommended Fix:** Move `_recordSpend` before the external call:
```solidity
ptx.executed = true;
++nonce;
_recordSpend(ptx.token, ptx.amount); // BEFORE external call
(bool success, ) = ptx.to.call{value: ptx.value}(ptx.data);
```

---

## High Findings

### H-1: Operator Can Bypass ALL Token Limits via `agentExecute` Arbitrary Calldata

**Severity:** High (escalated from C-1 detail)

**Description:** This is the direct exploitation path from C-1. `agentExecute` allows operators to pass arbitrary `data` to any `to` address. The spend tracking only checks against the ETH policy using `value`. An operator can:

1. Call `agentExecute(usdcAddress, 0, approve(attacker, type(uint256).max))` — approve unlimited USDC to their EOA
2. Then transfer tokens from their own wallet

This bypasses both `agentTransferToken` limits AND the pending queue.

**Impact:** Total ERC20 drain. Also allows operators to call `setOperator` or `setSpendPolicy` if the account owns the NFT for another account (chain of TBAs).

**Recommended Fix:** Restrict operator `agentExecute` to disallow calls to known token contracts, or only allow it for ETH transfers (data must be empty for operators).

### H-2: No Reentrancy Guard

**Severity:** High

**Description:** None of the contracts use OpenZeppelin's `ReentrancyGuard`. While some functions follow checks-effects-interactions, the absence of an explicit guard means any future code changes or complex interactions could introduce reentrancy.

**Recommended Fix:** Add `nonReentrant` modifier to `execute`, `agentExecute`, `agentTransferToken`, and `approvePending`.

### H-3: Pending Queue Griefing — Unbounded Queue with No Expiry

**Severity:** High

**Description:** An operator can spam `agentExecute` with over-limit transactions indefinitely, creating thousands of pending entries. There is:
- No maximum pending queue size
- No expiry/TTL on pending transactions
- No cost to the operator for queuing

The owner must individually cancel or approve each one. The pending transactions live in a mapping (not iterable), so there's no way to bulk-cancel.

**Impact:** Operational DoS. Owner's UI becomes unusable. Gas costs to cancel many pending txs could be significant.

**Recommended Fix:**
- Add a maximum pending queue size (e.g., 10-50)
- Add expiry (e.g., pending txs expire after 7 days)
- Add `cancelAllPending()` function for owner
- Consider rate-limiting operator queue submissions

### H-4: `validateUserOp` Accepts Operator Signatures Without Spend Limit Checks

**Severity:** High  
**Contract:** AgentAccountV2_4337.sol

**Description:** `validateUserOp` returns `0` (valid) for both owner AND operator signatures. However, the EntryPoint will then call `execute` or `agentExecute` based on `callData`. If an operator signs a UserOp with callData targeting `execute()` (owner-only function), the validation passes but execution will revert (due to `onlyOwner`). This wastes gas.

More critically: if the operator signs a UserOp calling `agentExecute`, the spend limits apply — but the prefund (`missingAccountFunds`) is paid from the account's ETH balance regardless of spend limits. An operator can craft UserOps that fail execution but still drain ETH via gas prefunding.

**Impact:** Gas griefing — operator can drain account ETH through failed UserOps that still pay the prefund.

**Recommended Fix:** In `validateUserOp`, if the signer is an operator (not owner), validate that the callData targets an allowed function and the spend would be within limits. Or don't pay `missingAccountFunds` for operator-signed ops.

---

## Medium Findings

### M-1: `setSpendPolicy` Resets `periodSpent` — Owner Can Be Frontrun

**Severity:** Medium

**Description:** When `setSpendPolicy` is called, it creates a fresh `SpendPolicy` with `periodSpent: 0` and `periodStart: block.timestamp`. If an owner reduces limits (e.g., from 10 ETH to 1 ETH per period), the operator can frontrun the policy change by spending up to the old limit.

**Impact:** Operator can spend more than intended during policy transitions.

**Recommended Fix:** Allow `setSpendPolicy` to optionally preserve `periodSpent`, or add a `freezeOperator` function that instantly blocks all operator spending.

### M-2: ERC-1271 Doesn't Validate Operator Signatures

**Severity:** Medium

**Description:** `isValidSignature` only validates the NFT owner's signature. If protocols check ERC-1271 for operator authorization (e.g., permit2, DEX orders), operator-signed messages will be rejected.

This is arguably by design (operators shouldn't sign on behalf of the account), but it means operators cannot use any protocol requiring ERC-1271 verification.

**Impact:** Reduced operator functionality for DeFi interactions.

**Recommended Fix:** Document this as intentional, or add an optional flag to allow operator signatures in ERC-1271 with scope restrictions.

### M-3: No Input Validation on `setOperator(address(0))`

**Severity:** Medium

**Description:** `setOperator(address(0), true)` would set the zero address as an operator. While nobody can send from address(0), it wastes a storage slot and could confuse off-chain indexers.

**Recommended Fix:** Add `require(operator != address(0), "Invalid operator")`.

### M-4: `agentTransferToken` Uses `safeTransfer` But `approvePending` Uses Raw `.call`

**Severity:** Medium

**Description:** `agentTransferToken` correctly uses SafeERC20's `safeTransfer`. But when an ERC20 pending tx is approved via `approvePending`, it executes via raw `.call` with the encoded `transfer` selector. This skips SafeERC20's return-value checking, making it vulnerable to tokens that don't return `bool` (like USDT).

**Impact:** Approved pending ERC20 transfers may silently fail for non-standard tokens.

**Recommended Fix:** In `approvePending`, detect if `ptx.token != address(0)` and use `IERC20(ptx.token).safeTransfer()` instead of raw call. Or re-decode the transfer params and execute via SafeERC20.

### M-5: Factory `createAccount` Has No Access Control

**Severity:** Medium  
**Contract:** AgentAccountFactoryV2.sol

**Description:** Anyone can call `createAccount` for any NFT. This means someone can deploy an account for an NFT they don't own. While the deployed account's owner is correctly the NFT holder (via `ownerOf`), there are edge cases:
- Front-running: if NFT owner wants to deploy with specific initialization, an attacker can deploy first
- The deployer gets no special privileges, but they control the deployment timing

**Impact:** Low practical impact since the NFT owner controls the account. But deployment timing can be manipulated.

**Recommended Fix:** Consider requiring `msg.sender == IERC721(tokenContract).ownerOf(tokenId)` or making it permissionless by design (document it).

---

## Low Findings

### L-1: `nonce` Not Used for Replay Protection

**Severity:** Low

**Description:** The `nonce` variable is incremented on execution but never checked or used in any signature validation (in the base contract). It's purely informational. In the 4337 contract, `validateUserOp` receives a `nonce` in the `UserOperation` but doesn't check it against the contract's `nonce` — the EntryPoint handles nonce management separately.

**Recommended Fix:** Either remove the `nonce` variable (save gas) or document it as informational-only. The dual nonce (contract + EntryPoint) could confuse integrators.

### L-2: Missing `data` Field in `getPending` Return

**Severity:** Low

**Description:** `getPending()` returns most fields but omits `data` (the calldata). Off-chain tools need this to display what the pending transaction will do.

**Recommended Fix:** Add `bytes memory data` to the return values, or add a separate `getPendingData(uint256 txId)` function.

### L-3: Events Emit Inconsistent `to` for Queued Token Transfers

**Severity:** Low

**Description:** In `agentTransferToken`, when a transfer is queued, the `TransactionQueued` event emits `to` (the recipient) but the `PendingTx.to` is set to the **token contract address**. This inconsistency between the event and the stored data could confuse indexers.

**Recommended Fix:** Either store the recipient in `PendingTx` separately, or emit the token contract address in the event.

---

## What's Well-Designed

1. **Spend limit architecture** — Per-token, per-period limits with per-tx caps is a solid design pattern. The rolling window approach is clean.
2. **Owner always bypasses** — The NFT-holder-as-owner pattern via ERC-6551 is elegant. Owner can always execute directly.
3. **Pending queue pattern** — Over-limit transactions don't revert; they queue for approval. This is excellent UX.
4. **SafeERC20 usage** in `agentTransferToken` — Correct use of safe transfer wrappers.
5. **Deterministic deployment** via CREATE2 factory — One wallet per NFT, predictable addresses.
6. **Solidity 0.8.19** — Built-in overflow protection eliminates integer overflow class.
7. **Immutable core state** — `tokenContract`, `tokenId`, `entryPoint` are immutable.
8. **Clean separation** — Base contract vs 4337 extension is well-structured.

---

## Overall Recommendation

### 🟡 DEPLOY WITH FIXES

**Must fix before mainnet (Critical/High):**
1. **C-1/H-1:** Restrict `agentExecute` calldata for operators — this is the most dangerous finding. An operator can drain all ERC20s.
2. **C-2:** Reorder `_recordSpend` before external call in `approvePending`.
3. **H-2:** Add `ReentrancyGuard` to all state-mutating external functions.
4. **H-3:** Add pending queue limits and expiry.
5. **H-4:** Fix `validateUserOp` gas griefing for operator-signed ops.

**Should fix (Medium):**
- M-4: Use SafeERC20 in `approvePending` for token transfers.
- M-1: Add operator freeze mechanism.
- M-3: Validate operator address.

The architecture is fundamentally sound. The critical issue (C-1) is a design gap rather than a bug — `agentExecute` was designed for ETH transfers but its arbitrary calldata capability creates an unintended bypass of the carefully designed token spend limits. Closing this gap transforms the contract from "exploitable" to "production-ready."
