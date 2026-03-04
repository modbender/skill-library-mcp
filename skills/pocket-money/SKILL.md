---
name: pocket-money
description: Give your AI agent crypto wallets on Base. Create purpose-specific wallets, ask your human to fund each one, check balances, and manage budgets. No accounts, no KYC — just wallet addresses and USDC on Base.
metadata:
  openclaw:
    requires:
      bins:
        - node
        - npm
      config:
        - .auteng/wallets/
    install:
      - kind: node
        package: "@auteng/pocket-money"
        bins: []
    homepage: https://github.com/operator-auteng-ai/pocket-money
---

# Pocket Money — Fund Your Agent's Wallets

You have a tool that lets you create and manage crypto wallets (USDC on Base). Each wallet is a separate keypair with its own balance — create one per purpose or budget.

**Package**: [`@auteng/pocket-money`](https://www.npmjs.com/package/@auteng/pocket-money) — published by AutEng ([source on GitHub](https://github.com/operator-auteng-ai/pocket-money)).

## Setup (first time only)

Install the pocket-money library:

```bash
npm install @auteng/pocket-money
```

## Creating a Wallet

Create a named wallet for each purpose or budget:

```typescript
import { wallet } from '@auteng/pocket-money';

const w = await wallet.create({ name: "feb-2026" });
console.log(w.address); // 0xABC123...
```

If a wallet with that name already exists on disk, it loads it. Each wallet is stored at `.auteng/wallets/<name>.json`.

You can also create a quick default wallet:

```typescript
const w = await wallet.create();
```

### Network

```typescript
// Base mainnet (default)
const w = await wallet.create({ name: "prod" });

// Base Sepolia testnet
const w = await wallet.create({ name: "test", network: "base-sepolia" });
```

## Requesting Funding

When you need money, ask your human to fund a specific wallet:

```
I need $12 in USDC for today's tasks.

Please send USDC on **Base** to this address:
`0xABC123...` (wallet: "feb-2026")

You can send from Coinbase, an exchange, or any wallet that supports Base.
```

Be specific about:
- **How much** you need and **why** (e.g., "$5 for API calls", "$20 for a batch processing job")
- **Which wallet** (by name) so both you and your human can track budgets
- The **network**: always Base (not Ethereum mainnet, not Arbitrum)
- The **token**: USDC (not ETH, not other tokens)

## Waiting for Funding

After asking, wait for the USDC to arrive:

```typescript
await w.waitForFunding(12_000000n);
// Polls Base every 10s until >= 12 USDC is available
```

With a timeout:

```typescript
await w.waitForFunding(12_000000n, { timeout: 120_000 });
// Throws after 2 minutes if balance < $12
```

Tell your human you're waiting — they may need a minute to complete the transfer.

## Human Approval Before Spending

**IMPORTANT**: Before making any payment, you MUST:

1. Tell your human exactly what you're about to spend and why
2. Show the estimated cost
3. **Wait for explicit human approval** before proceeding

Example:

```
I'd like to call an x402 API endpoint.

  Service: api.example.com/generate
  Cost:    ~$0.05 per request
  Wallet:  "feb-2026" ($0.98 remaining)

OK to proceed?
```

Never batch multiple paid operations without listing them first. If running a loop of paid calls, present the total estimated cost upfront and get approval for the batch.

## Managing Wallets

```typescript
// Retrieve an existing wallet by name
const w = wallet.get("feb-2026");

// List all wallets
const all = wallet.list();
for (const w of all) {
  const bal = await w.checkBalance();
  console.log(`${w.name}: ${w.address} — ${bal} USDC`);
}

// Check balance
const balance = await w.checkBalance();
// Returns USDC in minor units (6 decimals)
// e.g., 12_000000n = $12.00
```

If running low, ask your human for more funding before expensive operations.

## Security & Storage

**Private keys**: Wallet private keys are stored as unencrypted JSON at `.auteng/wallets/<name>.json` with restricted file permissions (0600). These keys can sign USDC payment authorizations. If the file is leaked or the machine is compromised, funds in that wallet can be stolen. Treat wallet files like passwords.

**Network access**: This skill makes outbound HTTPS requests to:
- **Base RPC** (`mainnet.base.org`) — to check USDC balances

**Mitigations**:
- **Always get human approval** before any operation that spends funds
- Only fund wallets with small amounts appropriate for the task — treat them as petty cash, not savings
- Create separate wallets for separate budgets so you and your human can track spending
- Your wallets only need **USDC on Base** — no ETH needed for gas
