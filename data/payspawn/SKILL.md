---
name: payspawn
description: "Add spending controls to any AI agent that makes API payments. Supports x402 auto-pay, daily limits, per-transaction limits, address allowlists, and fleet provisioning. Use when your agent calls paid APIs or sends payments autonomously. Works on Base with USDC."
requires:
  env:
    - name: PAYSPAWN_CREDENTIAL
      description: "Scoped spending credential issued from payspawn.ai/dashboard. This is NOT a private key — it is a base64-encoded spend permission authorizing the PaySpawn V5 contract to transfer USDC up to the limits you set. The credential encodes: daily cap, per-transaction limit, optional address whitelist, and expiry. Revocable on-chain at any time via dashboard or ps.agent.pause(). Set the lowest limits sufficient for your use case."
      secret: true
      required: false
      lifetime: "Up to 1 year from creation (set at credential creation time). Revocable immediately on-chain — revocation takes effect on the next transaction attempt."
      minPrivilege: "Set daily cap to the minimum USDC needed per day. Use allowedTo address whitelist to restrict payment destinations. Use per-tx cap to limit single-payment exposure."
  install:
    - package: "@payspawn/sdk"
      registry: "npm"
      version: ">=5.3.0"
      source: "https://www.npmjs.com/package/@payspawn/sdk"
      audit: "https://github.com/adambrainai/payspawn"
metadata:
  {
    "openclaw": {
      "emoji": "🔐",
      "color": "#F65B1A"
    }
  }
---

# PaySpawn — Agent Payment Controls

Set spending limits for AI agents that make payments autonomously. Limits are enforced at the smart contract level on Base — not in software, not on a server. The contract cannot be overridden.

## Install

```bash
npm install @payspawn/sdk
```

## Credential Setup (One Human Step)

Before the agent can make payments, the wallet owner must create a credential:

1. Go to [payspawn.ai/dashboard](https://payspawn.ai/dashboard)
2. Connect your wallet (MetaMask, Coinbase Wallet, or any USDC wallet on Base)
3. Approve a USDC spending ceiling (one on-chain transaction, ~$0.005 gas)
4. Set limits: daily cap, per-transaction cap, optional address whitelist
5. Sign the credential (EIP-712 signature — no gas, no transaction)
6. Copy the credential string and set it as `PAYSPAWN_CREDENTIAL` in your environment

The credential is not a private key. Your wallet key never leaves your control. The agent can only spend within the limits you set — the contract enforces this and cannot be bypassed.

## Usage

```typescript
import { PaySpawn } from "@payspawn/sdk";
const ps = new PaySpawn(process.env.PAYSPAWN_CREDENTIAL);

// Auto-pay x402 APIs within your set limits
const res = await ps.fetch("https://api.example.com/endpoint");

// Send a payment
await ps.pay("0xRecipientAddress", 1.00);

// Check balance and remaining daily allowance
const { balance, remaining } = await ps.check();

// Pause all payments instantly (on-chain, immediate effect)
await ps.agent.pause();

// Resume payments
await ps.agent.unpause();
```

## Fleet Mode

Provision multiple agent credentials from one shared pool. One wallet funds the pool; each agent gets its own credential with its own daily limit.

```typescript
// Create a shared budget pool
const pool = await ps.pool.create({ totalBudget: 100, agentDailyLimit: 10 });

// Fund the pool: send USDC to pool.address from your wallet

// Provision credentials for each agent
const fleet = await ps.fleet.provision({ poolAddress: pool.address, count: 10 });
// fleet[0], fleet[1], ... → credential strings, one per agent
```

## Contract Enforcement

Every payment is checked by the PaySpawn V5 contract on Base before any USDC moves:

- Daily allowance exceeded → transaction reverts
- Amount exceeds per-tx cap → transaction reverts  
- Recipient not on whitelist → transaction reverts

No API override. No config flag. Math runs first, every time.

**Contract address (Base Mainnet):** `0xaa8e6815b0E8a3006DEe0c3171Cf9CA165fd862e`  
**USDC (Base):** `0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913`

## Links

- [payspawn.ai](https://payspawn.ai)
- [payspawn.ai/dashboard](https://payspawn.ai/dashboard)
- [@payspawn](https://x.com/payspawn)
- [npm: @payspawn/sdk](https://www.npmjs.com/package/@payspawn/sdk)
