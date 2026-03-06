# Migration Guide

This file documents all breaking changes and required migration steps between versions. When the user says **"update to latest"**, the agent must:

1. Run `git fetch --tags origin` in the clawlett repo
2. Compare the current version (`version` in `scripts/package.json`) against the latest git tag
3. Look up the migration path in this file (current version → latest version)
4. Show the user a summary of what changed and what steps are required (code-only vs on-chain)
5. **Ask the user explicitly: "Do you want to proceed with this update?"**
6. Only if the user confirms: run `git checkout <latest-tag>` and execute the migration steps

If the migration requires on-chain transactions (e.g., updating Roles permissions), the agent must clearly explain this and confirm the user understands before proceeding.

---

## v0.1.0 → v0.2.0

**Summary:** CoW Protocol added as default swap mechanism (MEV-protected). Aerodrome preserved as alternative.

### What changed

| Change | Type |
|--------|------|
| New `swap.js` — CoW Protocol presign flow | Code |
| Old `swap.js` renamed to `swap-aerodrome.js` | Code |
| ZodiacHelpers contract updated to `0xb34a6210013977FC7D6082287e03915a66249799` | Code + On-chain |
| `package.json` — added `swap-aerodrome` script entry | Code |
| `SKILL.md` — documents CoW as default, Aerodrome as alternative | Code |

### ZodiacHelpers address change

| | Address |
|---|---------|
| Old | `0xc235D2475E4424F277B53D19724E2453a8686C54` |
| New | `0xb34a6210013977FC7D6082287e03915a66249799` |

The new contract adds `cowPreSign()` and `approveForCow()` while retaining all existing functions (`approveForRouter`, `executeSwap`).

### Migration steps

#### Step 1: Update code (automatic)

```bash
cd <clawlett-repo>
git fetch --tags origin
git checkout v0.2.0
```

#### Step 2: Update on-chain Roles permissions (required for existing Safes)

The Safe **owner** must submit a transaction to allow the new ZodiacHelpers address in the Roles modifier. This requires the owner's wallet — the agent cannot do this autonomously.

Use the [Safe Transaction Builder](https://app.safe.global) to batch these calls to the **Roles Modifier** (`roles` address from `config/wallet.json`):

```
1. scopeTarget(roleKey, 0xb34a6210013977FC7D6082287e03915a66249799)
2. allowTarget(roleKey, 0xb34a6210013977FC7D6082287e03915a66249799, 3)
3. revokeTarget(roleKey, 0xc235D2475E4424F277B53D19724E2453a8686C54)
```

Where:
- `roleKey` = the `WalletSwapper` role key from `config/wallet.json`
- `3` = ExecutionOptions.Both (Send + DelegateCall)
- Step 3 (revokeTarget) is optional but recommended to clean up the old address

The Roles Modifier ABI for these functions:
```
function scopeTarget(bytes32 roleKey, address targetAddress) external
function allowTarget(bytes32 roleKey, address targetAddress, uint8 options) external
function revokeTarget(bytes32 roleKey, address targetAddress) external
```

#### Step 3: Refresh config

Re-run initialize to update `config/wallet.json` with the new contracts:

```bash
node scripts/initialize.js --owner <OWNER_ADDRESS>
```

This is idempotent — it detects the existing Safe/Roles and refreshes the config file.

#### Step 4: Verify

```bash
# Test CoW quote (no execution)
node scripts/cow.js --from USDC --to WETH --amount 10

# Test Aerodrome still works (no execution)
node scripts/swap-aerodrome.js --from ETH --to USDC --amount 0.1
```

### New deployments

No migration needed. Run `initialize.js` which uses the new ZodiacHelpers address automatically.

---

## v0.2.0 → v0.3.0

**Summary:** KyberSwap Aggregator added as **default** swap mechanism. CoW Protocol remains available.

### What changed

| Change | Type |
|--------|------|
| `swap.js` renamed to `cow.js` | Code |
| New `swap.js` — KyberSwap aggregator (now default) | Code |
| ZodiacHelpers contract updated (adds `kyberSwap` function) | Code + On-chain |
| `SKILL.md` — documents KyberSwap as default | Code |
| `initialize.js` — adds KyberSwapRouter address | Code |

### ZodiacHelpers address change

| | Address |
|---|---------|
| Old | `0xb34a6210013977FC7D6082287e03915a66249799` |
| New | `0x49E596467D5e3C876Eece999d88a2135596bde18` |

The new contract adds `kyberSwap()` for executing swaps via KyberSwap Meta Aggregation Router V2 while retaining all existing functions (`cowPreSign`, `wrapETH`, `unwrapWETH`, `createViaFactory`, `tradeViaFactory`).

### New features

**KyberSwap Aggregator:**
- Finds optimal routes across multiple DEXs on Base
- Native ETH supported directly (no wrapping needed)
- 0.1% partner fee (10 bps)
- Slippage protection via minAmountOut validation

### Migration steps

#### Step 1: Update code

```bash
cd <clawlett-repo>
git fetch --tags origin
git checkout v0.3.0
```

#### Step 2: Update on-chain Roles permissions (required for existing Safes)

The Safe **owner** must submit a transaction to allow the new ZodiacHelpers address in the Roles modifier. This requires the owner's wallet — the agent cannot do this autonomously.

Use the [Safe Transaction Builder](https://app.safe.global) to batch these calls to the **Roles Modifier** (`roles` address from `config/wallet.json`):

```
1. scopeTarget(roleKey, 0x49E596467D5e3C876Eece999d88a2135596bde18)
2. allowTarget(roleKey, 0x49E596467D5e3C876Eece999d88a2135596bde18, 3)
3. revokeTarget(roleKey, 0xb34a6210013977FC7D6082287e03915a66249799)
```

Where:
- `roleKey` = the `WalletSwapper` role key from `config/wallet.json`
- `3` = ExecutionOptions.Both (Send + DelegateCall)
- Step 3 (revokeTarget) is optional but recommended to clean up the old address

#### Step 3: Refresh config

Re-run initialize to update `config/wallet.json` with the new contracts:

```bash
node scripts/initialize.js --owner <OWNER_ADDRESS>
```

This is idempotent — it detects the existing Safe/Roles and refreshes the config file.

#### Step 4: Verify

```bash
# Test KyberSwap quote (now default swap.js)
node scripts/swap.js --from ETH --to USDC --amount 0.1

# Test CoW still works (now cow.js)
node scripts/cow.js --from USDC --to WETH --amount 10
```

### New deployments

No migration needed. Run `initialize.js` which uses the new ZodiacHelpers address automatically.

### When to use KyberSwap vs CoW

| Use Case | Recommended |
|----------|-------------|
| Large swaps (MEV concern) | CoW Protocol |
| Best price discovery | KyberSwap |
| Native ETH swaps | KyberSwap |
| Partial fills acceptable | CoW Protocol |
| Immediate execution needed | KyberSwap |
