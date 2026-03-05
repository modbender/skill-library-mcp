---
name: Seattle
slug: seattle
version: 1.0.0
homepage: https://clawic.com/skills/seattle
description: Navigate Seattle as visitor, resident, or tech worker with neighborhoods, transport, costs, weather, and local insights.
metadata: {"clawdbot":{"emoji":"🌲","requires":{"bins":[]},"os":["linux","darwin","win32"]}}
---

## When to Use

User asks about Seattle for any purpose: visiting, moving, working in tech, studying, or enjoying Pacific Northwest lifestyle. Agent provides practical neighborhood, transport, cost, and lifestyle guidance.

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
| Downtown and Belltown | `neighborhoods-downtown.md` |
| Capitol Hill and Central District | `neighborhoods-central.md` |
| Queen Anne and Magnolia | `neighborhoods-queen-anne.md` |
| Ballard, Fremont, Wallingford | `neighborhoods-north.md` |
| Eastside (Bellevue, Kirkland, Redmond) | `neighborhoods-eastside.md` |
| South Seattle | `neighborhoods-south.md` |
| **Food** | |
| Overview and dining scene | `food-overview.md` |
| Local specialties (seafood, coffee) | `food-local.md` |
| International cuisine | `food-international.md` |
| Best areas for dining | `food-areas.md` |
| Practical (apps, grocery, dietary) | `food-practical.md` |
| **Practical** | |
| Moving and settling | `resident.md` |
| Transport (car vs transit reality) | `transport.md` |
| Cost of living | `cost.md` |
| Safety | `safety.md` |
| Weather (myth vs reality) | `climate.md` |
| Local services | `local.md` |
| **Career** | |
| Tech industry and salaries | `tech.md` |
| Startups and funding | `startup.md` |
| Students | `student.md` |
| Remote workers | `remote.md` |

## Core Rules

### 1. Identify User Context First
- **Role**: Tourist, resident, tech worker, student, outdoor enthusiast
- **Timeline**: Short visit, planning to move, already there
- Load relevant auxiliary file for details

### 2. Weather Reality
The Seattle rain reputation is exaggerated but the grey is real.

| Myth | Reality |
|------|---------|
| "Rains constantly" | 37 inches/year (less than NYC, Miami, Atlanta) |
| "Need umbrella always" | Light drizzle, locals rarely use umbrellas |
| "Always cloudy" | TRUE: 200+ overcast days/year |
| "No summer" | Jul-Sep is gorgeous (70-80F, sunny, dry) |

**Seasonal affective disorder is real.** Many residents use light therapy lamps October-March.

### 3. No State Income Tax
Washington has NO state income tax. This is a major draw for tech workers.
- California tech workers save 10-13% moving to Seattle
- Trade-off: Higher sales tax (10.25% in Seattle)
- Trade-off: Property taxes moderate but rising

### 4. Reference Data

| Item | Range |
|------|-------|
| 1BR rent (Capitol Hill) | $1,800-2,400/month |
| 1BR rent (Eastside) | $2,200-3,000/month |
| Senior SWE salary (L6) | $350K-500K total comp |
| Coffee (specialty) | $5-7 |
| Light rail monthly pass | $99 |
| Median home price | $850K |

### 5. Tech Hub Reality
Seattle metro is one of the top 3 tech hubs in the US.

| Company | Location | Notes |
|---------|----------|-------|
| Amazon | South Lake Union | HQ, 50K+ employees in Seattle |
| Microsoft | Redmond | HQ, massive campus |
| Meta | Bellevue | Large office, growing |
| Google | Kirkland, Seattle | Multiple offices |
| Apple | Seattle | Growing presence |

**Eastside vs Seattle:** Microsoft people live on Eastside (Bellevue, Kirkland, Redmond). Amazon people live in Seattle proper. The commute across Lake Washington is painful.

### 6. Neighborhood Matching

| Profile | Best Areas |
|---------|------------|
| Young tech (Amazon) | Capitol Hill, South Lake Union, Ballard |
| Young tech (Microsoft) | Bellevue, Kirkland, Redmond |
| Families | Eastside, West Seattle, North Seattle |
| Nightlife and culture | Capitol Hill |
| Hip and artsy | Fremont, Ballard |
| Quiet and nature | Magnolia, Queen Anne |
| Budget-conscious | South Seattle, Beacon Hill |

### 7. Transit is Improving
Seattle was car-dependent but light rail is changing that.

| Mode | Reality |
|------|---------|
| Light rail | Expanding rapidly, now reaches airport and Northgate |
| Buses | Extensive, reliable, free downtown (sometimes) |
| Car | Still needed for suburbs, Eastside, outdoor trips |
| Bike | Growing infrastructure, hilly but e-bikes help |

See `transport.md` for detailed breakdown.

## Seattle-Specific Traps

- **"It rains all the time"** - No. It's grey and drizzly, not heavy rain. Bring layers, not umbrella.
- **Underestimating the grey** - 200+ overcast days. SAD is real. Budget for light therapy.
- **Thinking Seattle = Eastside** - They're different worlds. 520/I-90 bridge traffic is brutal.
- **Skipping Pike Place morning** - Go at 9am. By noon it's tourist chaos.
- **Ignoring the Eastside** - Bellevue is a legit city now with great dining and safer feel.
- **Summer FOMO** - Everyone disappears to mountains/islands Jul-Sep. Book ahead.
- **Forgetting layers** - Morning fog, midday sun, evening chill. Layer up.
- **Capitol Hill = party only** - It's also the best walkable urban neighborhood.
- **Passive-aggressive locals** - "Seattle Freeze" is real. Making friends takes effort.

## Outdoor Context

Seattle's biggest draw is nature access. Within 1-3 hours:

| Destination | Distance | Best For |
|-------------|----------|----------|
| Mt. Rainier | 2h | Hiking, views |
| Olympic National Park | 2-3h | Rainforest, coast |
| San Juan Islands | 2h + ferry | Kayaking, orcas |
| Snoqualmie Falls | 30min | Easy day trip |
| Crystal Mountain | 2h | Skiing |
| North Cascades | 2-3h | Remote wilderness |

**REI flagship** is in Seattle for a reason. Outdoor gear is a lifestyle here.

## Coffee Culture

Seattle invented modern coffee culture (Starbucks, 1971). But locals drink at:

| Type | Examples |
|------|----------|
| Third-wave roasters | Victrola, Elm, Slate, Milstead |
| Classic Seattle | Caffe Vita, Espresso Vivace |
| Everywhere | Independent shops on every block |

**Ordering tip:** Just say what you want. No judgment. But expect baristas to care about their craft.

## Related Skills
Install with `clawhub install <slug>` if user confirms:
- `travel` — trip planning and logistics
- `dubai` — another city guide
- `negotiate` — salary and offer discussions

## Feedback

- If useful: `clawhub star seattle`
- Stay updated: `clawhub sync`
