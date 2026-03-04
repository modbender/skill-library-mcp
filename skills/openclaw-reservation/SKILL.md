---
name: clawcierge
description: Restaurant search and booking for OpenClaw. Finds and books restaurants worldwide — Israel via direct API (Ontopo + Tabit), Europe and NYC via browser handoff (TheFork, OpenTable, Resy). Michelin Bib Gourmand and Time Out recommendations baked in. Use when someone wants to find a restaurant, check availability, or book a table.
metadata:
  openclaw:
    env:
      - RESERVATION_EMAIL
      - RESERVATION_PHONE
      - GOOGLE_MAPS_API_KEY
---

# ClawCierge — Restaurant Booking for OpenClaw

<div align="center">
<img src="assets/banner.jpg" alt="ClawCierge — Restaurant Search & Booking" width="100%">
</div>

Finds and books restaurants worldwide. Israel via direct API, Europe and NYC via browser handoff, with Michelin and Time Out recommendations baked in.

## Platform Coverage

| Region | Platform | Method |
|--------|----------|--------|
| 🇮🇱 Israel | Ontopo + Tabit | Direct API |
| 🇫🇷🇮🇹 Europe | TheFork | Browser handoff |
| 🇺🇸 NYC | OpenTable + Resy | Browser handoff |
| 🌍 Worldwide | Michelin Guide (Algolia) | Direct API |

## Setup

```bash
pip install requests
export RESERVATION_EMAIL="your@email.com"
export RESERVATION_PHONE="+1234567890"
export GOOGLE_MAPS_API_KEY="your-key"  # optional — for live ratings
```

## Usage

```python
from unified import search_and_format

# Search + recommend
results = search_and_format(
    city="tel_aviv",
    date="2026-04-01",
    time="20:00",
    party_size=2
)
print(results)

# Israel direct booking (Ontopo)
from ontopo import OntopoCli
client = OntopoCli()
slots = client.availability_search("taizu", date="20260401", time="2000", size="2")

# Israel direct booking (Tabit)
from tabit import TabitCli
tabit = TabitCli()
avail = tabit.check_availability(org_id="...", date="2026-04-01", time="20:00", party_size=2)
```

## Recommendation Sources

- **Michelin Guide** — Bib Gourmand + Selected/Plate (no stars by default)
- **Time Out** — city-specific curated lists
- **Curated lists** — TLV, NYC, Barcelona, Marseille, Genova, Messina, Valletta

## Key Design Decisions

- **No CC stored** — payment always via browser handoff
- **Tabit hold is real** — `check_availability()` creates a ~15 min hold; call `delete_temp_reservation()` on cancel
- **Ontopo search is read-only** — no hold created
- **Michelin filter** — always `BIB_GOURMAND` or `selected`; never 1/2/3-star

## Supported Cities

Israel (TLV · Haifa · Beer Sheva), Marseille, Genova, Messina, Valletta, NYC, Barcelona, London, Lisbon, Prague, Athens

## License

MIT
