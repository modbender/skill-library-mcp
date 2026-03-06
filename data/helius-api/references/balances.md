# Balances Endpoint

`GET /v1/wallet/{address}/balances?api-key=KEY`

Returns all token and NFT holdings with USD pricing, sorted by value descending.

## Parameters

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| page | int | 1 | Page number (1-indexed) |
| limit | int | 100 | Max tokens per page (1-100) |
| showZeroBalance | bool | false | Include zero-balance tokens |
| showNative | bool | true | Include native SOL |
| showNfts | bool | false | Include NFTs (max 100, first page only) |

## Response

```json
{
  "balances": [
    {
      "mint": "So11111111111111111111111111111111111111112",
      "symbol": "SOL",
      "name": "Solana",
      "balance": 1.5,
      "decimals": 9,
      "pricePerToken": 145.32,
      "usdValue": 217.98,
      "logoUri": "https://...",
      "tokenProgram": "spl-token"
    }
  ],
  "nfts": [
    {
      "mint": "...",
      "name": "Degen Ape #1234",
      "imageUri": "https://...",
      "collectionName": "Degen Ape Academy",
      "collectionAddress": "...",
      "compressed": false
    }
  ],
  "totalUsdValue": 1218.48,
  "pagination": { "page": 1, "limit": 100, "hasMore": true }
}
```

## Pagination

```javascript
let allBalances = [];
let page = 1;
let hasMore = true;
while (hasMore) {
  const res = await fetch(`https://api.helius.xyz/v1/wallet/${addr}/balances?api-key=${KEY}&page=${page}`);
  const data = await res.json();
  allBalances.push(...data.balances);
  hasMore = data.pagination.hasMore;
  page++;
}
```

Supports both `spl-token` and `token-2022` programs.
