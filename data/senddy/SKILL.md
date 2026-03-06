---
name: senddy
description: Create and manage private stablecoin wallets using Senddy's zero-knowledge protocol on Base. Use when building payment agents, bots, server-side apps, or any system that needs private USDC transfers. Covers @senddy/node for headless agents and @senddy/client for browser apps.
metadata: {"openclaw":{"requires":{"env":["SENDDY_API_KEY","AGENT_SEED_HEX"]},"primaryEnv":"SENDDY_API_KEY","emoji":"🛡️","homepage":"https://senddy.com"}}
---

# Senddy Private Wallet

Build private stablecoin wallets with zero-knowledge proofs on Base.
Senddy lets agents and apps hold, transfer, and withdraw USDC privately —
no public on-chain linkage between deposits, transfers, and withdrawals.

## Quick Start (Headless Agent)

**5 steps to a working private wallet:**

```bash
npm install @senddy/node
```

```typescript
import { createSenddyAgent, toUSDC } from '@senddy/node';
import { randomBytes } from 'node:crypto';

// 1. Generate a seed (store this securely — it controls the wallet)
const seed = randomBytes(32);

// 2. Create the agent (only seed + apiKey required)
const agent = createSenddyAgent({
  seed,
  apiKey: process.env.SENDDY_API_KEY!,
});

// 3. Initialize (derives keys, loads WASM prover, first sync)
await agent.init();

// 4. Get your receive address
console.log('Address:', agent.getReceiveAddress()); // senddy1...

// 5. Check balance, transfer, withdraw
const balance = await agent.getBalance();
await agent.transfer('senddy1...recipient', toUSDC('5.00'));
await agent.withdraw('0xPublicAddress...', toUSDC('10.00'));
```

Set `SENDDY_API_KEY` in your environment. Get one at https://senddy.com.

## Configuration

### Minimal Config (recommended)

Only `seed` and `apiKey` are required. Everything else defaults to the
canonical Base mainnet deployment:

```typescript
createSenddyAgent({
  seed: Uint8Array,        // 32-byte secret (REQUIRED)
  apiKey: string,          // 'sk_live_...' (REQUIRED)
})
```

### Full Config (overrides)

```typescript
createSenddyAgent({
  seed: Uint8Array,
  apiKey: string,
  apiUrl: string,          // default: 'https://senddy.com/api/v1'
  chainId: number,         // default: 8453 (Base)
  rpcUrl: string,          // default: 'https://mainnet.base.org'
  pool: '0x...',           // default: canonical pool
  usdc: '0x...',           // default: canonical USDC
  permit2: '0x...',        // default: canonical Permit2
  subgraphUrl: string,     // default: canonical subgraph
  attestorUrl: string,     // override: bypass API gateway for attestor
  relayerUrl: string,      // override: bypass API gateway for relayer
  context: string,         // default: 'main' (for multi-agent from one seed)
  debug: boolean,          // default: false
})
```

### What the API Key Gates

The `apiKey` authenticates all requests through the Senddy API gateway:
- **Attestor** — ZK proof verification (TEE-based, off-chain)
- **Relayer** — Gas-sponsored transaction submission (you don't pay gas)
- **Usernames** — Resolve `senddy1...` addresses to human-readable names
- **Merkle tree** — Proof generation helper endpoints

## Operations

### Balance

```typescript
const balance = await agent.getBalance();
// { shares: bigint, estimatedUSDC: bigint, noteCount: number }
```

`estimatedUSDC` is in 6-decimal USDC units. `shares` are 18-decimal internal units.

### Transfer

```typescript
// Simple transfer
const result = await agent.transfer('senddy1...', toUSDC('25.00'));
// { txHash, shares, nullifierCount, circuit: 'spend' | 'spend9' }

// With memo (max 31 ASCII chars)
await agent.transfer('senddy1...', toUSDC('5.00'), { memo: 'Payment' });

// Anonymous (hide sender identity)
await agent.transfer('senddy1...', toUSDC('5.00'), { anonymous: true });
```

Auto-escalation: tries `spend` circuit (3 inputs), escalates to `spend9`
(9 inputs), and auto-consolidates if neither suffices.

### Withdraw

Withdraw to a public Ethereum address (USDC leaves the privacy pool):

```typescript
const result = await agent.withdraw('0x...', toUSDC('50.00'));
// { txHash, shares, to, circuit }
```

### Sync

State is synced automatically on `init()`. For long-running agents:

```typescript
// Manual sync
const result = await agent.sync();
// { newNotes, newSpent, unspentCount, durationMs }
```

### Consolidation

When notes fragment (many small UTXOs), consolidate them:

```typescript
const result = await agent.consolidate({ noteThreshold: 16 });
// { txHash, notesConsolidated, totalShares, needsMore }
```

### Receive Address

```typescript
const address = agent.getReceiveAddress(); // 'senddy1qw508d6q...'
```

Share this address to receive private transfers. It's derived from
your viewing public key and is deterministic for a given seed + context.

### Transaction History

```typescript
const txs = await agent.getTransactions({ limit: 50 });
// Array<{ id, type, shares, estimatedUSDC, counterparty, memo, timestamp, status }>
```

### Events

```typescript
agent.on('balanceChange', (balance) => { /* ... */ });
agent.on('sync', (result) => { /* ... */ });
agent.on('noteStrategy', (event) => { /* escalation/consolidation info */ });
agent.on('error', (err) => { /* ... */ });
```

## Multiple Agents from One Seed

Use the `context` parameter to derive different wallets from the same seed:

```typescript
const treasury = createSenddyAgent({ seed, apiKey, context: 'treasury' });
const payroll  = createSenddyAgent({ seed, apiKey, context: 'payroll' });
const tips     = createSenddyAgent({ seed, apiKey, context: 'tips' });
```

Each context produces different keys and a different receive address.

## Amounts

Always use `toUSDC()` to convert human-readable amounts:

```typescript
import { toUSDC } from '@senddy/node';

toUSDC('1.00')     // 1_000_000n
toUSDC('100')      // 100_000_000n
toUSDC('0.01')     // 10_000n
toUSDC(50)         // 50_000_000n
```

Raw amounts are in USDC's 6-decimal format (`bigint`).

## Address Validation

```typescript
import { isValidSenddyAddress } from '@senddy/node';

isValidSenddyAddress('senddy1qw508d6q...');  // true
isValidSenddyAddress('0x...');                // false
```

## Contract Addresses

```typescript
import { SHARED_CONTRACTS, V3_CONTRACTS } from '@senddy/node';

SHARED_CONTRACTS.USDC     // '0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913'
SHARED_CONTRACTS.Permit2  // '0x000000000022D473030F116dDEE9F6B43aC78BA3'
V3_CONTRACTS.Pool         // '0x0b4e0C18e4005363A10a93cb30e0a11A88bee648'
```

## Cleanup

```typescript
agent.destroy(); // Zeros key material and cleans up resources
```

Always call `destroy()` when done (especially in short-lived processes).

## CRITICAL: Run as a Persistent Process

**Do NOT create a new agent and call `init()` on every request.** The `init()`
call takes 5-15 seconds because it compiles WASM, loads the SRS into memory,
and syncs the full state from the subgraph. Re-initializing on every request
will make the agent unusably slow.

Instead, run the agent as a **long-lived background process** that initializes
once and handles requests over a local HTTP API or Unix socket:

```typescript
// senddy-daemon.ts — run once, stays alive forever
import { createSenddyAgent, toUSDC, isValidSenddyAddress } from '@senddy/node';
import { createServer } from 'node:http';

const agent = createSenddyAgent({
  seed: Buffer.from(process.env.AGENT_SEED_HEX!, 'hex'),
  apiKey: process.env.SENDDY_API_KEY!,
});

await agent.init();
console.log(`Agent ready: ${agent.getReceiveAddress()}`);

// Periodic sync to stay up-to-date
setInterval(() => agent.sync().catch(console.error), 30_000);

// Simple JSON-RPC over HTTP
const server = createServer(async (req, res) => {
  if (req.method !== 'POST') { res.writeHead(405); res.end(); return; }

  const chunks: Buffer[] = [];
  for await (const chunk of req) chunks.push(chunk as Buffer);
  const { method, params } = JSON.parse(Buffer.concat(chunks).toString());

  try {
    let result: any;
    switch (method) {
      case 'getBalance':
        result = await agent.getBalance();
        result = { ...result, shares: result.shares.toString(), estimatedUSDC: result.estimatedUSDC.toString() };
        break;
      case 'getAddress':
        result = { address: agent.getReceiveAddress() };
        break;
      case 'transfer':
        result = await agent.transfer(params.to, toUSDC(params.amount), params.opts);
        result = { ...result, shares: result.shares.toString() };
        break;
      case 'withdraw':
        result = await agent.withdraw(params.to, toUSDC(params.amount));
        result = { ...result, shares: result.shares.toString() };
        break;
      case 'sync':
        result = await agent.sync();
        break;
      case 'getTransactions':
        result = await agent.getTransactions(params);
        break;
      default:
        res.writeHead(400);
        res.end(JSON.stringify({ error: `Unknown method: ${method}` }));
        return;
    }
    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({ ok: true, result }));
  } catch (err: any) {
    res.writeHead(500, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({ ok: false, error: err.message }));
  }
});

const PORT = parseInt(process.env.SENDDY_DAEMON_PORT ?? '0');
server.listen(PORT, '127.0.0.1', () => {
  const addr = server.address() as import('node:net').AddressInfo;
  console.log(`Senddy daemon on :${addr.port}`);
});
```

Start the daemon once. It picks a free port automatically (or set
`SENDDY_DAEMON_PORT` to pin one). Read the port from stdout and use it
for all subsequent requests:

```bash
AGENT_SEED_HEX="your64charhex..." SENDDY_API_KEY="sk_live_..." \
  npx tsx senddy-daemon.ts
# Output: "Senddy daemon on :18790"  (port varies)
```

Then query it instantly from any client:
```bash
# Check balance (use the port printed at startup)
curl -s -X POST http://127.0.0.1:18790 \
  -d '{"method":"getBalance"}' | jq

# Transfer
curl -s -X POST http://127.0.0.1:18790 \
  -d '{"method":"transfer","params":{"to":"senddy1...","amount":"5.00"}}' | jq
```

For a complete daemon example with process management, see [examples.md](examples.md).

## Gotchas

- **No deposits**: Agents can't deposit directly. Fund them by sending a
  private transfer from a funded wallet (browser app or another agent).
- **In-memory storage**: Notes are lost on process restart. The agent re-syncs
  from the subgraph on `init()`, so this is safe — just costs a few seconds.
- **First init downloads SRS**: The first `init()` downloads a ~16 MB
  structured reference string (cached to `~/.bb-crs/` for subsequent runs).
- **WASM compilation**: Even with cached SRS, `init()` takes 5-15s to compile
  the WASM prover. Always run the agent persistently, not per-request.
- **Shares vs USDC**: Internal values are in 18-decimal shares. Use
  `balance.estimatedUSDC` and `toUSDC()` for human-readable amounts.

## Additional Resources

- For full type signatures and advanced composition, see [reference.md](reference.md)
- For copy-paste usage examples, see [examples.md](examples.md)