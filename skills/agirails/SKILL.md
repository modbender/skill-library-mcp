---
name: AGIRAILS Payments
version: 3.0.0
description: Trustless payment protocol for AI agents — ACTP escrow + x402 instant payments, USDC on Base L2.
homepage: https://github.com/agirails/openclaw-skill
author:
  name: AGIRAILS
  colony: agirails
license: MIT
metadata:
  clawdbot:
    requires:
      env:
        - ACTP_KEY_PASSWORD
      bins:
        - node
        - npm
    primaryEnv: ACTP_KEY_PASSWORD
    emoji: "💸"
    install:
      - kind: node
        package: "@agirails/sdk"
        bins: [actp]
---

> **How to activate**: Tell your agent: *"Read SKILL.md and set up AGIRAILS payments for my agent"*
>
> **Credential policy:** mock mode needs no secrets. Testnet/mainnet require wallet credentials.

# AGIRAILS — Trustless Payments for AI Agents

The open payment protocol for AI agents. Two payment modes, one SDK, settled in USDC on Base L2.

**ACTP** (Escrow) — for jobs that take time
- Lock USDC → work → deliver → dispute window → settle
- 8-state machine with delivery proof + dispute resolution
- Full escrow + on-chain reputation
- Think: hiring a contractor

**x402** (Instant) — for API calls
- Pay → get response. One step. Atomic.
- No escrow, no disputes — payment is final
- Think: buying from a vending machine

Both modes: **1% fee** ($0.05 minimum) · **USDC only** · **Gasless** (ERC-4337 Smart Wallet + Paymaster)

### Why AGIRAILS

- **Full lifecycle** — escrow, delivery proof, dispute resolution, on-chain reputation. Not just payments — the complete trust layer.
- **Gasless** — Smart Wallet + Paymaster sponsorship. Your agent never needs ETH.
- **USDC only** — real stablecoin settlement. $1 = $1. No gas tokens, no volatile currencies.
- **Open protocol** — ACTP is a public specification (RFC-style). No vendor lock-in.
- **Testnet preloaded** — 1,000 USDC minted automatically on Base Sepolia. Start building for free.
- **Two SDKs** — `npm install @agirails/sdk` · `pip install agirails`
- **Deployment-ready** — encrypted keystores, fail-closed key policy, secret scanning CLI.

> [FAQ](https://agirails.app/faq) · [Docs](https://docs.agirails.io) · [Discord](https://discord.gg/nuhCt75qe4)

---

## 30-Second Quick Start

Try AGIRAILS in mock mode — no wallet, no keys, no `actp init` needed:

```bash
npm install @agirails/sdk
```

Save as `quickstart.js` and run with `node quickstart.js`:

```javascript
const { ACTPClient } = require('@agirails/sdk');
const { parseUnits } = require('ethers');

async function main() {
  // No actp init needed — mock mode works standalone
  const client = await ACTPClient.create({ mode: 'mock' });

  // Mint test USDC (mock only). parseUnits handles the 6-decimal math for you.
  await client.mintTokens(client.getAddress(), parseUnits('10000', 6));

  // All payment amounts are human-readable strings
  const result = await client.pay({
    to: '0x0000000000000000000000000000000000000001',
    amount: '5.00', // 5 USDC
  });
  console.log('Payment:', result.txId, '| State:', result.state);
  console.log('Escrow:', result.escrowId, '| Release required:', result.releaseRequired);
}

main().catch(console.error);
```

> **Note**: This quick start runs without `actp init`. If you use `actp init -m mock` first (recommended for real projects), it auto-mints 10,000 test USDC — no need to call `mintTokens()` in code.

**Already set up?** Just say: *"Pay 10 USDC to 0xProvider for translation service"*

**New agent?** Follow the [onboarding steps below](#for-ai-agents) to set up from scratch.

---

## Now vs Roadmap

### Now

- **Two payment modes**: ACTP (escrow) for complex jobs, x402 (instant) for API calls. Same SDK, same fee.
- **Provider**: `provide('service', handler)` — listen for jobs, do work, get paid
- **Requester**: `request('service', { input, budget, provider })` — pay a specific provider
- **Escrow lifecycle**: 8-state machine — INITIATED → COMMITTED → IN_PROGRESS → DELIVERED → SETTLED (with QUOTED, DISPUTED, CANCELLED branches)
- **Gasless**: Smart Wallet (ERC-4337) + Paymaster. Use `wallet: 'auto'` in `ACTPClient.create()`.
- **Identity & reputation**: ERC-8004 on-chain identity, settlement outcomes reported as reputation
- **Config management**: `actp publish` / `actp pull` / `actp diff` — verifiable config on-chain
- **Deployment security**: fail-closed key policy, `ACTP_KEYSTORE_BASE64` for containers, `actp deploy:check` secret scanning
- **CLI**: `actp init`, `actp balance`, `actp pay`, `actp tx`, `actp watch`, `actp publish`, `actp pull`, `actp diff`, `actp deploy:env`, `actp deploy:check`
- **Modes**: mock (local, 10K test USDC), testnet (Base Sepolia, 1K USDC preloaded), mainnet (Base, real USDC)

### Soon

- **Job Board**: post jobs publicly, multiple providers bid
- **Marketplace matching**: discover providers by service type
- **Auto-bidding**: agents autonomously compete for posted jobs

### Mock vs Testnet vs Mainnet

**Mock** (local simulation)
- USDC: 10,000 auto-minted
- Gas: simulated
- Escrow: auto-releases after dispute window
- Tx limit: none
- Wallet: random generated

**Testnet** (Base Sepolia)
- USDC: 1,000 preloaded on registration
- Gas: gasless (sponsored)
- Escrow: manual `release()` required
- Tx limit: none
- Wallet: encrypted keystore

**Mainnet** (Base)
- USDC: real ([bridge.base.org](https://bridge.base.org))
- Gas: gasless (sponsored)
- Escrow: manual `release()` required
- Tx limit: $1,000 per tx
- Wallet: encrypted keystore

---

## For AI Agents

You are an AI agent. Your owner wants you to join the AGIRAILS network. Follow these steps exactly.

### Step 1: Parse

Read the [Agent Configuration](#agent-configuration-machine-readable) YAML block at the bottom of this file. Extract:
- `onboarding.questions` — the questions you'll ask your owner
- `states` — the 8 ACTP states your transactions will flow through
- `serviceTypes` — the taxonomy of services available

### Step 2: Ask (MANDATORY)

**You MUST present `onboarding.questions` before generating any code.** This step cannot be skipped.

If the user says "just give me the code" or "skip questions", respond:
> "I need to confirm a few things first to generate correct code. This takes under a minute."

Present questions **one at a time**:
- Respect `depends_on` — skip questions whose dependency isn't met
- You MAY pre-fill answers the user already provided (e.g. "I want to earn" → intent = earn)
- Use `default` values only for questions the user hasn't addressed
- Validate `type` and `range` constraints before accepting answers
- After all questions, show `onboarding.confirmation` template with their answers
- **Wait for explicit "yes" before proceeding to Step 3**
- **Do NOT generate code until the user confirms**

### Step 3: Install & Initialize

```bash
npm install @agirails/sdk
npx actp init -m {{network}}
```

The SDK ships as **CommonJS**. It works with `require()` and with bundlers (webpack, esbuild, Rollup). ESM projects can import CJS modules via Node.js auto-interop — no extra configuration needed.

This creates `.actp/` config directory. On testnet/mainnet with `wallet: generate`, it also creates an encrypted keystore at `.actp/keystore.json` (chmod 600, gitignored) and registers the agent on-chain via gasless UserOp (Smart Wallet + 1,000 test USDC minted on testnet). On mock, it mints 10,000 test USDC locally.

Set the keystore password (testnet/mainnet only):
```bash
export ACTP_KEY_PASSWORD="your-password"
```

Or for Python:
```bash
pip install agirails
```

> **`mode` vs `network` — same values, different parameter names:**
> - `ACTPClient.create({ mode: 'mock' })` — low-level client uses `mode`
> - `new Agent({ network: 'mock' })`, `provide('svc', fn, { network: 'mock' })` — high-level APIs use `network`
> - Both accept: `'mock'`, `'testnet'`, `'mainnet'`

### Step 4: Write Code

**Prerequisites**: Steps 1-3 complete, user confirmed with "yes".

All generated code MUST follow these rules:
- Wrap in `async function main() { ... } main().catch(console.error);` (SDK is CommonJS, no top-level await)
- See `mode` vs `network` note above — use the correct parameter name for each API
- Testnet/mainnet requesters: release escrow after verifying delivery (mock auto-releases, real networks do NOT)

Based on the owner's answers, generate the appropriate code.

#### If intent = "earn" (Provider)

**Level 0 — Simplest (one function call):**

```typescript
import { provide } from '@agirails/sdk';

async function main() {
  const provider = provide('{{serviceTypes[0]}}', async (job) => {
    // job.input  — the data to process (object with request payload)
    // job.budget — how much the requester is paying (USDC)
    // TODO: Replace with your actual service logic
    const result = `Processed: ${JSON.stringify(job.input)}`;
    return result;
  }, {
    network: '{{network}}',           // 'mock' | 'testnet' | 'mainnet'
    filter: { minBudget: {{price}} }, // reject jobs below your price
  });

  console.log(`Provider running at ${provider.address}`);
  // provider.status, provider.stats
  // provider.on('payment:received', (amount) => ...)
  // provider.pause(), provider.resume(), provider.stop()
}

main().catch(console.error);
```

**Level 1 — Agent class (multiple services, lifecycle control):**

```typescript
import { Agent } from '@agirails/sdk';

async function main() {
  const agent = new Agent({
    name: '{{name}}',
    network: '{{network}}',
    behavior: {
      concurrency: {{concurrency}},
    },
  });

  agent.provide('{{serviceTypes[0]}}', async (job, ctx) => {
    ctx.progress(50, 'Working...');
    // TODO: Replace with your actual service logic
    const result = `Processed: ${JSON.stringify(job.input)}`;
    return result;
  });

  agent.on('payment:received', (amount) => {
    console.log(`Earned ${amount} USDC`);
  });

  await agent.start();
  console.log(`Agent running at ${agent.address}`);
}

main().catch(console.error);
```

#### If intent = "pay" (Requester)

**If payment_mode = "actp"** (escrow, disputes, multi-step):

```typescript
import { request } from '@agirails/sdk';

async function main() {
  const { result, transaction } = await request('{{services_needed}}', {
    provider: '0xProviderAddress',
    input: { /* your data here */ },
    budget: {{budget}},
    network: '{{network}}',
  });

  console.log(result);
  console.log(`Transaction: ${transaction.id}, Amount: ${transaction.amount}`);

  // IMPORTANT: On testnet/mainnet, release escrow after verifying delivery.
  // Mock mode auto-releases after the dispute window — real networks do NOT.
  // const client = await ACTPClient.create({ mode: '{{network}}' });
  // await client.standard.releaseEscrow(transaction.id);
}

main().catch(console.error);
```

**If payment_mode = "x402"** (instant HTTP payment, no escrow):

> x402 requires a real HTTP endpoint that returns `402 Payment Required`. It works on **testnet and mainnet** — in mock mode, use ACTP for everything.
> 
> **Critical 402 header format:** `x-payment-token` must be `USDC` (symbol), not a token address.
> 
> ```http
> x-payment-required: true
> x-payment-address: 0xYourProviderAddress
> x-payment-amount: 1000000
> x-payment-network: base-sepolia
> x-payment-token: USDC
> x-payment-deadline: 1708...
> ```

```typescript
import { ACTPClient, X402Adapter } from '@agirails/sdk';
import { ethers } from 'ethers';

async function main() {
  const client = await ACTPClient.create({
    mode: '{{network}}',  // 'testnet' or 'mainnet' (x402 needs real endpoints)
  });

  // Register x402 adapter (not registered by default)
  // The SDK provides the signer from your keystore — get it from the wallet provider
  const signer = client.getSigner(); // ethers.Wallet from your keystore
  const usdcAddress = client.getUSDCAddress(); // SDK knows the correct address per network

  client.registerAdapter(new X402Adapter(client.getAddress(), {
    expectedNetwork: 'base-sepolia', // or 'base-mainnet'
    transferFn: async (to, amount) => {
      const usdc = new ethers.Contract(usdcAddress, ['function transfer(address,uint256) returns (bool)'], signer);
      return (await usdc.transfer(to, amount)).hash;
    },
  }));

  const result = await client.basic.pay({
    to: 'https://api.provider.com/service',  // HTTPS endpoint that returns 402
    amount: '{{budget}}',
  });

  console.log(result.response?.status); // 200
  console.log(result.feeBreakdown);     // { grossAmount, providerNet, platformFee, feeBps }
  // No release() needed — x402 is atomic (instant settlement)
}

main().catch(console.error);
```

> **ACTP vs x402 — when to use which?**
>
> **ACTP (escrow)** — for complex jobs
> - Use for: code review, audits, translations, anything with deliverables
> - Flow: Lock USDC -> work -> deliver -> dispute window -> settle
> - Dispute protection: Yes — 48h window, on-chain evidence
> - Escrow: Yes — funds locked until delivery
> - Think: hiring a contractor
>
> **x402 (instant)** — for API calls
> - Use for: lookups, queries, one-shot requests
> - Flow: Pay -> get response (atomic, one step)
> - Dispute protection: No — payment is final
> - Escrow: No — instant settlement
> - Think: buying from a vending machine
>
> Rule of thumb: if the provider needs time to do work -> ACTP. If it's a synchronous HTTP call -> x402.

**Level 1 — Agent class (ACTP):**

```typescript
import { Agent } from '@agirails/sdk';

async function main() {
  const agent = new Agent({
    name: '{{name}}',
    network: '{{network}}',
  });

  await agent.start();

  const { result, transaction } = await agent.request('{{services_needed}}', {
    input: { text: 'Hello world' },
    budget: {{budget}},
  });

  console.log(result);
  // IMPORTANT: On testnet/mainnet, release escrow after verifying delivery:
  // const actpClient = await ACTPClient.create({ mode: '{{network}}' });
  // await actpClient.standard.releaseEscrow(transaction.id);
}

main().catch(console.error);
```

#### If intent = "both"

An Agent can both `provide()` services and `request()` services in the same process:

```typescript
import { Agent } from '@agirails/sdk';

async function main() {
  const agent = new Agent({
    name: '{{name}}',
    network: '{{network}}',
    behavior: { concurrency: {{concurrency}} },
  });

  // EARN: Provide a service
  agent.provide('{{serviceTypes[0]}}', async (job, ctx) => {
    ctx.progress(50, 'Working...');
    // TODO: Replace with your actual service logic
    const result = `Processed: ${JSON.stringify(job.input)}`;
    return result;
  });

  agent.on('payment:received', (amount) => {
    console.log(`Earned ${amount} USDC`);
  });

  await agent.start();
  console.log(`Agent running at ${agent.address}`);

  // PAY: Request a service from another agent (ACTP escrow)
  const { result, transaction } = await agent.request('{{services_needed}}', {
    input: { text: 'Hello world' },
    budget: {{budget}},
  });
  console.log(result);
  // IMPORTANT: On testnet/mainnet, release escrow after verifying delivery:
  // const client = await ACTPClient.create({ mode: '{{network}}' });
  // await client.standard.releaseEscrow(transaction.id);
}

main().catch(console.error);
```

> **If payment_mode = "both"**: In mock mode, generate ACTP-only code (above). x402 requires real HTTPS endpoints and only works on testnet/mainnet. When the user switches to testnet or mainnet, add x402 support by registering `X402Adapter` — see the [x402 template above](#if-payment_mode--x402-instant-http-payment-no-escrow). You do NOT need to generate x402 code for mock mode.

### Step 5: Verify

Confirm that initialization (Step 3) succeeded:

```bash
npx actp balance        # confirm USDC (10,000 in mock, 1,000 on testnet)
npx actp config show    # confirm mode + address
```

### Step 6: Confirm

Show the owner:
- Agent name, address, and network
- Registered services (if provider)
- Balance
- Ask: "Your agent is ready. Start it?"

### Step 7: Go Live

Run your agent code:

```bash
node agent.js          # JavaScript
npx ts-node agent.ts   # TypeScript
```

In mock mode, everything runs locally with simulated USDC. The `actp` CLI is for inspection and manual operations (balance, tx status) — your agent code is what runs. Switch to `testnet` when ready to test on-chain, then `mainnet` for production.

---

## Provider Path (deterministic)

This is the minimum to earn USDC today:

```bash
npx actp init --mode mock
npx actp init --scaffold --intent earn --service code-review --price 5
npx ts-node agent.ts
```

The generated `agent.ts` calls `provide('code-review', handler)`. When a requester calls `request('code-review', { provider: '<your-address>', ... })`, your handler runs, and USDC is released after the dispute window.

**No marketplace matching exists yet.** The requester must know your address and call your exact service name.

---

## Requester Path (deterministic)

This is the minimum to pay a provider today:

```bash
npx actp init --mode mock
npx actp init --scaffold --intent pay --service code-review --price 5
npx ts-node agent.ts
```

Or directly in code:

```typescript
import { request } from '@agirails/sdk';

const { result } = await request('code-review', {
  provider: '0xProviderAddress',  // specific address, or omit for ServiceDirectory lookup
  input: { code: '...' },
  budget: 5,
  network: 'mock',
});
```

**There is no provider discovery.** You specify the provider address directly, or omit `provider` to use the local ServiceDirectory. The `serviceTypes` taxonomy in the YAML above is a local naming convention — not a global registry.

**For instant API payments (x402):** Register `X402Adapter` via `client.registerAdapter()`, then use `client.basic.pay({ to: 'https://...' })`. x402 is NOT registered by default — see Step 4 for the full setup.

**Testnet/mainnet limitation:** `request()` does not auto-release escrow on real networks — you must call `release()` manually after verifying delivery. Proofs can be generated via `ProofGenerator` (hashing) or `DeliveryProofBuilder` (full EAS + IPFS); IPFS/Arweave upload is optional and requires client configuration.

---

## Prerequisites

- **Node.js 18+** — check: `node --version` — install: [nodejs.org](https://nodejs.org)
- **ACTP Keystore** — check: `ls .actp/keystore.json` — install: `npx @agirails/sdk init -m testnet`
- **USDC Balance** — check wallet — bridge USDC to Base via [bridge.base.org](https://bridge.base.org)

### Wallet Setup

```bash
# Generate encrypted keystore (recommended)
npx @agirails/sdk init -m testnet

# Set password to decrypt keystore at runtime
export ACTP_KEY_PASSWORD="your-keystore-password"
```

The SDK auto-detects your wallet in this order:
1. `ACTP_PRIVATE_KEY` env var (policy-gated — see below)
2. `ACTP_KEYSTORE_BASE64` + `ACTP_KEY_PASSWORD` (for Docker/Railway/serverless)
3. `.actp/keystore.json` + `ACTP_KEY_PASSWORD` (local development)

```bash
# For containerized deployments (Docker, Railway, Vercel):
export ACTP_KEYSTORE_BASE64="$(base64 < .actp/keystore.json)"
export ACTP_KEY_PASSWORD="your-keystore-password"
```

> **Where to set env vars for OpenClaw:** Add `ACTP_KEY_PASSWORD` to your `openclaw.json` under `env.vars`, not `.bashrc`. This keeps the password scoped to the agent process and avoids shell-wide exposure. Example:
> ```json
> { "env": { "vars": { "ACTP_KEY_PASSWORD": "your-keystore-password" } } }
> ```

> **Note:** SDK includes default RPC endpoints. For high-volume production use, set up your own RPC via [Alchemy](https://alchemy.com) or [QuickNode](https://quicknode.com) and pass `rpcUrl` to client config.

### Private Key Policy

Using `ACTP_PRIVATE_KEY` directly is **discouraged**. The SDK enforces a fail-closed policy:

- **mainnet / unknown** — **hard fail** (throws error, refuses to start)
- **testnet** — warns once, then proceeds (backward compatibility)
- **mock** — silent (no real funds at risk)

**Always prefer encrypted keystores** (`.actp/keystore.json` or `ACTP_KEYSTORE_BASE64`). Raw private keys in env vars are a deployment security risk — they appear in process listings, CI logs, and crash dumps.

To check your deployment for leaked secrets:
```bash
actp deploy:check          # Scan for exposed keys, missing .dockerignore, etc.
actp deploy:env            # Generate .dockerignore/.railwayignore with safe defaults
```

### Installation

```bash
# TypeScript/Node.js
npm install @agirails/sdk

# Python
pip install agirails
```

---

## How It Works

```
REQUESTER                          PROVIDER
    |                                  |
    |  request('service', {budget})    |
    |--------------------------------->|
    |                                  |
    |         INITIATED (0)            |
    |                                  |
    |     [optional: QUOTED (1)]       |
    |<---------------------------------|
    |                                  |
    |   USDC locked --> Escrow Vault   |
    |                                  |
    |         COMMITTED (2)            |
    |                                  |
    |                          work... |
    |         IN_PROGRESS (3)          |
    |                                  |
    |      result + proof              |
    |<---------------------------------|
    |         DELIVERED (4)            |
    |                                  |
    |   [dispute window: 48h default]  |
    |                                  |
    |   Escrow Vault --> Provider      |
    |         SETTLED (5)              |
    |                                  |
```

Both sides can open a `DISPUTED (6)` state after delivery. Either party can `CANCELLED (7)` early states.

### Key Guarantees

- **Escrow Solvency** — vault always holds >= active transaction amounts
- **State Monotonicity** — states only move forward, never backwards
- **Deadline Enforcement** — no delivery after deadline passes
- **Dispute Protection** — 48h window to raise issues before settlement

---

## State Machine

```
INITIATED --+-> QUOTED --> COMMITTED --> IN_PROGRESS --> DELIVERED --> SETTLED
            |                  |              |              |
            +--> COMMITTED     |              |              +--> DISPUTED
                               |              |                    |    |
                               v              v                    v    v
                           CANCELLED      CANCELLED            SETTLED  CANCELLED

Any of INITIATED, QUOTED, COMMITTED, IN_PROGRESS can -> CANCELLED
Only DELIVERED can -> DISPUTED
SETTLED and CANCELLED are terminal (no outbound transitions)
```

**Valid transitions** (from `state.ts`):

- **INITIATED** → QUOTED, COMMITTED, CANCELLED
- **QUOTED** → COMMITTED, CANCELLED
- **COMMITTED** → IN_PROGRESS, CANCELLED
- **IN_PROGRESS** → DELIVERED, CANCELLED
- **DELIVERED** → SETTLED, DISPUTED
- **DISPUTED** → SETTLED, CANCELLED
- **SETTLED** → *(terminal)*
- **CANCELLED** → *(terminal)*

Note: INITIATED can go directly to COMMITTED (skipping QUOTED).

---

## Escrow

All payments flow through the `EscrowVault` smart contract:

1. **Lock** — On COMMITTED: requester's USDC is transferred to EscrowVault
2. **Hold** — During IN_PROGRESS and DELIVERED: funds are locked
3. **Release** — On SETTLED: USDC released to provider (minus 1% fee)
4. **Refund** — On CANCELLED: USDC returned to requester

In mock mode, escrow is simulated locally and `request()` auto-releases after the dispute window. On testnet/mainnet, **you must call `release()` explicitly** — the SDK will not auto-release real funds. Adapters set `releaseRequired: true` on real networks.

---

## Fee

- **Rate**: 1% of transaction amount
- **Minimum**: $0.05 per transaction
- **Calculation**: `fee = max(amount * 0.01, 0.05)`
- **ACTP**: fee deducted on escrow release (SETTLED state) via ACTPKernel
- **x402**: fee deducted atomically via X402Relay contract (same 1% / $0.05 min)
- **No subscriptions**. No hidden costs. Same fee on both payment paths.

Provider receives: `amount - max(amount * 0.01, $0.05)`

---

## Pricing

Set your price. Negotiate via the QUOTED state.

The SDK provides a **cost + margin** model:

```typescript
agent.provide({
  name: 'translation',
  pricing: {
    cost: {
      base: 0.50,                          // $0.50 fixed cost per job
      perUnit: { unit: 'word', rate: 0.005 } // $0.005 per word
    },
    margin: 0.40,  // 40% profit margin
    minimum: 1.00, // never accept less than $1
  },
}, handler);
```

**How it works:**
- SDK calculates: `price = cost / (1 - margin)`
- If job budget >= price: **accept**
- If job budget < price but > cost: **counter-offer** (via QUOTED state)
- If job budget < cost: **reject**

There are no predefined "competitive/market/premium" strategies. You set your costs and margin directly.

> The QUOTED state and PricingStrategy both exist in the SDK. However, the counter-offer flow requires both agents to be online — there is no persistent job board or stored quotes.

---

## Actions

- `pay` (Requester) — simple payment (create + escrow lock)
- `checkStatus` (Anyone) — get transaction state
- `createTransaction` (Requester) — create with custom params
- `linkEscrow` (Requester) — lock funds in escrow
- `transitionState` (Provider) — quote, start, deliver
- `releaseEscrow` (Requester) — release funds to provider
- `transitionState('DISPUTED')` (Either) — raise dispute for mediation

---

## Requester Flow (Paying for Services)

### Simple Payment

```typescript
import { ACTPClient } from '@agirails/sdk';

const client = await ACTPClient.create({
  mode: 'mainnet',  // auto-detects keystore or ACTP_PRIVATE_KEY
});

// One-liner payment
const result = await client.basic.pay({
  to: '0xProviderAddress',
  amount: '25.00',     // USDC
  deadline: '+24h',    // 24 hours from now
});

console.log(`Transaction: ${result.txId}`);
console.log(`State: ${result.state}`);

// IMPORTANT: On testnet/mainnet, release escrow after verifying delivery:
// await client.standard.releaseEscrow(result.txId);
```

### Instant HTTP Payment (x402)

For simple API calls with no deliverables or disputes, use x402 — atomic, one-step:

```typescript
import { ACTPClient, X402Adapter } from '@agirails/sdk';

const client = await ACTPClient.create({
  mode: 'mainnet',
});

// Register x402 adapter (not registered by default)
client.registerAdapter(new X402Adapter(client.getAddress(), {
    expectedNetwork: 'base-sepolia', // or 'base-mainnet'
    // Provide your own USDC transfer function (signer = your ethers.Wallet)
    transferFn: async (to, amount) => {
      const usdc = new ethers.Contract(USDC_ADDRESS, ['function transfer(address,uint256) returns (bool)'], signer);
      return (await usdc.transfer(to, amount)).hash;
    },
  }));

const result = await client.basic.pay({
  to: 'https://api.provider.com/service',  // HTTPS endpoint that returns 402
  amount: '5.00',
});

console.log(result.response?.status); // 200
// No release() needed — x402 is atomic (instant settlement)
```

---

### Advanced Payment (Full Control)

```typescript
// 1. Create transaction
const txId = await client.standard.createTransaction({
  provider: '0xProviderAddress',
  amount: '100',  // 100 USDC (user-friendly)
  deadline: Math.floor(Date.now() / 1000) + 86400,
  disputeWindow: 172800,  // 48 hours
  serviceDescription: 'Translate 500 words to Spanish',
});

// 2. Lock funds in escrow
const escrowId = await client.standard.linkEscrow(txId);

// 3. Wait for delivery... then release
// ...wait for DELIVERED
await client.standard.releaseEscrow(escrowId);
```

---

## Provider Flow (Receiving Payments)

```typescript
import { ethers } from 'ethers';
const abiCoder = ethers.AbiCoder.defaultAbiCoder();

// 1. Quote the job (encode amount as proof)
const quoteAmount = ethers.parseUnits('50', 6);
const quoteProof = abiCoder.encode(['uint256'], [quoteAmount]);
await client.standard.transitionState(txId, 'QUOTED', quoteProof);

// 2. Start work (REQUIRED before delivery!)
await client.standard.transitionState(txId, 'IN_PROGRESS');

// 3. Deliver with dispute window proof
const disputeWindow = 172800;  // 48 hours
const deliveryProof = abiCoder.encode(['uint256'], [disputeWindow]);
await client.standard.transitionState(txId, 'DELIVERED', deliveryProof);

// 4. Requester releases after dispute window (or earlier if satisfied)
```

**CRITICAL:** `IN_PROGRESS` is **required** before `DELIVERED`. Contract rejects direct `COMMITTED -> DELIVERED`.

---

## Proof Encoding

All proofs must be ABI-encoded hex strings:

- **QUOTED** — `['uint256']` amount — `encode(['uint256'], [parseUnits('50', 6)])`
- **DELIVERED** — `['uint256']` dispute window — `encode(['uint256'], [172800])`
- **SETTLED** (dispute) — `['uint256', 'uint256', 'address', 'uint256']` — `[reqAmt, provAmt, mediator, fee]`

```typescript
import { ethers } from 'ethers';
const abiCoder = ethers.AbiCoder.defaultAbiCoder();

// Quote proof
const quoteProof = abiCoder.encode(['uint256'], [ethers.parseUnits('100', 6)]);

// Delivery proof
const deliveryProof = abiCoder.encode(['uint256'], [172800]);

// Resolution proof (mediator only)
const resolutionProof = abiCoder.encode(
  ['uint256', 'uint256', 'address', 'uint256'],
  [requesterAmount, providerAmount, mediatorAddress, mediatorFee]
);
```

---

## Checking Status

```typescript
const status = await client.basic.checkStatus(txId);

console.log(`State: ${status.state}`);
console.log(`Can dispute: ${status.canDispute}`);
```

---

## Disputes

Either party can raise a dispute before settlement:

```typescript
// Raise dispute
await client.standard.transitionState(txId, 'DISPUTED');

// Mediator resolves (admin only)
const resolution = abiCoder.encode(
  ['uint256', 'uint256', 'address', 'uint256'],
  [
    ethers.parseUnits('30', 6),   // requester gets 30 USDC
    ethers.parseUnits('65', 6),   // provider gets 65 USDC
    mediatorAddress,
    ethers.parseUnits('5', 6),    // mediator fee
  ]
);
await client.standard.transitionState(txId, 'SETTLED', resolution);
```

---

## Client Modes

- `mock` — local simulation (development, testing)
- `testnet` — Base Sepolia (integration testing)
- `mainnet` — Base (production)

```typescript
// Development
const client = await ACTPClient.create({
  mode: 'mock',
});
await client.mintTokens('0x...', '1000000000');  // Mint test USDC

// Production (auto-detects keystore or ACTP_PRIVATE_KEY)
const client = await ACTPClient.create({
  mode: 'mainnet',
});
```

---

## Identity (ERC-8004)

Every agent gets a portable on-chain identity:

- **Optional** — resolve agents via `ERC8004Bridge` from `@agirails/sdk`. Neither `actp init` nor `Agent.start()` registers identity automatically.
- **Portable** — if registered, any marketplace reading ERC-8004 recognizes you
- **Reputation** — settlement outcomes are reported on-chain only if the agent has a non-zero `agentId` set during transaction creation and `release()` is called explicitly

The SDK handles all contract addresses automatically — no manual configuration needed.

```typescript
import { ERC8004Bridge, ReputationReporter } from '@agirails/sdk';

// Resolve agent identity (read-only, no gas)
const bridge = new ERC8004Bridge({ network: 'base-sepolia' });
const agent = await bridge.resolveAgent('12345');
console.log(agent.wallet);  // payment address

// Report reputation (requires signer, pays gas)
const reporter = new ReputationReporter({ network: 'base-sepolia', signer });
await reporter.reportSettlement({
  agentId: '12345',
  txId: '0x...',
  serviceType: 'code-review',
});
```

---

## Adapter Routing

The SDK uses an adapter router. By default, only ACTP adapters (basic + standard) are registered. Other adapters require explicit registration:

- `0x1234...` (Ethereum address) → **ACTP** (basic/standard) — registered by default
- `https://api.example.com/...` → **x402** — must register `X402Adapter` via `client.registerAdapter()`
- `agent-name` or agent ID → **ERC-8004** — must configure ERC-8004 bridge

```typescript
// ACTP — works out of the box (default adapters)
await client.basic.pay({ to: '0xProviderAddress', amount: '5' });

// x402 — requires registering the adapter first:
import { X402Adapter } from '@agirails/sdk';
client.registerAdapter(new X402Adapter(client.getAddress(), {
    expectedNetwork: 'base-sepolia', // or 'base-mainnet'
    // Provide your own USDC transfer function (signer = your ethers.Wallet)
    transferFn: async (to, amount) => {
      const usdc = new ethers.Contract(USDC_ADDRESS, ['function transfer(address,uint256) returns (bool)'], signer);
      return (await usdc.transfer(to, amount)).hash;
    },
  }));
await client.basic.pay({ to: 'https://api.provider.com/service', amount: '1' });

// ERC-8004 — requires bridge configuration:
import { ERC8004Bridge } from '@agirails/sdk';
const bridge = new ERC8004Bridge({ network: 'base-sepolia' });
const agent = await bridge.resolveAgent('12345');
await client.basic.pay({ to: agent.wallet, amount: '5', erc8004AgentId: '12345' });
```

Only ACTP address routing works out of the box. x402 and ERC-8004 require explicit setup.

You can also force a specific adapter via metadata:

```typescript
await client.basic.pay({
  to: '0xProvider',
  amount: '5.00',
  metadata: { paymentMethod: 'x402' },  // force x402
});
```

---

## x402 Fee Splitting

Both ACTP (escrow) and x402 (instant) payments carry the same 1% platform fee ($0.05 minimum).

For x402 payments, fees are split atomically on-chain via the `X402Relay` contract:
- Provider receives 99% (or gross minus $0.05 minimum)
- Treasury receives 1% fee
- Single transaction — no partial failure risk

```typescript
// Fee breakdown is included in the result
const result = await client.basic.pay({
  to: 'https://api.provider.com/service',
  amount: '100.00',
});

console.log(result.feeBreakdown);
// { grossAmount: '100000000', providerNet: '99000000',
//   platformFee: '1000000', feeBps: 100, estimated: true }
```

> The `estimated: true` flag means the breakdown was calculated client-side. The on-chain X402Relay contract is the source of truth for actual fee amounts.

---

## Config Management (AGIRAILS.md as Source of Truth)

This file is your agent's canonical configuration. You can publish its hash on-chain for verifiable config management:

```bash
actp publish          # Hash AGIRAILS.md -> store configHash + configCID in AgentRegistry
actp diff             # Compare local AGIRAILS.md hash vs on-chain — detect drift
actp pull             # Restore AGIRAILS.md from on-chain configCID (IPFS)
```

This enables:
- **Verifiable config**: anyone can verify your agent's stated service types match on-chain
- **Drift detection**: SDK checks config hash on startup (non-blocking warning if mismatch)
- **Recovery**: restore your config from on-chain if local file is lost

**AGIRAILS.md format** — must start with YAML frontmatter (`---`):

```yaml
---
name: my-agent
version: 1.0.0
services:
  - type: code-review
    price: 5.00
    currency: USDC
  - type: bug-fixing
    price: 10.00
    currency: USDC
network: base-sepolia
---

# My Agent

Optional markdown description of your agent's capabilities.
```

Required fields: `name`, `services` (with `type`, `price`, `currency`). Optional: `version`, `network`, `description`.

---

## Deployment Security

Before deploying your agent to production, run the security checks:

```bash
# Scan for leaked secrets, missing .dockerignore, exposed keystores
actp deploy:check

# Generate .dockerignore and .railwayignore with safe defaults
actp deploy:env
```

**Key rules:**
- **Never** use `ACTP_PRIVATE_KEY` on mainnet — the SDK will hard-fail. Use encrypted keystores.
- For containerized environments (Docker, Railway, Vercel), use `ACTP_KEYSTORE_BASE64`:
  ```bash
  export ACTP_KEYSTORE_BASE64="$(base64 < .actp/keystore.json)"
  export ACTP_KEY_PASSWORD="your-password"
  ```
- `actp deploy:check` recursively scans your project (depth 5, skips `node_modules`/`.git`) for exposed keys.
- `--quiet` flag hides PASS and WARN, showing only FAIL results.

---

## Service Types (MVP limitation)

The `serviceTypes` taxonomy in the YAML frontmatter is a **suggested naming convention**, not a discovery mechanism.

- `provide('code-review')` only matches `request('code-review')` — **exact string match, case-sensitive**
- Typos like `content-writting` instead of `content-writing` will silently fail to match — double-check spelling
- There is no global registry, search, or automatic matching between agents
- Requesters must know the provider's address and service name
- **ServiceDirectory is in-memory, per-process.** A provider in one process is not visible to a requester in another process. For cross-process communication, pass the provider's address explicitly via the `provider:` field.
- The planned Job Board (Phase 1D) will add public job posting and bidding

---

## Discovery (Optional)

Agents can publish an A2A-compatible Agent Card for discovery:

```json
{
  "name": "{{name}}",
  "description": "AI agent on AGIRAILS settlement network",
  "url": "https://your-agent-endpoint.com",
  "capabilities": {{capabilities}},
  "protocol": "ACTP",
  "network": "{{network}}",
  "payment": {
    "currency": "USDC",
    "network": "base",
    "address": "{{agent.address}}"
  }
}
```

Host at `/.well-known/agent.json` for directory listings.

> Discovery is not built into the SDK. This Agent Card follows the A2A spec and can be consumed by external directories or marketplaces. The SDK itself does not query or consume Agent Cards.

---

## Integration by Runtime

AGIRAILS works with any AI runtime. Here's how to integrate with specific platforms:

### Claude Code

Install the AGIRAILS skill:

```bash
mkdir -p ~/.claude/skills/agirails
curl -sL https://market.agirails.io/skills/claude-code/skill.md \
  -o ~/.claude/skills/agirails/skill.md
```

Then use: `/agirails init`, `/agirails status`, `/agirails deliver`

### OpenClaw

Install the AGIRAILS skill:

```bash
git clone https://github.com/agirails/openclaw-skill.git ~/.openclaw/skills/agirails
```

Then tell your agent: *"Pay 10 USDC to 0xProvider for translation service"*

See `{baseDir}/openclaw/QUICKSTART.md` for the 5-minute setup guide.

### n8n

Install the community node in your n8n instance:

```bash
npm install n8n-nodes-actp
```

Adds ACTP nodes to any workflow: create transactions, track state, release escrow.

### Any Other Runtime

Install the SDK (`npm install @agirails/sdk` or `pip install agirails`), use `provide()` / `request()` or the `Agent` class. The SDK handles wallet creation, escrow, and settlement automatically.

---

## CLI Reference

- `actp init` — initialize ACTP in current directory
- `actp init --scaffold` — generate starter agent.ts (use `--intent earn/pay/both`)
- `actp pay <to> <amount>` — create a payment transaction
- `actp balance [address]` — check USDC balance
- `actp tx create` — create transaction (advanced)
- `actp tx status <txId>` — check transaction state
- `actp tx list` — list all transactions
- `actp tx deliver <txId>` — mark transaction as delivered
- `actp tx settle <txId>` — release escrow funds
- `actp tx cancel <txId>` — cancel a transaction
- `actp watch <txId>` — watch transaction state changes
- `actp simulate pay` — dry-run a payment
- `actp simulate fee <amount>` — calculate fee for amount
- `actp batch [file]` — execute batch commands from file
- `actp mint <address> <amount>` — mint test USDC (mock only)
- `actp config show` — view current configuration
- `actp config set <key> <value>` — set configuration value
- `actp config get <key>` — get configuration value
- `actp publish` — publish AGIRAILS.md config hash to on-chain AgentRegistry
- `actp pull` — restore AGIRAILS.md from on-chain config (via configCID)
- `actp diff` — compare local config vs on-chain snapshot
- `actp register` — register agent on-chain (deprecated — use `actp publish`)
- `actp deploy:env` — generate `.dockerignore`/`.railwayignore` with safe defaults
- `actp deploy:check` — scan project for leaked secrets and missing ignore files
- `actp time show` — show mock blockchain time
- `actp time advance <duration>` — advance mock time
- `actp time set <timestamp>` — set mock time

All commands support `--json` for machine-readable output and `-q`/`--quiet` for minimal output.

---

## Error Handling

```typescript
import {
  InsufficientFundsError,
  InvalidStateTransitionError,
  DeadlineExpiredError,
} from '@agirails/sdk';

try {
  await client.basic.pay({...});
} catch (error) {
  if (error instanceof InsufficientFundsError) {
    console.log(error.message);
  } else if (error instanceof InvalidStateTransitionError) {
    console.log(`Invalid state transition`);
  }
}
```

---

## Python Example

```python
import asyncio
import os
from agirails import ACTPClient

async def main():
    client = await ACTPClient.create(
        mode="mainnet",  # auto-detects keystore or ACTP_PRIVATE_KEY
    )

    result = await client.basic.pay({
        "to": "0xProviderAddress",
        "amount": "25.00",
        "deadline": "24h",
    })

    print(f"Transaction: {result.tx_id}")
    print(f"State: {result.state}")

asyncio.run(main())
```

---

## Troubleshooting

- **"Insufficient balance"** — Mock: `actp mint <address> 10000`. Testnet: faucet. Mainnet: bridge USDC via bridge.base.org.
- **"ACTP already initialized"** — use `actp init --force` to reinitialize.
- **"Invalid mode"** — valid modes: `mock`, `testnet`, `mainnet`.
- **"Address required for testnet"** — run `actp init -m testnet` to generate a keystore, or set `ACTP_PRIVATE_KEY`.
- **"Unknown network"** — SDK supports `base-sepolia` (testnet) and `base-mainnet` (mainnet).
- **Transaction stuck in INITIATED** — no provider registered for that service name. Ensure a provider is running with `provide('exact-service-name', handler)` on the same network.
- **"Invalid state transition"** — states only move forward, never backward. Check the state machine above.
- **`COMMITTED -> DELIVERED` reverts** — missing IN_PROGRESS. Add `transitionState(txId, 'IN_PROGRESS')` first.
- **Invalid proof error** — wrong encoding. Use `ethers.AbiCoder` with correct types.
- **Deadline expired** — create new transaction with longer deadline.
- **RPC 503 errors** — Base Sepolia public RPC has rate limits. Set `BASE_SEPOLIA_RPC` env var to Alchemy or other provider.
- **Large transaction caution** — security audit passed (Feb 2026), no hard cap. Use appropriate amounts for your use case.
- **"ACTP_PRIVATE_KEY rejected"** — blocked on mainnet. Use encrypted keystore or `ACTP_KEYSTORE_BASE64` for containers.
- **"deploy:check FAIL"** — run `actp deploy:env` to generate safe ignore files, then fix flagged issues.

---

## Files

- **`{baseDir}/references/requester-template.md`** — Full requester agent template
- **`{baseDir}/references/provider-template.md`** — Full provider agent template
- **`{baseDir}/references/state-machine.md`** — Detailed state transitions
- **`{baseDir}/examples/simple-payment.md`** — All 3 API levels explained
- **`{baseDir}/examples/full-lifecycle.md`** — Complete transaction lifecycle

---

## OpenClaw Integration

Ready-to-use templates for OpenClaw agents.

### Quick Setup (5 minutes)

```bash
# Run setup script
bash {baseDir}/scripts/setup.sh

# Add agent config to openclaw.json (see agent-config.json)
# Set environment variables
# Restart OpenClaw
```

See `{baseDir}/openclaw/QUICKSTART.md` for detailed guide.

### OpenClaw Files

- **`{baseDir}/openclaw/QUICKSTART.md`** — 5-minute setup guide
- **`{baseDir}/openclaw/agent-config.json`** — Ready-to-use agent configs
- **`{baseDir}/openclaw/SOUL-treasury.md`** — Treasury agent template (buyer)
- **`{baseDir}/openclaw/SOUL-provider.md`** — Merchant agent template (seller)
- **`{baseDir}/openclaw/SOUL-agent.md`** — Full autonomous agent (earn + pay + x402)
- **`{baseDir}/openclaw/cron-examples.json`** — Automation cron jobs
- **`{baseDir}/openclaw/validation-patterns.md`** — Delivery validation helpers
- **`{baseDir}/openclaw/security-checklist.md`** — Pre-launch security audit

### Scripts

- **`{baseDir}/scripts/setup.sh`** — Automated workspace setup
- **`{baseDir}/scripts/test-balance.ts`** — Check wallet balance
- **`{baseDir}/scripts/test-purchase.ts`** — Test purchase on testnet

---

## Resources

- **Documentation**: https://docs.agirails.io
- **SDK (npm)**: https://www.npmjs.com/package/@agirails/sdk
- **SDK (pip)**: https://pypi.org/project/agirails/
- **SDK repo**: https://github.com/agirails/sdk-js
- **Examples**: https://github.com/agirails/sdk-js/tree/main/examples
- **GitHub**: https://github.com/agirails
- **Discord**: https://discord.gg/nuhCt75qe4
- **Support**: support@agirails.io
- **Security**: security@agirails.io

---

*One file. Any agent. Earn or pay.*

---

## External Endpoints

| Endpoint | Purpose | Data Sent |
|----------|---------|-----------|
| `registry.npmjs.org` | Install `@agirails/sdk` | Package name |
| Base Sepolia RPC (`sepolia.base.org`) | Testnet transactions | Wallet address, signed tx data |
| Base Mainnet RPC (`mainnet.base.org`) | Mainnet transactions | Wallet address, signed tx data |
| Coinbase CDP Paymaster + Bundler | ERC-4337 gas sponsorship | UserOperation calldata |

## Security & Privacy

- **Private keys** are stored in an AES-128-CTR encrypted keystore (`.actp/keystore.json`, chmod 600, auto-gitignored). They are decrypted in-memory only when signing transactions, never transmitted.
- **Raw private keys** (`ACTP_PRIVATE_KEY`) are blocked on mainnet by the SDK's fail-closed policy. On testnet they trigger a one-time warning.
- **On-chain transactions** are public on Base L2. Wallet addresses and USDC amounts are visible to anyone.
- **No telemetry or analytics** are collected by the SDK or this skill.
- **No data is sent** to AGIRAILS servers. All transactions go directly to Base L2 via public or user-configured RPC endpoints.

## Trust

ACTP is an open-source protocol. Smart contracts are verified on-chain:
- Protocol source: [github.com/agirails/actp-kernel](https://github.com/agirails/actp-kernel)
- SDK source: [github.com/agirails/sdk-js](https://github.com/agirails/sdk-js)
- Contracts verified on Sourcify (Base Sepolia + Base Mainnet)

Gas sponsorship is provided by Coinbase CDP (ERC-4337 Paymaster). Review Coinbase's terms at [docs.cdp.coinbase.com](https://docs.cdp.coinbase.com).

---

## Agent Configuration (Machine-Readable)

AI agents: parse this YAML block to extract onboarding questions, service types, and state definitions. The SDK handles all contract addresses and network configuration automatically.

```yaml
name: AGIRAILS Payments
version: 3.0.0
protocol: AGIRAILS
spec: ACTP
description: Official ACTP (Agent Commerce Transaction Protocol) SDK — the first trustless payment layer for AI agents. Pay for services via escrow (ACTP) or instant HTTP payments (x402). Receive payments, check transaction status, resolve agent identities, or handle disputes — all with USDC on Base L2.
author: AGIRAILS Inc.
homepage: https://agirails.io
repository: https://github.com/agirails/openclaw-skill
license: MIT
network: base
currency: USDC
fee: "1% ($0.05 min)"
sdk:
  npm: "@agirails/sdk"
  pip: "agirails"
tags: [payments, blockchain, escrow, agent-commerce, base-l2, usdc, web3]
keywords: [AI agent payments, trustless escrow, ACTP protocol, agent-to-agent commerce, USDC payments]
serviceTypes:
  code: [code-review, bug-fixing, feature-dev, refactoring, testing]
  security: [security-audit, smart-contract-audit, pen-testing]
  data: [data-analysis, research, data-extraction, web-scraping]
  content: [content-writing, copywriting, translation, summarization]
  ops: [automation, integration, devops, monitoring]
states:
  - { name: INITIATED, value: 0, description: "Transaction created by requester" }
  - { name: QUOTED, value: 1, description: "Provider responded with price quote" }
  - { name: COMMITTED, value: 2, description: "USDC locked in escrow" }
  - { name: IN_PROGRESS, value: 3, description: "Provider is working on the job" }
  - { name: DELIVERED, value: 4, description: "Provider submitted deliverable" }
  - { name: SETTLED, value: 5, description: "USDC released to provider (terminal)" }
  - { name: DISPUTED, value: 6, description: "Either party opened a dispute" }
  - { name: CANCELLED, value: 7, description: "Transaction cancelled (terminal)" }
onboarding:
  questions:
    - id: intent
      ask: "What do you want to do on AGIRAILS?"
      options: [earn, pay, both]
      default: both
      type: select
      hint: "earn = provide services for USDC. pay = request services from other agents."
    - id: name
      ask: "What is your agent's name?"
      type: text
      hint: "Alphanumeric, hyphens, dots, underscores (a-zA-Z0-9._-). Example: my-translator"
    - id: network
      ask: "Which network?"
      options: [mock, testnet, mainnet]
      default: mock
      type: select
      hint: "mock = local simulation, no real funds. testnet = Base Sepolia (free test USDC). mainnet = real USDC."
    - id: wallet
      ask: "Wallet setup?"
      options: [generate, existing]
      default: generate
      type: select
      depends_on: { network: [testnet, mainnet] }
      hint: "generate = encrypted keystore (.actp/keystore.json). existing = ACTP_PRIVATE_KEY (testnet only). For containers: ACTP_KEYSTORE_BASE64."
    - id: serviceTypes
      ask: "What services will you provide?"
      type: multi-select
      depends_on: { intent: [earn, both] }
      hint: "Exact string match — provide('code-review') only reaches request('code-review'). No auto-discovery."
    - id: price
      ask: "What is your base price per job in USDC?"
      type: number
      range: [0.05, 10000]
      default: 1.00
      depends_on: { intent: [earn, both] }
      hint: "Minimum $0.05 (protocol minimum)."
    - id: concurrency
      ask: "Max concurrent jobs?"
      type: number
      range: [1, 100]
      default: 10
      depends_on: { intent: [earn, both] }
    - id: budget
      ask: "Default budget per request in USDC?"
      type: number
      range: [0.05, 1000]
      default: 10
      depends_on: { intent: [pay, both] }
      hint: "Mainnet limit: $1000."
    - id: payment_mode
      ask: "Payment mode?"
      options: [actp, x402, both]
      default: actp
      type: select
      depends_on: { intent: [pay, both] }
      hint: "actp = escrow (complex jobs). x402 = instant (API calls). Both use same SDK."
    - id: services_needed
      ask: "What service do you need from other agents? (ask once per service)"
      type: text
      depends_on: { intent: [pay, both] }
      hint: "One service name per answer. If the user needs multiple, repeat this question. Example: code-review"
  confirmation: |
    Agent: {{name}} | Network: {{network}} | Intent: {{intent}}
    {{#if serviceTypes}}Services: {{serviceTypes}}{{/if}}
    {{#if price}}Price: ${{price}}{{/if}}
    {{#if payment_mode}}Mode: {{payment_mode}}{{/if}}
    {{#if budget}}Budget: ${{budget}}{{/if}}
    Proceed? (yes/no)
  verify: ["npx actp balance", "npx actp config show"]
requiredBinaries:
  - node (>=18)
  - npm
requiredEnvVars:
  - none for mock mode
  - one wallet credential path for testnet/mainnet:
    - ACTP_KEY_PASSWORD (with .actp/keystore.json or ACTP_KEYSTORE_BASE64)
    - ACTP_PRIVATE_KEY (testnet only; blocked on mainnet)
    - PRIVATE_KEY (legacy fallback; treat as high-risk secret)
optionalEnvVars:
  - ACTP_KEY_PASSWORD (required only when decrypting .actp/keystore.json or ACTP_KEYSTORE_BASE64 for testnet/mainnet)
  - ACTP_PRIVATE_KEY (raw private key — testnet only, blocked on mainnet by SDK fail-closed policy)
  - ACTP_KEYSTORE_BASE64 (base64-encoded keystore — for Docker/Railway/serverless deployments)
  - PRIVATE_KEY (legacy raw private key fallback used by some tooling; not recommended)
  - BASE_SEPOLIA_RPC (custom testnet RPC endpoint — defaults to public Base Sepolia)
  - BASE_MAINNET_RPC (custom mainnet RPC endpoint — defaults to public Base Mainnet)
  - PROVIDER_ADDRESS (target provider wallet address — used in example scripts only)
  - MEDIATOR_ADDRESS (dispute mediator address — used in full-lifecycle example only)
  - IPFS_GATEWAY (IPFS gateway URL — defaults to https://ipfs.io/ipfs/, used in requester template)
  - AGIRAILS_MODE (mode override — mock, testnet, or mainnet — used in templates and scripts)
  - OPENCLAW_WORKSPACE (workspace directory path — defaults to ~/.openclaw/workspace, used by setup.sh)
install:
  - npm install @agirails/sdk (TypeScript/Node.js)
  - pip install agirails (Python alternative)
  - npx actp init -m <network> (creates keystore and config)
credentials:
  - ACTP_KEY_PASSWORD (conditional — required only with encrypted keystore/.actp/keystore.json or ACTP_KEYSTORE_BASE64; not needed in mock mode)
  - ACTP_PRIVATE_KEY (optional, testnet only — SDK hard-fails on mainnet, warns once on testnet)
  - ACTP_KEYSTORE_BASE64 (optional — base64-encoded keystore for containerized/serverless deployments)
  - PRIVATE_KEY (legacy optional raw private key fallback — high sensitivity, avoid on mainnet)
filesystemWrites:
  - .actp/keystore.json (encrypted wallet — AES-128-CTR, chmod 600, auto-gitignored)
  - .actp/config.json (SDK configuration — mode, network, contract addresses)
  - .actp/pending-publish.json (lazy publish state for deferred mainnet registration)
  - ~/.openclaw/workspace/ (setup.sh copies agent config templates here)
networkAccess:
  - npm registry at npmjs.com (package install)
  - Base Sepolia RPC (testnet on-chain transactions)
  - Base Mainnet RPC (mainnet on-chain transactions)
  - Coinbase CDP Paymaster and Bundler (ERC-4337 gas sponsorship)
scope: |
  This skill instructs agents to: (1) install @agirails/sdk from npm or agirails from pip,
  (2) run 'npx actp init' to create an AES-128-CTR encrypted keystore under .actp/ (chmod 600, gitignored),
  (3) read/write .actp/ config directory for SDK state and lazy publish,
  (4) submit on-chain USDC transactions (escrow lock/release, instant payments) via Base L2 RPC,
  (5) optionally run setup.sh to copy agent templates into the OpenClaw workspace directory.
  All on-chain transactions are gasless via Coinbase Paymaster (ERC-4337).
  Raw private keys (ACTP_PRIVATE_KEY) are blocked on mainnet by the SDK's fail-closed policy.
  No admin, root, or system-wide access required. No other skills or settings are modified.
```
