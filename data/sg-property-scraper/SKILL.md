---
name: sg-property-scraper
description: Search Singapore property rental and sale listings with flexible filters. Use when asked to search Singapore properties, find rental or sale listings, check property prices near MRT stations, or compare commute times. Supports filtering by listing type (rent/sale), property type (HDB/Condo/Landed), bedrooms, bathrooms, price range, size, TOP year, MRT station codes, distance to MRT, room type, availability, and commute time to a destination. Outputs JSON to stdout.
metadata:
  {"openclaw":{"requires":{"bins":["python3"]},"primaryEnv":"GOOGLE_MAPS_API_KEY"}}
---

# Singapore Property Scraper

Scrapes Singapore property listings via HTTP requests. Returns structured JSON.

## Script Location

```
scripts/scrape.py
```

Relative to this SKILL directory. Run with:
```bash
python3 <SKILL_DIR>/scripts/scrape.py [OPTIONS]
```

## Dependencies

- Python 3.8+
- `pip install curl_cffi beautifulsoup4 lxml`
- Optional: `GOOGLE_MAPS_API_KEY` env var for commute time calculation (Google Routes API)

## Quick Start

```bash
# Search 2BR condos for rent under SGD 4000 near Circle Line
python3 scripts/scrape.py \
  --listing-type rent --bedrooms 2 --max-price 4000 \
  --property-type-group N --mrt-range CC:20-24 \
  --output json

# JSON input mode (easier for AI tools)
python3 scripts/scrape.py --json '{
  "listingType": "rent",
  "bedrooms": 2,
  "maxPrice": 4000,
  "propertyTypeGroup": ["N"],
  "mrtStations": ["CC20","CC21","CC22","CC23","CC24"]
}'

# Dry run: print URL only without scraping
python3 scripts/scrape.py --dry-run --listing-type rent --bedrooms 3
```

## Filter Parameters

| Flag | URL Param | Type | Description |
|------|-----------|------|-------------|
| `--listing-type` | `listingType` | string | `rent` or `sale` |
| `--property-type-group` | `propertyTypeGroup` | string (repeatable) | `N`=Condo, `L`=Landed, `H`=HDB |
| `--entire-unit-or-room` | `entireUnitOrRoom` | string | `ent` for entire unit only; omit for all |
| `--room-type` | `roomType` | string (repeatable) | `master`, `common`, `shared` |
| `--bedrooms` | `bedrooms` | int | `-1`=room, `0`=studio, `1`-`5` |
| `--bathrooms` | `bathrooms` | int | Number of bathrooms |
| `--min-price` | `minPrice` | int | Minimum price (SGD) |
| `--max-price` | `maxPrice` | int | Maximum price (SGD) |
| `--min-size` | `minSize` | int | Minimum size (sqft) |
| `--max-size` | `maxSize` | int | Maximum size (sqft) |
| `--min-top-year` | `minTopYear` | int | Minimum TOP year |
| `--max-top-year` | `maxTopYear` | int | Maximum TOP year |
| `--distance-to-mrt` | `distanceToMRT` | float | Max distance to MRT in km (e.g. `0.5`, `0.75`) |
| `--availability` | `availability` | int | Availability filter |
| `--mrt-station` | `mrtStations` | string (repeatable) | MRT station code, e.g. `CC20` |
| `--mrt-range` | `mrtStations` | string (repeatable) | MRT range, e.g. `CC:20-24` |
| `--sort` | `sort` | string | `date`, `price`, `psf`, `size` |
| `--order` | `order` | string | `asc`, `desc` |
| `--commute-to` | `commuteTo` | string | Destination address for commute time (requires `GOOGLE_MAPS_API_KEY`) |

## Bedroom/Room Logic

- `--entire-unit-or-room ent --bedrooms 4` = 4-bedroom entire unit
- `--entire-unit-or-room ent --bedrooms 0` = studio
- `--bedrooms -1 --room-type master --room-type common` = room rental (master or common room)
- Omit `--entire-unit-or-room` to show both entire units and rooms

## MRT Station Syntax

- Individual station: `--mrt-station CC20`
- Range (same line): `--mrt-range CC:20-24` (expands to CC20, CC21, CC22, CC23, CC24)
- Multiple lines: use multiple flags
- In JSON: `"mrtStations": ["CC20", "EW15"]` or `[["CC", [20, 24]]]` (tuple format)

See `references/params.md` for the complete list of ~213 valid MRT station codes.

## Execution Parameters

| Flag | Description |
|------|-------------|
| `--pages N` | Number of pages to scrape (default: 1) |
| `--dry-run` | Build and print URL(s), skip scraping |
| `--no-validate` | Skip parameter validation |
| `--timeout N` | HTTP request timeout in seconds (default: 30) |
| `--raw-param K=V` | Extra URL query param (repeatable) |
| `--output json\|text\|none` | Output format (default: json when piped) |
| `--verbose` | Verbose logging to stderr |

## JSON Input Mode

Pass filters as a JSON string with `--json`. Keys use camelCase matching the URL parameter names:

```bash
python3 scripts/scrape.py --json '{
  "listingType": "rent",
  "propertyTypeGroup": ["N"],
  "bedrooms": 2,
  "bathrooms": 2,
  "maxPrice": 4000,
  "mrtStations": ["EW16", "EW17", "EW18"],
  "distanceToMRT": 0.75,
  "minTopYear": 1990
}'
```

Or load from a file: `--config filters.json`

## Output Format

JSON array on stdout (empty `[]` if no results):

```json
[
  {
    "id": "23744236",
    "name": "Kingsford Waterbay",
    "price": "S$ 3,900 /mo",
    "psf": "S$ 4.53 psf",
    "address": "68 Upper Serangoon View",
    "bedrooms": "2",
    "bathrooms": "2",
    "area": "861 sqft",
    "type": "Condominium",
    "built": "Built: 2018",
    "availability": "Ready to Move",
    "mrt_distance": "14 min (1.15 km) from SE4 Kangkar LRT Station",
    "list_date": "Listed on Feb 15, 2026 (2d ago)",
    "agent": "May Chong",
    "agency": "PROPNEX REALTY PTE. LTD.",
    "headline": "Perfect work from home unit, river facing, unblocked high floor cozy",
    "link": "https://www.propertyguru.com.sg/listing/for-rent-kingsford-waterbay-23744236",
    "commute_driving": "25 mins",
    "commute_transit": "45 mins"
  }
]
```

## Exit Codes

- `0`: Success, results found
- `1`: Error (bad parameters, scraping failure)
- `2`: Success but zero listings found

## Agent Usage Notes

When calling this script from an AI agent:
1. Use `--output json` for structured output (default when piped)
2. Use `--json` flag for easier parameter passing than individual CLI flags
3. Use `--dry-run` to preview the search URL before scraping
4. Use `--pages N` if the user wants more results (each page has ~20 listings)
5. Use `--commute-to` with a destination address to calculate commute times (driving + transit) for each listing. Requires `GOOGLE_MAPS_API_KEY` env var. If the key is not set, commute fields are omitted silently.
6. `commute_driving` and `commute_transit` fields are empty strings `""` when API key is missing or calculation fails
