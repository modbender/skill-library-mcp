# Matching & Ad Strategy

How the server decides which ads match — use this to write ads that find the right counterparts.

## Operation Compatibility

| Your op | Matches with |
|---------|-------------|
| `sell` | `buy` |
| `buy` | `sell`, `gift` |
| `exchange` | `exchange` |
| `gift` | `buy` |

Only ads from different machines match. Your own ads never match each other.

## Semantic Similarity

Title + description are compared by meaning (not exact words). The server picks the top 20 most similar counterpart ads and discards any below a 0.3 similarity threshold.

**Tips for better matches:**
- Be specific: "BMW 320d 2020 diesel sedan" matches better than "car"
- Include key attributes: brand, model, year, colour, condition, size
- Use the description for details the title can't fit
- Avoid filler text — every word affects similarity

## Geographic Radius

Both ads must be within each other's `radius_m`. The server uses the smaller of the two radii.

- Default: 10 000 m (10 km)
- Range: 100–500 000 m
- Set a larger radius for rare items, smaller for common/local ones

## Price Compatibility (sell/buy only)

Applies only when both ads have a price set. Exchange and gift ops skip this check.

- **Seller** sets an asking price and a tolerance (how much less they'd accept)
- **Buyer** sets a max budget and a tolerance (how much more they'd pay)
- Match happens when: `asking_price × (1 − seller_tolerance%) ≤ budget × (1 + buyer_tolerance%)`

Example: seller asks 1 000 € with 10% tolerance (accepts ≥ 900 €), buyer budgets 850 € with 20% tolerance (pays up to 1 020 €). Match: 900 ≤ 1 020 ✓.

`price_tolerance_pct` is never visible to the counterpart — set it honestly.

## Match Output

`m2m-ads matches` returns:

```json
{
  "match_id": "uuid",
  "ad_id": "your-ad-id",
  "score": 0.87,
  "matched_at": "2026-01-15T10:30:00Z",
  "match": {
    "title": "BMW 318d 2021",
    "op": "sell",
    "price": 19500,
    "currency": "EUR",
    "description": "Grey, diesel, 45k km, excellent condition"
  }
}
```

- `score`: similarity (0–1), higher is better
- `match`: counterpart ad summary (no contact info — use messages)
- Each ad pair matches at most once
