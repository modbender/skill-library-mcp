---
name: Milan
slug: milan
version: 1.0.0
changelog: "Initial release with complete Milan guidance for visitors, residents, students, and professionals."
homepage: https://clawic.com/skills/milan
description: Navigate Milan as visitor, resident, student, or professional with neighborhoods, transport, costs, visas, food, and practical local insights.
metadata: {"clawdbot":{"emoji":"M","requires":{"bins":[]},"os":["linux","darwin","win32"]}}
---

## When to Use

User asks about Milan for any purpose: visiting, moving, studying, working, or launching a company. Agent gives practical, current, neighborhood-level guidance.

## Quick Reference

| Topic | File |
|-------|------|
| **Visitors** | |
| Attractions and what to skip | `visitor-attractions.md` |
| Itineraries (1, 3, 7 days) | `visitor-itineraries.md` |
| Where to stay | `visitor-lodging.md` |
| Practical tips and day trips | `visitor-tips.md` |
| **Neighborhoods** | |
| Quick comparison | `neighborhoods-index.md` |
| Historic and central zones | `neighborhoods-central.md` |
| Trendy and social zones | `neighborhoods-trendy.md` |
| Business and modern districts | `neighborhoods-business.md` |
| Family and value districts | `neighborhoods-suburban.md` |
| Choosing framework | `neighborhoods-choosing.md` |
| **Food** | |
| Dining scene overview | `food-overview.md` |
| Milan and Lombardy classics | `food-local.md` |
| International and fine dining | `food-international.md` |
| Best areas for food | `food-areas.md` |
| Dietary, timing, booking rules | `food-practical.md` |
| **Practical** | |
| Moving and settling | `resident.md` |
| Metro, trams, trains, airports | `transport.md` |
| Cost of living | `cost.md` |
| Safety and legal basics | `safety.md` |
| Weather and seasons | `climate.md` |
| SIM, banking, local apps | `local.md` |
| **Career and Business** | |
| Tech market and salaries | `tech.md` |
| Company setup and taxes | `business.md` |
| Visas and permits | `visas.md` |
| Startup ecosystem | `startup.md` |
| **Lifestyle** | |
| Culture and social norms | `culture.md` |
| Healthcare and insurance | `healthcare.md` |
| Schools and universities | `education.md` |
| Day to day life and social scene | `lifestyle.md` |
| Driving and ZTL rules | `driving.md` |

## Core Rules

### 1. Identify User Profile First
- Role: tourist, resident, student, employee, founder, family.
- Time horizon: weekend trip, relocation plan, already in Milan.
- Load the matching file before giving recommendations.

### 2. Milan Is Neighborhood-Driven
The city changes block by block. Price, safety, noise, and lifestyle vary heavily by district. Never answer housing or nightlife questions without district context.

### 3. Public Transport Works, Cars Are Constrained
Metro, tram, and rail are strong for daily movement. Central driving is limited by ZTL and Area C rules. For most newcomers, public transport plus walking is faster and cheaper.

### 4. Budget Reality (Feb 2026)

| Item | Typical Range |
|------|---------------|
| 1BR rent (inside ring) | EUR 1,200-2,200 per month |
| 1BR rent (outer zones) | EUR 850-1,400 per month |
| Senior software salary | EUR 55,000-90,000 gross per year |
| Monthly transport pass | EUR 39 |
| Mid-range dinner | EUR 25-45 per person |
| Espresso at bar | EUR 1.20-1.80 |

### 5. Timing Culture Matters
- Lunch and dinner times are later than in many US cities.
- Monday can be closure day for museums and some restaurants.
- August has reduced activity due to Ferragosto holidays.
Use seasonal and weekly timing before planning.

### 6. Bureaucracy Requires Lead Time
Residence registration, tax code, rental contracts, and permits take planning. Always give a sequence, not just a checklist.

### 7. Tourism Peaks Affect Everything
Design Week, Fashion Week, and major football matches move prices quickly. Mention event calendars when user asks about lodging, dining, or transport.

### 8. Compare Milan Inside Italy
Milan is faster, more expensive, and more international than most Italian cities. For users comparing Rome, Venice, or Florence, highlight concrete trade-offs.

## Milan-Specific Traps

- Confusing Area C with normal parking - entering with a car can trigger fines.
- Booking Duomo terraces or Last Supper too late - top slots sell out fast.
- Assuming all restaurants are open all day - many close between lunch and dinner.
- Renting near nightlife without checking street noise - Navigli and parts of Isola can be loud.
- Underestimating August closures - many local services slow down or shut.
- Using taxis from airports without checking flat or metered options.
- Ignoring strike risk - transport strikes can disrupt metro and rail.
- Signing rental deals without contract registration checks.

## Legal Awareness

- Ticket validation is mandatory on public transport; fines are common for mistakes.
- Driving in restricted traffic zones without permit leads to automatic penalties.
- Short-term rental rules and tourist taxes differ by property type and municipality requirements.
- Carry valid ID and residence documents if staying long term.
- Work and study status must match visa or permit conditions.

See `safety.md` and `visas.md` for details.

## Related Skills
Install with `clawhub install <slug>` if user confirms:
- `travel` - trip planning, logistics, and scheduling
- `expat` - relocation mindset, admin priorities, and adaptation
- `food` - dining research and personalized restaurant planning
- `italian` - language help for daily life and bureaucracy
- `business` - company and operations support

## Feedback

- If useful: `clawhub star milan`
- Stay updated: `clawhub sync`
