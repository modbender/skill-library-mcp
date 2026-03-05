---
name: Vienna
slug: vienna
version: 1.0.0
description: Navigate Vienna as visitor, resident, tech worker, student, or entrepreneur with neighborhoods, transport, costs, safety, and local insights.
metadata: {"clawdbot":{"emoji":"🏛️","requires":{"bins":[]},"os":["linux","darwin","win32"]}}
---

## When to Use

User asks about Vienna for any purpose: visiting, moving, working, studying, or starting a business. Agent provides practical guidance with current data.

## Quick Reference

| Topic | File |
|-------|------|
| **Visitors** | |
| Attractions (must-see vs skip) | `visitor-attractions.md` |
| Itineraries (1/3/7 days) | `visitor-itineraries.md` |
| Where to stay | `visitor-lodging.md` |
| Tips & day trips | `visitor-tips.md` |
| **Neighborhoods** | |
| Quick comparison | `neighborhoods-index.md` |
| Inner city (1st district) | `neighborhoods-central.md` |
| Inner belt (2nd-9th) | `neighborhoods-inner.md` |
| Southern districts (10th-12th) | `neighborhoods-south.md` |
| Western districts (13th-17th) | `neighborhoods-west.md` |
| Outer suburbs (18th-23rd) | `neighborhoods-outer.md` |
| Choosing guide | `neighborhoods-choosing.md` |
| **Food** | |
| Overview & restaurants | `food-overview.md` |
| Traditional Viennese | `food-traditional.md` |
| Coffee houses | `food-coffee.md` |
| Markets & Heurigen | `food-markets.md` |
| Dietary & tips | `food-practical.md` |
| **Practical** | |
| Moving & settling | `resident.md` |
| Transport | `transport.md` |
| Cost of living | `cost.md` |
| Safety | `safety.md` |
| Weather | `climate.md` |
| Local services | `local.md` |
| **Career** | |
| Tech industry | `tech.md` |
| Students | `student.md` |
| Startups | `startup.md` |

## Core Rules

### 1. Identify User Context First
- **Role**: Tourist, resident, tech worker, student, entrepreneur
- **Timeline**: Short visit, planning to move, already there
- Load relevant auxiliary file for details

### 2. Safety Context
Vienna is one of the world's safest major cities, consistently ranking #1 for quality of life. Main considerations:
- Very low violent crime rate
- Some pickpocketing at tourist spots (Stephansplatz, metro stations)
- Occasional phone snatching on U-Bahn
- Safe to walk alone at night in most areas
See `safety.md` for area-specific guidance.

### 3. Weather Expectations
- Continental climate — cold winters, warm summers
- Summer: Warm (25-32°C), occasional heatwaves
- Winter: Cold (−2 to 5°C), occasional snow
- Best months: May-June, September
- Christmas markets: Late November-December

### 4. Current Data (Feb 2026)

| Item | Range |
|------|-------|
| 1BR rent | €900-1,500 (central), €600-1,000 (outer) |
| Senior SWE salary | €55K-90K total comp |
| Student budget | €900-1,300/month |
| Monthly transit pass | €51 (annual €365) |

### 5. Tourist Traps
- Skip: Restaurants on Stephansplatz (overpriced), Prater's overpriced food stalls
- Do: Naschmarkt, Neubau (7th), Karmelitermarkt, traditional Beisln (local taverns)

### 6. Cultural Notes
Vienna has distinct characteristics that differ from other German-speaking cities:
- **Coffeehouses are institutions** — staying hours with one coffee is expected and welcome
- **Grüß Gott** — standard greeting (not "Hallo")
- **Austrians ≠ Germans** — cultural differences are significant, never conflate them
- **Indirect communication** — Viennese are more indirect than Germans
- **Title usage** — academic titles matter (Herr Doktor, Frau Magister)
- **Sunday closures** — most shops closed, restaurants and cafés open

### 7. Language
- Official: German (Austrian German, with distinct vocabulary)
- English widely spoken in tourist areas, universities, tech companies
- Some useful Austrian terms:
  - Servus = Hello/Goodbye (informal)
  - Grüß Gott = Hello (formal)
  - Melange = Cappuccino
  - Beisl = Traditional tavern
  - Heuriger = Wine tavern
  - Schmäh = Viennese humor/charm
