# x402 Payment API Reference

**Purpose:** HTTP 402-gated file inscription to Solana
**Payment:** USDC or SOL
**Flow:** Quote → Pay → Inscribe → Download

## Overview

x402 enables paid data inscription to Solana. Files are chunked into transactions and stored permanently on-chain. Payment is required before inscription (HTTP 402 pattern).

## Flow

### 1. Quote

Request a price quote for inscribing data.

```
POST /quote
Content-Type: application/json

{
  "fileSize": 1024,        // bytes
  "fileName": "data.json",
  "paymentToken": "USDC"   // "USDC" or "SOL"
}
```

Response:
```json
{
  "quoteId": "q_abc123",
  "price": "0.05",
  "token": "USDC",
  "paymentAddress": "So1ana...addr",
  "expiresAt": "2026-01-30T12:00:00Z",
  "chunks": 4
}
```

### 2. Pay

Send the quoted amount to the provided payment address. Standard Solana transfer:

```typescript
import { Connection, PublicKey, Transaction, SystemProgram } from '@solana/web3.js';

// For SOL payment
const tx = new Transaction().add(
  SystemProgram.transfer({
    fromPubkey: wallet.publicKey,
    toPubkey: new PublicKey(quote.paymentAddress),
    lamports: Math.ceil(parseFloat(quote.price) * 1e9)
  })
);

const sig = await connection.sendTransaction(tx, [wallet]);
```

For USDC, use SPL token transfer to the payment address.

### 3. Inscribe

Submit payment proof to trigger inscription.

```
POST /inscribe
Content-Type: application/json

{
  "quoteId": "q_abc123",
  "paymentSignature": "5K7x...txsig"
}
```

Response:
```json
{
  "inscriptionId": "i_def456",
  "status": "processing",
  "txIds": ["tx1...", "tx2...", "tx3...", "tx4..."],
  "totalChunks": 4
}
```

The file is split into chunks that fit within Solana transaction size limits (~1232 bytes per tx). Each chunk is broadcast as a separate transaction.

### 4. Download

Reconstruct the file from on-chain chunks.

```
GET /download/:inscriptionId
```

Response: The original file, reassembled from on-chain transaction data.

### Status Check

```
GET /status/:inscriptionId
```

Response:
```json
{
  "inscriptionId": "i_def456",
  "status": "completed",
  "chunksConfirmed": 4,
  "totalChunks": 4,
  "txIds": ["tx1...", "tx2...", "tx3...", "tx4..."]
}
```

Status values: `processing`, `completed`, `failed`

## Cost Breakdown

- **Inscription fee** — Set by x402 service (covers chunk transaction fees + margin)
- **Solana tx fees** — ~0.000005 SOL per chunk transaction
- **Rent** — Not applicable (data stored in transaction logs, not accounts)

## Integration with IQDB

Use x402 for large data that doesn't fit in IQDB rows (which are PDA-constrained). IQDB stores structured metadata; x402 stores the raw file.

```javascript
// Store metadata in IQDB
const { createIQDB } = require('@iqlabsteam/iqdb');
const iqdb = createIQDB();

await iqdb.writeRow('files', JSON.stringify({
  name: 'report.pdf',
  inscId: 'i_def456',
  size: '102400'
}));

// Actual file data lives on-chain via x402
```

## Limitations

- Max file size depends on x402 service configuration
- Inscription is permanent — no deletion from Solana
- Payment is non-refundable once inscription starts
- Chunk transactions may fail individually — check status for confirmation
