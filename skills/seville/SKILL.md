---
name: Seville
slug: seville
version: 1.0.0
homepage: https://clawic.com/skills/seville
description: Navigate Seville as visitor, resident, tech worker, student, or entrepreneur with neighborhoods, transport, costs, flamenco, and local insights.
metadata: {"clawdbot":{"emoji":"🏛️","requires":{"bins":[]},"os":["linux","darwin","win32"]}}
---

## When to Use

User asks about Sevilla for any purpose: visiting, moving, working, studying, or starting a business. Agent provides practical guidance with current data.

## Quick Reference

| Topic | File |
|-------|------|
| **Visitors** | |
| Attractions (must-see vs skip) | `visitor-attractions.md` |
| Itineraries (1/3/7 days) | `visitor-itineraries.md` |
| Where to stay | `visitor-lodging.md` |
| Tips and day trips | `visitor-tips.md` |
| **Neighborhoods** | |
| Quick comparison | `neighborhoods-index.md` |
| Centro and Santa Cruz | `neighborhoods-centro.md` |
| Triana | `neighborhoods-triana.md` |
| La Macarena | `neighborhoods-macarena.md` |
| Nervion and Los Remedios | `neighborhoods-modern.md` |
| Choosing guide | `neighborhoods-choosing.md` |
| **Food** | |
| Overview and tapeo culture | `food-overview.md` |
| Traditional Sevillian dishes | `food-traditional.md` |
| Best tapas bars and areas | `food-tapas.md` |
| Markets and food halls | `food-markets.md` |
| Dietary tips and Ramadan | `food-practical.md` |
| **Practical** | |
| Moving and settling | `resident.md` |
| Transport (metro, bus, bike) | `transport.md` |
| Cost of living | `cost.md` |
| Safety | `safety.md` |
| Weather and survival tips | `climate.md` |
| Local services (banks, SIM) | `local.md` |
| **Career** | |
| Tech industry and salaries | `tech.md` |
| Startups and coworking | `startup.md` |
| **Lifestyle** | |
| Feria and Semana Santa | `fiestas.md` |
| Flamenco (real vs tourist) | `flamenco.md` |
| Students and universities | `student.md` |

## Core Rules

### 1. Identify User Context First
- **Role**: Tourist, resident, tech worker, student, entrepreneur
- **Timeline**: Short visit, planning to move, already there
- Load relevant auxiliary file for details

### 2. Heat Reality
Sevilla has extreme summers that affect everything:
- **Summer (Jun-Sep)**: 35-45C regularly, July-August brutal
- **Best months**: Mar-May, Oct-Nov (20-28C, perfect)
- **Siesta culture**: Many businesses close 14:00-17:00
See `climate.md` for survival strategies.

### 3. Tapeo Culture
Sevilla's social life revolves around tapas hopping:
- **Free tapas**: Many bars include free tapa with each drink
- **Standing culture**: Crowded bars, no seats = good sign
- **Timing**: Lunch tapas 13:30-16:00, dinner 20:30-midnight
See `food-overview.md` and `food-tapas.md` for specifics.

### 4. Current Data (Feb 2026)

| Item | Range |
|------|-------|
| 1BR rent (Centro) | EUR 700-1,000/month |
| 1BR rent (Triana) | EUR 600-900/month |
| 1BR rent (outer) | EUR 450-650/month |
| Tech salary (mid) | EUR 28,000-42,000/year |
| Tapa + beer | EUR 2.50-4.00 |
| Monthly transport | EUR 40 (Tarjeta Multiviaje) |
| Cerveza (cana) | EUR 1.50-2.50 |

### 5. Semana Santa and Feria Impact
Two events transform the city annually:
- **Semana Santa** (Easter week): Processions, crowds, emotional atmosphere
- **Feria de Abril** (2 weeks after): Week-long party, casetas, flamenco dress
These are NOT tourist shows — they're core Sevillian identity. Planning around them is essential.
See `fiestas.md` for complete guide.

### 6. Spanish Schedule
Sevilla runs on late Spanish time:
- **Lunch**: 14:00-16:00 (restaurants don't open earlier)
- **Dinner**: 21:00-23:00 (earlier = tourist places)
- **Nightlife**: Starts 01:00+
- **Siesta**: 14:00-17:00, many shops closed
Adjust expectations or suffer closed doors.

### 7. Neighborhood Matching

| Profile | Best Areas |
|---------|------------|
| Young professionals | Alameda, Feria, Centro |
| Families | Nervion, Los Remedios, Porvenir |
| Budget-conscious | Macarena, Cerro del Aguila, San Pablo |
| Students | Macarena, Nervion (near universities) |
| Beach lifestyle | N/A (beach is 1h+ away) |
| Remote workers | Alameda, Triana, Centro |
| Short-term visitors | Santa Cruz, Centro, Arenal |

### 8. Language Context
- **Spanish**: Everyone speaks it, Sevillian accent is strong
- **English**: Limited outside tourist areas and tech companies
- **Accent**: Sevillanos "eat" consonants (s, d at end of words)
- **Key phrases**: "Quillo" (mate), "mi arma" (endearment), "vamo a ve" (let's see)
Learn basic Spanish — it transforms the experience.

## Sevilla-Specific Traps

- **Summer heat underestimation** — 45C is real. July-August visitors must plan indoor activities.
- **Siesta timing** — Shops close 14:00-17:00. Plan morning and evening activities.
- **Eating too early** — Restaurant at 19:00 = empty tourist trap. Real places fill at 21:30+.
- **Flamenco tourist shows** — Tablao in Santa Cruz = expensive mediocrity. Real flamenco is in Triana bars.
- **Feria without caseta** — Feria casetas are private. Without local invite, limited access.
- **Semana Santa weekend trip** — Book hotels 6+ months ahead. Everything triples in price.
- **Street parking Centro** — Don't. ZBE zone, constant tickets, risk of theft.
- **Cash assumptions** — Many tapas bars are card-only now, but smaller places still cash-only.
- **Beach expectations** — Nearest beach is Matalascanas (1h+). Sevilla is NOT coastal.
- **AC in old buildings** — Historic center apartments often lack proper AC. Verify before renting.

## Comparing with Other Spanish Cities

| Aspect | Sevilla | Madrid | Barcelona |
|--------|---------|--------|-----------|
| Cost | Lower | Highest | High |
| Heat | Extreme summers | Hot but manageable | Mediterranean |
| Beach | 1h+ away | None | In city |
| Tech scene | Growing | Largest | Second |
| English | Limited | Good | Good |
| Nightlife | 01:00+ start | 01:00+ start | Earlier |
| Character | Traditional, festive | Cosmopolitan | Catalan, modern |

Sevilla is cheaper, more traditional, and has the strongest local identity of major Spanish cities.

## Related Skills
Install with `clawhub install <slug>` if user confirms:
- `dubai` — Expat-heavy city guide with neighborhoods, costs, visas
- `travel` — General travel planning and trip organization
- `spanish` — Spanish language learning and practice

## Feedback

- If useful: `clawhub star seville`
- Stay updated: `clawhub sync`
