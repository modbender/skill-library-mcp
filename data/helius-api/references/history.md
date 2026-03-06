# History Endpoint

`GET /v1/wallet/{address}/history?api-key=KEY`

Returns parsed transaction history with balance changes, newest first.

## Parameters

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| limit | int | 100 | Max transactions (1-100) |
| before | string | - | Cursor for next page (use `pagination.nextCursor`) |
| after | string | - | Fetch transactions after this signature |
| type | string | - | Filter: SWAP, TRANSFER, NFT_SALE, NFT_BID, NFT_LISTING, NFT_MINT, TOKEN_MINT, BURN, etc. |
| tokenAccounts | string | balanceChanged | `none` (direct only), `balanceChanged` (recommended, filters spam), `all` |

## Response

```json
{
  "data": [
    {
      "signature": "5wHu1...",
      "timestamp": 1704067200,
      "slot": 250000000,
      "fee": 0.000005,
      "feePayer": "86xCnP...",
      "error": null,
      "balanceChanges": [
        { "mint": "So111...112", "amount": -0.05, "decimals": 9 },
        { "mint": "EPjFW...t1v", "amount": 50.0, "decimals": 6 }
      ]
    }
  ],
  "pagination": { "hasMore": true, "nextCursor": "5wHu1..." }
}
```

## Pagination

```javascript
let all = [], before = null;
do {
  const url = `https://api.helius.xyz/v1/wallet/${addr}/history?api-key=${KEY}${before ? `&before=${before}` : ''}`;
  const data = await (await fetch(url)).json();
  all.push(...data.data);
  before = data.pagination.hasMore ? data.pagination.nextCursor : null;
} while (before);
```

## Transaction Types

SWAP, TRANSFER, NFT_SALE, NFT_BID, NFT_LISTING, NFT_MINT, NFT_CANCEL_LISTING, TOKEN_MINT, BURN, COMPRESSED_NFT_MINT, COMPRESSED_NFT_TRANSFER, COMPRESSED_NFT_BURN, CREATE_STORE, WHITELIST_CREATOR, INIT_STAKE, MERGE_STAKE, SPLIT_STAKE, EXECUTE_TRANSACTION
