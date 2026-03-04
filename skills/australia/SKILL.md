---
name: Australia
slug: australia
version: 1.0.0
homepage: https://clawic.com/skills/australia
changelog: "Initial release with expanded city-region guides, coast and outback routing, and practical Australia travel logistics."
description: Discover Australia like a local with deep city-region coverage, practical route planning, food context, and execution-ready travel logistics.
metadata: {"clawdbot":{"emoji":"🇦🇺","requires":{"bins":[],"config":["~/australia/"]},"os":["linux","darwin","win32"]}}
---

## Setup

If `~/australia/` doesn't exist or is empty, read `setup.md` and start naturally.

## When to Use

User planning a trip to Australia or asking for local insights: where to base, how to handle huge distances, what to prioritize by season, and how to manage transport, costs, weather, and safety.

## Architecture

Memory lives in `~/australia/`. See `memory-template.md` for structure.

```
~/australia/
└── memory.md     # Trip context
```

## Quick Reference

| Topic | File |
|-------|------|
| **Major Hubs and Regions** | |
| Sydney complete guide | `sydney.md` |
| Melbourne complete guide | `melbourne.md` |
| Brisbane and Gold Coast complete guide | `brisbane-gold-coast.md` |
| Cairns and Great Barrier Reef complete guide | `cairns-reef.md` |
| Adelaide and South Australia complete guide | `adelaide-sa.md` |
| Perth and Western Australia complete guide | `perth-wa.md` |
| Hobart and Tasmania complete guide | `hobart-tasmania.md` |
| Uluru and Red Centre complete guide | `uluru-red-centre.md` |
| Great Ocean Road complete guide | `great-ocean-road.md` |
| **Planning** | |
| Core itineraries | `itineraries.md` |
| Long-distance route patterns | `road-trips.md` |
| Where to stay by style | `accommodation.md` |
| Entry and biosecurity planning | `entry-and-biosecurity.md` |
| Useful apps | `apps.md` |
| **Food and Drink** | |
| Regional dishes and restaurant strategy | `food-guide.md` |
| Wine regions and bar strategy | `wine.md` |
| **Experiences** | |
| Signature experiences | `experiences.md` |
| Beaches and coastal planning | `beaches.md` |
| Hikes and trail safety | `hiking.md` |
| Nightlife by city type | `nightlife.md` |
| **Reference** | |
| Regions and route differences | `regions.md` |
| Culture, etiquette, expectations | `culture.md` |
| Seasonality and climate strategy | `seasonality.md` |
| Traveling with children | `with-kids.md` |
| Wildlife and outdoor safety | `wildlife-safety.md` |
| National parks and permits | `national-parks-and-permits.md` |
| **Practical** | |
| Intercity transport and flight/rail tradeoffs | `transport.md` |
| Phone and internet | `telecoms.md` |
| Payments and cost planning | `payment-and-costs.md` |
| Emergencies and safety | `emergencies.md` |

## Core Rules

### 1. Specific Over Generic
Do not say "do Australia highlights." Say "pick 2-3 anchors max for short trips, then build each around one urban cluster and one nature block with transfer buffers."

### 2. Local Perspective
What locals and repeat travelers actually do, not brochure advice:
- Australia rewards fewer bases with deeper local coverage
- Domestic transfer days often consume most useful daylight
- Weather windows can reshape coastal and outback plans quickly
- Car vs flight decisions should be route-specific, not ideology

### 3. Regional Differences

| Region | Key difference |
|--------|----------------|
| NSW (Sydney and coast) | Big-city pace plus coastal add-ons and strong weekend demand |
| Victoria (Melbourne and surrounds) | Food and culture density, strong road-trip overlays |
| Queensland | Tropical north, reef logic, humidity and cyclone-season considerations |
| South Australia | Wine and outback gateway routes, lower crowd pressure |
| Western Australia | Huge distances, premium nature routes, transfer-heavy planning |
| Tasmania | Cool-climate food and nature with weather-sensitive driving |
| NT Red Centre | Desert conditions, heat risk, sunrise/sunset pacing |

### 4. Timing is Everything
- Australian seasons are opposite to northern-hemisphere assumptions
- School holidays and long weekends can spike pricing and occupancy
- Wet season affects parts of tropical north route reliability
- Bushfire and heat periods can change road and park access
- Shoulder windows often give best crowd-value balance

### 5. Flag Tourist Traps
Be explicit about what to avoid:
- Trying Sydney, Melbourne, Uluru, and Reef in one short trip with no slack
- Overpaying in harbor/beach strips without quality checks
- Ignoring realistic self-drive fatigue on long open-road segments
- Treating every reef or outback day as weather-guaranteed

### 6. Match Trip Style

| Traveler | Focus on |
|----------|----------|
| Foodie | `food-guide.md`, `melbourne.md`, `sydney.md` |
| Coast and beaches | `beaches.md`, `cairns-reef.md`, `brisbane-gold-coast.md` |
| Nature and hiking | `hiking.md`, `hobart-tasmania.md`, `national-parks-and-permits.md` |
| Family | `with-kids.md`, `accommodation.md`, `itineraries.md` |
| Nightlife and city | `nightlife.md`, `sydney.md`, `melbourne.md` |
| Long route explorer | `road-trips.md`, `transport.md`, `seasonality.md` |

## Common Traps

- Treating Australia as one compact destination.
- Too many bases for the available days.
- Underestimating domestic flight and transfer overhead.
- Ignoring seasonal weather and bushfire dynamics.
- No backup plans for coastal or remote-day routes.
- Assuming late booking works in all regions year-round.

## Security & Privacy

**Data that stays local:** Trip preferences in `~/australia/`

**This skill does NOT:** Access files outside `~/australia/` or make network requests.

## Related Skills
Install with `clawhub install <slug>` if user confirms:
- `travel` — General trip planning and itinerary structuring
- `food` — Deeper restaurant and cuisine recommendations
- `english` — Communication support and booking clarity
- `booking` — Reservation and scheduling support workflows

## Feedback

- If useful: `clawhub star australia`
- Stay updated: `clawhub sync`
