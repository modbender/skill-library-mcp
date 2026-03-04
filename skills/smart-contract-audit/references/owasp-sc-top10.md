# OWASP Smart Contract Top 10 (2025/2026) — Condensed Reference

Source: https://owasp.org/www-project-smart-contract-top-10/

## 2026 Top 10 (Forward-Looking, based on 2025 incident data)

### SC01: Access Control Vulnerabilities [MOST CRITICAL]
**What:** Unauthorized users invoke privileged functions or modify critical state.
**Look for:**
- Missing `onlyOwner`/role modifiers on admin functions
- `tx.origin` used instead of `msg.sender`
- Unprotected `initialize()` functions
- Exposed governance/upgrade paths
- Parent contract functions not properly overridden
**Code pattern:** Any `external`/`public` function that modifies state without access checks

### SC02: Business Logic Vulnerabilities
**What:** Design-level flaws that break intended economic/functional rules.
**Look for:**
- Incorrect reward/fee distribution math
- Wrong ordering of operations
- Missing edge case handling (zero amounts, empty arrays)
- Flawed liquidation/collateral logic
- State machine violations (skipping states)
**Code pattern:** Complex multi-step processes, reward calculations, lending logic

### SC03: Price Oracle Manipulation
**What:** Attackers skew reference prices for under-collateralized borrowing or unfair liquidations.
**Look for:**
- Spot price from DEX pools (manipulable via flash loans)
- Missing TWAP or Chainlink integration
- Stale oracle data (no heartbeat/freshness check)
- Single oracle dependency (no fallback)
- `get_virtual_price()` read-only reentrancy (Curve)
**Code pattern:** Any `getPrice()`, `latestRoundData()`, pool ratio calculations

### SC04: Flash Loan–Facilitated Attacks
**What:** Large uncollateralized loans amplify small bugs into large drains.
**Look for:**
- Price derived from token balance ratios
- Governance votes based on current token balance
- Share/LP calculations manipulable in single tx
- Missing flash loan guards (same-block checks)
**Code pattern:** `balanceOf()` used for pricing, single-tx economic assumptions

### SC05: Lack of Input Validation
**What:** Unsafe parameters reach core logic, corrupting state.
**Look for:**
- Missing zero-address checks
- No bounds on numeric inputs (amounts, percentages, durations)
- Unchecked array lengths
- Missing ownership validation on position/token IDs
- Arbitrary calldata forwarded without sanitization
**Code pattern:** External functions without `require()` at top

### SC06: Unchecked External Calls
**What:** Failures, reverts, or callbacks from external contracts not handled.
**Look for:**
- Low-level `call()` without checking return bool
- Missing `try/catch` on external calls
- ERC20 `transfer()` without `SafeERC20`
- No contract existence check before `delegatecall`
**Code pattern:** `.call()`, `.send()`, `.transfer()`, raw `delegatecall`

### SC07: Arithmetic Errors
**What:** Integer math, scaling, rounding bugs causing precision loss or value siphoning.
**Look for:**
- Division before multiplication
- Rounding in wrong direction (should favor protocol)
- Unchecked arithmetic in `unchecked {}` blocks
- Precision loss with different decimal tokens
- Share/interest calculations with small numbers
**Code pattern:** Any division, percentage calculation, share math

### SC08: Reentrancy Attacks
**What:** External calls re-enter before state is updated.
**Look for:**
- State changes AFTER external calls (CEI violation)
- Missing reentrancy guards on state-changing functions
- Read-only reentrancy (view functions return stale data)
- Cross-contract reentrancy (shared state across contracts)
- ERC-777/ERC-721 callbacks (`onTokenReceived`, `onERC721Received`)
**Code pattern:** `call()`, `transfer()`, token callbacks before state update

### SC09: Integer Overflow and Underflow
**What:** Wrapped values from arithmetic without checks.
**Look for:**
- `unchecked {}` blocks with user-controlled values
- Solidity < 0.8.0 without SafeMath
- Type casting (uint256→uint128, int→uint)
- Multiplication that can exceed type bounds
**Code pattern:** `unchecked { }`, type casts, pre-0.8 contracts

### SC10: Proxy & Upgradeability Vulnerabilities
**What:** Misconfigured proxy, initialization, or upgrade mechanisms.
**Look for:**
- Uninitialized implementation contracts
- Storage layout mismatch (proxy vs implementation)
- Missing `initializer` modifier / can call `initialize()` twice
- Function selector clashes
- `selfdestruct` in implementation
- Missing upgrade access controls
**Code pattern:** `delegatecall`, `initializer`, `_disableInitializers()`
