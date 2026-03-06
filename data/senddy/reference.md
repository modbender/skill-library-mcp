# Senddy Node — API Reference

## `createSenddyAgent(config): SenddyClient`

Factory that returns a fully-configured `SenddyClient` for headless use.

### `SenddyAgentConfig`

```typescript
interface SenddyAgentConfig {
  seed: Uint8Array;            // 32-byte secret (REQUIRED)
  apiKey: string;              // Developer API key (REQUIRED)
  apiUrl?: string;             // API gateway base URL (default: 'https://www.senddy.com/api/v1')
  chainId?: number;            // Chain ID (default: 8453)
  rpcUrl?: string;             // JSON-RPC URL (default: 'https://mainnet.base.org')
  pool?: `0x${string}`;       // Pool contract (default: V3_CONTRACTS.Pool)
  usdc?: `0x${string}`;       // USDC address (default: SHARED_CONTRACTS.USDC)
  permit2?: `0x${string}`;    // Permit2 address (default: SHARED_CONTRACTS.Permit2)
  subgraphUrl?: string;        // Subgraph URL (default: V3_CONTRACTS.Subgraph[0])
  attestorUrl?: string;        // Override: direct attestor URL
  relayerUrl?: string;         // Override: direct relayer URL
  context?: string;            // Key derivation context (default: 'main')
  debug?: boolean;             // Debug logging (default: false)
}
```

## SenddyClient Methods

### Lifecycle

| Method | Signature | Description |
|--------|-----------|-------------|
| `init()` | `async init(): Promise<void>` | Derive keys, init storage, load WASM, first sync |
| `sync()` | `async sync(opts?): Promise<ClientSyncResult>` | Incremental state sync from subgraph |
| `destroy()` | `destroy(): void` | Zero keys, clean up resources |

### Balance & Identity

| Method | Signature | Description |
|--------|-----------|-------------|
| `getBalance()` | `async getBalance(): Promise<BalanceInfo>` | Current private balance |
| `getReceiveAddress()` | `getReceiveAddress(): string` | Bech32m receive address (`senddy1...`) |
| `getTransactions()` | `async getTransactions(opts?): Promise<TransactionRecord[]>` | Transaction history |

### Transfers

| Method | Signature | Description |
|--------|-----------|-------------|
| `transfer()` | `async transfer(to, amount, opts?): Promise<TransferResult>` | Full transfer (prove + attest + relay) |
| `prepareTransfer()` | `async prepareTransfer(to, amount, opts?): Promise<PreparedTransfer>` | Proof + attestation without submission |
| `submitTransfer()` | `async submitTransfer(prepared): Promise<TransferResult>` | Submit a prepared transfer |

### Withdrawals

| Method | Signature | Description |
|--------|-----------|-------------|
| `withdraw()` | `async withdraw(to, amount): Promise<WithdrawResult>` | Full withdrawal to public address |
| `prepareWithdraw()` | `async prepareWithdraw(to, amount, opts?): Promise<PreparedWithdraw>` | Proof + attestation without submission |
| `submitWithdraw()` | `async submitWithdraw(prepared): Promise<WithdrawResult>` | Submit a prepared withdrawal |

### Consolidation

| Method | Signature | Description |
|--------|-----------|-------------|
| `consolidate()` | `async consolidate(opts?): Promise<ConsolidationResult \| null>` | Merge fragmented notes |

### Events

| Method | Signature | Description |
|--------|-----------|-------------|
| `on()` | `on(event, callback): void` | Subscribe to events |
| `off()` | `off(event, callback): void` | Unsubscribe from events |

## Result Types

### `BalanceInfo`

```typescript
{
  shares: bigint;           // Raw share value (18 decimals)
  estimatedUSDC: bigint;    // USDC value (6 decimals)
  noteCount: number;        // Number of unspent notes
}
```

### `TransferResult`

```typescript
{
  txHash: `0x${string}`;
  shares: bigint;
  nullifierCount: number;
  circuit: 'spend' | 'spend9';
}
```

### `WithdrawResult`

```typescript
{
  txHash: `0x${string}`;
  shares: bigint;
  to: `0x${string}`;
  circuit: 'spend' | 'spend9';
}
```

### `ClientSyncResult`

```typescript
{
  newNotes: number;
  newSpent: number;
  unspentCount: number;
  durationMs: number;
}
```

### `ConsolidationResult`

```typescript
{
  txHash: `0x${string}`;
  notesConsolidated: number;
  totalShares: bigint;
  needsMore: boolean;
}
```

### `TransactionRecord`

```typescript
{
  id: string;
  type: 'deposit' | 'transfer_in' | 'transfer_out' | 'withdraw';
  shares: bigint;
  estimatedUSDC?: bigint;
  counterparty?: string;
  memo?: string;
  timestamp: number;
  status: 'confirmed' | 'pending';
}
```

### `TransferOptions`

```typescript
{
  memo?: string;         // Max 31 ASCII chars
  anonymous?: boolean;   // Hide sender identity
}
```

### `ConsolidationOptions`

```typescript
{
  noteThreshold?: number;  // Default: 16
  maxInputs?: number;      // Default: 9
}
```

## Event Types

```typescript
'balanceChange' -> BalanceInfo
'sync'          -> ClientSyncResult
'noteStrategy'  -> NoteStrategyEvent
'ready'         -> void
'error'         -> Error
```

`NoteStrategyEvent` variants:
- `{ type: 'trying-spend', inputCount }` — attempting standard circuit
- `{ type: 'escalating-to-spend9', reason }` — escalating to high-capacity circuit
- `{ type: 'auto-consolidating', noteCount, round }` — auto-consolidation triggered
- `{ type: 'consolidation-round-complete', notesConsolidated, remaining }`
- `{ type: 'strategy-complete', circuit }` — done

## Building Blocks (Advanced)

### `SeedKeyDeriver`

For custom key derivation without the full agent factory:

```typescript
import { SeedKeyDeriver } from '@senddy/node';

const kd = new SeedKeyDeriver({ seed, context: 'custom' });
await kd.deriveKeys();
console.log(kd.address);        // Virtual 0x address
console.log(kd.receiveAddress);  // senddy1... Bech32m address
kd.destroy();                    // Zero key material
```

### `RelayerSubmitter`

For custom transaction submission:

```typescript
import { RelayerSubmitter } from '@senddy/node';

const submitter = new RelayerSubmitter({
  publicClient,
  relayerUrl: 'https://senddy.com/api/v1',
  apiKey: 'sk_live_...',
  addresses: { pool, usdc, permit2 },
});
```

## Contract Addresses (Base Mainnet)

| Contract | Address |
|----------|---------|
| Pool (V3) | `0x0b4e0C18e4005363A10a93cb30e0a11A88bee648` |
| Attestor | `0xFa9b23627cd128325cae7300193B394746f09e22` |
| USDC | `0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913` |
| Permit2 | `0x000000000022D473030F116dDEE9F6B43aC78BA3` |

## Utility Exports

| Export | Source | Description |
|--------|--------|-------------|
| `toUSDC(n)` | `@senddy/client` | Convert human-readable USDC to 6-decimal bigint |
| `SHARED_CONTRACTS` | `@senddy/core` | Canonical shared contract addresses |
| `V3_CONTRACTS` | `@senddy/core` | V3-specific contract addresses |
| `encodeSenddyAddress(viewKey)` | `@senddy/core` | Encode a Bech32m Senddy address |
| `isValidSenddyAddress(addr)` | `@senddy/core` | Validate a Senddy address |
| `DEFAULT_API_URL` | `@senddy/node` | Default API gateway URL |
