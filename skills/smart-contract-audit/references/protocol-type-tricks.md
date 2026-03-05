# Protocol-Type-Specific Audit Tricks

Condensed from Forefy and community sources. After detecting protocol type, load the relevant section for targeted checks.

## DeFi AMM/DEX

- Check if external calls use `.call()` but don't validate return data length for contracts that might self-destruct
- Verify token transfers handle non-standard decimals (not all tokens are 18 decimals)
- Look for MEV extraction in multi-hop swaps or arbitrage paths
- Verify slippage protection accounts for fee-on-transfer tokens reducing received amounts
- Check swap calculations for intermediate overflow in complex pricing formulas
- Search for price impact manipulation via sandwich attacks on low-liquidity pools
- Verify `k` invariant is maintained after every swap (constant product/sum)

## Lending/Borrowing

- Check liquidation logic handles underwater positions during market crashes (bad debt socialization)
- Look for interest rate overflow with extremely high utilization rates
- Verify collateral valuation uses TWAP or Chainlink, not spot prices (flash-loanable)
- Check repayment functions update debt correctly with compound interest
- Look for governance proposals that can execute immediately by manipulating `block.timestamp`
- Verify flash loan callbacks verify the original caller owns the loan
- Check that health factor calculations use consistent price sources for collateral vs debt
- Look for liquidation cascades where liquidating one position triggers more liquidations

## Stablecoin / Pegged Asset

- **Peg mechanism:** How is $1.00 maintained? Mint/redeem, AMM, algorithmic?
- **Depeg scenarios:** What happens when collateral drops below backing? Graceful degradation or cliff?
- **CAP pricing:** Is the price capped at $1.00 or can it exceed? What's the formula?
- **Reserve composition:** Single-asset or multi-asset? How are different assets valued?
- **Decimal normalization:** All reserve assets normalized to same precision? Watch for 6↔18 decimal mismatches.
- **Fee-on-transfer interactions:** Does the stablecoin itself have transfer fees? How do other protocols handle this?
- **Denylist/freeze:** USDC-style address freezing — does it propagate to DeFi positions?
- **Cash-in-flight:** During asset conversion (USDC→T-bills), is the gap properly accounted for?
- **Circular dependencies:** Does price calculation depend on supply, which depends on price?

## Yield Vault / Staking (ERC4626)

- **First depositor attack:** Can the first depositor inflate share price to steal from subsequent depositors? (donate assets to vault before others deposit)
- **Donation attacks:** Can direct token transfer to vault manipulate share price?
- **Synthetic vs real totalAssets:** If `totalAssets()` is synthetic (not based on balance), donation attacks are mitigated but verify the synthetic math.
- **Share price manipulation:** Can share price be moved within a single transaction?
- **Rounding direction:** Deposits should round DOWN (fewer shares), withdrawals round UP (more shares needed). Protocol-favorable rounding.
- **Cooldown/timelock bypass:** Can the cooldown be circumvented by transferring shares to a fresh address?
- **Yield stream attacks:** If yield is admin-set, can it be set to extract value from existing depositors?
- **Empty vault edge case:** What happens when totalSupply = 0? Division by zero? type(uint256).max?
- **Cross-reference ERC4626 compliance:** `maxDeposit`, `maxWithdraw`, `previewDeposit`, `previewRedeem` must be consistent with actual behavior.

## Bridge / Cross-chain

- Check message verification validates merkle proofs against correct block headers
- Look for relay systems that don't verify message ordering or prevent replay attacks
- Verify asset locks on source chain require corresponding unlocks on destination
- Check for validator consensus that can be manipulated with <33% stake
- Look for time-locked withdrawals that can be front-run during dispute periods
- Verify cross-chain message passing validates sender authenticity
- Check for stuck assets when bridge fails (no recovery mechanism)

## NFT / Gaming

- Check metadata URIs can't be modified by unauthorized parties after minting
- Look for predictable randomness (block.timestamp, blockhash for VRF)
- Verify royalty calculations handle zero prices and maximum royalties
- Check batch operations validate individual item permissions
- Look for game state front-running or sandwich attacks
- Verify play-to-earn has anti-sybil protections

## Governance / DAO

- Check voting power can't be flash-loaned (snapshot-based vs current-balance)
- Look for proposal execution without state validation
- Verify timelock delays can't be bypassed through proposal dependencies or emergency functions
- Check quorum calculations account for total supply changes
- Look for delegation loops or vote buying mechanisms
- Verify treasury access requires multi-sig approval
- Check for proposal griefing (spam proposals to exhaust gas or attention)

## Cross-Cutting Concerns (All Protocol Types)

- **Upgrade safety:** UUPS/transparent proxy — is storage layout preserved? Can admin rug via upgrade?
- **Fee calculations:** Division before multiplication? Rounding direction consistent?
- **Token assumptions:** Does the protocol assume all ERC20s behave like standard tokens? (fee-on-transfer, rebasing, pausable, denylistable)
- **Decimal handling:** Mixed decimal tokens (6-decimal USDC + 18-decimal tokens) — are conversions correct?
- **Admin key compromise:** What's the blast radius of a compromised admin key?
- **External dependency failure:** What if oracle/bridge/DEX goes down? Are user funds stuck?
