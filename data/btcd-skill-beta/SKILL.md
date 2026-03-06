---
name: btcd-skill-beta
description: Run the BTCD collateralization flow on PGP chain. Use when the user asks to run a BTCD loan, collateralization flow, create/take orders, lock BTC, submit proofs, claim BTCD tokens, or repay loans on the PGP network.
---

# BTCD PGP Collateralization Flow

This skill contains a **complete, self-contained** Node.js project to run the full BTCD collateralization lifecycle on the PGP (Elastos) chain.

## Bundled Code Location

All runnable code is inside the `scripts/` directory relative to this SKILL.md:

```
scripts/
├── package.json
├── .env.template.txt
├── setup.js
├── 00-create-order.js
├── 01-take-order.js
├── 02-lock-btc-collateral.js
├── 03-submit-btc-proof.js
├── 05-claim-btcd-tokens.js
├── 06-repay-loan.js
├── abi/                    # Contract ABIs (LoanContract, Order, Issuer, ERC20, ArbitratorManager)
├── utils/                  # Shared utilities (config, wallet, EVM/BTC clients, logger, state, proof, arbiter)
└── state/                  # Flow state persists here
```

## Setup Instructions

1. **Copy the entire `scripts/` directory** to a working directory:
   ```bash
   cp -r <path-to-this-skill>/scripts/ /tmp/btcd-flow/
   cd /tmp/btcd-flow/
   ```

2. **Create `.env`** from the template. Only two values need changing:
   ```bash
   cp .env.template.txt .env
   ```
   Edit `.env` and set:
   - `EVM_PRIVATE_KEY` — your EVM private key (with `0x` prefix)
   - `BTC_PRIVATE_KEY` — your BTC private key (hex, **no** `0x` prefix)

   Optionally adjust `LENDING_AMOUNT` (minimum 10) and `LENDING_DAYS` (only 90 or 180).

   All other values (contract addresses, RPC URLs, subgraph URLs) are **fixed for PGP chain** and must not be changed.

3. **Install dependencies:**
   ```bash
   npm install
   ```

4. **Ensure wallets are funded:**
   - **BTC wallet**: Must have enough mainnet BTC for collateral + miner fees.
   - **EVM wallet**: Must have PGA tokens for gas fees on PGP chain. To get PGA tokens, go to **https://swap.pgpgas.org** — you need USDT on BSC chain, bridge it to PGP, then swap for PGA tokens and/or BTCD.

## CRITICAL: Check State Before Running

**Before running any step**, always read `state/flow-state.json` to understand what has already been completed. This prevents catastrophic errors like double-locking BTC collateral.

- If the `steps` object already has a completed entry for the step you're about to run, **do not re-run it**.
- If step `02-lock-btc-collateral` has a `btcTxId` but no `confirmations` (or `confirmations < 3`), the BTC was already broadcast — re-running will **resume confirmation waiting**, not send a new transaction.
- If `02-lock-btc-collateral` shows `confirmations >= 3`, it is fully done — proceed to step 03.

Example of a partially completed state (safe to resume step 02, do NOT re-run steps 00 or 01):
```json
{
  "steps": {
    "00-create-order": { "orderId": "0x...", "completedAt": "..." },
    "01-take-order": { "orderId": "0x...", "preImage": "...", "completedAt": "..." },
    "02-lock-btc-collateral": { "btcTxId": "abc...", "confirmations": 0 }
  }
}
```

## Execution Steps

Run each step **sequentially** from the scripts directory. Each step has interactive confirmation prompts (press `y` + Enter).

```
Flow Progress:
- [ ] Step 0: Setup
- [ ] Step 1: Create Order
- [ ] Step 2: Take Order
- [ ] Step 3: Lock BTC Collateral
- [ ] Step 4: Submit BTC Proof
- [ ] Step 5: Claim BTCD Tokens  ← flow complete here
- [ ] Step 6: Repay Loan  ← ONLY when user explicitly requests
```

### Step 0: Setup
```bash
npm run setup
```
Validates config, initializes wallets, checks EVM balance, creates `state/flow-state.json`.

### Step 1: Create Order
```bash
npm run 00-create-order
```
Creates a lending order via the Issuer contract. Uses `LENDING_AMOUNT` and `LENDING_DAYS` from `.env`. Saves the **Order ID** to state.

### Step 2: Take Order
```bash
npm run 01-take-order
```
Takes the order from Step 1. Generates a preImage, selects the best arbiter from the subgraph, and calls `takeOrder()`. Pays the arbiter's fee in native PGA tokens.

### Step 3: Lock BTC Collateral
```bash
npm run 02-lock-btc
```
Sends BTC to the lock script address. **No interactive prompts** — the script is fully automated:
- Checks `state/flow-state.json` first. If a `btcTxId` already exists, it resumes confirmation waiting instead of sending new BTC.
- If already completed (`confirmations >= 3`), it skips entirely.
- Defaults to standard collateral amount (no staking discount).
- Broadcasts BTC tx and waits for **3 confirmations** (~30 min).

Safe to re-run if interrupted — it will never double-send BTC.

### Step 4: Submit BTC Proof
```bash
npm run 03-submit-proof
```
Generates ZKP proof from the BTC transaction and submits to the EVM order contract.

**Skip `04-arbiter-fee`** — not needed.

### Step 5: Claim BTCD Tokens
```bash
npm run 05-claim-btcd
```
Calls `borrow()` with the preImage from Step 2. BTCD tokens are minted to your EVM wallet.

### Step 6: Repay Loan (ONLY when explicitly requested by user)
```bash
npm run 06-repay
```
Calculates repayment (principal + interest), approves BTCD, signs the BTC repayment transaction, and calls `repay()`.

**DO NOT run this step automatically.** The flow is considered complete after Step 5 (Claim BTCD). Repaying the loan unlocks the BTC collateral and closes the position — only do this when the user explicitly asks to repay. Running it prematurely defeats the purpose of the collateralization.

**Skip `07-unlock`** — not needed.

## State Management

State persists in `state/flow-state.json`. Each step reads from prior steps and writes its results.

When Step 6 (Repay) completes, the state file is **automatically archived** to `state/flow-state-<timestamp>.json` and removed, so the next run starts fresh. Archived files serve as a historical record of completed flows.

| Step | Writes | Read By |
|------|--------|---------|
| 00-create-order | `orderId` | 01-take-order |
| 01-take-order | `orderId`, `preImage`, `btcAddress`, `btcPublicKey`, `arbiterAddress` | 02-lock-btc, 05-claim-btcd, 06-repay |
| 02-lock-btc | `btcTxId`, `scriptAddress`, `confirmations` | 03-submit-proof, 06-repay |
| 05-claim-btcd | `btcdReceived` | 06-repay |

## Troubleshooting

- **"Order status is X, expected Y"**: Steps must run in order. Check `state/flow-state.json`.
- **BTC confirmation timeout**: Re-run Step 3 — it detects the existing `btcTxId` and resumes waiting.
- **Insufficient PGA for gas**: Get PGA tokens from https://swap.pgpgas.org (USDT on BSC → bridge to PGP → swap for PGA).
- **Insufficient BTC**: Ensure BTC wallet has enough for collateral amount + miner fees.
- **Contract error on takeOrder**: Order may already be taken. Check order status on-chain.
- **Explorer**: PGP chain transactions can be viewed at `https://pgp.elastos.io/tx/<hash>`.

## PGP Chain Contract Addresses

| Contract | Address |
|----------|---------|
| Loan Contract | `0x5cD194C9d34e5B9b7A0E5cBC64C93c1c9277891e` |
| Issuer | `0x91cf47c5d2b44Da124d4B54E9207aE6FB63D5Fa7` |
| BTCD Token | `0xF9BF836FEd97a9c9Bfe4D4c28316b9400C59Cc6B` |

## Alternative RPC Endpoints

| URL | Notes |
|-----|-------|
| `https://api.elastos.io/pg` | Primary (default) |
| `https://api2.elastos.io/pg` | Backup |
| `https://pgp-node.elastos.io` | Alternative |
