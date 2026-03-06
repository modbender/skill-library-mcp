# EthSkills Security Reference — Condensed for Audit Agents

Source: ethskills.com (security, building-blocks, concepts)

---

## What You Probably Got Wrong (Sanity Check for ALL Agents)

**"Solidity 0.8+ prevents overflows, so I'm safe."** Overflow is one of dozens of attack vectors. The big ones: reentrancy, oracle manipulation, approval exploits, decimal mishandling.

**"I tested it and it works."** Working correctly ≠ secure. Most exploits call functions in orders or with values the developer never considered.

**"It's a small contract, it doesn't need an audit."** The DAO hack was simple reentrancy. Euler was a single missing check.

**"Smart contracts run automatically."** No. There is no cron, no scheduler, no background process. Every function needs a caller who pays gas. This misconception is the root cause of most broken onchain designs.

**"The protocol team will handle that."** If your design requires an operator, it has a single point of failure.

---

## Incentive Design Framework ("Who Pokes It? Why Would They?")

**For EVERY state transition in a protocol, answer:**

1. **Who pokes it?** (someone must pay gas)
2. **Why would they?** (what's their incentive?)
3. **Is the incentive sufficient?** (covers gas + profit?)

If you can't answer these, that state transition will never happen. The contract sits in its current state forever.

### The Hyperstructure Test
"Could this run forever with no team behind it?"
- Yes → hyperstructure (incentives sustain it)
- No → service (dies when team stops operating it)

### Good Incentive Patterns
- **Liquidations:** Anyone can call, caller gets bonus collateral
- **LP fees:** Depositors earn swap fees, flywheel is self-reinforcing
- **Yield harvesting:** Anyone can call harvest(), caller gets % reward
- **Arbitrage:** Price differences resolved by profit-seeking actors

### Bad Incentive Patterns (Red Flags for Auditors)
- "The contract will check prices every hour" → WHO pays gas? WHY?
- "Expired listings get automatically removed" → Nothing is automatic
- "The protocol rebalances daily" → Whose gas? What profit?
- "An admin will manually trigger the next phase" → Single point of failure

---

## Critical Security Patterns

### Token Decimals
USDC=6, WBTC=8, DAI/WETH=18. Never hardcode 1e18. Normalize across tokens:
```
uint256 normalized = usdcAmount * 1e12; // 6→18 decimals
```

### Integer Math
Always multiply before dividing. Division first = precision loss.
```
// ❌ a / b * c  (precision loss)
// ✅ (a * c) / b
```
Use basis points (1 bp = 0.01%): `fee = (amount * feeBps) / 10_000`

### Reentrancy
Checks → Effects → Interactions (CEI). Always use ReentrancyGuard as safety net.
State changes BEFORE external calls.

### SafeERC20
Some tokens (USDT) don't return bool. Use SafeERC20 for all token ops.
Watch for: fee-on-transfer tokens, rebasing tokens, pausable tokens, blocklist tokens.

### Oracle Safety
Never use DEX spot prices — flash-loan manipulable. Use Chainlink with staleness checks.
If using onchain prices, use TWAP (30+ min window).

### Vault Inflation Attack (ERC-4626)
First depositor manipulates share price via donation. Fix: virtual offset in share math.
OpenZeppelin v5 ERC4626 includes mitigation by default.

### Access Control
Every state-changing function needs explicit access control. Map the full privilege hierarchy.

### Input Validation
Zero addresses, zero amounts, array length mismatches, values exceeding bounds.

---

## DeFi Composability Attack Surfaces

### Flash Loan Vectors
- Borrow → manipulate price → profit → repay, all in one tx
- Governance voting with borrowed tokens
- Share/LP ratio manipulation in single transaction
- Cost: ~$0.05-0.50 gas on mainnet (economically viable for any amount)

### MEV / Sandwich Attacks
- Missing slippage protection = sandwich target
- Two-step processes (approve + action) = front-running opportunity
- DEX trades without minAmountOut

### Composability Risks
- Every composed protocol is a dependency (if Aave is hacked, your vault is affected)
- Interaction between two safe contracts can create unsafe behavior
- Oracle manipulation cascades across integrated protocols

### Vault Accounting Attacks
- Deposit and withdraw in same block to extract value
- Donation attacks via direct token transfer
- Share/asset ratio skewed by large deposit or donation

---

## Pre-Deploy Security Checklist

- [ ] Access control on every admin/privileged function
- [ ] Reentrancy: CEI + nonReentrant on all external-calling functions
- [ ] Token decimal handling: no hardcoded 1e18
- [ ] Oracle: Chainlink/TWAP, not DEX spot. Staleness checks.
- [ ] Integer math: multiply before divide
- [ ] Return values: SafeERC20 for all token operations
- [ ] Input validation: zero address, zero amount, bounds
- [ ] Events emitted for every state change
- [ ] Incentive design: maintenance functions callable by anyone with incentive
- [ ] No infinite approvals
- [ ] Fee-on-transfer safe if accepting arbitrary tokens
- [ ] Edge cases tested: zero values, max values, unauthorized callers
