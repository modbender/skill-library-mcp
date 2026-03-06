# Security Policy — OpenCLAW Tour Planner

## Honest Capability Summary

This skill makes **outbound HTTP requests** to public APIs and writes a **local performance cache** to disk. Here is exactly what it does and does not do.

---

## What This Skill DOES

| Capability | Detail |
|-----------|--------|
| **Outbound HTTP (read-only)** | Calls Nominatim, Wikivoyage, Open-Meteo, and optionally Visual Crossing |
| **Local disk cache** | Writes API responses to `~/.openclaw/cache/tour-planner.db` (SQLite) to reduce repeat API calls |
| **Reads env vars** | Reads `VISUAL_CROSSING_API_KEY` if set (optional — improves weather accuracy) |

## What This Skill Does NOT Do

- Does **not** store user travel plans, queries, or personal data
- Does **not** transmit any data to third parties beyond the listed APIs
- Does **not** contain hardcoded credentials or secrets
- Does **not** implement web scraping (Playwright is **not** a dependency — `ANALYSIS.md` is a design/roadmap document only)
- Does **not** require elevated OS privileges
- Does **not** install background daemons or persistent processes

---

## API Keys

### Core features — no key needed
The primary data sources (Nominatim, Wikivoyage, Open-Meteo) are **100% free and keyless**.

### Optional keys (improve accuracy)
| Key | Purpose | Where to get |
|-----|---------|-------------|
| `VISUAL_CROSSING_API_KEY` | Enhanced 15-day weather + historical data | [visualcrossing.com](https://www.visualcrossing.com/weather-api) (free tier: 1000 records/day) |
| `OPENWEATHER_API_KEY` | Alternative weather source | Optional fallback only |
| `AMADEUS_API_KEY` + `AMADEUS_API_SECRET` | Flight search (Phase 2, not yet implemented) | Not needed for current release |

---

## Local Cache (Disk Writes)

The skill caches API responses in a SQLite database at:
```
~/.openclaw/cache/tour-planner.db
```

**What is cached:** Raw API responses (geocoding results, weather forecasts, travel guides).  
**What is NOT cached:** User queries, itinerary content, or any personal information.  
**TTLs:** Geocoding 30 days · Wikivoyage guides 7 days · Weather 1 hour.

To disable or redirect the cache, set the `TOUR_PLANNER_CACHE_PATH` environment variable to a custom path, or delete the `.db` file at any time without affecting functionality.

---

## Dependencies

| Package | Purpose | Native build? |
|---------|---------|--------------|
| `axios` | HTTP client | No |
| `better-sqlite3` | Local response cache | **Yes** (native C++ binding) |

`better-sqlite3` builds a native module during `npm install`. It does **not** make network requests during build. Source: [github.com/WiseLibs/better-sqlite3](https://github.com/WiseLibs/better-sqlite3).

---

## About ANALYSIS.md

`ANALYSIS.md` is an **architecture design document** describing a potential future roadmap, including optional Playwright-based scrapers for flight and hotel data. This capability is **not implemented** in the current release — Playwright is not listed in `package.json` dependencies and no scraping code exists in `src/`. It documents possible future directions only.

---

## Reporting Issues

Open an issue at: https://github.com/Asif2BD/openclaw.tours/issues

## License

MIT — see repository root.
