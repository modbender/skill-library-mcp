# Yield.xyz Usage Examples

## OpenClaw Agent Conversations

These are real conversation flows showing how an agent uses the yield-agent skill on OpenClaw. Each example shows the user prompt, what the agent does behind the scenes, and how it responds. All yield IDs are real and verified against the live Yield.xyz API on Base network.

---

### Conversation 1: First-Time Discovery

**User:** "What yield opportunities are available for USDC on Base?"

**Agent thinks:** I'll search for USDC yields on Base using the yield-agent skill.

**Agent runs:**
```bash
./scripts/find-yields.sh base USDC
```

**Agent responds:**

> I found several **USDC yield opportunities** on Base. Here are the top options by APY:
>
> | Protocol | Type | APY | Yield ID |
> |----------|------|-----|----------|
> | Morpho (Flagship) | Vault | 5.72% | `base-usdc-cousdc-0x1d3b1cd0a0f242d598834b3f2d126dc6bd774657-4626-vault` |
> | Morpho (MEV Capital) | Vault | 4.91% | `base-usdc-mevfusdc-0x8773447e6369472d9b72f064ea62e405216e9084-4626-vault` |
> | Morpho (Gauntlet) | Vault | 4.36% | `base-usdc-gtusdcf-0x236919f11ff9ea9550a4287696c2fc9e18e6e890-4626-vault` |
> | Aave v3 | Lending | 3.82% | `base-usdc-aave-v3-lending` |
> | Compound v3 | Lending | 3.19% | `base-usdc-compound-v3-lending` |
>
> The **Morpho Flagship vault** at 5.72% is the highest. Morpho vaults are curated by professional risk managers and auto-optimize across lending markets. Aave and Compound are simpler lending protocols — lower APY but more battle-tested.
>
> Would you like me to deposit into any of these? I'll need your wallet address and the amount.

---

### Conversation 2: Depositing into Morpho Flagship

**User:** "Deposit 500 USDC into the Morpho flagship vault. My wallet is 0x742d35Cc6634C0532925a3b844Bc454e4438f44e"

**Agent thinks:** I'll enter 500 USDC into the Morpho flagship vault. First let me check the yield's argument schema.

**Agent runs:**
```bash
./scripts/enter-position.sh base-usdc-cousdc-0x1d3b1cd0a0f242d598834b3f2d126dc6bd774657-4626-vault 0x742d35Cc6634C0532925a3b844Bc454e4438f44e '{"amount":"500"}'
```

**Agent responds:**

> I've prepared your deposit of **500 USDC** into the Morpho Flagship USDC vault on Base.
>
> **Transaction Summary:**
> - Action: Deposit (Enter)
> - Amount: 500 USDC ($500.00)
> - Protocol: Morpho (Flagship vault)
> - Network: Base
> - Current APY: 5.72%
> - Estimated Annual Earnings: ~$28.60
>
> The transaction is ready for signing. There are **2 steps**:
> 1. Approve USDC spending (if not already approved)
> 2. Deposit into Morpho vault
>
> Shall I sign and submit this with your wallet?

**Illustrative API Response (actual IDs and data will vary):**
```json
{
  "id": "<action-uuid>",
  "intent": "enter",
  "type": "SUPPLY",
  "yieldId": "base-usdc-cousdc-0x1d3b1cd0a0f242d598834b3f2d126dc6bd774657-4626-vault",
  "address": "0x742d...",
  "amount": "500.000000",
  "amountRaw": "500000000",
  "status": "CREATED",
  "transactions": [
    {
      "id": "<tx-uuid-1>",
      "title": "Approve Transaction",
      "network": "base",
      "status": "CREATED",
      "type": "APPROVAL",
      "unsignedTransaction": "<JSON string - parse before signing>",
      "stepIndex": 0,
      "gasEstimate": "<JSON string with amount and gasLimit>"
    },
    {
      "id": "<tx-uuid-2>",
      "title": "SUPPLY Transaction",
      "network": "base",
      "status": "CREATED",
      "type": "SUPPLY",
      "unsignedTransaction": "<JSON string - parse before signing>",
      "stepIndex": 1,
      "gasEstimate": "<JSON string with amount and gasLimit>"
    }
  ]
}
```

**Transaction signing flow:**
```bash
# For each transaction in stepIndex order:
# 1. Pass unsignedTransaction to wallet skill for signing + broadcasting — do NOT modify any field (WILL RESULT IN PERMANENT LOSS OF FUNDS)
# 2. Submit hash: PUT /v1/transactions/{txId}/submit-hash { "hash": "0x..." }
# 3. Poll: GET /v1/transactions/{txId} until status = "CONFIRMED"
# 4. Proceed to next transaction
```

---

### Conversation 3: Checking a Position

**User:** "How is my Morpho USDC position doing?"

**Agent thinks:** I'll check the balance for their Morpho flagship USDC vault position.

**Agent runs:**
```bash
./scripts/check-portfolio.sh base-usdc-cousdc-0x1d3b1cd0a0f242d598834b3f2d126dc6bd774657-4626-vault 0x742d35Cc6634C0532925a3b844Bc454e4438f44e
```

**Agent responds:**

> Your **Morpho Flagship USDC** vault position on Base:
>
> | | Amount | Value |
> |---|--------|-------|
> | Deposited | 502.35 USDC | $502.35 |
> | Status | Earning | Active |
>
> You've earned **$2.35 in interest** since your deposit. Your position is actively earning at the current 5.72% APY.
>
> At this rate, you'd earn approximately:
> - **$28.73** per year
> - **$2.39** per month
>
> Would you like to add more, withdraw some, or check other positions?

**Illustrative API Response (actual values will vary):**
```json
{
  "yieldId": "base-usdc-cousdc-0x1d3b1cd0a0f242d598834b3f2d126dc6bd774657-4626-vault",
  "balances": [
    {
      "address": "0x742d...",
      "type": "active",
      "amount": "502.350000",
      "amountRaw": "502350000",
      "amountUsd": "502.35",
      "token": { "symbol": "USDC", "decimals": 6, "network": "base" },
      "pendingActions": [],
      "isEarning": true
    }
  ]
}
```

---

### Conversation 4: Claiming Rewards

**User:** "Do I have any rewards to claim on my Cosmos staking?"

**Agent thinks:** I'll check balances for their ATOM staking position and look for pendingActions in the response.

**Agent runs:**
```bash
./scripts/check-portfolio.sh cosmos-atom-native-staking 0x742d35Cc6634C0532925a3b844Bc454e4438f44e
```

**Agent responds:**

> Your **ATOM Native Staking** position on Cosmos:
>
> | | Amount | Value |
> |---|--------|-------|
> | Staked | 100 ATOM | $850.00 |
> | Claimable Rewards | 2.5 ATOM | $21.25 |
>
> You have **2.5 ATOM ($21.25)** in claimable staking rewards. Would you like me to claim them?
>
> *Note: Cosmos staking distributes rewards separately from your staked balance. You need to explicitly claim them.*

**User:** "Yes, claim my rewards"

**Agent thinks:** I'll use the passthrough value from the pendingActions in the balance response.

**Agent runs:**
```bash
# The passthrough value comes from the pendingActions array in the balance response
./scripts/manage-position.sh cosmos-atom-native-staking 0x742d35Cc6634C0532925a3b844Bc454e4438f44e CLAIM_REWARDS "<passthrough-from-balances>"
```

**Agent responds:**

> Reward claim submitted for **2.5 ATOM ($21.25)** from your Cosmos staking position.
>
> Transaction confirmed. The ATOM has been sent to your wallet.
>
> Would you like to restake these rewards to compound your earnings, or keep them liquid?
>
> *Tip: Not all staking protocols require manual claiming. Lido (ETH) and other liquid staking protocols auto-compound rewards into your staked balance. Cosmos, Polkadot, and similar PoS chains require explicit reward claims.*

---

### Conversation 5: Withdrawing from a Vault

**User:** "I want to withdraw 200 USDC from my Morpho vault"

**Agent thinks:** I'll exit 200 USDC from the Morpho vault.

**Agent runs:**
```bash
./scripts/exit-position.sh base-usdc-cousdc-0x1d3b1cd0a0f242d598834b3f2d126dc6bd774657-4626-vault 0x742d35Cc6634C0532925a3b844Bc454e4438f44e '{"amount":"200"}'
```

**Agent responds:**

> Withdrawal prepared for **200 USDC** from Morpho Flagship vault on Base.
>
> **Transaction Summary:**
> - Action: Withdraw (Exit)
> - Amount: 200 USDC ($200.00)
> - Network: Base
> - Estimated Gas: ~0.000028 ETH ($0.07)
>
> After this withdrawal, your remaining position will be approximately **302.35 USDC** continuing to earn 5.72% APY.
>
> Ready to sign and submit?

---

### Conversation 6: Comparing ETH Yields on Base

**User:** "Where can I get the best yield for my ETH on Base?"

**Agent thinks:** I'll search ETH/WETH yields on Base to compare protocols.

**Agent runs:**
```bash
./scripts/find-yields.sh base ETH 10
./scripts/find-yields.sh base WETH 10
```

**Agent responds:**

> Here are the best **ETH yield opportunities on Base**, all above 2% APY:
>
> | Protocol | Type | APY | Token | Yield ID |
> |----------|------|-----|-------|----------|
> | Morpho (9Summits Core) | Vault | 7.06% | WETH | `base-weth-9sethcore-0x5496b...-4626-vault` |
> | KelpDAO | Restaking | 2.95% | ETH | `base-kelpdao-rseth-staking` |
> | Morpho (Steakhouse) | Vault | 2.77% | WETH | `base-weth-cseth-0x0983...-4626-vault` |
> | Renzo | Restaking | 2.68% | ETH | `base-renzo-ezeth-staking` |
> | Morpho | Vault | 2.31% | WETH | `base-weth-exmweth-0x5a32...-4626-vault` |
>
> **My recommendation:** The **Morpho 9Summits Core vault** at 7.06% APY is the highest. It's a curated Morpho vault — higher APY but involves smart contract risk across multiple lending markets.
>
> For lower risk, **KelpDAO Restaking** at 2.95% earns you restaking rewards on top of ETH staking yield. **Renzo** is similar at 2.68%.
>
> Which option interests you?

---

### Conversation 7: Portfolio Rebalance — Compound to Morpho

**User:** "Move my USDC from Compound to wherever the APY is higher"

**Agent thinks:** I'll check their Compound position, find better yields, then execute the move.

**Agent runs:**
```bash
# Step 1: Check current position
./scripts/check-portfolio.sh base-usdc-compound-v3-lending 0x742d35Cc6634C0532925a3b844Bc454e4438f44e

# Step 2: Find better yields
./scripts/find-yields.sh base USDC
```

**Agent responds:**

> Your **Compound v3** position: **200 USDC** earning **3.19% APY**.
>
> I found better options on Base:
>
> | Protocol | APY | Improvement |
> |----------|-----|-------------|
> | Morpho Flagship | 5.72% | +2.53% |
> | Morpho (MEV Capital) | 4.91% | +1.72% |
> | Aave v3 | 3.82% | +0.63% |
>
> **Rebalance plan** (moving to Morpho Flagship at 5.72%):
> 1. Withdraw 200 USDC from Compound v3 (gas: ~$0.05)
> 2. Deposit 200 USDC into Morpho Flagship vault (gas: ~$0.08)
> 3. Total gas cost: ~$0.13
>
> This would increase your annual earnings from **$6.38 to $11.44** (+$5.06/year).
>
> The extra yield covers the gas cost **immediately**. Want me to proceed?

**User:** "Yes, do it"

**Agent runs:**
```bash
# Exit Compound
./scripts/exit-position.sh base-usdc-compound-v3-lending 0x742d35Cc6634C0532925a3b844Bc454e4438f44e '{"amount":"200"}'
# Sign + submit + confirm

# Enter Morpho Flagship
./scripts/enter-position.sh base-usdc-cousdc-0x1d3b1cd0a0f242d598834b3f2d126dc6bd774657-4626-vault 0x742d35Cc6634C0532925a3b844Bc454e4438f44e '{"amount":"200"}'
# Sign + submit + confirm
```

**Agent responds:**

> Done! Your USDC has been moved:
>
> - Withdrew **200 USDC** from Compound v3
> - Deposited **200 USDC** into Morpho Flagship vault
> - Total gas used: **$0.11**
>
> You're now earning **5.72% APY** instead of 3.19%. Your new position is active and earning.

---

### Conversation 8: Staking with Validator Selection

**User:** "I want to stake my ATOM on Cosmos"

**Agent thinks:** Cosmos staking requires validator selection. I'll find yields first, then fetch available validators.

**Agent runs:**
```bash
# Step 1: Find the staking yield
./scripts/find-yields.sh cosmos ATOM

# Step 2: Inspect the yield schema to see if validators are needed
./scripts/get-yield-info.sh cosmos-atom-native-staking

# Step 3: Fetch available validators
./scripts/list-validators.sh cosmos-atom-native-staking
```

**Agent responds:**

> I found **ATOM staking on Cosmos** with an APY of approximately **15-20%** depending on the validator.
>
> This type of staking **requires you to choose a validator**. I fetched the top validators for you:
>
> | Validator | Commission | Status |
> |-----------|------------|--------|
> | Chorus One | 7.5% | Active |
> | Figment | 9.0% | Active |
> | Everstake | 5.0% | Active |
>
> Lower commission means more rewards for you. How much ATOM would you like to stake, and which validator do you prefer?

**User:** "Stake 100 ATOM with Everstake"

**Agent runs:**
```bash
./scripts/enter-position.sh cosmos-atom-native-staking 0x742d... '{"amount":"100","validatorAddress":"cosmos1everstakevalidatoraddress"}'
```

**Agent responds:**

> Staking transaction prepared for **100 ATOM** with Everstake (5% commission).
>
> **Expected earnings:** ~15-20 ATOM per year at current rates.
>
> Note: Unstaking ATOM has a **21-day cooldown period**. During this time, your tokens won't earn rewards and can't be transferred.
>
> Ready to sign?

---

### Conversation 9: Swap-Then-Yield

**User:** "I have ETH but I want to earn yield on USDC. Can you handle the swap and deposit?"

**Agent thinks:** I'll swap ETH to USDC via the wallet skill, then enter a high-yield vault position.

**Agent responds:**

> Sure! Here's what I'll do:
>
> 1. Swap your ETH to USDC on Base via wallet skill
> 2. Deposit the USDC into the highest-yielding vault (Morpho Flagship at 5.72%)
>
> How much ETH would you like to convert?

**User:** "0.5 ETH"

**Agent runs:**
```bash
# Step 1: Swap ETH to USDC via wallet skill
# Result: ~1,300 USDC received

# Step 2: Find best yield
./scripts/find-yields.sh base USDC

# Step 3: Enter Morpho Flagship vault
./scripts/enter-position.sh base-usdc-cousdc-0x1d3b1cd0a0f242d598834b3f2d126dc6bd774657-4626-vault 0xWallet '{"amount":"1300"}'
# Sign via wallet skill
```

**Agent responds:**

> All done! Here's what happened:
>
> 1. Swapped **0.5 ETH** to **1,300 USDC** on Base
> 2. Deposited **1,300 USDC** into Morpho Flagship vault at **5.72% APY**
> 3. Estimated annual earnings: **$74.36**
>
> Your USDC is now earning yield automatically. You can check your position or withdraw anytime.

---

### Conversation 10: Safety Guardrails in Action

**User:** "Deposit all my USDC into the highest APY vault"

**Agent thinks:** Safety checks: I should verify the amount, check the protocol, and warn about concentration risk.

**Agent runs:**
```bash
./scripts/check-portfolio.sh base-usdc-aave-v3-lending 0xWallet
./scripts/find-yields.sh base USDC
```

**Agent responds:**

> Before I proceed, a few safety notes:
>
> Your wallet has **5,000 USDC**. The highest APY vault I found on Base is the **Morpho Flagship** at **5.72% APY**. Here are some things to consider:
>
> 1. **Concentration risk** — Putting all funds in one vault is risky. Consider splitting across 2-3 protocols.
> 2. **APY volatility** — Vault APYs fluctuate as capital flows in and out.
> 3. **Smart contract risk** — Morpho vaults interact with multiple lending markets, adding layers of smart contract risk.
>
> **My suggestion — split across two trusted protocols:**
> - 3,000 USDC into Morpho Flagship (5.72% APY, curated vault)
> - 2,000 USDC into Aave v3 (3.82% APY, battle-tested lending)
>
> **Blended APY: ~4.96%** | Estimated annual earnings: **~$248**
>
> This gives you diversification across a curated vault and an established lending protocol. What would you prefer?

---

## API Reference Examples

### Discovery with Pagination

```bash
# First page
./scripts/find-yields.sh base USDC 20 0

# Second page
./scripts/find-yields.sh base USDC 20 20

# All yields on a network (no token filter)
./scripts/find-yields.sh ethereum "" 50
```

### Common Yield IDs

| Yield ID | Network | Token | Protocol | Type |
|----------|---------|-------|----------|------|
| `base-usdc-cousdc-0x1d3b1...-4626-vault` | Base | USDC | Morpho (Flagship) | Vault |
| `base-weth-9sethcore-0x5496b...-4626-vault` | Base | WETH | Morpho (9Summits) | Vault |
| `base-usdc-aave-v3-lending` | Base | USDC | Aave V3 | Lending |
| `base-usdc-compound-v3-lending` | Base | USDC | Compound V3 | Lending |
| `base-kelpdao-rseth-staking` | Base | ETH | KelpDAO | Restaking |
| `base-renzo-ezeth-staking` | Base | ETH | Renzo | Restaking |
| `ethereum-eth-lido-staking` | Ethereum | ETH | Lido | Staking |
| `cosmos-atom-native-staking` | Cosmos | ATOM | Native | Staking |

> Morpho and Euler vault IDs include contract addresses (e.g., `base-usdc-mevfusdc-0x8773...-4626-vault`). Use `find-yields.sh` to discover current IDs.

### Amount Formatting

Amounts are human-readable strings — use the value as the user would say it:

```
"100"   →  100 tokens
"0.5"   →  0.5 tokens
"1"     →  1 token
```

The API handles decimal conversion internally. No need to know token decimals.

### Environment Variable Overrides

Override skill.json values without editing the file:

```bash
export YIELDS_API_KEY="your-custom-key"
export YIELDS_API_URL="https://api.stakek.it"
export YIELD_NETWORK="ethereum"

./scripts/find-yields.sh    # Uses env vars instead of skill.json
```

---

## Testing Guide

### Quick Smoke Test

Run this immediately after unzipping to verify everything works:

```bash
cd yield-agent
chmod +x scripts/*.sh

# Test 1: Discovery (should return JSON with yields)
echo "=== Test 1: Discovery ==="
./scripts/find-yields.sh base USDC 2

# Test 2: Balance check (should return JSON with balances)
echo "=== Test 2: Balance Check ==="
./scripts/check-portfolio.sh base-usdc-aave-v3-lending 0x0000000000000000000000000000000000000001

# Test 3: Build transaction (should return Action with transactions)
echo "=== Test 3: Build Transaction ==="
./scripts/enter-position.sh base-usdc-aave-v3-lending 0x0000000000000000000000000000000000000001 '{"amount":"1"}'

# Test 4: Exit position (should return Action with transactions)
echo "=== Test 4: Exit Position ==="
./scripts/exit-position.sh base-usdc-aave-v3-lending 0x0000000000000000000000000000000000000001 '{"amount":"0.5"}'

# Test 5: Input validation (should show error)
echo "=== Test 5: Input Validation ==="
./scripts/enter-position.sh base-usdc-aave-v3-lending 0x0000000000000000000000000000000000000001 "not-json"
```

### Validation Checklist

| Test | Command | Expected |
|------|---------|----------|
| API works | `./scripts/find-yields.sh base` | JSON with `items` array |
| Token filter | `./scripts/find-yields.sh base USDC` | Only USDC yields |
| Balance check | `./scripts/check-portfolio.sh <id> <addr>` | JSON with `balances` |
| Enter | `./scripts/enter-position.sh <id> <addr> '{"amount":"100"}'` | Action with `transactions` |
| Bad JSON | `./scripts/enter-position.sh <id> <addr> "not-json"` | Error: must be valid JSON |
| No args | `./scripts/find-yields.sh` | Usage message |
| Bad API key | `YIELDS_API_KEY=bad ./scripts/find-yields.sh base` | 401 error |

### Error Handling

```bash
# Invalid API key
YIELDS_API_KEY="invalid" ./scripts/find-yields.sh base USDC
# Expected: 401 Unauthorized

# Invalid yield ID
./scripts/enter-position.sh "nonexistent-yield" "0x..." '{"amount":"100"}'
# Expected: 404 or error message

# Malformed JSON
./scripts/enter-position.sh "base-usdc-aave-v3-lending" "0x..." "not-json"
# Expected: "Error: arguments_json must be valid JSON"
```

---

## Transaction Signing Flow

After building a transaction, for each transaction in `stepIndex` order:

1. **Pass** `unsignedTransaction` to the wallet skill for signing and broadcasting — do NOT modify any field (WILL RESULT IN PERMANENT LOSS OF FUNDS). Format varies by chain — see SKILL.md.
2. **Submit hash**: `PUT /v1/transactions/{txId}/submit-hash` with `{ "hash": "0x..." }`
3. **Poll** `GET /v1/transactions/{txId}` until status is `CONFIRMED` or `FAILED`
4. **Proceed** to the next transaction

Signing, gas management, and nonce handling are the wallet skill's responsibility.

---

## Implementation Checklist

- [ ] API key in skill.json (included by default)
- [ ] Scripts executable (`chmod +x scripts/*.sh`)
- [ ] `jq` and `curl` installed
- [ ] Wallet skill configured for signing
- [ ] Always fetch yield schema before calling actions
- [ ] Amounts are human-readable strings
- [ ] Transactions executed in `stepIndex` order, waiting for CONFIRMED between each
