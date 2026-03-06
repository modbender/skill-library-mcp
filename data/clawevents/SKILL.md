---
name: clawevents
description: Multi-city event discovery for Tel Aviv, Barcelona, and New York. Searches concerts, jazz, cinema, theatre, nightlife, family events, comedy, art, and festivals. Supports filtering by age group (kids/family/adults), time of day (morning/afternoon/evening/late-night), date range, and free-only. Returns ranked, deduplicated results from multiple sources per city.
version: 0.1.0
homepage: https://github.com/yhyatt/clawevents
metadata: {"kai": {"emoji": "🎉", "category": "lifestyle", "cities": ["tel-aviv", "barcelona", "new-york"]}}
---

# ClawEvents 🎉

Multi-city event discovery — Tel Aviv, Barcelona, New York.

## Triggers

- "What's on in Tel Aviv this weekend?"
- "Find jazz concerts in Barcelona next week"
- "Cinema in Tel Aviv tonight"
- "Free family events in NYC this Saturday"
- "Events in Tel Aviv and Barcelona for the group trip"
- "Lev Cinema schedule this week"
- "Live music in New York, adults only, evening"

## CLI Usage

```bash
# Basic search
python3 -m clawevents search --city tel-aviv --days 7

# Jazz in Tel Aviv this week
python3 -m clawevents search --city tel-aviv --type jazz --days 7

# Cinema tonight (Lev + others)
python3 -m clawevents search --city tel-aviv --type cinema --days 1

# Multi-city: what's on in Barcelona and NYC this weekend
python3 -m clawevents search --city barcelona new-york --days 3

# Family events, free, afternoon
python3 -m clawevents search --city tel-aviv --type family --age family --time afternoon --free

# Concert, adults, evening, specific dates
python3 -m clawevents search --city tel-aviv barcelona --type concert --age adults --time evening --from 2026-06-21 --to 2026-06-27

# JSON output (for programmatic use)
python3 -m clawevents search --city new-york --type jazz --format json --limit 10
```

## Supported Cities

| City | Alias | Sources |
|------|-------|---------|
| Tel Aviv | `tel-aviv`, `tlv` | TLV Municipality API, Eventbrite, Lev Cinema |
| Barcelona | `barcelona`, `bcn` | Ticketmaster, Eventbrite |
| New York | `new-york`, `nyc` | Ticketmaster, Eventbrite, NYC Open Data |

## Event Types

`jazz` · `concert` / `music` · `cinema` / `movie` · `theatre` · `nightlife` · `family` / `kids` · `comedy` · `art` · `sport` · `festival` · `community`

## Filters

| Flag | Values | Default |
|------|--------|---------|
| `--type` | jazz, concert, cinema, theatre, ... | all |
| `--age` | kids, family, adults | all |
| `--time` | morning, afternoon, evening, late-night | all |
| `--from` / `--to` | YYYY-MM-DD | today / +7d |
| `--days` | integer | 7 |
| `--free` | flag | false |
| `--limit` | integer | 20 |
| `--format` | text, json | text |

## Setup

### Install dependencies
```bash
cd skills/clawevents
pip3 install -r requirements.txt
```

### API Keys (optional but recommended)

| Key | Source | Cities unlocked |
|-----|--------|-----------------|
| `TICKETMASTER_API_KEY` | [developer.ticketmaster.com](https://developer.ticketmaster.com) — free | Barcelona, NYC |
| `EVENTBRITE_TOKEN` | [eventbrite.com/platform/api](https://www.eventbrite.com/platform/api) — free | All 3 |
| `TLV_API_KEY` | [apiportal.tel-aviv.gov.il](https://apiportal.tel-aviv.gov.il) — free | Tel Aviv (official events) |

Without API keys: Tel Aviv scrapes TLV website; Barcelona/NYC use Eventbrite free tier only + NYC Open Data.

Add to `~/.zshrc` or `~/.bashrc`:
```bash
export TICKETMASTER_API_KEY="your_key"
export EVENTBRITE_TOKEN="your_token"
export TLV_API_KEY="your_key"         # optional
```

## Data Sources

### Tel Aviv
- **TLV Municipality API** — Official city events (DigiTel source). Free with API key.
- **Eventbrite** — Tech, community, cultural events
- **Lev Cinema** — Boutique cinema (Dizengoff). Web scrape.
- *(planned)* Time Out Israel scraper — jazz, clubs, theatre picks

### Barcelona
- **Ticketmaster Discovery API** — Concerts, theatre, sports, 230K+ events
- **Eventbrite** — Community + cultural events
- *(planned)* Fever/Xceed scraper — nightlife, club events, immersive experiences

### New York
- **Ticketmaster Discovery API** — Concerts, Broadway, sports
- **Eventbrite** — Community events
- **NYC Open Data** — Free parks events, city programmes

## Architecture

```
ClawEventsEngine
├── Fetchers (parallel, per-city)
│   ├── TLVMunicipalityFetcher  → Tel Aviv
│   ├── TicketmasterFetcher     → Barcelona, NYC
│   ├── EventbriteFetcher       → All cities
│   ├── LevCinemaFetcher        → Tel Aviv (cinema)
│   └── NYCOpenDataFetcher      → NYC (free events)
├── Filter layer  (types, age, time-of-day, date, free)
├── Dedup layer   (same title + time across sources)
└── Rank layer    (chronological, no-time events last)
```

## Extending

To add a new city or source:
1. Create `clawevents/fetchers/your_source.py` implementing `BaseFetcher`
2. Register in `_FETCHER_REGISTRY` and `_CITY_FETCHERS` in `engine.py`
3. Add city alias in `cli.py`
