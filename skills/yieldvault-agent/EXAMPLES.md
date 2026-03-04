# Yield Farming Agent - Decision Examples

This document shows real-world decision scenarios and the corresponding agent outputs.

## Scenario 1: HARVEST Decision

**Situation:** High pending rewards in BNB-BUSD vault

```javascript
const allocation = {
  vault_bnb_lp_001: {
    shares: "1000",
    amount_usd: "50000",
    pending_rewards_usd: "1500"  // >= 25 USD threshold
  },
  vault_usdc_stable_001: {
    shares: "2000",
    amount_usd: "30000",
    pending_rewards_usd: "15"
  }
};
```

**Engine Decision:**
- Best vault: `vault_bnb_lp_001` (NET_APR: 37.5%)
- Pending rewards: $1500 >= $25 threshold
- **Action: HARVEST** $1500 of CAKE rewards

```json
{
  "action": "HARVEST",
  "vault_id": "vault_bnb_lp_001",
  "token": "CAKE",
  "amount": "1500.00"
}
```

**Rationale:** Claim accumulated rewards; rewards are valuable enough to pay gas fees.

---

## Scenario 2: COMPOUND Decision

**Situation:** Moderate APR vault with no pending rewards

```javascript
const allocation = {
  vault_cake_farm_001: {
    shares: "500",
    amount_usd: "100000",
    pending_rewards_usd: "5"  // < 25 USD, skip harvest
  }
};
```

**Engine Decision:**
- Best vault: `vault_cake_farm_001` (NET_APR: 50.5%)
- No harvest trigger (only $5 pending)
- NET_APR (50.5%) >= compound threshold (2%)
- **Action: COMPOUND** $5050 back into vault

```json
{
  "action": "COMPOUND",
  "vault_id": "vault_cake_farm_001",
  "token": "CAKE",
  "amount": "5050.00"
}
```

**Rationale:** High APR environment; reinvesting gains amplifies compounding effects (Einstein's "8th wonder").

---

## Scenario 3: REBALANCE Decision

**Situation:** Better APR opportunity exists in another vault

```javascript
const allocation = {
  vault_bnb_lp_001: {
    shares: "1000",
    amount_usd: "50000",
    pending_rewards_usd: "20"  // No harvest
  },
  vault_eth_staking_001: {
    shares: "500",
    amount_usd: "40000",
    pending_rewards_usd: "30"  // No harvest
  },
  vault_link_oracle_001: {
    shares: "0",
    amount_usd: "0",
    pending_rewards_usd: "0"
  }
};
```

**Vault Rankings (NET_APR):**
1. LINK Oracle (35.0%) - Unallocated
2. BNB-BUSD LP (37.5%) - $50k allocated
3. ETH Staking (5.0%) - $40k allocated

**Engine Decision:**
- Best vault: `vault_link_oracle_001` (NET_APR: 35.0%)
- Best allocation has 0 capital (unallocated opportunity)
- APR delta vs current: 35% - 5% = +30% > 2% threshold
- **Action: REBALANCE** $20k from ETH → LINK

```json
{
  "action": "REBALANCE",
  "from_vault_id": "vault_eth_staking_001",
  "to_vault_id": "vault_link_oracle_001",
  "token": "WETH",
  "amount": "20000.00"
}
```

**Rationale:** Move capital from low-yield (5% NET) to high-yield (35% NET) opportunity.

---

## Scenario 4: NOOP Decision (All Optimized)

**Situation:** Portfolio is already well-balanced

```javascript
const allocation = {
  vault_bnb_lp_001: {
    shares: "1000",
    amount_usd: "50000",
    pending_rewards_usd: "10"
  },
  vault_link_oracle_001: {
    shares: "800",
    amount_usd: "48000",
    pending_rewards_usd: "8"
  },
  vault_cake_farm_001: {
    shares: "600",
    amount_usd: "30000",
    pending_rewards_usd: "5"
  }
};
```

**Vault Rankings:**
1. CAKE (50.5% NET)
2. BNB-BUSD (37.5% NET)
3. LINK (35.0% NET)

**Engine Decision:**
- Best vault: `vault_cake_farm_001` (NET_APR: 50.5%)
- Current allocation: $30k (20% of portfolio)
- Rewards $5 < threshold ($25)
- No higher-APR vault available to rebalance to
- **Action: NOOP** (All optimized)

```json
{
  "action": "NOOP",
  "vault_id": "vault_cake_farm_001",
  "reason": "all_optimized"
}
```

**Rationale:** Portfolio is balanced across quality vaults; no actionable improvement exists.

---

## Scenario 5: NOOP Decision (Risk Filter)

**Situation:** Best APR vault exceeds risk threshold

```javascript
const allocation = {
  vault_high_risk_001: {
    shares: "100",
    amount_usd": "10000",
    pending_rewards_usd": "500"
  }
};
```

**Vault with Best Raw APR:**
- `vault_high_risk_001`: 250% APR, 20% fees, **risk_score: 0.80** ❌ Filtered out

**Eligible Vaults (risk_score ≤ 0.5):**
- Best: `vault_cake_farm_001` (50.5% NET)

**Engine Decision:**
- High-risk vault is **excluded** from consideration
- Falls back to safe alternatives
- **Action: NOOP** (no action on excluded vault)

```json
{
  "action": "NOOP",
  "vault_id": "vault_cake_farm_001",
  "reason": "best_eligible_vault_already_allocated"
}
```

**Rationale:** Risk management > yield maximization. High APR doesn't justify extreme risk.

---

## Scenario 6: MAX_ALLOCATION Constraint

**Situation:** Best vault is near allocation limit

```javascript
const allocation = {
  vault_cake_farm_001: {
    shares: "3500",
    amount_usd": "175000",  // 70% of $250k portfolio
    pending_rewards_usd": "0"
  }
};
```

**Rebalance Opportunity:** LINK (35% APR) vs CAKE (50.5% APR)
- LINK has 0 allocation
- APR delta: 15.5% > 2% threshold ✓
- But moving to LINK would violate max_allocation (35%) at destination

**Engine Decision:**
- Rebalance blocked by constraint
- **Action: NOOP** (constraint prevents action)

```json
{
  "action": "NOOP",
  "vault_id": "vault_cake_farm_001",
  "reason": "destination_allocation_limit_exceeded"
}
```

**Rationale:** Safety first. Max 35% per vault prevents concentration risk.

---

## Scenario 7: Multi-Cycle Evolution

**Cycle 1:** Initial state, scattered allocation

```json
{
  "action": "REBALANCE",
  "from_vault_id": "vault_eth_staking_001",
  "to_vault_id": "vault_cake_farm_001",
  "amount": "30000"
}
```

**After Cycle 1 execution:** CAKE vault now has $60k

**Cycle 2:** Harvest trigger hit

```json
{
  "action": "HARVEST",
  "vault_id": "vault_cake_farm_001",
  "token": "CAKE",
  "amount": "3030"
}
```

**After Cycle 2 execution:** Claimed rewards

**Cycle 3:** High APR environment, reinvest

```json
{
  "action": "COMPOUND",
  "vault_id": "vault_cake_farm_001",
  "token": "CAKE",
  "amount": "3030"
}
```

**Portfolio Evolution:**
- Started: $50k CAKE, $40k ETH, $30k USDC
- Cycle 1: Consolidated to best vault
- Cycle 2: Harvested compounding gains
- Cycle 3: Reinvested for exponential growth

---

## Net APR Calculation Examples

### Example 1: Low-risk, high-fee vault

```
vault_usdc_stable_001:
  apr: 12%
  fees: 3%
  risk_score: 0.05
  risk_penalty: 0.05 × 10% = 0.5%
  net_apr: 12% - 3% - 0.5% = 8.5%
```

### Example 2: High-risk, no-fee vault

```
vault_high_risk_001:
  apr: 250%
  fees: 0%
  risk_score: 0.80
  risk_penalty: 0.80 × 10% = 8%
  net_apr: 250% - 0% - 8% = 242%
  
  BUT: risk_score > 0.5 → FILTERED OUT ❌
```

### Example 3: Balanced vault (selected most often)

```
vault_cake_farm_001:
  apr: 65%
  fees: 10%
  risk_score: 0.45
  risk_penalty: 0.45 × 10% = 4.5%
  net_apr: 65% - 10% - 4.5% = 50.5%  ✓ BEST
```

---

## Key Takeaways

1. **Harvest** when rewards accumulate (>= $25)
2. **Compound** in high-APR environments (APR >= 2%)
3. **Rebalance** to capture APR gaps (>= 2% delta)
4. **Risk first**: Filter out vaults with risk_score > 0.5
5. **Concentration safety**: Never exceed 35% in one vault
6. **NOOP when optimal**: Portfolio already balanced = do nothing

The agent makes **one deterministic decision per cycle**, with clear rationale and audit trail.
