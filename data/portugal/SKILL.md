---
name: Portugal
slug: portugal
version: 1.0.0
homepage: https://clawic.com/skills/portugal
description: Discover Portugal like a local with specific restaurants, hidden gems, wine regions, and tips beyond the tourist traps.
metadata: {"clawdbot":{"emoji":"🇵🇹","requires":{"bins":[],"config":["~/portugal/"]},"os":["linux","darwin","win32"]}}
---

## Setup

If `~/portugal/` doesn't exist or is empty, read `setup.md` and start naturally.

## When to Use

User planning a trip to Portugal or wanting local insights: where to eat, what to skip, regional differences, fado, wine, beaches, hidden gems, and practical tips.

## Architecture

Memory lives in `~/portugal/`. See `memory-template.md` for structure.

```
~/portugal/
└── memory.md     # Trip context
```

## Quick Reference

| Topic | File |
|-------|------|
| **Cities** | |
| Lisbon complete guide | `lisbon.md` |
| Porto complete guide | `porto.md` |
| Sintra palaces & gardens | `sintra.md` |
| Algarve beaches & towns | `algarve.md` |
| **Planning** | |
| Sample itineraries | `itineraries.md` |
| Where to stay by city | `accommodation.md` |
| Useful apps | `apps.md` |
| **Food & Drink** | |
| Regional dishes, restaurants | `food-guide.md` |
| Wine regions & quintas | `wine.md` |
| **Experiences** | |
| Fado, surfing, festivals | `experiences.md` |
| Beach guide by coast | `beaches.md` |
| Hiking routes | `hiking.md` |
| Nightlife by city | `nightlife.md` |
| **Reference** | |
| Regions overview | `regions.md` |
| Culture, fado, saudade | `culture.md` |
| Traveling with children | `with-kids.md` |
| **Practical** | |
| Getting around | `transport.md` |
| Phone & internet | `telecoms.md` |
| Emergencies & safety | `emergencies.md` |

## Core Rules

### 1. Specific Over Generic
Don't say "try pastéis de nata in Lisbon". Say "Manteigaria in Chiado, Rua do Loreto 2, has the crispiest, warmest pastéis—€1.30 each, eat them standing at the counter within 30 seconds of coming out of the oven."

### 2. Local Perspective
What locals actually do, not what guides say:
- Pastéis de Belém queue = tourist ritual → Manteigaria or Aloma are better, no wait
- Bairro Alto dinner = tourist prices → Santos or Principe Real for locals
- Tram 28 = sardine can → walk Alfama or take Tram 12E
- Sangria = tourist drink → vinho verde or ginjinha

### 3. Regional Differences

| Region | Key difference |
|--------|----------------|
| Lisboa | Petiscos (small plates). Ginjinha culture. Fado in Alfama. |
| Porto | Francesinha mandatory. Port wine caves. More reserved people. |
| Alentejo | Slow pace. Porco preto. Wine country. Cork oak landscapes. |
| Algarve | Beach resort vibe. Fish/seafood. Cataplana. Tourist-heavy coast. |
| Douro | Wine valley. Quintas. Dramatic landscapes. |
| Madeira | Subtropical. Poncha. Levada walks. No beaches (rocks). |
| Azores | Green, volcanic. Whale watching. Cozido das Furnas. |

### 4. Timing is Everything
- Lunch: 12:30-15:00 (Portuguese take long lunches)
- Dinner: 20:00+ (kitchens don't really open before 19:30)
- August: Lisbon empties, everyone at beaches
- Sunday: Many restaurants closed, especially outside Lisbon/Porto
- Fado: Starts late, 21:30-22:00 minimum
- Shops: Many close 13:00-15:00 (less so in malls)

### 5. Flag Tourist Traps
Be explicit about what to avoid:
- Restaurants in Praça do Comércio with photos on menus
- Any restaurant with "traditional fado" signs and hawkers outside
- Overpriced seafood on Rua Augusta
- Canned sardines as "authentic souvenir" (locals don't eat them much)
- "Free" walking tours with guilt-trip donations
- €8 pastéis de Belém at the famous shop vs €1.30 elsewhere

### 6. Match Trip Style

| Traveler | Focus on |
|----------|----------|
| Foodie | food-guide.md, wine.md, porto.md |
| Beach | beaches.md, algarve.md |
| Culture | lisbon.md, sintra.md, culture.md |
| Adventure | hiking.md, experiences.md, azores/madeira in regions.md |
| Family | with-kids.md, beaches.md, algarve.md |
| Nightlife | nightlife.md, lisbon.md, porto.md |
| Wine | wine.md, regions.md (Douro, Alentejo) |

## Common Traps

- Queueing 45 min for Pastéis de Belém — same recipe everywhere, try Manteigaria
- Taking Tram 28 — pickpocket central, overcrowded, walk instead
- Eating at Ribeira waterfront in Porto — tourist prices, go uphill to Cedofeita
- Booking last-minute in August — beaches packed, book months ahead
- Tipping 15-20% like USA — not expected, round up or 5-10% max
- Paying in euros at bad exchange — always pay in local currency
- Renting car in Lisbon center — nightmare parking, use only for day trips
- Expecting beach weather in Lisbon — Atlantic is cold, even in summer (18-20°C)

## Security & Privacy

**Data that stays local:** Trip preferences in ~/portugal/

**This skill does NOT:** Access files outside ~/portugal/ or make network requests.

## Related Skills
Install with `clawhub install <slug>` if user confirms:
- `travel` — Travel planning
- `food` — Food and cooking
- `portuguese` — Portuguese language

## Feedback

- If useful: `clawhub star portugal`
- Stay updated: `clawhub sync`
