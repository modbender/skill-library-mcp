---
name: Italy
slug: italy
version: 1.0.0
homepage: https://clawic.com/skills/italy
description: Discover Italy beyond the clichés with specific restaurants, hidden gems, and insights that only locals know.
metadata: {"clawdbot":{"emoji":"🇮🇹","requires":{"bins":[],"config":["~/italy/"]},"os":["linux","darwin","win32"]}}
---

## Setup

If `~/italy/` doesn't exist or is empty, read `setup.md` and start naturally.

## When to Use

User planning a trip to Italy or wanting local insights: where to eat, what to skip, regional differences, hidden gems, and practical tips.

## Architecture

Memory lives in `~/italy/`. See `memory-template.md` for structure.

```
~/italy/
└── memory.md     # Trip context
```

## Quick Reference

| Topic | File |
|-------|------|
| **Cities** | |
| Rome complete guide | `rome.md` |
| Florence complete guide | `florence.md` |
| Venice complete guide | `venice.md` |
| Naples & pizza guide | `naples.md` |
| **Planning** | |
| Sample itineraries | `itineraries.md` |
| Where to stay by city | `accommodation.md` |
| Useful apps | `apps.md` |
| **Food & Drink** | |
| Regional dishes, restaurants | `food-guide.md` |
| Wine regions & wineries | `wine.md` |
| **Experiences** | |
| Places, cooking classes, artisan visits | `experiences.md` |
| Beach guide by coast | `beaches.md` |
| Hiking routes | `hiking.md` |
| Nightlife by city | `nightlife.md` |
| **Reference** | |
| 20 regions, what makes each special | `regions.md` |
| Culture, etiquette, customs | `culture.md` |
| Traveling with children | `with-kids.md` |
| **Practical** | |
| Getting around, ZTL zones | `transport.md` |
| Phone & internet | `telecoms.md` |
| Emergencies & safety | `emergencies.md` |

## Core Rules

### 1. Specific Over Generic
Don't say "try pasta in Italy". Say "Da Enzo al 29 in Trastevere, Via dei Vascellari 29, has perfect cacio e pepe — €12, opens 12:00, closed Sunday, arrive 11:45 or wait 45 min."

### 2. Local Perspective
What locals actually do, not what guides say:
- Piazza Navona restaurants = tourist trap → Testaccio or Trastevere
- Venice San Marco = overpriced → bacari in Dorsoduro
- Cappuccino after 11am = tourist giveaway
- Alfredo pasta = doesn't exist in Italy

### 3. Regional Differences

| Region | Key difference |
|--------|----------------|
| Naples | Fork and knife for pizza. Street food culture. |
| Venice | No tipping. Bacari/cicchetti culture. |
| Florence | Tripe sandwiches (lampredotto). Steak cult. |
| Rome | Cacio e pepe, amatriciana, carbonara — no cream ever. |
| Milan | Aperitivo with free food. Fashion-conscious. |

### 4. Timing is Everything
- Riposo: 13:00-16:00 most shops close
- Lunch: 12:30-14:30 (main meal for many)
- Dinner: 20:00+ (no food before 19:30)
- August: Many close, locals flee to beaches
- Monday: Many museums closed

### 5. Flag Tourist Traps
Be explicit about what to avoid:
- Restaurants with photos on menus
- Waiters beckoning from doorways
- Any restaurant on Piazza San Marco
- "Fettuccine Alfredo" (invented for tourists)
- Gelato with bright, artificial colors

### 6. Match Trip Style

| Traveler | Focus on |
|----------|----------|
| Foodie | food-guide.md, wine.md, naples.md |
| Beach | beaches.md, regions.md |
| Culture | rome.md, florence.md, venice.md |
| Adventure | hiking.md, experiences.md |
| Family | with-kids.md, beaches.md |
| Nightlife | nightlife.md, rome.md, milan section |

## Common Traps

- Ordering cappuccino after breakfast — marks you as tourist
- Asking for Alfredo or chicken pasta — doesn't exist here
- Paying €5 for espresso at table — bar is €1-1.50
- Driving into ZTL zones — €100+ fine, cameras everywhere
- Buying tickets on-site — museums need advance booking
- Eating dinner before 20:00 — kitchen may not be ready
- Accepting "free" gifts from street sellers — they'll demand money

## Security & Privacy

**Data that stays local:** Trip preferences in ~/italy/

**This skill does NOT:** Access files outside ~/italy/ or make network requests.

## Related Skills
Install with `clawhub install <slug>` if user confirms:
- `travel` — Travel planning
- `food` — Food and cooking
- `italian` — Italian language

## Feedback

- If useful: `clawhub star italy`
- Stay updated: `clawhub sync`
