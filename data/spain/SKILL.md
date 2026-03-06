---
name: Spain
slug: spain
version: 1.0.0
homepage: https://clawic.com/skills/spain
description: Discover Spain like a local with specific restaurants, hidden gems, regional tips, and experiences beyond the tourist traps.
metadata: {"clawdbot":{"emoji":"🇪🇸","requires":{"bins":[],"config":["~/spain/"]},"os":["linux","darwin","win32"]}}
---

## Setup

If `~/spain/` doesn't exist or is empty, read `setup.md` and start naturally.

## When to Use

User planning a trip to Spain or wanting local insights: where to eat, what to skip, regional differences, festivals, hidden gems, and practical tips.

## Architecture

Memory lives in `~/spain/`. See `memory-template.md` for structure.

```
~/spain/
└── memory.md     # Trip context
```

## Quick Reference

| Topic | File |
|-------|------|
| **Cities** | |
| Madrid complete guide | `madrid.md` |
| Barcelona complete guide | `barcelona.md` |
| Sevilla complete guide | `sevilla.md` |
| San Sebastián & pintxos | `san-sebastian.md` |
| **Planning** | |
| Sample itineraries | `itineraries.md` |
| Where to stay by city | `accommodation.md` |
| Useful apps | `apps.md` |
| **Food & Drink** | |
| Regional dishes, restaurants | `food-guide.md` |
| Wine regions & bodegas | `wine.md` |
| **Experiences** | |
| Places, festivals, tips | `experiences.md` |
| Beach guide by coast | `beaches.md` |
| Hiking routes | `hiking.md` |
| Nightlife by city | `nightlife.md` |
| **Reference** | |
| 17 regions, what makes each special | `regions.md` |
| Culture, eating times, customs | `culture.md` |
| Traveling with children | `with-kids.md` |
| **Practical** | |
| Getting around | `transport.md` |
| Phone & internet | `telecoms.md` |
| Emergencies & safety | `emergencies.md` |

## Core Rules

### 1. Specific Over Generic
Don't say "try tapas in Spain". Say "Casa Dani in Mercado de la Paz has the best tortilla in Madrid, go at lunch."

### 2. Local Perspective
What locals actually do, not what guides say:
- Mercado San Miguel = tourist trap → San Fernando, Antón Martín better
- La Rambla = pickpockets → Gothic Quarter side streets
- Sangría = tourist → tinto de verano

### 3. Regional Differences

| Region | Key difference |
|--------|----------------|
| País Vasco | Pintxos not tapas. Pay by toothpicks. |
| Granada, Jaén | Free tapas with every drink |
| Valencia | Paella ONLY at lunch, never dinner |
| Cataluña | Politics sensitive. Catalan spoken. |

### 4. Timing is Everything
- Lunch: 14:00-16:00 (kitchen closed before)
- Dinner: 21:00+ (no food before 20:30)
- August: Everything closes, locals flee cities
- Monday: Many restaurants closed

### 5. Flag Tourist Traps
Be explicit about what to avoid:
- Overpriced food in main squares
- "Free" tours with guilt-trip tips
- Restaurants with photos on menus
- Any paella on Barcelona beach

### 6. Match Trip Style

| Traveler | Focus on |
|----------|----------|
| Foodie | food-guide.md, wine.md, san-sebastian.md |
| Beach | beaches.md, regions.md |
| Culture | madrid.md, barcelona.md, sevilla.md |
| Adventure | hiking.md, experiences.md |
| Family | with-kids.md, beaches.md |
| Nightlife | nightlife.md, barcelona.md, madrid.md |

## Common Traps

- Eating at 19:00 — kitchen closed, you'll wait hungry
- Visiting Barcelona/Madrid in August — locals gone, tourists everywhere, hot
- Tipping 20% like USA — not expected, just round up
- Paying with €50 bills — small places won't have change
- Beach clothes in city — Spaniards dress up more
- Trusting "best paella" signs in tourist zones

## Security & Privacy

**Data that stays local:** Trip preferences in ~/spain/

**This skill does NOT:** Access files outside ~/spain/ or make network requests.

## Related Skills
Install with `clawhub install <slug>` if user confirms:
- `travel` — Travel planning
- `food` — Food and cooking
- `spanish` — Spanish language

## Feedback

- If useful: `clawhub star spain`
- Stay updated: `clawhub sync`
