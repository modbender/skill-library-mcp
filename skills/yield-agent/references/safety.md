# YieldAgent Safety System

*Transaction guardrails, approval workflows, and risk controls for on-chain yield operations.*

> **Critical: The agent must NEVER bypass safety checks.**

---

## Quick Reference

| Risk Level | Actions | Default Behavior |
|------------|---------|------------------|
| **Safe** | Discovery, balance checks, rate lookups | Auto-execute |
| **Review** | Enter position, exit position, claim rewards | Show details, ask confirmation |
| **Caution** | Large amounts, new protocols | Require explicit approval |

---

## Pre-Execution Checks

Every write operation (enter, exit, manage) must follow these checks in order.

### 1. Read the Yield Schema

Before calling any action, fetch the yield via `GET /v1/yields/{yieldId}` and read `mechanics.arguments`. The API is self-documenting — never guess what arguments are needed.

```bash
./scripts/get-yield-info.sh <yieldId> | jq '.mechanics.arguments.enter'
```

### 2. Balance Verification

Does the user have the token balance they're trying to deposit?

```bash
./scripts/check-portfolio.sh <yieldId> <address>
# If balance < amount, abort and inform the user
```

### 3. Yield Status Check

Is the yield active, or is it deprecated/under maintenance?

```bash
./scripts/get-yield-info.sh <yieldId> | jq '{
  canEnter: .status.enter,
  canExit: .status.exit,
  deprecated: .metadata.deprecated,
  maintenance: .metadata.underMaintenance
}'
```

Block if `deprecated: true` or `underMaintenance: true`.

### 4. Network Validation

The yield ID encodes its network (e.g., `base-usdc-aave-v3-lending` = Base). Ensure the wallet supports the correct network before submitting transactions.

### 5. Amount Format

Amounts are human-readable strings. The API handles decimal conversion internally.

```bash
# CORRECT:
"100"     # 100 USDC
"1"       # 1 ETH
"0.5"     # 0.5 SOL

# INCORRECT:
"1e18"           # Scientific notation
"100,000"        # Commas
100              # Number (must be string)
```

### 6. Transaction Execution Order

If an action produces multiple transactions (e.g., APPROVAL + STAKE):
- Execute in exact `stepIndex` order
- Wait for `CONFIRMED` before proceeding to next
- Never skip or reorder

After signing and broadcasting every transaction:

```bash
# Submit the hash — balances won't update until you do
PUT /v1/transactions/{txId}/submit-hash { "hash": "0x..." }
```

---

## Safety Rules

1. **NEVER modify `unsignedTransaction`.** Sign exactly what the API returns. Modifying any field (including `to`, `value`, `data`, `gas`, `nonce`) WILL RESULT IN PERMANENT LOSS OF FUNDS. If anything needs to change, request a new action from the API.
2. **Wallet Handoff.** Pass `unsignedTransaction` to the wallet skill exactly as received — do not modify, reformat, or "fix" any field.
3. **User Confirmation.** Present transaction details and get user approval before signing.
4. **Rate Limits.** Respect the `retry-after` header on 429 responses.
5. **Key Security.** API keys should be in skill.json or YIELDS_API_KEY env var, not in code.
6. **Sequential Processing.** Never submit multiple transactions simultaneously.
7. **Passthrough Integrity.** Never modify the `passthrough` string from `pendingActions[]`.

---

## User-Configurable Guardrails

Store in `~/.openclaw/skills/yield-agent/state/yield-safety.json`:

```json
{
  "version": 1,

  "limits": {
    "maxSingleTxUsd": 1000,
    "maxDailyTotalUsd": 5000,
    "requireApprovalAboveUsd": 500
  },

  "protocols": {
    "mode": "allowlist",
    "allowlist": ["aave", "lido", "morpho", "compound", "yearn", "pendle"],
    "blocklist": []
  },

  "networks": {
    "allowed": ["base", "ethereum", "arbitrum", "optimism", "polygon"],
    "blocked": []
  },

  "risk": {
    "minTvlUsd": 10000000,
    "warnTvlUsd": 50000000,
    "maxReasonableApy": 0.50,
    "warnApyAbove": 0.20,
    "blockDeprecated": true,
    "blockMaintenance": true
  },

  "tracking": {
    "dailySpentUsd": {},
    "lastReset": null
  }
}
```

### Limits

| Field | Description | Default |
|-------|-------------|---------|
| maxSingleTxUsd | Max USD value for a single transaction | 1000 |
| maxDailyTotalUsd | Max USD across all transactions per day | 5000 |
| requireApprovalAboveUsd | Require explicit confirmation above this | 500 |

Agent behavior:
- Under `requireApprovalAboveUsd` → confirm once, execute
- Over `requireApprovalAboveUsd` → show full breakdown, require explicit "yes"
- Over `maxSingleTxUsd` → refuse, suggest splitting
- Over `maxDailyTotalUsd` → refuse until next day

### Protocol Allowlist

| Mode | Behavior |
|------|----------|
| allowlist | Only listed protocols allowed |
| blocklist | Listed protocols blocked, others allowed |
| open | All protocols allowed |

Extract provider from yield response:

```bash
./scripts/get-yield-info.sh <yieldId> | jq '.providerId'
```

### Risk Thresholds

| Check | Action |
|-------|--------|
| TVL below `minTvlUsd` | Block transaction |
| TVL below `warnTvlUsd` | Warn but allow |
| APY above `warnApyAbove` | Warn: "High yield often means high risk" |
| APY above `maxReasonableApy` | Block: "APY unusually high" |

---

## Cross-Skill Safety

When combining yield-agent with wallet skills:

1. **Address match.** Ensure the address passed to yield-agent matches the wallet's address.
2. **Chain alignment.** Verify the yield's network is supported by the wallet.
3. **Sequential operations.** When chaining workflows (e.g., swap then deposit), wait for each step's confirmation.
4. **Single signer.** Each unsigned transaction should be signed by exactly one wallet.

---

## Golden Rule

> Build transactions. Pass them unmodified to the wallet skill for signing.
