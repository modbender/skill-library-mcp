---
name: Ireland
slug: ireland
version: 1.0.1
homepage: https://clawic.com/skills/ireland
changelog: "Refined city and coastal guidance, expanded practical route-planning details, and improved travel traps coverage."
description: Discover Ireland like a local with concrete pubs, coastal routes, city guides, and practical trip-planning tips.
metadata: {"clawdbot":{"emoji":"🇮🇪","requires":{"bins":[],"config":["~/ireland/"]},"os":["linux","darwin","win32"]}}
---

## Setup

If `~/ireland/` doesn't exist or is empty, read `setup.md` and start naturally.

## When to Use

User planning a trip to Ireland or asking for local insights: where to eat, what to skip, which routes are realistic, and how to handle weather, driving, and timing.

## Architecture

Memory lives in `~/ireland/`. See `memory-template.md` for structure.

```
~/ireland/
└── memory.md     # Trip context
```

## Quick Reference

| Topic | File |
|-------|------|
| **Cities & Routes** | |
| Dublin complete guide | `dublin.md` |
| Cork complete guide | `cork.md` |
| Galway complete guide | `galway.md` |
| Wild Atlantic Way complete guide | `wild-atlantic-way.md` |
| **Planning** | |
| Sample itineraries | `itineraries.md` |
| Where to stay by style | `accommodation.md` |
| Useful apps | `apps.md` |
| **Food & Drink** | |
| Regional dishes and restaurants | `food-guide.md` |
| Wine bars, whiskey, tastings | `wine.md` |
| **Experiences** | |
| Signature experiences | `experiences.md` |
| Beaches and coastal stops | `beaches.md` |
| Hikes and safety by season | `hiking.md` |
| Nightlife by city | `nightlife.md` |
| **Reference** | |
| Regions and route differences | `regions.md` |
| Culture, etiquette, pub norms | `culture.md` |
| Traveling with children | `with-kids.md` |
| **Practical** | |
| Intercity transport and driving | `transport.md` |
| Phone and internet | `telecoms.md` |
| Emergencies and safety | `emergencies.md` |

## Core Rules

### 1. Specific Over Generic
Do not say "do a Dublin pub night." Say "start outside Temple Bar around 17:30, then move to a live-music pub in Smithfield or The Liberties before 20:00 to avoid peak tourist pricing and queues."

### 2. Local Perspective
What locals actually do, not brochure advice:
- Temple Bar is fun for one pass, but poor value for repeated nights
- Cliffs of Moher midday in peak season is crowded; early or late windows are better
- One-night county hopping looks efficient on paper but burns most of the day in transfers
- Coastal weather can change fast; always keep backup indoor options

### 3. Regional Differences

| Region | Key difference |
|--------|----------------|
| Dublin | Big-city pace, museums, nightlife, strongest transit |
| Cork & Kerry | Food-first towns plus scenic drives and peninsulas |
| Galway & Connemara | Music culture, compact city core, rugged west access |
| Wild Atlantic Way | Scenic coastline with long drive times and weather volatility |
| Ancient East corridor | Castles, heritage sites, easier short road loops |
| Border/North day trips | Great options, but needs ID and logistics awareness |

### 4. Timing is Everything
- Shoulder months (Apr-May, Sep-Oct) often give best value/crowd balance
- Peak summer requires early accommodation planning in popular coastal counties
- Winter city breaks are great for culture but daylight is short
- Weekend nightlife and event pricing can shift dramatically by city
- Route plans should include weather fallback time every day

### 5. Flag Tourist Traps
Be explicit about what to avoid:
- Overpaying for generic pub meals in highest-traffic blocks
- Attempting full-island loops in too few days
- Treating scenic drive distances as if roads were motorway-speed throughout
- Booking no-reservation weekends in high-demand food neighborhoods

### 6. Match Trip Style

| Traveler | Focus on |
|----------|----------|
| Foodie | `food-guide.md`, `cork.md`, `dublin.md` |
| Coastal scenery | `wild-atlantic-way.md`, `beaches.md`, `hiking.md` |
| Culture and history | `dublin.md`, `regions.md`, `culture.md` |
| Family | `with-kids.md`, `accommodation.md`, `itineraries.md` |
| Pub and music | `nightlife.md`, `galway.md`, `dublin.md` |
| Road-trip | `transport.md`, `itineraries.md`, `wild-atlantic-way.md` |

## Common Traps

- Trying to do Dublin, Cork, Galway, and full Wild Atlantic Way in one short trip.
- Not booking key summer stays early in west-coast areas.
- Assuming weather forecasts are stable all day on the coast.
- Driving narrow rural roads at unrealistic average speeds.
- Staying only in hyper-tourist nightlife zones and missing better-value neighborhoods.
- Forgetting to budget for peak-season transport and accommodation jumps.

## Security & Privacy

**Data that stays local:** Trip preferences in `~/ireland/`

**This skill does NOT:** Access files outside `~/ireland/` or make network requests.

## Related Skills
Install with `clawhub install <slug>` if user confirms:
- `travel` — General trip planning and itinerary structuring
- `food` — Deeper restaurant and cuisine recommendations
- `irish` — Irish language and local phrase support
- `english` — Booking and communication support

## Feedback

- If useful: `clawhub star ireland`
- Stay updated: `clawhub sync`
