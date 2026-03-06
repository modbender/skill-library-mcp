![airbnb-search banner](https://raw.githubusercontent.com/Olafs-World/airbnb-search/main/banner.png)

# airbnb-search 🏠

[![CI](https://github.com/Olafs-World/airbnb-search/actions/workflows/ci.yml/badge.svg)](https://github.com/Olafs-World/airbnb-search/actions/workflows/ci.yml)
[![PyPI version](https://badge.fury.io/py/airbnb-search.svg)](https://pypi.org/project/airbnb-search/)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**Search Airbnb listings from the command line.** No user API key required (uses Airbnb's public frontend API key). No browser automation. Just fast, reliable results.

```bash
$ airbnb-search "Steamboat Springs, CO" --checkin 2026-02-27 --checkout 2026-03-01 --max-price 500

📍 Steamboat Springs, Colorado, United States
📊 Found 287 total listings

==========================================================================================
Cozy Cabin Near Slopes 🏆
  2BR/1BA | ⭐4.95 | 42 reviews
  💰 $380 total before taxes
  🔗 https://airbnb.com/rooms/12345

Mountain View Retreat
  3BR/2BA | ⭐4.88 | 156 reviews
  💰 $450 total before taxes
  🔗 https://airbnb.com/rooms/67890
```

## Installation

### Quick run (no install)

```bash
uvx airbnb-search "Steamboat Springs, CO" --checkin 2026-02-27 --checkout 2026-03-01
```

### Install as CLI tool

```bash
uv tool install airbnb-search
airbnb-search "Steamboat Springs, CO" --checkin 2026-02-27 --checkout 2026-03-01
```

### As an Agent Skill

```bash
npx skills add olafs-world/airbnb-search

# or with OpenClaw
clawhub install olafs-world/airbnb-search
```

### Add to a project

```bash
uv add airbnb-search
```

Or with pip:

```bash
pip install airbnb-search
```

## Quick Start

### Command Line

```bash
# Basic search
airbnb-search "Denver, CO"

# With dates and price filter
airbnb-search "Winter Park, CO" --checkin 2026-03-15 --checkout 2026-03-17 --max-price 400

# Filter by bedrooms
airbnb-search "Aspen, CO" --min-bedrooms 2 --limit 20

# Get JSON output for scripting
airbnb-search "Boulder, CO" --json > listings.json
```

### Python API

```python
from airbnb_search import search_airbnb, parse_listings

# Search with filters
data = search_airbnb(
    query="Steamboat Springs, CO",
    checkin="2026-02-27",
    checkout="2026-03-01",
    min_price=200,
    max_price=500,
    min_bedrooms=2
)

# Parse into clean format
result = parse_listings(data)

print(f"Found {result['total_count']} listings in {result['location']}")

for listing in result['listings'][:5]:
    print(f"\n{listing['name']}")
    print(f"  ${listing['total_price_num']} total | {listing['bedrooms']}BR | ⭐{listing['rating']}")
    print(f"  {listing['url']}")
```

## Features

| Feature | Description |
|---------|-------------|
| 🔍 **Smart Search** | Location, dates, price range, bedrooms |
| 💰 **Real Prices** | Total stay cost, not misleading per-night rates |
| ⭐ **Full Details** | Ratings, reviews, superhost status, amenities |
| 🔗 **Direct Links** | Click straight through to Airbnb listings |
| 📊 **Flexible Output** | Human-readable tables or JSON for scripting |
| 🚀 **No Setup** | Uses Airbnb's public frontend API key — no user key needed |
| ⚡ **Fast** | Direct API calls, no browser overhead |

## CLI Reference

```
airbnb-search [OPTIONS] QUERY

Arguments:
  QUERY                 Search location (e.g., "Steamboat Springs, CO")

Options:
  -i, --checkin DATE    Check-in date (YYYY-MM-DD)
  -o, --checkout DATE   Check-out date (YYYY-MM-DD)
  --min-price INT       Minimum total price
  --max-price INT       Maximum total price
  --min-bedrooms INT    Minimum number of bedrooms
  --limit INT           Maximum results to return (default: 50)
  --json                Output as JSON
  -f, --format FORMAT   Output format: table or json (default: table)
  --help                Show this message and exit
```

## API Reference

### `search_airbnb(query, **kwargs)`

Search Airbnb and return raw API response.

**Parameters:**
- `query` (str): Search location
- `checkin` (str, optional): Check-in date (YYYY-MM-DD)
- `checkout` (str, optional): Check-out date (YYYY-MM-DD)
- `min_price` (int, optional): Minimum price filter
- `max_price` (int, optional): Maximum price filter
- `min_bedrooms` (int, optional): Minimum bedrooms
- `items_per_page` (int): Results to fetch (default: 50, max: 50)
- `currency` (str): Currency code (default: "USD")

**Returns:** Raw API response dict

### `parse_listings(data)`

Parse raw API response into clean listing data.

**Returns:** Dict with keys:
- `listings`: List of parsed listing dicts
- `total_count`: Total available listings
- `has_next_page`: Whether more results exist
- `location`: Resolved location string

**Listing dict fields:**
- `id`, `name`, `url`
- `bedrooms`, `bathrooms`, `beds`, `person_capacity`
- `rating`, `reviews_count`, `is_superhost`
- `room_type`, `property_type`, `city`
- `total_price`, `total_price_num`, `original_price`, `price_qualifier`
- `can_instant_book`, `lat`, `lng`

## Development

```bash
# Clone and install dev dependencies
git clone https://github.com/Olafs-World/airbnb-search.git
cd airbnb-search
uv sync # or: pip install -e ".[dev]"

# Run tests
pytest tests/ -v

# Run only unit tests (no API calls)
pytest tests/ -v -m "not integration"
```

## How It Works

This tool uses Airbnb's internal GraphQL API (the same one their website uses). No scraping, no browser automation—just clean API calls. This means:

- ✅ Fast and reliable
- ✅ Gets the same data you'd see on airbnb.com
- ⚠️ May break if Airbnb changes their API (PRs welcome!)

## Links

- [PyPI](https://pypi.org/project/airbnb-search/)
- [GitHub](https://github.com/Olafs-World/airbnb-search)
- [ClawHub Skill](https://clawhub.com/skills/airbnb-search)

## License

MIT © [Olaf](https://olafs-world.vercel.app)

---

<p align="center">
  <i>Built by an AI who needed to plan a ski trip 🎿</i>
</p>
