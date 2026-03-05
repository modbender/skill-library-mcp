---
name: Los Angeles
slug: los-angeles
version: 1.0.1
changelog: Minor refinements for consistency
description: Navigate Los Angeles as visitor, resident, tech worker, student, or creative with neighborhoods, transport, costs, safety, and local insights.
metadata: {"clawdbot":{"emoji":"🌴","requires":{"bins":[]},"os":["linux","darwin","win32"]}}
---

## When to Use

User asks about Los Angeles for any purpose: visiting, moving, working, studying, or pursuing entertainment/creative careers. Agent provides practical guidance with current data.

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
| Westside (Santa Monica, Venice, etc.) | `neighborhoods-westside.md` |
| Hollywood/Central | `neighborhoods-central.md` |
| South Bay | `neighborhoods-southbay.md` |
| Valley | `neighborhoods-valley.md` |
| East/Northeast | `neighborhoods-east.md` |
| **Food** | |
| Overview & what makes LA special | `food-overview.md` |
| Local specialties | `food-local.md` |
| By area | `food-areas.md` |
| Practical (apps, grocery, dietary) | `food-practical.md` |
| **Practical** | |
| Moving & settling | `resident.md` |
| Transport (car culture reality) | `transport.md` |
| Cost of living | `cost.md` |
| Safety | `safety.md` |
| Weather & microclimates | `climate.md` |
| Local services | `local.md` |
| **Career** | |
| Tech industry (Silicon Beach) | `tech.md` |
| Entertainment industry | `entertainment.md` |
| Students | `student.md` |
| Startups | `startup.md` |

## Core Rules

### 1. Identify User Context First
- **Role**: Tourist, resident, tech worker, student, creative/entertainment
- **Timeline**: Short visit, planning to move, already there
- Load relevant auxiliary file for details

### 2. Car Reality is Critical
LA is a car city. Period.
- 95% of life requires a car
- Metro is improving but limited
- Traffic: 405, 101, 10 are brutal at rush hour
- Budget $400-600/month for car costs
See `transport.md` for survival guide.

### 3. Weather Microclimates
| Myth | Reality |
|------|---------|
| "Always sunny" | Coastal = June Gloom (May-July fog) |
| "Same weather everywhere" | Valley is 10-15°F HOTTER than coast |
| "Never rains" | Rainy season Dec-Mar |

**Best weather:** September-November (warmest, clearest)

### 4. Current Data
| Item | Range |
|------|-------|
| 1BR rent | $2,000-3,000 (varies wildly by area) |
| Senior SWE salary | $180K-350K total comp |
| Car insurance | $150-300/month (HIGH) |
| Tacos | $2-4 each |

### 5. Tourist Traps
- Skip: Hollywood Walk of Fame (dirty, disappointing), Venice Beach boardwalk (sketchy)
- Do: Griffith Observatory (FREE, best views), Getty Center (FREE, world-class)
- Book ahead: Universal Studios, popular restaurants

### 6. Neighborhood Spread
LA is HUGE. Where you live = your lifestyle.

| Profile | Best Areas |
|---------|------------|
| Young tech workers | Santa Monica, Culver City, Playa Vista |
| Entertainment industry | West Hollywood, Los Feliz, Silver Lake |
| Families | Pasadena, South Bay, Studio City |
| Budget-conscious | Valley (Sherman Oaks, Burbank), Koreatown |
| Beach lifestyle | Santa Monica, Manhattan Beach, Venice |

### 7. Safety Varies Dramatically
- Generally safe but very block-dependent
- Areas to research carefully: parts of DTLA, Hollywood at night
- Car break-ins: less than SF but still common in tourist areas
See `safety.md` for specifics.

## LA-Specific Traps

- **"I don't need a car"** — You do. Metro is improving but not enough.
- **Hollywood glamour** — Hollywood Blvd is grimy and disappointing.
- **"Traffic isn't that bad"** — It is. Plan 1.5-2x Google Maps time.
- **Valley = undesirable** — Actually great value, more space, family-friendly.
- **Beach = best living** — Coastal fog May-July. Valley is sunnier.
- **Everything is close** — LA is 50+ miles across. Plan your life by area.
- **Universal over Disneyland** — Disneyland is better but in Anaheim (1+ hr).
