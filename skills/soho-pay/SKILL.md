---
name: sohopay
description: "Initiate payments on the SOHO Pay credit layer using EIP-712 signatures."
invocation: manual
require_confirmation: true
---

# SOHO Pay — Credit Layer Payments

This skill orchestrates payments through the SOHO Pay `Creditor` smart contract using the `spendWithAuthorization` EIP-712 flow.

**This skill is manual-invocation only.** It must not be triggered autonomously by a model. Every invocation requires explicit user confirmation.

---

## Architecture — Three-Party Separation

```
┌──────────────────┐     ┌──────────────────┐     ┌──────────────────┐
│  Wallet Signer   │     │   SoHo (Credit)  │     │   Blockchain     │
│  (user/operator) │     │                  │     │   (Base)         │
│                  │     │  Credit checks   │     │                  │
│  Signs EIP-712   │────▶│  JIT funding     │────▶│  Settlement      │
│  Owns keys       │     │  Authorization   │     │  Creditor.sol    │
│                  │     │                  │     │                  │
│  MPC / HSM /     │     │  NEVER signs     │     │                  │
│  Turnkey / Privy │     │  NEVER holds keys│     │                  │
└──────────────────┘     └──────────────────┘     └──────────────────┘
```

**SoHo is a credit layer only.** It does not custody, hold, generate, or control any signing keys or key shards, and it does not produce EIP-712 signatures.

All EIP-712 signatures come from a separate **Wallet Signer** owned and controlled by the user or agent operator (e.g., MPC provider like Turnkey/Privy/Fireblocks, or a user wallet).

The skill orchestrates between:
- **Wallet Signer** — signing (user/operator-controlled)
- **SoHo** — credit checks + just-in-time funding (credit layer only)
- **Blockchain** — settlement

---

## Usage

```bash
node scripts/pay.js <amount> <merchantAddress> [payerAddress]
```

| Argument          | Description                                                        |
| ----------------- | ------------------------------------------------------------------ |
| `amount`          | Decimal USDC value (e.g. `10`, `0.5`)                             |
| `merchantAddress` | Explicit 0x-prefixed EVM address (checksummed). **Never a name.** |
| `payerAddress`    | Required when `SIGNER_PROVIDER=WALLET_SIGNER_REMOTE`              |

### Example — Base Sepolia with local key (dev only)

```bash
export RPC_URL=https://sepolia.base.org
export CHAIN_ID=84532
export SIGNER_PROVIDER=LOCAL_PRIVATE_KEY
export SOHO_DEV_PRIVATE_KEY=0xabc...

node scripts/pay.js 10 0x1234567890abcdef1234567890abcdef12345678
```

### Example — Base Sepolia with remote wallet signer (production pattern)

```bash
export RPC_URL=https://sepolia.base.org
export CHAIN_ID=84532
export SIGNER_PROVIDER=WALLET_SIGNER_REMOTE
export WALLET_SIGNER_SERVICE_URL=https://your-mpc-signer.example.com
export SIGNER_SERVICE_AUTH_TOKEN=sk_live_...

node scripts/pay.js 10 0xMERCHANT... 0xPAYER...
```

---

## Workflow

1. **Validate config** — all env vars checked with Zod at startup; unknown chains rejected.
2. **Parse inputs** — amount and explicit merchant address (no name-to-address generation).
3. **Pre-flight credit checks** — SoHo credit layer verifies borrower registration, active status, credit limit.
4. **Sign EIP-712** — Wallet Signer (user-controlled) produces signature. SoHo never signs.
5. **Submit tx** — call `spendWithAuthorization` on the Creditor contract.
6. **Return result** — transaction hash + block number.

---

## Supported Networks

| Network       | Chain ID | Status                                     |
| ------------- | -------- | ------------------------------------------ |
| Base Sepolia  | 84532    | Supported                                  |
| Base Mainnet  | 8453     | Requires `SOHO_MAINNET_CONFIRM=YES`        |

Unknown chain IDs are rejected at config validation time.

## Contract Addresses (Base Sepolia)

| Contract         | Address                                      |
| ---------------- | -------------------------------------------- |
| Creditor         | `0x1867a19816f38ec31ec3af1be15fd7104f161978` |
| Borrower Manager | `0x76e51158015e869ab2875fa17b87383d8886e93c` |
| USDC (test)      | `0x55b8ff660d4f0f176de84f325d39a773a7a3bda7` |

---

## Security Model

### Key Custody Boundary

| Entity         | Role                                 | Holds keys? |
| -------------- | ------------------------------------ | ----------- |
| **Wallet Signer** | Produces EIP-712 signatures       | **Yes** — user/operator-controlled |
| **SoHo**       | Credit authorization + JIT funding   | **No** — credit layer only |
| **This skill** | Orchestration between the above      | **No** — passes typed data to signer |

SoHo must NEVER custody, hold, generate, or control any signing keys or key shards.

### Wallet Signer Providers

| Provider                 | When to use                | Risk level |
| ------------------------ | -------------------------- | ---------- |
| `WALLET_SIGNER_REMOTE`  | **Production / Mainnet**   | Low — keys stay in user's MPC/HSM (Turnkey, Privy, Fireblocks, etc.) |
| `LOCAL_PRIVATE_KEY`      | **Dev / Testnet only**     | High — raw key in env |

- **Default and recommended**: `WALLET_SIGNER_REMOTE`. The skill sends EIP-712 typed data to the user's wallet signing service and never touches private keys.
- **Dev-only fallback**: `LOCAL_PRIVATE_KEY` is gated to testnet chain IDs. Using it on mainnet requires `DEV_ALLOW_LOCAL_KEY=YES` and is **strongly discouraged**.

### Mainnet Safety Gate

Transactions on Base Mainnet (`CHAIN_ID=8453`) are refused unless `SOHO_MAINNET_CONFIRM=YES` is set. This prevents accidental mainnet spends during development.

### Recipient Address Policy

The skill **never** derives or generates an address from a merchant name. The `merchantAddress` argument must be an explicit, valid, checksummed EVM address. Any non-address input is rejected with an error.

### Invocation Policy

- `invocation: manual` — the skill cannot be triggered autonomously.
- `require_confirmation: true` — the orchestrator must obtain user confirmation before execution.
- A runtime guard rejects execution if `SOHO_AUTONOMOUS=true` is detected in the environment.

---

## Threat Model & Mitigations

| Threat | Mitigation |
| ------ | ---------- |
| **Signer compromise** | Default to `WALLET_SIGNER_REMOTE` (MPC/HSM); keys never leave the user's signing service. Local key gated to testnet only. |
| **Replay attacks** | Random 32-byte nonce per transaction; `validAfter` / `expiry` window (10 min). On-chain nonce check in Creditor contract. |
| **Wrong merchant address** | Address generation from names removed. Only explicit checksummed EVM addresses accepted; checksum validated before signing. |
| **Accidental mainnet transaction** | `SOHO_MAINNET_CONFIRM=YES` safety gate required for chain ID 8453. |
| **Autonomous invocation with signing authority** | `invocation: manual` in metadata; `require_confirmation: true`; runtime guard blocks `SOHO_AUTONOMOUS=true`. |
| **SoHo used as signer** | Architecture enforces SoHo = credit-only. No signing key env vars reference SoHo as a signer. Skill never passes keys to SoHo API. |
| **Undeclared env var dependencies** | All env vars declared in `skill.json` with types and sensitivity flags. |
| **MITM on wallet signer service** | Use HTTPS for `WALLET_SIGNER_SERVICE_URL`; bearer token auth via `SIGNER_SERVICE_AUTH_TOKEN`. |

---

## Environment Variables

### Required (all modes)

| Variable          | Example                          | Description                              |
| ----------------- | -------------------------------- | ---------------------------------------- |
| `RPC_URL`         | `https://sepolia.base.org`       | JSON-RPC endpoint                        |
| `CHAIN_ID`        | `84532`                          | 84532 (Sepolia) or 8453 (Mainnet)       |
| `SIGNER_PROVIDER` | `WALLET_SIGNER_REMOTE`           | `WALLET_SIGNER_REMOTE` or `LOCAL_PRIVATE_KEY` |

### Required for `WALLET_SIGNER_REMOTE`

| Variable                     | Description                                          | Sensitive |
| ---------------------------- | ---------------------------------------------------- | --------- |
| `WALLET_SIGNER_SERVICE_URL`  | Base URL of user/operator's wallet signing service   | No        |
| `SIGNER_SERVICE_AUTH_TOKEN`  | Bearer auth token for the wallet signing service     | **Yes**   |

### SoHo Credit Layer

| Variable       | Description                                           | Sensitive |
| -------------- | ----------------------------------------------------- | --------- |
| `SOHO_API_URL` | SoHo credit-layer API (credit checks, JIT funding)   | No        |

### Required for `LOCAL_PRIVATE_KEY` (dev / testnet only)

| Variable               | Description                                  | Sensitive |
| ---------------------- | -------------------------------------------- | --------- |
| `SOHO_DEV_PRIVATE_KEY` | User/operator's raw hex private key (NOT a SoHo key) | **Yes** |

### Conditional

| Variable               | When required                                         |
| ---------------------- | ----------------------------------------------------- |
| `SOHO_MAINNET_CONFIRM` | Must be `YES` when `CHAIN_ID=8453`                   |
| `DEV_ALLOW_LOCAL_KEY`  | Set `YES` to allow local key on non-testnet (dangerous) |

---

## Dependencies

Install with:

```bash
npm install
```

| Package  | Purpose                            |
| -------- | ---------------------------------- |
| `ethers` | EVM interactions, EIP-712 signing  |
| `dotenv` | Load `.env` files                  |
| `zod`    | Env var validation at startup      |
