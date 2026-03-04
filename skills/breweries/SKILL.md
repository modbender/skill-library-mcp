---
name: breweries
version: 1.0.0
description: "CLI for AI agents to find breweries for their humans. Uses Open Brewery DB. No auth required."
homepage: https://www.openbrewerydb.org
metadata:
  openclaw:
    emoji: "🍺"
    requires:
      bins: ["bash", "curl", "jq"]
    tags: ["breweries", "beer", "search", "openbrewerydb", "cli"]
---

# Brewery Lookup

CLI for AI agents to find breweries for their humans. "What breweries are in Portland?" — now your agent can answer.

Uses Open Brewery DB. No account or API key needed.

## Usage

```
"Find breweries named Sierra Nevada"
"What breweries are in San Diego?"
"Show me breweries in Oregon"
"Find me a random brewery"
"What brewpubs are there?"
```

## Commands

| Action | Command |
|--------|---------|
| Search by name | `breweries search "name"` |
| Find by city | `breweries city "city name"` |
| Find by state | `breweries state "state"` |
| Find by type | `breweries type <type>` |
| Random | `breweries random [count]` |

### Brewery Types
- `micro` — Most craft breweries
- `nano` — Very small breweries
- `regional` — Regional craft breweries
- `brewpub` — Brewery with restaurant/bar
- `large` — Large national breweries
- `planning` — Breweries in planning
- `bar` — Bars that brew on premises
- `contract` — Contract brewing
- `proprietor` — Alternating proprietor
- `closed` — Closed breweries

### Examples

```bash
breweries search "stone brewing"    # Find breweries by name
breweries city "portland"           # Find breweries in Portland
breweries state oregon              # Find breweries in Oregon
breweries type brewpub              # Find all brewpubs
breweries random 3                  # Get 3 random breweries
```

## Output

```
🍺 Sierra Nevada Brewing Co. — Chico, California, Regional Brewery
   https://sierranevada.com
```

## Notes

- Uses Open Brewery DB API v1 (api.openbrewerydb.org)
- No authentication required
- No rate limiting documented
- Returns up to 10 results per query
- State names can be full name or abbreviation

---

## Agent Implementation Notes

**Script location:** `{skill_folder}/breweries` (wrapper) → `scripts/breweries`

**When user asks about breweries:**
1. Run `./breweries search "name"` to find by name
2. Run `./breweries city "city"` for location-based search
3. Run `./breweries state "state"` for state-wide search
4. Run `./breweries type brewpub` for specific types
5. Run `./breweries random` for discovery/recommendations

**Common patterns:**
- "Find me a brewery in [city]" → `breweries city "[city]"`
- "What breweries are in [state]?" → `breweries state "[state]"`
- "Search for [name] brewery" → `breweries search "[name]"`
- "Surprise me with a brewery" → `breweries random`
- "Where can I get craft beer in [city]?" → `breweries city "[city]"` or `breweries type micro`

**Don't use for:** Bars without brewing, liquor stores, wine/spirits.
