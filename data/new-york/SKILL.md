---
name: New York
slug: new-york
version: 1.0.0
description: Navigate New York City as visitor, resident, tech worker, student, or entrepreneur with neighborhoods, transport, costs, safety, and local insights.
metadata: {"clawdbot":{"emoji":"🗽","requires":{"bins":[]},"os":["linux","darwin","win32"]}}
---

## When to Use

User asks about NYC for any purpose: visiting, moving, working, studying, or starting a business. Agent provides practical guidance with current data.

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
| Manhattan | `neighborhoods-manhattan.md` |
| Brooklyn | `neighborhoods-brooklyn.md` |
| Queens | `neighborhoods-queens.md` |
| Choosing guide | `neighborhoods-choosing.md` |
| **Food** | |
| Overview & essentials | `food-overview.md` |
| NYC classics (pizza, bagels, deli) | `food-classics.md` |
| Ethnic neighborhoods | `food-ethnic.md` |
| Food halls & markets | `food-halls.md` |
| Budget & dietary | `food-practical.md` |
| **Practical** | |
| Moving & settling | `resident.md` |
| Transport | `transport.md` |
| Cost of living | `cost.md` |
| Safety | `safety.md` |
| Weather | `climate.md` |
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
NYC is one of the safest large US cities. Main concerns:
- Phone snatching (subway doors)
- Pickpocketing in tourist areas
- Package theft
See `safety.md` for area-specific guidance.

### 3. Weather Surprises
| Myth | Reality |
|------|---------|
| "Always cold" | Summers are HOT and humid (85°F+) |
| "Don't need AC" | July-August brutal without it |
| "Winters mild" | Can drop to 20°F, wind makes it worse |

**Best weather:** September-October (fall), April-May (spring)

### 4. Current Data
| Item | Range |
|------|-------|
| 1BR rent (Manhattan) | $4,200-5,600/mo |
| 1BR rent (Brooklyn) | $3,200-4,100/mo |
| Senior SWE salary | $220K-300K total comp |
| Student budget | $2,000-2,700/month |
| Subway single ride | $3.00 (OMNY caps at $35/week) |

### 5. Tourist Traps
- Skip: Times Square dining, Madame Tussauds, most of Little Italy
- Do: Free museums (Met, AMNH pay-what-you-wish for NY residents), Staten Island Ferry (FREE Statue views)
- Book ahead: Statue of Liberty crown (3-6 months), Broadway shows, hot restaurants

### 6. Transit is King
- Subway covers everything 24/7
- OMNY (contactless) = auto fare cap ($35/week)
- Taxis/Uber expensive — subway faster for most trips
- Citymapper app essential

### 7. Neighborhood Matching
| Profile | Best Areas |
|---------|------------|
| Young professionals | East Village, Williamsburg, LIC, Bushwick |
| Families | Park Slope, UWS, Astoria, Brooklyn Heights |
| Budget-conscious | Washington Heights, Jackson Heights, Crown Heights |
| Tech workers | Flatiron, DUMBO, LIC, Williamsburg |

## NYC-Specific Traps

- **Times Square dining** — Tourist prices, mediocre food. Walk 5 blocks for better.
- **Little Italy** — 2 blocks of overpriced tourist traps. Arthur Ave (Bronx) is real Italian.
- **Airbnb short stays** — Mostly illegal since Sept 2023. Use hotels.
- **Summer humidity** — Heat index makes 85°F feel like 100°F. Subway platforms brutal.
- **Phone snatching** — Most common crime. Don't use phone at subway doors.
- **Dollar pizza** — $1.50-2 now. Spend $4-5 for actual quality (Joe's, Scarr's).
