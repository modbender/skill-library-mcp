---
name: geizhals-at
description: Search Geizhals.at (Austria) with HTTP-only autocomplete + detail-page parsing (no browser automation). Use when users want quick price checks from Geizhals.at and accept unofficial/best-effort scraping limits.
---

# geizhals-at

Geizhals-only lookup skill (Austria) using plain HTTP.

## Behavior

- Query Geizhals autocomplete endpoint (`/acs`) for product candidates.
- Fetch top candidate detail pages.
- Extract:
  - `min_price_eur`
  - `shop`
  - `offer_count`
  - `price_confidence` + `price_source`
- Return stable JSON records with `schema_version`.

## Constraints

- No browser automation.
- No JS execution.
- Unofficial integration: HTML patterns can change and break extraction.
- Keep request volume low.

## Usage

Run commands from the `geizhals-at` skill directory.

`uv` first:

```bash
uv run scripts/geizhals.py search "iphone 15" --limit 5
```

JSON output:

```bash
uv run scripts/geizhals.py search "mac mini" --limit 5 --json
```

Debug + explicit cache dir:

```bash
uv run scripts/geizhals.py search "bosch akkuschrauber" --limit 5 --json --debug --cache-dir /tmp/geizhals-cache
```

Fallback without `uv`:

```bash
python3 scripts/geizhals.py search "iphone 15" --limit 5
```

## Output contract

Each result includes:

- `schema_version` (currently `1.0`)
- `name`
- `detail_url`
- `min_price_eur` (nullable)
- `shop` (nullable)
- `offer_count` (nullable)
- `price_confidence`: `high|medium|low|unknown`
- `price_source`: `embedded_offer_raw_price|meta_product_price|title_ab_price|none`
- `error` (nullable)

## Testing

Run parser tests from the skill directory:

```bash
uv run --with pytest python -m pytest tests/test_parsers.py
```

Fallback:

```bash
python3 -m pytest tests/test_parsers.py
```

Fixtures live in `tests/fixtures/`.

## Known limitations

- Results are Geizhals-only by design.
- Some products may miss a shop or exact cheapest offer if page structure changes.
- If Geizhals rate-limits, the script retries with exponential backoff but can still fail.
