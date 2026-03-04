# SG Property Scraper

Search Singapore property rental and sale listings from the command line. Supports flexible filters (location, price, bedrooms, MRT proximity, etc.) and optional commute time calculation via Google Routes API.

## Setup

```bash
# Python 3.8+ required
pip install curl_cffi beautifulsoup4 lxml
```

Optional — for commute time calculation:

```bash
export GOOGLE_MAPS_API_KEY="your-key-here"  # needs Routes API enabled
```

## Usage

### CLI flags

```bash
# 2BR rentals under SGD 4000
python3 scripts/scrape.py --listing-type rent --bedrooms 2 --max-price 4000

# Condos near Circle Line MRT stations
python3 scripts/scrape.py --listing-type rent --property-type-group N --mrt-range CC:20-24

# With commute time to office
GOOGLE_MAPS_API_KEY=xxx python3 scripts/scrape.py \
  --listing-type rent --bedrooms 2 --max-price 4000 \
  --commute-to "1 Raffles Place, Singapore" \
  --output text
```

### JSON mode

```bash
python3 scripts/scrape.py --json '{
  "listingType": "rent",
  "bedrooms": 2,
  "maxPrice": 4000,
  "propertyTypeGroup": ["N"],
  "mrtStations": ["CC20", "CC21", "CC22"],
  "commuteTo": "1 Raffles Place, Singapore"
}'
```

### Dry run (preview URL without scraping)

```bash
python3 scripts/scrape.py --dry-run --listing-type rent --bedrooms 3
```

## Filter Parameters

| Flag | Type | Description |
|------|------|-------------|
| `--listing-type` | string | `rent` or `sale` |
| `--property-type-group` | string | `N`=Condo, `L`=Landed, `H`=HDB (repeatable) |
| `--bedrooms` | int | `-1`=room, `0`=studio, `1`-`5` |
| `--bathrooms` | int | Number of bathrooms |
| `--min-price` / `--max-price` | int | Price range in SGD |
| `--min-size` / `--max-size` | int | Size range in sqft |
| `--mrt-station` | string | MRT code e.g. `CC20` (repeatable) |
| `--mrt-range` | string | MRT range e.g. `CC:20-24` (repeatable) |
| `--distance-to-mrt` | float | Max distance to MRT in km |
| `--commute-to` | string | Destination for commute calculation |
| `--sort` | string | `date`, `price`, `psf`, `size` |
| `--order` | string | `asc`, `desc` |

See `references/params.md` for the full list of MRT station codes.

## Execution Options

| Flag | Description |
|------|-------------|
| `--pages N` | Pages to scrape (default: 1, ~20 listings/page) |
| `--output json\|text\|none` | Output format (default: json when piped, text in terminal) |
| `--verbose` | Verbose logging to stderr |
| `--dry-run` | Print URL(s) only, skip scraping |
| `--timeout N` | HTTP timeout in seconds (default: 30) |
| `--config FILE` | Load filters from a JSON file |

## Output

JSON array to stdout:

```json
[
  {
    "id": "23744236",
    "name": "Kingsford Waterbay",
    "price": "S$ 3,900 /mo",
    "address": "68 Upper Serangoon View",
    "bedrooms": "2",
    "bathrooms": "2",
    "area": "861 sqft",
    "type": "Condominium",
    "mrt_distance": "14 min (1.15 km) from SE4 Kangkar LRT Station",
    "commute_driving": "25 mins",
    "commute_transit": "45 mins",
    "link": "https://..."
  }
]
```

Text output (`--output text`):

```
[23744236] Kingsford Waterbay — S$ 3,900 /mo
  861 sqft | 2BR | 2BA | Condominium
  68 Upper Serangoon View
  MRT: 14 min (1.15 km) from SE4 Kangkar LRT Station
  Commute: 25 mins drive | 45 mins transit
  Ready to Move
  https://...
```

## Commute Calculation

When `--commute-to` is specified and `GOOGLE_MAPS_API_KEY` is set:

- Uses Google Routes API (`computeRouteMatrix`)
- Calculates driving time (departure 8 AM SGT) and transit time (arrival 9 AM SGT) for the next weekday
- Results added as `commute_driving` and `commute_transit` fields
- Without API key: commute fields are silently omitted, scraping works normally

## Exit Codes

- `0` — Success, results found
- `1` — Error (bad parameters, scraping failure)
- `2` — Success, zero listings found
