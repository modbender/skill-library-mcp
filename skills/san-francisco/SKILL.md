---
name: San Francisco
slug: san-francisco
version: 1.1.0
description: Navigate San Francisco as visitor, resident, tech worker, student, or entrepreneur with neighborhoods, transport, costs, safety, and local insights.
metadata: {"clawdbot":{"emoji":"🌉","requires":{"bins":[]},"os":["linux","darwin","win32"]}}
---

## When to Use

User asks about San Francisco for any purpose: visiting, moving, working, studying, or starting a business. Agent provides practical guidance with current data.

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
| Central (Hayes, SoMa, Nob Hill) | `neighborhoods-central.md` |
| South (Mission, Castro, Noe) | `neighborhoods-south.md` |
| North (Marina, Pacific Heights) | `neighborhoods-north.md` |
| Outer (Richmond, Sunset) | `neighborhoods-outer.md` |
| **Food** | |
| Overview & restaurants | `food-overview.md` |
| Local specialties | `food-local.md` |
| By neighborhood | `food-areas.md` |
| Coffee, dietary, tips | `food-practical.md` |
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

### 2. Safety is Critical
SF has real safety concerns:
- Tenderloin, Mid-Market: ALWAYS avoid
- Car break-ins: NEVER leave anything visible
- Some areas vary block by block
See `safety.md` for specifics.

### 3. Weather Surprises
| Myth | Reality |
|------|---------|
| "California = warm" | SF summers are COLD and foggy |
| "Don't need jacket" | Always bring layers |
| "Sunny beaches" | Ocean Beach is often foggy |

**Best weather:** September-October (SF's real summer)

### 4. Current Data
| Item | Range |
|------|-------|
| 1BR rent | $2,500-3,500 (varies by neighborhood) |
| Senior SWE salary | $200K-400K+ total comp |
| Burrito | $12-15 |
| BART to SFO | ~$10 |

### 5. Tourist Traps
- Skip: Most of Fisherman's Wharf, Lombard Street drive, Union Square
- Do: Alcatraz (book ahead!), Golden Gate, Mission tacos
- Free: Golden Gate Park, Lands End, de Young tower views

### 6. Neighborhood Matching
| Profile | Best Areas |
|---------|------------|
| Young professionals | Mission, Marina, Hayes Valley |
| Families | Noe Valley, Cole Valley |
| Budget-conscious | Outer Sunset, Richmond |
| Tech workers | SoMa, Mission |
| AVOID | Tenderloin, Mid-Market, 6th-8th SoMa |

## SF-Specific Traps

- **Summer fog** — June-August are coldest. Sept-Oct are warmest.
- **Fisherman's Wharf** — Sea lions YES, everything else NO.
- **Tenderloin** — Never recommend housing, even if cheap.
- **Car break-ins** — #1 property crime. EMPTY your car completely.
- **Alcatraz** — Must book 2-4 weeks ahead. Sells out.
- **Hills** — Use Uber. Don't walk up Nob Hill exhausted.
- **Richmond dim sum** — Better than Chinatown.
