# Funded By Endpoint

`GET /v1/wallet/{address}/funded-by?api-key=KEY`

Returns the original funding source (first incoming SOL transfer). Returns 404 if never funded.

## Response

```json
{
  "funder": "26MAyP...",
  "funderName": null,
  "funderType": null,
  "mint": "So111...112",
  "symbol": "SOL",
  "amount": 0.098,
  "amountRaw": "98119720",
  "decimals": 9,
  "date": "2022-01-19T20:46:34.000Z",
  "signature": "5WX9C5...",
  "timestamp": 1642625194,
  "slot": 116984883,
  "explorerUrl": "https://orbmarkets.io/tx/..."
}
```

## Fields

- `funder` — address that sent first SOL
- `funderName` — human-readable name if known entity
- `funderType` — category (e.g. "exchange", "defi-protocol")
- `amount` — initial SOL amount (human-readable)

Use cases: sybil detection (cluster wallets by funder), exchange attribution, compliance/AML, bot farm detection.
