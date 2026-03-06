# Cyfrin/Solodit Audit Checklist — Condensed Reference

Source: https://github.com/Cyfrin/audit-checklist

## Attacker's Mindset Categories

### DoS Attacks
- [ ] Is withdrawal pattern (pull-based) used to prevent DoS?
- [ ] Is there a minimum transaction amount enforced (prevent dust spam)?
- [ ] How does protocol handle tokens with blacklisting (USDC)?
- [ ] Can forcing protocol to process a queue (dust withdrawals) cause DoS?
- [ ] What happens with low decimal tokens (rounding to zero)?
- [ ] Are external contract interactions handled safely (Chainlink revert)?

### Donation Attack
- [ ] Does protocol rely on `balance`/`balanceOf` instead of internal accounting? (inflate via donation)

### Front-running
- [ ] Are "get-or-create" patterns protected against front-running?
- [ ] Are two-transaction actions safe from front-running?
- [ ] Can users cause others' txs to revert by preempting with dust?
- [ ] Is commit-reveal scheme properly user-bound (include msg.sender in hash)?

### Griefing
- [ ] Is there an external function relying on states changeable by others?
- [ ] Can contract operations be manipulated with precise gas limit specifications?

### Miner/Validator Attack
- [ ] Is `block.timestamp` used for time-sensitive operations? (manipulable)
- [ ] Are block properties used for randomness? (use Chainlink VRF instead)
- [ ] Is contract logic sensitive to transaction ordering?

### Price Manipulation
- [ ] Is price calculated by ratio of token balances? (flash loan manipulable)
- [ ] Is price from DEX spot prices? (use TWAP or Chainlink)

### Reentrancy
- [ ] Is there a view function returning stale values during interactions? (read-only reentrancy)
- [ ] Is there state change AFTER external call? (CEI pattern violation)
- [ ] Cross-protocol reentrancy via callbacks?

### Replay Attack
- [ ] Are failed transactions protected against replay?
- [ ] Is there chain-specific domain separator for signatures?

### Rug Pull
- [ ] Can admin pull user assets directly? (timelock mitigation)

### Sandwich Attack
- [ ] Does protocol have explicit slippage protection?

### Sybil Attack
- [ ] Is there a mechanism depending on number of users? (quorum gaming)

---

## Basics Categories

### Access Control
- [ ] Are all actors and allowed interactions clarified?
- [ ] Are there functions lacking proper access controls?
- [ ] Do certain addresses require whitelisting?
- [ ] Is privilege transfer done in two-step process?
- [ ] Does protocol work correctly during privilege transfer?
- [ ] Are parent contract public functions properly restricted?
- [ ] Is `tx.origin` used in validation? (use `msg.sender`)

### Array / Loop
- [ ] First and last iteration edge cases checked?
- [ ] Array deletion: using swap-and-pop (not just `delete`)?
- [ ] Functions taking array index as argument — index stability?
- [ ] Summation precision vs individual calculations?
- [ ] Duplicate items in arrays validated?
- [ ] Unbounded iteration possible (block gas limit DoS)?
- [ ] External calls inside loops (single failure reverts all)?
- [ ] `msg.value` used inside loop? (consistent for whole tx)
- [ ] Batch fund transfer handles residual/dust correctly?
- [ ] Break/continue inside loops — unexpected state changes?

### Block Reorganization
- [ ] Factory pattern using CREATE opcode? (use CREATE2 for reorg safety)

### Events
- [ ] Events emitted on important state changes?

### Function
- [ ] Inputs validated (min/max, ownership, dates)?
- [ ] Outputs validated?
- [ ] Can function be front-run?
- [ ] Comments coherent with implementation?
- [ ] Edge case inputs (0, max) handled?
- [ ] Arbitrary user input in low-level calls?
- [ ] Visibility modifier appropriate (prefer private/internal)?
- [ ] EOA-only or contract-only restriction needed?

### Inheritance
- [ ] Parent contract public functions properly overridden/restricted?
- [ ] All necessary functions implemented for inheritance?

---

## DeFi-Specific Checks

### Token Integration
- [ ] Does contract handle fee-on-transfer tokens?
- [ ] Does contract handle rebasing tokens?
- [ ] Does contract handle ERC-777 tokens (callbacks/reentrancy)?
- [ ] Does contract handle tokens with different decimals?
- [ ] Does contract handle tokens that return false instead of reverting?
- [ ] Does contract handle tokens with no return value (USDT)?
- [ ] Does contract handle tokens with multiple addresses (double-entry)?
- [ ] Is `SafeERC20` / `safeTransfer` used?

### Oracle
- [ ] Is oracle data validated for staleness (heartbeat check)?
- [ ] Is Chainlink `latestRoundData()` return checked for all values?
- [ ] Is there a fallback oracle?
- [ ] Are L2 sequencer uptime checks implemented?
- [ ] Can oracle return price of 0?

### Vault / Share
- [ ] First depositor inflation attack mitigated? (virtual shares/minimum deposit)
- [ ] Share calculation: rounding direction correct? (favor vault)
- [ ] Empty vault edge cases handled?

### Lending / Borrowing
- [ ] Liquidation threshold calculated correctly?
- [ ] Interest accrual timing issues?
- [ ] Can dust positions prevent liquidation?

### Governance
- [ ] Flash loan governance attack possible?
- [ ] Proposal/vote timing manipulation?
- [ ] Quorum bypass with delegation?

### Cross-chain / Bridge
- [ ] Message replay across chains?
- [ ] Failed message handling?
- [ ] Chain-specific behavior differences?

### Proxy / Upgradeability
- [ ] Implementation initialized immediately?
- [ ] Storage layout matches between proxy and implementation?
- [ ] Initializer can only be called once?
- [ ] No `selfdestruct` or `delegatecall` in implementation?
- [ ] Function selector clashes between proxy and implementation?

### Math / Precision
- [ ] Division before multiplication (precision loss)?
- [ ] Rounding direction correct for protocol (round against user)?
- [ ] Overflow/underflow in unchecked blocks?
- [ ] Casting between types (uint256 to uint128, int to uint)?

### Signature
- [ ] EIP-712 domain separator includes chainId?
- [ ] Nonce used to prevent replay?
- [ ] Signature malleability handled (use ECDSA library)?
- [ ] `ecrecover` return value of address(0) checked?
- [ ] Deadline/expiry enforced?

### ETH Handling
- [ ] Contract can receive ETH when needed (receive/fallback)?
- [ ] Forced ETH via selfdestruct handled?
- [ ] `msg.value` checked in non-payable multicall?

### Timestamp
- [ ] Block timestamp manipulation tolerance acceptable?
- [ ] Time-dependent logic uses appropriate granularity?
