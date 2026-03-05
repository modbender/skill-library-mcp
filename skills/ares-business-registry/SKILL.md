---
name: ares-business-registry
description: Query Czech ARES business registry by ICO or name with human/JSON/raw outputs, retries, and legal-form decoding.
---

# ARES Business Registry (CZ)

Use `scripts/ares_client.py` for ICO lookup and business search.

## Working directory

- From workspace root:
  - `python3 skills/ares-business-registry/scripts/ares_client.py ...`
- From `skills/ares-business-registry`:
  - `python3 scripts/ares_client.py ...`

## Commands

You can run via the wrapper (recommended):
- `./ares ico <ico>`
- `./ares name "NAME" [--nace CODE ...] [--city CITY] [--limit N] [--offset N] [--pick INDEX]`

The underlying script also supports:
- `python3 scripts/ares_client.py search --name "NAME" ...`
- `python3 scripts/ares_client.py search --nace CODE [CODE ...] ...`
- `python3 scripts/ares_client.py search --name "NAME" --nace CODE ...` (combined)

## Output modes

- default: human-readable summary
- `--json`: normalized JSON output (stable keys)
- `--raw`: full raw ARES payload

## Examples

```bash
# ICO lookup
python3 scripts/ares_client.py ico 27604977
python3 scripts/ares_client.py ico 27604977 --json
python3 scripts/ares_client.py ico 27604977 --raw

# Search by name
python3 scripts/ares_client.py search --name Google
python3 scripts/ares_client.py search --name Google --limit 3 --json
python3 scripts/ares_client.py search --name Google --city Praha --limit 10 --offset 0
python3 scripts/ares_client.py search --name Google --limit 3 --pick 1

# Search by NACE code (CZ-NACE, exactly 5 digits)
python3 scripts/ares_client.py search --nace 47710 --limit 10            # all clothing retailers
python3 scripts/ares_client.py search --nace 47710 --city Praha --json    # clothing retailers in Praha
python3 scripts/ares_client.py search --nace 47710 47910 --limit 5        # clothing retail + mail order

# Combined: name + NACE (AND filter)
python3 scripts/ares_client.py search --name sport --nace 47710 --json    # "sport" in clothing retail
```

## Normalized JSON

- `ico` output:
  - `{ "subject": { "name", "ico", "dic", "datumVzniku", "address", "codes", "decoded" } }`
- `search` output:
  - `{ "query", "total", "items", "picked?" }`
  - `query` includes: `name` (nullable), `city` (nullable), `nace` (nullable array), `limit`, `offset`
- `dic` can be `null`.
- `datumVzniku` can be `null`.

## Error JSON contract (`--json` only)

```json
{
  "error": {
    "code": "validation_error | ares_error | network_error",
    "message": "Human readable message",
    "status": 429,
    "details": {}
  }
}
```

## Validation and exits

- ICO: exactly 8 digits + mod11 checksum
- Search: at least `--name` (length >= 3) or `--nace` required; both can be combined
- `--nace`: exactly 5 digits per code (CZ-NACE format, e.g. `47710`); multiple codes accepted (space-separated)
- `--limit`: default 10, capped to 100
- `--offset`: must be >= 0
- Exit codes:
  - `0` success
  - `1` validation error
  - `2` ARES non-OK response
  - `3` network/timeout

## Caching and decoding

- Legal form decoding (`PravniForma`) is loaded via POST `/ciselniky-nazevniky/vyhledat`
- Cache path: `skills/ares-business-registry/.cache/pravni_forma.json`
- Cache TTL: 24h
- In-memory fallback is used if cache file is stale/unavailable
- Curated overrides:
  - `112 -> s.r.o.`
  - `121 -> a.s.`
  - `141 -> z.s.`
  - `701 -> OSVČ`
  - `301 -> s.p.`
  - `331 -> p.o.`

## NACE code search

- `--nace` sends the `czNace` field to the ARES complex filter endpoint
- Codes must be exactly 5 digits (CZ-NACE_2025 format)
- Multiple codes can be passed (space-separated) — ARES returns entities matching **any** of them
- When combined with `--name`, both filters apply as AND (entities must match name AND have the NACE code)
- NACE-only search (without `--name`) is supported — useful for browsing all entities in a sector
- Common e-commerce NACE codes:
  - `47710` — Retail sale of clothing
  - `47910` — Retail sale via mail order or internet
  - `47410` — Retail sale of computers and software
  - `47750` — Retail sale of cosmetic and toilet articles
  - `46420` — Wholesale of clothing and footwear
- Full CZ-NACE list: https://www.czso.cz/csu/czso/klasifikace_ekonomickych_cinnosti_cz_nace

## City filter limitation

- `--city` maps to `sidlo.nazevObce` (structured filter).
- Matching remains best-effort only; ARES server-side matching/ranking can still return records outside the expected municipality.

## Retries and rate limits

- HTTP timeout: connect 5s, read 20s
- Retries for transient failures: `429/502/503/504` + network timeout/connection issues
- Backoff: `1s`, `2s`, `4s`
- Honors `Retry-After` for 429 where provided
