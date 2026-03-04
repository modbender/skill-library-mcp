# IQDB Core SDK Reference

## New Official SDK (2026-02-08)

**Package:** `@iqlabs-official/solana-sdk` (v0.1.1, published 2026-02-08 by Zo)
**Program ID (mainnet):** `9KLLchQVJpGkw4jPuUmnvqESdR7mtNCYr3qS4iQLabs`
**Runtime:** Node.js 18+ (CJS and ESM)

### Setup
```javascript
const { writer, reader, setRpcUrl, contract } = require('@iqlabs-official/solana-sdk');
setRpcUrl('https://api.mainnet-beta.solana.com');
```

### Key API Changes from Old SDK
- No wrapper object — functions are direct imports: `writer.writeRow()`, `reader.readTableRows()`, etc.
- `writeRow(connection, signer, dbRootId, tableSeed, rowJson)` — takes connection and signer explicitly
- `readTableRows(accountPubkey, options?)` — read rows from a table PDA
- `getTablelistFromRoot(connection, dbRootId)` — list all tables
- `codeIn({connection, signer}, data)` — raw data storage (auto-creates User State PDA)
- `readCodeIn(txSignature, speed?)` — retrieve stored data
- Connection system: `requestConnection()`, `readConnection()`, `fetchUserConnections()`, `writeConnectionRow()`
- User State PDAs auto-created on first `codeIn()` call

### Root and Table Initialization (Low-level)
The new SDK does NOT have high-level `ensureRoot()` or `ensureTable()`. Use contract instructions directly:
```javascript
const { contract } = require('@iqlabs-official/solana-sdk');
const { sendTx } = require('@iqlabs-official/solana-sdk/dist/sdk/writer/writer_utils');
const { toSeedBytes } = require('@iqlabs-official/solana-sdk/dist/sdk/utils/seed');
const IDL = require('@iqlabs-official/solana-sdk/idl/code_in.json');

// Monkey-patch for Node v24 Buffer compatibility
const seedModule = require('@iqlabs-official/solana-sdk/dist/sdk/utils/seed');
const origFn = seedModule.toSeedBytes;
seedModule.toSeedBytes = (v) => Buffer.from(origFn(v));

const programId = new PublicKey(contract.DEFAULT_ANCHOR_PROGRAM_ID);
const builder = contract.createInstructionBuilder(IDL, programId);
const dbRootSeed = Buffer.from(toSeedBytes('my-db-root'));
const dbRoot = contract.getDbRootPda(dbRootSeed, programId);

// Initialize root
const ix = contract.initializeDbRootInstruction(builder, {
  db_root: dbRoot, signer: signer.publicKey, system_program: SystemProgram.programId
}, { db_root_id: dbRootSeed });
await sendTx(connection, signer, ix);

// Create table
const tableSeed = Buffer.from(toSeedBytes('my_table'));
const tablePda = contract.getTablePda(dbRoot, tableSeed, programId);
const instructionTablePda = contract.getInstructionTablePda(dbRoot, tableSeed, programId);
const createTableIx = contract.createTableInstruction(builder, {
  db_root: dbRoot, receiver: feeReceiver, signer: signer.publicKey,
  table: tablePda, instruction_table: instructionTablePda, system_program: SystemProgram.programId
}, {
  db_root_id: dbRootSeed, table_seed: tableSeed,
  table_name: Buffer.from('my_table', 'utf8'),
  column_names: ['col1', 'col2'].map(c => Buffer.from(c, 'utf8')),
  id_col: Buffer.from('col1', 'utf8'), ext_keys: [],
  gate_mint_opt: null, writers_opt: null
});
await sendTx(connection, signer, createTableIx);
```

### Known Gotchas
- **Buffer bug (Node v24):** SDK's `toSeedBytes()` returns `Uint8Array` but Anchor Borsh needs `Buffer` for `[u8; 32]` fields. Monkey-patch `seedModule.toSeedBytes` to wrap in `Buffer.from()`.
- **Mainnet RPC rate limits:** Public RPC (`api.mainnet-beta.solana.com`) throttles at 5+ rapid transactions. Add 2-3s delays between writes. Use Helius for production.
- **Program ID differs from local pre-release:** Published SDK = `9KLLchQVJpGkw4jPuUmnvqESdR7mtNCYr3qS4iQLabs`. Local dev repo had `7dL1jKd4CaFHQRV2SU23XJtSCrPXaLpEbq9FteRXup8v`. Old SDK (`@iqlabsteam/iqdb`) used `7Vk5JJDxUBAaaAkpYQpWYCZNz4SVPm3mJFSxrBzTQuAX` (now closed on mainnet).
- **Root + table creation costs ~0.01-0.02 SOL each** due to PDA rent. Budget accordingly.
- **Old SDK (`@iqlabsteam/iqdb`) still works on devnet** but its program is closed on mainnet. Use new SDK for mainnet.

### Cost Estimates (Mainnet)
| Operation | Approximate Cost |
|-----------|-----------------|
| Initialize DB Root | ~0.01 SOL (rent) |
| Create Table | ~0.02 SOL (rent) |
| Write Row | ~0.005-0.01 SOL |
| Read | Free |

---

## Legacy SDK Reference (`@iqlabsteam/iqdb`)

**Package:** `@iqlabsteam/iqdb`
**GitHub:** github.com/IQCoreTeam
**Runtime:** Node.js 18+ (CommonJS only — ESM not supported)

## Setup

```javascript
// Set env vars BEFORE importing the SDK
process.env.NETWORK_URL = process.env.ANCHOR_PROVIDER_URL || 'https://api.devnet.solana.com';

const { createIQDB } = require('@iqlabsteam/iqdb');
const iqdb = createIQDB();
```

### Required Environment Variables
```bash
ANCHOR_WALLET=/path/to/solana/keypair.json
ANCHOR_PROVIDER_URL=https://api.devnet.solana.com
NETWORK_URL=https://api.devnet.solana.com  # Must match ANCHOR_PROVIDER_URL
```

**RPC Note:** The standard `api.devnet.solana.com` aggressively rate-limits and may return 403 errors. The SDK has a built-in Helius devnet RPC as fallback. For reliable development, use a dedicated RPC or omit `NETWORK_URL` to use the SDK default. If setting a custom `ANCHOR_PROVIDER_URL`, always set `NETWORK_URL` to the same value.

## Writer Methods

### `ensureRoot()`
Initialize the root PDA for the connected wallet. Idempotent — safe to call multiple times.

```javascript
await iqdb.ensureRoot();
```

### `ensureTable(tableName, columns, idCol)`
Create a table if it doesn't exist. **Preferred over `createTable`** — idempotent.

```javascript
await iqdb.ensureTable('users', ['name', 'email', 'role'], 'name');
```

- `tableName` — Table identifier. Must be unique per root.
- `columns` — Array of column names.
- `idCol` — The column that serves as the row identifier.

### `createTable(tableName, columns, idCol?, extKeys?)`
Create a new table. **Fails if table already exists** — use `ensureTable` instead.

```javascript
const result = await iqdb.createTable('users', ['name', 'email'], 'name');
// result: { initialized, initSignature, createSignature, root, table }
```

### `writeRow(tableName, jsonString)`
Write a new row to a table. **Data must be a JSON string, not an object.**

```javascript
await iqdb.writeRow('users', JSON.stringify({
  name: 'Bob', email: 'bob@example.com', role: 'admin'
}));
```

- All values stored as strings.
- Append-only — each call creates a new transaction.
- **Row JSON must be under ~100 bytes** or the on-chain program rejects with `TxTooLong`.

### `pushInstruction(tableName, targetTxSig, beforeStr, afterStr)`
Update or delete an existing row by referencing its transaction signature.

```javascript
// Update: provide before and after JSON strings
await iqdb.pushInstruction('users', txSignature,
  JSON.stringify({ name: 'Bob', role: 'admin' }),
  JSON.stringify({ name: 'Bob', role: 'superadmin' })
);

// Delete: provide empty string as afterStr
await iqdb.pushInstruction('users', txSignature,
  JSON.stringify({ name: 'Bob' }),
  ''
);
```

**Important:** `pushInstruction` writes to a separate instruction log — it does NOT modify the original row data. `readRowsByTable` returns raw rows without applying instructions. To get the full picture, use `searchTableByName` which returns both `rows` (raw) and `instruRows`/`targetContent` (instruction corrections). Your application is responsible for applying corrections on top of raw rows.

To get a tx signature for targeting, use `searchTableByName` and inspect the `sigMap` keys.

### `createExtTable(baseTable, rowId, extKey, columns, idCol?, extKeysForExt?)`
Create an extension (child) table linked to a parent table row.

```javascript
await iqdb.createExtTable('users', 'Bob', 'sessions',
  ['session_id', 'timestamp'], 'session_id');
```

### `ensureExtTable(baseTable, rowId, extKey, columns, idCol)`
Idempotent version of `createExtTable`.

```javascript
await iqdb.ensureExtTable('users', 'Bob', 'sessions',
  ['session_id', 'timestamp'], 'session_id');
```

### `updateTableList(tableNames)`
Update the root PDA's table name list.

```javascript
await iqdb.updateTableList(['users', 'sessions', 'logs']);
```

### `updateTable(tableName, columns, idCol?, extKeys?)`
Update an existing table's column schema or extension keys.

```javascript
await iqdb.updateTable('users', ['name', 'email', 'role', 'status'], 'name');
```

## Reader Methods

### `readRowsByTable({ userPubkey, tableName, maxTx?, perTableLimit? })`
Read all rows from a table. Free RPC call.

```javascript
const rows = await iqdb.readRowsByTable({
  userPubkey: 'BtErPc3vB64wg2edmXf5byTRCjHBf3ezNFaYsCyEeJZT',
  tableName: 'users'
});
// Returns: [{ name: 'Bob', email: 'bob@example.com', role: 'admin' }, ...]
```

### `listRootTables()`
List all tables in the root PDA.

```javascript
const tables = await iqdb.listRootTables();
// Returns: [{ name: 'users', seedHex: '...' }, ...]
```

### `readTableMeta(tableName)`
Read table metadata (columns, ID column, extension keys).

```javascript
const meta = await iqdb.readTableMeta('users');
// Returns: { columns: ['name', 'email', 'role'], idCol: 'name', extKeys: [] }
```

### `searchTableByName({ userPubkey, tableName, maxTx? })`
Full table search with instruction history, signature maps, and extension data.

```javascript
const result = await iqdb.searchTableByName({
  userPubkey: 'YOUR_PUBKEY',
  tableName: 'users'
});
// Returns: { tableName, columns, rows, instruRows, sigContentRows, ... }
```

### `getTableColumns({ userPubkey, tableName })`
Get just the column names for a table.

```javascript
const { columns } = await iqdb.getTableColumns({
  userPubkey: 'YOUR_PUBKEY',
  tableName: 'users'
});
```

## Rolling Hash System

Every write operation extends a keccak hash chain:

```
hash_n = keccak256(domain || hash_{n-1} || tx_data)
```

- **Domain:** Table-specific namespace to prevent cross-table collision
- **Tamper detection:** Any modification to historical data breaks the chain
- **Verification:** Replay all transactions and compare final hash

## Cost Estimates

| Operation | Approximate Cost |
|-----------|-----------------|
| Root PDA init | ~0.002 SOL (rent) |
| Create table | ~0.001 SOL (rent) |
| Write row | ~0.001 SOL (rent) |
| Update/Delete (pushInstruction) | TX fee only (~0.000005 SOL) |
| Read | Free |

100 tables ~ 0.012 SOL total rent.

## Error Handling

Common errors:
- `TxTooLong` — Row JSON exceeds on-chain size limit. Shorten data.
- `Table PDA not found` — Table doesn't exist or `NETWORK_URL` points to wrong RPC.
- `account already in use` — Table already exists. Use `ensureTable` instead of `createTable`.
- `ANCHOR_WALLET is not set` — Set the environment variable before importing the SDK.
- `ColumnMismatch` — Row data keys don't match table schema.
