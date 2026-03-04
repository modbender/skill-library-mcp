# Housing Scout Provider Adapter Contract (Phase 1)

Each provider adapter should export:

- `searchListings(query): Promise<Listing[]>`

Where `Listing` uses normalized schema fields expected by core pipeline:

- `provider` (string)
- `providerId` (string)
- `status` (`for_sale` | `for_rent` | `sold`)
- `address` `{ street, city, state, zip }`
- `url`
- `price` / `rent`
- `beds`, `baths`, `sqft`
- `homeType`
- optional: `schoolScore`, `schools`, `lat`, `lng`, `daysOnRedfin`

## Aggregation rules

- Multi-provider aggregation is orchestrated by `providers/index.mjs`.
- `--providers` controls which adapters run (default: `redfin`).
- Results are deduplicated in core layer; duplicate rows from different providers should merge source provenance.

## Phase 2 scope (current)

- `redfin` adapter is live/default.
- `zillow` and `realtor` adapters now support live-cache ingestion from local harvested files:
  - `tools/housing_scout/data/live_zillow_buy.json`
  - `tools/housing_scout/data/live_zillow_rent.json`
  - `tools/housing_scout/data/live_realtor_buy.json`
  - `tools/housing_scout/data/live_realtor_rent.json`
- Cache freshness windows:
  - buy: 24h
  - rent: 12h
- If caches are stale/empty, adapters return zero rows (best-effort behavior).
