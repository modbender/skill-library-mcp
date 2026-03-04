# Enhanced Transactions API

Transforms raw Solana transactions into human-readable structured data.

**Note:** Uses a different base URL than the Wallet API: `https://api-mainnet.helius-rpc.com`

## Parse Transactions

`POST https://api-mainnet.helius-rpc.com/v0/transactions/?api-key=KEY`

Parse one or more transaction signatures into structured data.

### Request Body

```json
{ "transactions": ["sig1", "sig2"] }
```

### Response

```json
{
  "description": "Transfer 0.1 SOL to FXvSt...",
  "type": "TRANSFER",
  "source": "SYSTEM_PROGRAM",
  "fee": 5000,
  "feePayer": "M2mx9...",
  "signature": "5rfFL...",
  "slot": 171341028,
  "timestamp": 1674080473,
  "nativeTransfers": [
    { "fromUserAccount": "M2mx9...", "toUserAccount": "FXvSt...", "amount": 100000000 }
  ],
  "tokenTransfers": [],
  "events": {
    "sol": { "from": "M2mx9...", "to": "FXvSt...", "amount": 0.1 }
  }
}
```

Fields: `description` (human-readable summary), `type` (TRANSFER, SWAP, NFT_SALE, etc.), `source` (program), `nativeTransfers`, `tokenTransfers`, `events`.

---

## Enhanced Transaction History

`GET https://api-mainnet.helius-rpc.com/v0/addresses/{address}/transactions?api-key=KEY`

Returns enhanced parsed transactions for an address. Powered by `getTransactionsForAddress` RPC.

### Parameters

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| limit | int | 10 | Results per page (1-100) |
| before-signature | string | - | Pagination cursor (descending) |
| after-signature | string | - | Pagination cursor (ascending) |
| type | string | - | Filter: TRANSFER, SWAP, NFT_SALE, NFT_MINT, BURN, etc. |
| sort-order | string | desc | `asc` or `desc` |
| token-accounts | string | none | `none`, `balanceChanged` (recommended), `all` |
| commitment | string | finalized | `confirmed` or `finalized` |

### Time-Based Filtering

| Param | Description |
|-------|-------------|
| gt-time | After this Unix timestamp |
| gte-time | At or after this Unix timestamp |
| lt-time | Before this Unix timestamp |
| lte-time | At or before this Unix timestamp |

### Slot-Based Filtering

| Param | Description |
|-------|-------------|
| gt-slot | After this slot |
| gte-slot | At or after this slot |
| lt-slot | Before this slot |
| lte-slot | At or before this slot |

### Pagination

```javascript
let all = [], lastSig = null;
while (true) {
  let url = `https://api-mainnet.helius-rpc.com/v0/addresses/${addr}/transactions?api-key=${KEY}`;
  if (lastSig) url += `&before-signature=${lastSig}`;
  const txs = await (await fetch(url)).json();
  if (!Array.isArray(txs) || txs.length === 0) break;
  all.push(...txs);
  lastSig = txs[txs.length - 1].signature;
}
```

### Type Filter Continuation

When filtering by type, if no matches exist in current search window, API returns:
```json
{ "error": "Failed to find events within the search period. To continue search, query the API again with the `before-signature` parameter set to <sig>." }
```
Extract the signature from the error and retry with `before-signature=<sig>`.

### Network Support

- **Mainnet:** Unlimited retention
- **Devnet:** 2 weeks retention
- **Testnet:** Not supported
