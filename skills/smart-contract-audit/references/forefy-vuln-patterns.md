# Forefy Vulnerability Patterns — Unique Insights

Condensed from Forefy's FV-SOL categories. Only patterns not already covered in our other references.

## FV-SOL-1: Reentrancy — Advanced Patterns

Beyond basic CEI violations:
- **Cross-contract reentrancy via shared state:** Contract A calls Contract B, which calls back to Contract A through Contract C. The shared state between A and C is inconsistent during B's execution.
- **Read-only reentrancy:** View functions called during reentrancy return stale state. Particularly dangerous when other protocols use these view functions for pricing (e.g., Curve `get_virtual_price()`).
- **ERC-777/ERC-1155 callbacks:** `tokensReceived` and `onERC1155Received` hooks create reentrancy vectors even in seemingly safe transfers.
- **Transient storage reentrancy guards (EIP-1153):** Cheaper than storage-based guards but only protect within the same transaction. Cross-transaction reentrancy still possible.

## FV-SOL-2: Precision Errors — Subtle Patterns

- **Phantom overflow in mulDiv:** Even with Solidity 0.8, `a * b` can overflow before division. Use `Math.mulDiv()` for intermediate products exceeding uint256.
- **Decimal mismatch accumulation:** Small rounding errors per operation compound over many operations. A vault processing 1000 deposits/day can accumulate significant drift.
- **Price ratio inversion:** When computing `a/b` vs `b/a`, the rounding direction changes. Ensure the direction favors the protocol.
- **Mixed-precision arithmetic:** Combining 6-decimal (USDC) with 18-decimal (ETH) values — always normalize BEFORE arithmetic, not after.

## FV-SOL-3: Arithmetic — Edge Cases

- **Sign extension in type casting:** Casting negative `int256` to `uint256` produces a very large number, not an error in Solidity 0.8.
- **Truncation in downcasting:** `uint256` to `uint128` silently truncates in Solidity < 0.8.19. Use OpenZeppelin's `SafeCast`.
- **`block.timestamp` manipulation:** Miners can manipulate by ~15 seconds. Don't use for precise timing or randomness.
- **`unchecked` blocks:** Solidity 0.8 protections are disabled inside `unchecked {}`. Audit every unchecked block for potential overflow.

## FV-SOL-5: Logic Errors — Non-Obvious

- **Epoch boundary bugs:** Reward calculations that span epoch boundaries may double-count or skip rewards at the transition point.
- **Off-by-one in comparison:** `>=` vs `>` in time-based checks can allow one-block-early execution.
- **Initialization front-running:** Unprotected `initialize()` can be called by anyone if the deployer doesn't call it atomically.
- **Storage layout collision in upgrades:** New storage variables in upgraded contracts must go AFTER the gap, not in the middle.

## FV-SOL-6: Unchecked Returns — Modern Patterns

- **ERC20 `approve` race condition:** `approve(0)` then `approve(newAmount)` is not atomic. Use `increaseAllowance`/`decreaseAllowance` or `safeIncreaseAllowance`.
- **`permit` front-running:** If `permit` is called separately from the operation, it can be front-run. Always try-catch permit calls and proceed if allowance is already set.
- **Low-level `call` to EOA:** Always returns `true` for externally-owned accounts, even if the address has no code. Verify target is a contract if needed.

## FV-SOL-7: Proxy Insecurities

- **Uninitialized implementation:** The implementation contract itself can be initialized by anyone, potentially allowing `selfdestruct` (pre-Dencun) or state manipulation.
- **Storage collision between proxy and implementation:** Both proxy and implementation use slot 0+. EIP-1967 admin/implementation slots avoid this.
- **Function selector clashing:** Proxy admin functions can shadow implementation functions if selectors collide.
- **UUPS: missing `_authorizeUpgrade` override:** If the override is empty or unrestricted, anyone can upgrade.

## FV-SOL-8: Slippage & MEV

- **Deadline parameter missing:** Swap transactions without a deadline can be held by validators and executed at a worse price later.
- **Hardcoded slippage (especially 0):** `minAmountOut = 0` means the user accepts any price. Always require caller-specified slippage.
- **Multi-step operations:** If a complex operation involves multiple swaps, slippage protection on the final output doesn't protect intermediate steps.

## FV-SOL-10: Oracle Manipulation

- **Chainlink staleness:** Check `updatedAt` against a heartbeat threshold. Stale prices can be arbitraged.
- **L2 sequencer uptime:** On Optimism/Arbitrum, if the sequencer goes down, prices are stale. Check the sequencer uptime feed.
- **TWAP manipulation cost:** For Uniswap V3 TWAPs, calculate the cost to manipulate the price for the TWAP window. Short windows are cheaper to attack.
- **Compound oracle (price A * price B):** Compound oracles multiply error margins. If both sources have 1% error, the compound has ~2% error.
