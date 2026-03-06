<div align="center">
<img src="assets/banner.jpg" alt="ClawCierge — Restaurant Search & Booking" width="100%">

# ClawCierge 🦞🍽️

**Finds and books restaurants worldwide.**  
Israel via direct API · Europe & NYC via browser handoff · Michelin + Time Out recommendations baked in.

[![Python](https://img.shields.io/badge/python-3.10+-blue)](https://github.com/yhyatt/clawcierge)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![OpenClaw Skill](https://img.shields.io/badge/OpenClaw-Skill-blue)](https://clawhub.com/skills/clawcierge)

</div>

---

## Platform Coverage

| Region | Platform | Method |
|--------|----------|--------|
| 🇮🇱 Israel | Ontopo + Tabit | Direct API |
| 🇫🇷🇮🇹🇲🇹 Europe | TheFork | Browser handoff |
| 🇺🇸 NYC | OpenTable + Resy | Browser handoff |
| 🌍 Worldwide | Michelin Guide | Direct API (Algolia) |

## Features

- **Multi-platform routing** — detects the right booking system per restaurant automatically
- **Michelin filter** — Bib Gourmand + Selected only; stars excluded by default
- **Curated lists** — TLV, NYC, Barcelona, Marseille, Genova, Messina, Valletta and more
- **No CC stored** — payment always via browser handoff, never raw card data in code
- **Israel-first** — Ontopo covers ~1000 IL restaurants; Tabit covers the rest

## Setup

```bash
pip install requests
export RESERVATION_EMAIL="your@email.com"
export RESERVATION_PHONE="+1234567890"
export GOOGLE_MAPS_API_KEY="your-key"  # optional
```

## Quick Start

```python
from unified import search_and_format

results = search_and_format("tel_aviv", date="2026-04-01", time="20:00", party_size=2)
print(results)
```

## Architecture

```
search_and_format()
    ├── recommender.py   — Michelin Algolia + Time Out
    ├── maps.py          — curated city lists
    ├── ontopo.py        — Israel direct API (Ontopo)
    ├── tabit.py         — Israel direct API (Tabit)
    ├── thefork.py       — Europe browser handoff
    └── opentable.py     — NYC browser handoff (OpenTable + Resy)
```

## Important Notes

- **Tabit `check_availability()` creates a real ~15 min hold** — always call `delete_temp_reservation()` on cancel
- **Ontopo `availability_search` is read-only** — safe to call freely
- **Michelin doesn't cover Israel** — fallback to curated Maps lists + Time Out for IL

## License

MIT © [Yonatan Hyatt](https://github.com/yhyatt)
