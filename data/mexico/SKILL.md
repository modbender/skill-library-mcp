---
name: Mexico
slug: mexico
version: 1.0.0
homepage: https://clawic.com/skills/mexico
changelog: "Initial release with city guides, coastal routes, and practical Mexico travel playbooks."
description: Discover Mexico like a local with concrete city tips, regional route planning, food guidance, and practical travel logistics.
metadata: {"clawdbot":{"emoji":"🇲🇽","requires":{"bins":[],"config":["~/mexico/"]},"os":["linux","darwin","win32"]}}
---

## Setup

If `~/mexico/` doesn't exist or is empty, read `setup.md` and start naturally.

## When to Use

User planning a trip to Mexico or asking for local insights: what to eat, where to base, what to skip, and how to handle transport, weather, and safety decisions.

## Architecture

Memory lives in `~/mexico/`. See `memory-template.md` for structure.

```
~/mexico/
└── memory.md     # Trip context
```

## Quick Reference

| Topic | File |
|-------|------|
| **Cities and Regions** | |
| Mexico City complete guide | `cdmx.md` |
| Oaxaca complete guide | `oaxaca.md` |
| Guadalajara complete guide | `guadalajara.md` |
| Yucatan and Riviera Maya complete guide | `yucatan-riviera-maya.md` |
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
| Hikes and altitude safety | `hiking.md` |
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
Do not say "do Mexico City food." Say "start with a market lunch in Roma Norte before 13:00, reserve dinner in Condesa or Juarez, and avoid peak queue windows in central tourist corridors."

### 2. Local Perspective
What locals and repeat travelers actually do, not brochure advice:
- Staying only in one high-tourist zone usually raises costs and lowers food quality
- Same-day transfer plans between distant regions look easy on maps but burn most of the day
- Midday heat and sun exposure can break beach and archaeological plans without pacing
- Historic centers are great, but neighborhood-level planning usually improves value and experience

### 3. Regional Differences

| Region | Key difference |
|--------|----------------|
| Mexico City | Museum and food density, strongest urban transit, neighborhood-driven planning |
| Oaxaca | Culture and cuisine depth, slower rhythm, day-trip craft and mezcal routes |
| Guadalajara and Jalisco | Urban culture plus Tequila day routes, balanced city value |
| Yucatan and Riviera Maya | Beaches, cenotes, ruins, and humidity-driven pacing needs |
| Baja California | Wine routes, desert-coast contrast, road-trip logic |
| Central Highlands | Colonial cities, cooler climate, culture-first itineraries |

### 4. Timing is Everything
- Dry season is usually easier for long route planning in many regions
- Rain and hurricane windows require flexible coastal itineraries
- Peak holiday weeks can change pricing and transfer reliability fast
- Urban museums and top restaurants perform better with weekday timing
- Heat index and UV intensity should shape daily plans, not just distance

### 5. Flag Tourist Traps
Be explicit about what to avoid:
- Paying premium prices in high-traffic restaurant strips without quality signal
- Attempting CDMX, Oaxaca, and Riviera Maya in a short trip with no buffer
- Overstacking ruins, beach time, and nightlife in one day in humid regions
- Ignoring airport-to-hotel transfer strategy until arrival

### 6. Match Trip Style

| Traveler | Focus on |
|----------|----------|
| Foodie | `food-guide.md`, `cdmx.md`, `oaxaca.md` |
| Culture and history | `regions.md`, `cdmx.md`, `oaxaca.md` |
| Beach and nature | `yucatan-riviera-maya.md`, `beaches.md`, `hiking.md` |
| Family | `with-kids.md`, `accommodation.md`, `itineraries.md` |
| Nightlife | `nightlife.md`, `cdmx.md`, `guadalajara.md` |
| Mixed route trip | `itineraries.md`, `transport.md`, `regions.md` |

## Common Traps

- Treating Mexico as one compact destination with easy transfers.
- Choosing too many bases for short trips.
- Booking key beach and holiday stays too late.
- Ignoring heat and humidity limits for outdoor-heavy days.
- Using only social-media spots with long queues and weak value.
- Assuming all areas have the same safety profile.

## Security & Privacy

**Data that stays local:** Trip preferences in `~/mexico/`

**This skill does NOT:** Access files outside `~/mexico/` or make network requests.

## Related Skills
Install with `clawhub install <slug>` if user confirms:
- `travel` — General trip planning and itinerary structuring
- `food` — Deeper restaurant and cuisine recommendations
- `spanish` — Language support for bookings and local communication
- `english` — Backup communication support for international logistics

## Feedback

- If useful: `clawhub star mexico`
- Stay updated: `clawhub sync`
