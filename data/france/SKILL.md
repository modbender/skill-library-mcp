---
name: France
slug: france
version: 1.0.0
homepage: https://clawic.com/skills/france
changelog: "Initial release with city guides, regional routing, and practical France travel playbooks."
description: Discover France like a local with concrete city advice, regional route planning, food context, and practical travel logistics.
metadata: {"clawdbot":{"emoji":"🇫🇷","requires":{"bins":[],"config":["~/france/"]},"os":["linux","darwin","win32"]}}
---

## Setup

If `~/france/` doesn't exist or is empty, read `setup.md` and start naturally.

## When to Use

User planning a trip to France or asking for local insights: what to prioritize, where to base, what to skip, and how to handle transport, timing, and budgeting.

## Architecture

Memory lives in `~/france/`. See `memory-template.md` for structure.

```
~/france/
└── memory.md     # Trip context
```

## Quick Reference

| Topic | File |
|-------|------|
| **Cities and Regions** | |
| Paris complete guide | `paris.md` |
| Lyon complete guide | `lyon.md` |
| Marseille and Provence complete guide | `marseille-provence.md` |
| French Riviera complete guide | `french-riviera.md` |
| **Planning** | |
| Sample itineraries | `itineraries.md` |
| Where to stay by style | `accommodation.md` |
| Useful apps | `apps.md` |
| **Food and Drink** | |
| Regional dishes and restaurant strategy | `food-guide.md` |
| Wine regions and tastings | `wine.md` |
| **Experiences** | |
| Signature experiences | `experiences.md` |
| Beaches and coastal strategy | `beaches.md` |
| Hikes and mountain safety | `hiking.md` |
| Nightlife by city and coast | `nightlife.md` |
| **Reference** | |
| Regions and route differences | `regions.md` |
| Culture, etiquette, expectations | `culture.md` |
| Traveling with children | `with-kids.md` |
| **Practical** | |
| Intercity transport and transfers | `transport.md` |
| Phone and internet | `telecoms.md` |
| Emergencies and safety | `emergencies.md` |

## Core Rules

### 1. Specific Over Generic
Do not say "do Paris highlights." Say "start museums early, shift to neighborhood lunch away from the biggest landmarks, then move to evening river-side or local bistro zones with a reservation."

### 2. Local Perspective
What locals and repeat travelers actually do, not brochure advice:
- Hyper-tourist blocks near landmark clusters often have weaker value for food
- One-night city hopping looks efficient on paper but burns time in station transfers
- Southern summer heat changes pacing for outdoor sightseeing and day trips
- Sundays and Mondays can change restaurant and shop availability by area

### 3. Regional Differences

| Region | Key difference |
|--------|----------------|
| Paris and Ile-de-France | Museum density, strongest rail access, reservation pressure |
| Lyon and Rhone corridor | Food-first city rhythm and easier urban pace |
| Provence and Marseille | Market culture, coast plus inland villages, heat-aware planning |
| French Riviera | Scenic coast with high seasonal pricing and congestion |
| Bordeaux and Atlantic | Wine routes, ocean towns, strong shoulder-season value |
| Alps and east routes | Mountain logistics, weather variability, activity-first trips |

### 4. Timing is Everything
- Shoulder months often deliver best value and crowd balance
- Peak summer requires earlier booking in coast and famous small towns
- Winter city breaks are great for museums and food with shorter daylight
- Rail strikes or disruptions can reshape route timing quickly
- Meal windows and reservation timing are major quality levers in France

### 5. Flag Tourist Traps
Be explicit about what to avoid:
- Eating every meal in landmark-adjacent restaurant rows
- Attempting Paris, Provence, and Riviera in a short trip with no transfer buffer
- Booking no-reservation weekends in high-demand dining zones
- Treating all Cote d'Azur beach towns as same-cost and same-crowd patterns

### 6. Match Trip Style

| Traveler | Focus on |
|----------|----------|
| Foodie | `food-guide.md`, `lyon.md`, `paris.md` |
| Culture and museums | `paris.md`, `regions.md`, `culture.md` |
| Coast and scenery | `french-riviera.md`, `beaches.md`, `experiences.md` |
| Family | `with-kids.md`, `accommodation.md`, `itineraries.md` |
| Nightlife | `nightlife.md`, `paris.md`, `marseille-provence.md` |
| Mixed route trip | `itineraries.md`, `transport.md`, `regions.md` |

## Common Traps

- Treating France as one compact destination with no transfer cost.
- Choosing too many bases for short trips.
- Ignoring reservation timing for top restaurants and museums.
- Overplanning summer days without heat and crowd buffers.
- Relying on car-first planning where rail is faster and lower stress.
- Assuming every town follows the same opening-hour rhythm.

## Security & Privacy

**Data that stays local:** Trip preferences in `~/france/`

**This skill does NOT:** Access files outside `~/france/` or make network requests.

## Related Skills
Install with `clawhub install <slug>` if user confirms:
- `travel` — General trip planning and itinerary structuring
- `food` — Deeper restaurant and cuisine recommendations
- `french` — Language support for local communication and bookings
- `english` — Backup communication support for multilingual travel

## Feedback

- If useful: `clawhub star france`
- Stay updated: `clawhub sync`
