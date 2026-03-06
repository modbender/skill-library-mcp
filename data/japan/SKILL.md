---
name: Japan
slug: japan
version: 1.0.0
homepage: https://clawic.com/skills/japan
changelog: "Initial release with city guides, route planning, and practical Japan travel playbooks."
description: Discover Japan like a local with concrete city tips, regional route planning, food context, and practical travel logistics.
metadata: {"clawdbot":{"emoji":"🇯🇵","requires":{"bins":[],"config":["~/japan/"]},"os":["linux","darwin","win32"]}}
---

## Setup

If `~/japan/` doesn't exist or is empty, read `setup.md` and start naturally.

## When to Use

User planning a trip to Japan or asking for local insights: what to prioritize, where to base, what to skip, and how to handle transport, seasonality, and budgeting.

## Architecture

Memory lives in `~/japan/`. See `memory-template.md` for structure.

```
~/japan/
└── memory.md     # Trip context
```

## Quick Reference

| Topic | File |
|-------|------|
| **Cities and Regions** | |
| Tokyo complete guide | `tokyo.md` |
| Kyoto complete guide | `kyoto.md` |
| Osaka complete guide | `osaka.md` |
| Hiroshima and Miyajima complete guide | `hiroshima-miyajima.md` |
| **Planning** | |
| Sample itineraries | `itineraries.md` |
| Where to stay by style | `accommodation.md` |
| Useful apps | `apps.md` |
| **Food and Drink** | |
| Regional dishes and restaurant strategy | `food-guide.md` |
| Wine, sake, and whisky context | `wine.md` |
| **Experiences** | |
| Signature experiences | `experiences.md` |
| Beaches and island stops | `beaches.md` |
| Hikes and mountain safety | `hiking.md` |
| Nightlife by city | `nightlife.md` |
| **Reference** | |
| Regions and route differences | `regions.md` |
| Culture, etiquette, expectations | `culture.md` |
| Traveling with children | `with-kids.md` |
| **Practical** | |
| Intercity transport and passes | `transport.md` |
| Phone and internet | `telecoms.md` |
| Emergencies and safety | `emergencies.md` |

## Core Rules

### 1. Specific Over Generic
Do not say "do Tokyo highlights." Say "start Asakusa or Meiji-area mornings early, reserve one flagship dinner, then shift to neighborhood-level bars away from the busiest crossing zones."

### 2. Local Perspective
What locals and repeat travelers actually do, not brochure advice:
- One-night city hopping across long rail legs drains trip quality fast
- Major icon spots are best early or late, not peak midday
- Convenience-store meals are useful but should not replace regional food planning
- Small etiquette misses are avoidable with simple behavior adjustments

### 3. Regional Differences

| Region | Key difference |
|--------|----------------|
| Tokyo and Kanto | Dense urban options, best transit depth, high reservation pressure |
| Kyoto and Nara corridor | Heritage sites, temple density, stronger seasonality crowds |
| Osaka and Kansai | Food-first pace, lively nightlife, practical city value |
| Hiroshima and western Honshu | History focus plus island routes and calmer rhythm |
| Hokkaido | Nature, seafood, winter sports, wider distance logistics |
| Okinawa | Subtropical islands, beaches, distinct local culture |

### 4. Timing is Everything
- Cherry blossom and autumn foliage periods require early booking
- Golden Week and New Year windows can reshape transport availability
- Summer heat and humidity require slower daytime pacing
- Winter can be excellent for cities and snow regions with logistics planning
- Temple and museum quality improves with early start windows

### 5. Flag Tourist Traps
Be explicit about what to avoid:
- Eating only in landmark-adjacent strips with long lines and weak value
- Attempting Tokyo, Kyoto, Osaka, and Hiroshima in one short trip without buffer
- Buying rail passes without route math
- Stacking long transit day plus heavy nightlife and early temple start

### 6. Match Trip Style

| Traveler | Focus on |
|----------|----------|
| Foodie | `food-guide.md`, `osaka.md`, `tokyo.md` |
| Culture and temples | `kyoto.md`, `regions.md`, `culture.md` |
| City and nightlife | `tokyo.md`, `osaka.md`, `nightlife.md` |
| Family | `with-kids.md`, `accommodation.md`, `itineraries.md` |
| Nature and hiking | `hiking.md`, `experiences.md`, `regions.md` |
| Mixed route trip | `itineraries.md`, `transport.md`, `regions.md` |

## Common Traps

- Treating Japan as one compact destination with no transfer cost.
- Choosing too many bases for short trips.
- Ignoring restaurant and experience reservation timing.
- Underestimating summer heat and seasonal weather shifts.
- Not checking if a rail pass actually saves money on planned legs.
- Assuming etiquette is the same as other major destinations.

## Security & Privacy

**Data that stays local:** Trip preferences in `~/japan/`

**This skill does NOT:** Access files outside `~/japan/` or make network requests.

## Related Skills
Install with `clawhub install <slug>` if user confirms:
- `travel` — General trip planning and itinerary structuring
- `food` — Deeper restaurant and cuisine recommendations
- `japanese` — Language support for local communication and signage
- `english` — Backup communication support for multilingual travel

## Feedback

- If useful: `clawhub star japan`
- Stay updated: `clawhub sync`
