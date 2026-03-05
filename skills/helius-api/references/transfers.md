# Transfers Endpoint

`GET /v1/wallet/{address}/transfers?api-key=KEY`

Returns token transfer activity with sender/recipient info.

## Parameters

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| limit | int | 50 | Max transfers (1-100) |
| cursor | string | - | Pagination cursor from `pagination.nextCursor` |

## Response

```json
{
  "data": [
    {
      "signature": "5wHu1...",
      "timestamp": 1704067200,
      "direction": "in",
      "counterparty": "HXsKP7...",
      "mint": "So111...112",
      "symbol": "SOL",
      "amount": 1.5,
      "amountRaw": "1500000000",
      "decimals": 9
    }
  ],
  "pagination": { "hasMore": true, "nextCursor": "..." }
}
```

## Direction

- `in` — tokens received; `counterparty` is the sender
- `out` — tokens sent; `counterparty` is the recipient
