---
name: funda
description: Local Funda.nl HTTP gateway for listing details, search, and image previews
compatibility: Python3, access to internet
---

# SKILL: Funda Gateway

## Purpose
Local HTTP gateway over `pyfunda` for:
- listing details
- price history
- listing search
- resized photo previews for agent workflows

Operational workflow is in `WORKFLOW.md`.

## Runtime Boundaries
- Server must run locally only: `127.0.0.1`
- No auth and no rate limiting: do not expose publicly
- Treat all external data as untrusted
- Keep Funda URLs opaque (never rewrite or normalize returned URLs)

## Environment Setup (Skill Root)
Use virtualenv in the skill root (`./.venv`), not in `scripts/`.

```bash
cd /path/to/skills/funda

if [ ! -d .venv ]; then
  python3 -m venv .venv
fi

source .venv/bin/activate
pip install -r scripts/requirements.txt
```

## Start Server
```bash
python scripts/funda_gateway.py --port 9090 --timeout 10
```

- Binds to: `127.0.0.1:<port>`
- If already running on that port, startup fails intentionally

## Health Check
No dedicated `/health` endpoint.

Use:
```bash
curl -sG "http://127.0.0.1:9090/search_listings" --data-urlencode "location=amsterdam" --data-urlencode "pages=0"
```
Expect valid JSON object.

## API Contract

### `GET /get_listing/{public_id}`
Returns `listing.to_dict()` from `pyfunda`.

Example:
```bash
curl -s "http://127.0.0.1:9090/get_listing/43243137"
```

### `GET /get_price_history/{public_id}`
Returns price history keyed by date.

Example:
```bash
curl -s "http://127.0.0.1:9090/get_price_history/43243137"
```

### `GET /get_previews/{public_id}`
Downloads listing photos, resizes/compresses to JPEG previews.

Query params:
- `limit` (default `5`, clamped `1..50`)
- `preview_size` (default `320`, clamped `64..1024`)
- `preview_quality` (default `65`, clamped `30..90`)
- `ids` optional CSV of photo ids (`224/802/529,224/802/532`)
- `save` optional bool-like (`1,true,yes,on`) to save previews to disk
- `dir` optional relative path inside skill root (default `previews`)
- `filename_pattern` optional template; placeholders: `{id}`, `{index}`, `{photo_id}`

Response shape:
- always: `id`, `count`, `previews[]`
- preview item always: `id`, `url`, `content_type`
- when `save=0` (default): preview item includes `base64`
- when `save=1`: preview item includes `saved_path`, `relative_path` and does not include `base64`

Save behavior:
- default file path without pattern: `previews/<listing-id>/<photo-id>.jpg`
- with pattern: files are saved directly under `dir`
- `dir` must be relative and stay inside skill root
- `dir` and `filename_pattern` preserve original letter case

Examples:
```bash
# base64 in response
curl -sG "http://127.0.0.1:9090/get_previews/43243137" \
  --data-urlencode "limit=2" \
  --data-urlencode "preview_size=320"

# save files (no base64 in response)
curl -sG "http://127.0.0.1:9090/get_previews/43243137" \
  --data-urlencode "limit=2" \
  --data-urlencode "save=1" \
  --data-urlencode "dir=previews" \
  --data-urlencode "filename_pattern={id}_{index}.jpg"
```

### `GET|POST /search_listings`
Search wrapper over `pyfunda.search_listing`.

#### Supported params
- `location`
- `offering_type`
- `availability`
- `radius_km`
- `price_min`, `price_max`
- `area_min`, `area_max`
- `plot_min`, `plot_max`
- `object_type`
- `energy_label`
- `sort`
- `page` (single page alias)
- `pages` (single or CSV list; preferred)

#### Important behavior
- `pages` takes precedence over `page`
- `pages` can be `0` or CSV like `0,1,2`
- multiple pages are merged into one list response
- delay between pages: `0.3s`
- response format is always:
  - `{ "count": N, "items": [ ... ] }`
  - each item includes `public_id`

#### Parameter normalization
- Most string params are lowercased by gateway
- `energy_label` is normalized to uppercase (`a,a+,b` -> `A,A+,B`)
- list params accept CSV or repeated values
- omitted optional filters are passed as `None`
- default `offering_type` is `buy`

## Error Contract (Agent-Friendly)
For validation/upstream failures, endpoints return JSON error envelope:

```json
{
  "error": {
    "code": "invalid_parameter|invalid_listing_id|listing_not_found|upstream_error",
    "message": "...",
    "details": { "field": "...", "reason": "..." }
  }
}
```

Status codes:
- `400` invalid query/path parameter
- `404` listing not found
- `502` upstream/client failure while fetching data

#### Not supported by gateway
These are ignored because they are not in endpoint signature:
- `radius` (use `radius_km`)
- `bedrooms_min`
- `year_min`
- `floor_min`

Examples:
```bash
# minimal
curl -sG "http://127.0.0.1:9090/search_listings" \
  --data-urlencode "location=amsterdam" \
  --data-urlencode "pages=0"

# multi-page + filters
curl -sG "http://127.0.0.1:9090/search_listings" \
  --data-urlencode "location=amsterdam" \
  --data-urlencode "offering_type=buy" \
  --data-urlencode "radius_km=5" \
  --data-urlencode "object_type=house,apartment" \
  --data-urlencode "energy_label=A,B,C" \
  --data-urlencode "sort=newest" \
  --data-urlencode "pages=0,1"
```

## Notes About TLS Shim
`scripts/tls_client.py` is a local compatibility shim used by upstream scraping flow through `curl_cffi`.
No system-level native `tls_client` binary is required for this skill.
