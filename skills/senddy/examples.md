# Senddy Node — Examples

## 1. Persistent Daemon (Recommended for All Agents)

Run the agent as a long-lived process with a local HTTP API.
This is the **recommended pattern** — `init()` takes 5-15s due to WASM
compilation and subgraph sync, so you should only do it once.

```typescript
// senddy-daemon.ts
import { createSenddyAgent, toUSDC, isValidSenddyAddress } from '@senddy/node';
import { createServer } from 'node:http';

const agent = createSenddyAgent({
  seed: Buffer.from(process.env.AGENT_SEED_HEX!, 'hex'),
  apiKey: process.env.SENDDY_API_KEY!,
});

console.log('Initializing agent (this takes 5-15s on first run)...');
await agent.init();
console.log(`Agent ready: ${agent.getReceiveAddress()}`);

// Background sync every 30s
setInterval(() => agent.sync().catch(console.error), 30_000);

function serializeBigInts(obj: any): any {
  if (typeof obj === 'bigint') return obj.toString();
  if (Array.isArray(obj)) return obj.map(serializeBigInts);
  if (obj && typeof obj === 'object') {
    return Object.fromEntries(
      Object.entries(obj).map(([k, v]) => [k, serializeBigInts(v)])
    );
  }
  return obj;
}

const server = createServer(async (req, res) => {
  if (req.method !== 'POST') { res.writeHead(405); res.end(); return; }

  const chunks: Buffer[] = [];
  for await (const chunk of req) chunks.push(chunk as Buffer);
  const { method, params } = JSON.parse(Buffer.concat(chunks).toString());

  try {
    let result: any;
    switch (method) {
      case 'getBalance':    result = await agent.getBalance(); break;
      case 'getAddress':    result = { address: agent.getReceiveAddress() }; break;
      case 'transfer':      result = await agent.transfer(params.to, toUSDC(params.amount), params.opts); break;
      case 'withdraw':      result = await agent.withdraw(params.to, toUSDC(params.amount)); break;
      case 'sync':          result = await agent.sync(); break;
      case 'getTransactions': result = await agent.getTransactions(params); break;
      default:
        res.writeHead(400, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({ error: `Unknown method: ${method}` }));
        return;
    }
    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({ ok: true, result: serializeBigInts(result) }));
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

Start it once in the background. It picks a free port automatically
(or set `SENDDY_DAEMON_PORT` to pin one):
```bash
AGENT_SEED_HEX="..." SENDDY_API_KEY="sk_live_..." npx tsx senddy-daemon.ts &
# Output: "Senddy daemon on :18790"  (port varies)
```

Query it from any script or agent (instant responses — use the port from stdout):
```bash
curl -s -X POST http://127.0.0.1:18790 -d '{"method":"getBalance"}' | jq
curl -s -X POST http://127.0.0.1:18790 -d '{"method":"transfer","params":{"to":"senddy1...","amount":"5.00"}}' | jq
```

## 2. Payment Bot

A bot that checks for incoming transfers and logs them:

```typescript
import { createSenddyAgent, toUSDC } from '@senddy/node';

const agent = createSenddyAgent({
  seed: Buffer.from(process.env.AGENT_SEED_HEX!, 'hex'),
  apiKey: process.env.SENDDY_API_KEY!,
});

await agent.init();
console.log('Bot address:', agent.getReceiveAddress());

let lastBalance = (await agent.getBalance()).estimatedUSDC;

// Poll for new transfers every 30 seconds
setInterval(async () => {
  await agent.sync();
  const balance = await agent.getBalance();

  if (balance.estimatedUSDC > lastBalance) {
    const received = balance.estimatedUSDC - lastBalance;
    console.log(`Received ${Number(received) / 1_000_000} USDC`);
  }

  lastBalance = balance.estimatedUSDC;
}, 30_000);
```

## 3. Tipping Agent

Send small tips to Senddy addresses:

```typescript
import { createSenddyAgent, toUSDC, isValidSenddyAddress } from '@senddy/node';

const agent = createSenddyAgent({
  seed: Buffer.from(process.env.AGENT_SEED_HEX!, 'hex'),
  apiKey: process.env.SENDDY_API_KEY!,
});

await agent.init();

async function sendTip(recipient: string, amountUSDC: string, memo?: string) {
  if (!isValidSenddyAddress(recipient)) {
    throw new Error(`Invalid Senddy address: ${recipient}`);
  }

  const balance = await agent.getBalance();
  const amount = toUSDC(amountUSDC);

  if (balance.estimatedUSDC < amount) {
    throw new Error(`Insufficient balance: ${balance.estimatedUSDC} < ${amount}`);
  }

  const result = await agent.transfer(recipient, amount, { memo });
  console.log(`Tipped ${amountUSDC} USDC -> ${recipient} (tx: ${result.txHash})`);
  return result;
}

await sendTip('senddy1qw508d6q...', '1.00', 'Great work!');
```

## 4. Treasury Agent (Scheduled Withdrawal)

Consolidate notes and withdraw to a public address on a schedule:

```typescript
import { createSenddyAgent, toUSDC } from '@senddy/node';

const agent = createSenddyAgent({
  seed: Buffer.from(process.env.TREASURY_SEED_HEX!, 'hex'),
  apiKey: process.env.SENDDY_API_KEY!,
  context: 'treasury',
});

await agent.init();

async function sweepToTreasury(publicAddress: `0x${string}`, minAmount: string) {
  await agent.sync();
  const balance = await agent.getBalance();
  const threshold = toUSDC(minAmount);

  if (balance.estimatedUSDC < threshold) {
    console.log(`Balance ${balance.estimatedUSDC} below threshold ${threshold}, skipping`);
    return;
  }

  // Consolidate fragmented notes first
  if (balance.noteCount > 8) {
    console.log(`Consolidating ${balance.noteCount} notes...`);
    await agent.consolidate({ noteThreshold: 8 });
    await agent.sync();
  }

  // Withdraw everything minus a small reserve
  const reserve = toUSDC('10.00');
  const withdrawAmount = balance.estimatedUSDC - reserve;

  if (withdrawAmount > 0n) {
    const result = await agent.withdraw(publicAddress, withdrawAmount);
    console.log(`Withdrew ${Number(withdrawAmount) / 1_000_000} USDC (tx: ${result.txHash})`);
  }
}

await sweepToTreasury('0xYourPublicTreasury...', '100.00');
```

## 5. Multi-Agent Setup (Department Wallets)

Multiple wallets from a single master seed:

```typescript
import { createSenddyAgent, toUSDC } from '@senddy/node';

const masterSeed = Buffer.from(process.env.MASTER_SEED_HEX!, 'hex');
const apiKey = process.env.SENDDY_API_KEY!;

const agents = {
  operations: createSenddyAgent({ seed: masterSeed, apiKey, context: 'ops' }),
  payroll:    createSenddyAgent({ seed: masterSeed, apiKey, context: 'payroll' }),
  grants:    createSenddyAgent({ seed: masterSeed, apiKey, context: 'grants' }),
};

// Initialize all agents
await Promise.all(Object.values(agents).map(a => a.init()));

// Each has a unique receive address
for (const [name, agent] of Object.entries(agents)) {
  const balance = await agent.getBalance();
  console.log(`${name}: ${agent.getReceiveAddress()} (${balance.estimatedUSDC} USDC)`);
}

// Transfer from operations to payroll
await agents.operations.transfer(
  agents.payroll.getReceiveAddress(),
  toUSDC('500.00'),
  { memo: 'Feb payroll' }
);
```

## 6. Event-Driven Agent

React to balance changes in real-time:

```typescript
import { createSenddyAgent } from '@senddy/node';

const agent = createSenddyAgent({
  seed: Buffer.from(process.env.AGENT_SEED_HEX!, 'hex'),
  apiKey: process.env.SENDDY_API_KEY!,
});

agent.on('balanceChange', (balance) => {
  console.log(`Balance: ${Number(balance.estimatedUSDC) / 1_000_000} USDC (${balance.noteCount} notes)`);
});

agent.on('noteStrategy', (event) => {
  if (event.type === 'auto-consolidating') {
    console.log(`Auto-consolidating ${event.noteCount} notes (round ${event.round})`);
  }
});

agent.on('error', (err) => {
  console.error('Agent error:', err);
});

await agent.init();

// Keep the process alive, syncing periodically
const SYNC_INTERVAL_MS = 60_000;
setInterval(() => agent.sync().catch(console.error), SYNC_INTERVAL_MS);
```

## 7. Prepare/Submit Pattern (Two-Phase Transfer)

Separate proof generation from submission (useful for approval flows):

```typescript
import { createSenddyAgent, toUSDC } from '@senddy/node';

const agent = createSenddyAgent({
  seed: Buffer.from(process.env.AGENT_SEED_HEX!, 'hex'),
  apiKey: process.env.SENDDY_API_KEY!,
});

await agent.init();

// Phase 1: Generate proof + get attestation (can take 5-30s)
const prepared = await agent.prepareTransfer(
  'senddy1...recipient',
  toUSDC('25.00'),
  { memo: 'Invoice #42' }
);

console.log(`Proof ready (circuit: ${prepared.circuit})`);

// ... approval logic, logging, etc. ...

// Phase 2: Submit the transaction (fast — just relay + confirm)
const result = await agent.submitTransfer(prepared);
console.log(`Submitted: ${result.txHash}`);
```

## 8. Seed Management

Generate and persist seeds securely:

```typescript
import { randomBytes } from 'node:crypto';
import { writeFileSync, readFileSync } from 'node:fs';

// Generate a new seed
function generateSeed(): Uint8Array {
  return randomBytes(32);
}

// Save seed to an encrypted file (use your own encryption)
function saveSeed(seed: Uint8Array, path: string) {
  writeFileSync(path, Buffer.from(seed).toString('hex'), { mode: 0o600 });
}

// Load seed from file
function loadSeed(path: string): Uint8Array {
  const hex = readFileSync(path, 'utf-8').trim();
  return Buffer.from(hex, 'hex');
}

// Usage:
const seed = generateSeed();
saveSeed(seed, '.senddy-seed');
// Later:
const loaded = loadSeed('.senddy-seed');
```

**Important**: Never commit seeds to version control. Use environment
variables, secret managers (AWS Secrets Manager, Vault), or encrypted files.
