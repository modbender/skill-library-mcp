---
name: jlm-coffee
version: 2.0.0
description: Search Jerusalem specialty coffee shops by name, amenities, ratings, and opening hours. Use when user asks about "coffee in Jerusalem", "Jerusalem cafe", "בית קפה בירושלים", "קפה בירושלים", "specialty coffee Jerusalem", "where to get coffee in Jerusalem", "dog-friendly cafe Jerusalem", "laptop cafe Jerusalem", "open now coffee Jerusalem".
author: Alex Polonsky (https://github.com/alexpolonsky)
homepage: https://github.com/alexpolonsky/agent-skill-jlm-coffee
license: MIT
metadata: {"openclaw": {"emoji": "☕", "os": ["darwin", "linux"], "requires": {"bins": ["python3"]}}}
---

# Jerusalem Coffee Finder

Search specialty coffee shops in Jerusalem - ratings, amenities, opening hours, reviews, and locations from [coffee.amsterdamski.com](https://coffee.amsterdamski.com), created and curated by [Shaul Amsterdamski](https://x.com/amsterdamski2) ([@amsterdamski2](https://x.com/amsterdamski2)).

> Data from the official public JSON export provided by the site maintainer. May not reflect current status. Provided "as is" without warranty of any kind.

## Quick Start

```bash
# List all coffee shops
python3 {baseDir}/scripts/jlm-coffee.py list

# Find a shop by name
python3 {baseDir}/scripts/jlm-coffee.py search "סיבריס"
```

## Commands

| Command | Description |
|---------|-------------|
| `list` | List all approved specialty coffee shops |
| `search <query>` | Search shops by name (Hebrew or English) |
| `get <id_or_name>` | Get full details for a specific shop |
| `filter <amenity>` | Filter shops by amenity (wifi, dogs, kosher, etc.) |
| `open-now` | Show shops currently open |
| `amenities` | List all available amenity filters |
| `surprise` | Pick a random coffee shop (prefers open ones) |

## Search and Filter Examples

```bash
# Search by name (Hebrew or English)
python3 {baseDir}/scripts/jlm-coffee.py search "רוסטרס"
python3 {baseDir}/scripts/jlm-coffee.py search "Cafe Pepa"

# Filter by amenity
python3 {baseDir}/scripts/jlm-coffee.py filter wifi
python3 {baseDir}/scripts/jlm-coffee.py filter dogs
python3 {baseDir}/scripts/jlm-coffee.py filter kosher
python3 {baseDir}/scripts/jlm-coffee.py filter laptop

# Shops open right now
python3 {baseDir}/scripts/jlm-coffee.py open-now

# Full details for a shop
python3 {baseDir}/scripts/jlm-coffee.py get "בארוק"
python3 {baseDir}/scripts/jlm-coffee.py get EljFiggwObssQpypWMf0
```

## Options Reference

| Option | Commands | Description |
|--------|----------|-------------|
| `--json` | all | Output in JSON format (agent-friendly) |
| `--no-color` | all | Disable colored output (auto-detected for non-TTY) |

## Amenity Filters

| Key | Label | Aliases |
|-----|-------|---------|
| `wifi` | WiFi | |
| `dogs` | Dog-friendly | dog, dog-friendly |
| `laptop` | Laptop-friendly | laptops |
| `outdoor` | Outdoor seating | outside, terrace |
| `accessible` | Wheelchair accessible | wheelchair |
| `vegan` | Vegan options | |
| `kids` | Kid-friendly | children, kid-friendly |
| `quiet` | Quiet atmosphere | |
| `smoking` | Smoking area | |
| `local-roasting` | Local roasting | roasting |
| `sell-beans` | Sells beans | beans |
| `filter-coffee` | Filter coffee | filter |
| `kosher` | Kosher | |
| `open-saturday` | Open Saturday | saturday, shabbat |
| `power` | Power outlets | outlets |
| `parking` | Parking | |

## Workflow Example

```bash
# 1. Find shops with WiFi and look at the list
python3 {baseDir}/scripts/jlm-coffee.py filter wifi

# 2. Get details on one that looks good
python3 {baseDir}/scripts/jlm-coffee.py get "מטאפורה"

# 3. Check what's open right now
python3 {baseDir}/scripts/jlm-coffee.py open-now

# 4. Feeling lucky? Get a random pick
python3 {baseDir}/scripts/jlm-coffee.py surprise
```

## Notes

- **Community-curated**: All specialty coffee in Jerusalem, community-reviewed
- **Official data source**: Reads from a public JSON export provided by the site maintainer (no API key, no Firestore)
- **Bilingual**: Search works with Hebrew and English names
- **Opening hours**: Based on Google Places data, cached by the site
- **Reviews included**: Shop details show community reviews with ratings
- **Color output**: ANSI colors in terminal (respects `NO_COLOR` env var and `--no-color` flag)
- **CLI shortcut**: Install as `jlm-coffee` via symlink to the wrapper script
- **No dependencies**: Python stdlib only (urllib, json)
- **Fast caching**: 15-minute local cache TTL - one fetch covers all commands
