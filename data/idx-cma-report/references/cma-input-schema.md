# CMA Input Schema

Use these JSON shapes before running `scripts/build_cma.py`.

## `subject.json`

```json
{
  "address": "123 Main St, Austin, TX",
  "price": 615000,
  "beds": 4,
  "baths": 3,
  "sqft": 2540,
  "lot_sqft": 6400,
  "year_built": 2014,
  "property_type": "Single Family",
  "zip": "78704",
  "lat": 30.2474,
  "lng": -97.7735
}
```

## `comps.json`

Array of comparable listings:

```json
[
  {
    "address": "111 Oak St, Austin, TX",
    "price": 599000,
    "beds": 4,
    "baths": 3,
    "sqft": 2480,
    "lot_sqft": 6200,
    "year_built": 2012,
    "days_on_market": 14,
    "distance_miles": 0.7,
    "status": "Closed",
    "close_date": "2025-12-01",
    "lat": 30.2461,
    "lng": -97.7712
  }
]
```

## Required vs Optional

- Required for each comp: `price`, `sqft`
- Strongly recommended: `distance_miles`, `days_on_market`, `beds`, `baths`, `year_built`
- Subject recommended: `sqft`, `beds`, `baths`, `year_built`

If optional fields are missing, script still runs but confidence should be reduced.
