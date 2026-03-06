# SplitXCH API Reference

## POST https://splitxch.com/api/compute/fast

Create a split address from recipients. Returns the computed XCH address.

### Request
```json
{
  "recipients": [
    {
      "name": "Artist",
      "address": "xch1...",
      "points": 4925,
      "id": 1
    },
    {
      "name": "Manager",
      "address": "xch1...",
      "points": 4925,
      "id": 2
    }
  ]
}
```

### Key Rules
- **Basis points**: 10,000 = 100%. Platform fee is 150 bps (1.5%).
- Recipient points must sum to **9,850** (10,000 minus 150 fee).
- Up to **128 recipients** per split. For more, use cascading splits.
- All addresses must be valid XCH addresses (start with `xch1`).
- All addresses must be unique within a single split.
- Each recipient's points must be > 0.

### Response
```json
{
  "id": "66f21c17eb854b8fab7327280ac5eb21",
  "message": "Saved",
  "pctProgress": 100,
  "address": "xch1q3ge2z5g5fsk4ckkunmszwlhpcmgns7c5y5gwku86tdsa4wfhg6qszeuzg"
}
```

### Errors
HTTP 400 with `message` field describing the validation failure.

## GET https://splitxch.com/api/compute/{id}

Check status of a previously created split.

### Response
```json
{
  "address": "xch1...",
  "error": false,
  "id": "...",
  "message": "Complete",
  "pctProgress": 100
}
```

## Cascading Splits (Nested)

For >128 recipients or complex hierarchies, create splits-of-splits:
1. Create leaf splits first (bottom-up)
2. Use the returned split addresses as recipients in parent splits
3. Each level has its own 150 bps fee

## Basis Points Math

| Percentage | Basis Points (of 9850) |
|-----------|----------------------|
| 50%       | 4925                 |
| 25%       | 2462 or 2463         |
| 10%       | 985                  |
| 5%        | 492 or 493           |
| 1%        | 98 or 99             |

Formula: `points = round(percentage / 100 * 9850)`

When rounding causes the sum to not equal 9850, adjust the last recipient.
