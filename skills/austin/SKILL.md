---
name: Austin
slug: austin
version: 1.0.0
homepage: https://clawic.com/skills/austin
description: Navigate Austin as visitor, relocator, tech worker, or entrepreneur with neighborhoods, transport, costs, visas, and Texas-specific insights.
metadata: {"clawdbot":{"emoji":"🤠","requires":{"bins":[]},"os":["linux","darwin","win32"]}}
---

## Setup

On first use, read `setup.md` for integration guidelines.

## When to Use

User asks about Austin, Texas for any purpose: visiting, relocating, working in tech, starting a business, or experiencing the music and food scene. Agent provides practical guidance with current data.

## Architecture

Memory lives in `~/.austin/`. See `memory-template.md` for structure.

```
~/.austin/
└── memory.md     # User context and preferences
```

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
| Central Austin (Downtown, East Side, South Congress) | `neighborhoods-central.md` |
| North Austin (Domain, Arboretum, Cedar Park) | `neighborhoods-north.md` |
| South Austin (Zilker, Barton Hills, Bouldin) | `neighborhoods-south.md` |
| East & Southeast (Mueller, Manor, Del Valle) | `neighborhoods-east.md` |
| West & Hill Country (Westlake, Lakeway, Bee Cave) | `neighborhoods-west.md` |
| Choosing guide | `neighborhoods-choosing.md` |
| **Food** | |
| Overview & dining scene | `food-overview.md` |
| BBQ (the definitive guide) | `food-bbq.md` |
| Tex-Mex & Mexican | `food-mexican.md` |
| Food trucks & trailers | `food-trucks.md` |
| Fine dining & international | `food-international.md` |
| Best areas for dining | `food-areas.md` |
| Practical (tipping, dietary, hours) | `food-practical.md` |
| **Music & Entertainment** | |
| Live music scene | `music-live.md` |
| SXSW guide | `music-sxsw.md` |
| ACL & festivals | `music-festivals.md` |
| Venues by genre | `music-venues.md` |
| **Practical** | |
| Moving & settling | `resident.md` |
| Transport (car culture vs alternatives) | `transport.md` |
| Cost of living | `cost.md` |
| Safety & laws | `safety.md` |
| Weather & seasonal tips | `climate.md` |
| Local services (utilities, DMV, taxes) | `local.md` |
| **Career** | |
| Tech industry & salaries | `tech.md` |
| Business setup & Texas LLC | `business.md` |
| Work visas & sponsorship | `visas.md` |
| Startups & VC scene | `startup.md` |
| **Lifestyle** | |
| Culture & customs | `culture.md` |
| Healthcare & insurance | `healthcare.md` |
| Schools & UT Austin | `education.md` |
| Outdoor lifestyle | `outdoors.md` |
| Driving & car ownership | `driving.md` |

## Core Rules

### 1. Identify User Context First
- **Role**: Tourist, relocator, tech worker, remote worker, entrepreneur, student
- **Timeline**: Short visit, planning to move, already there, considering Austin vs other cities
- Load relevant auxiliary file for details

### 2. The Tech Migration Hub
Austin has transformed into America's hottest tech destination. Key factors:
- **No state income tax**: Massive draw for high earners (CA refugees save 10-13%)
- **Major HQs relocated**: Tesla, Oracle, Charles Schwab, COTA
- **Big Tech campuses**: Apple ($1B), Google, Meta, Amazon, Dell HQ
- **Startup ecosystem**: 8th largest in US, strong VC presence
- **Remote work friendly**: Many California/NYC companies have Austin offices
See `tech.md` for industry details and `visas.md` for work authorization.

### 3. Cultural Context
Austin is Texas's liberal island but still fundamentally Texan:
- **Keep Austin Weird**: Local slogan supporting indie businesses
- **Music identity**: "Live Music Capital of the World" — taken seriously
- **Tex-Mex is religion**: Breakfast tacos are a daily ritual
- **Outdoor culture**: Running, biking, kayaking are lifestyle defaults
- **Casual dress**: Tech casual everywhere; suits are rare and suspicious
See `culture.md` for detailed guidance.

### 4. Weather Reality
- **Subtropical climate**: Mild winters, brutally hot summers
- **Best seasons**: Spring (Mar-May) and Fall (Oct-Nov) — 20-28C, gorgeous
- **Summer (Jun-Sep)**: Extreme heat (38-42C), everyone moves indoors
- **Winter (Dec-Feb)**: Mild (5-18C) but occasional ice storms
- **"Allergy capital"**: Cedar fever (Dec-Feb), oak (Mar-Apr) are severe
See `climate.md` for monthly breakdown and survival tips.

### 5. Current Data (Feb 2026)

| Item | Range |
|------|-------|
| 1BR rent (central) | $1,800-2,500/month |
| 1BR rent (suburbs) | $1,300-1,800/month |
| Median home price | $550,000+ |
| Senior SWE salary | $180,000-280,000/year |
| Junior SWE salary | $90,000-130,000/year |
| Gas price | $2.80-3.20/gallon |
| BBQ plate | $18-28 |
| Breakfast taco | $3-5 |
| Rideshare to airport | $25-40 |

### 6. Cost Reality
Austin is no longer cheap — the tech boom changed everything:
- **Housing**: Doubled in 5 years; crisis-level competition
- **No income tax**: Offset by high property taxes (~2.1% of home value)
- **Food & entertainment**: Reasonable for a tech hub
- **Car required**: Transit exists but car is near-essential
- **Healthcare**: Private insurance required; costs vary wildly
- **Savings vs CA**: Still significant, but gap narrowing

### 7. Transit Reality
Unlike coastal cities, Austin is car-centric:
- **Car**: Near-essential for most lifestyles
- **CapMetro buses**: Exist but limited coverage
- **MetroRail**: One line, commuter-focused, limited hours
- **Rideshare**: Uber/Lyft widely available
- **Biking**: Growing infrastructure, good in central areas
- **E-scooters**: Everywhere downtown, useful for short trips
- **I-35 traffic**: Legendary. Plan around it or suffer.
See `transport.md` for complete guide.

### 8. Neighborhood Matching

| Profile | Best Areas |
|---------|------------|
| Young tech workers | East Austin, Downtown, South Lamar |
| Families | Circle C, Steiner Ranch, Cedar Park |
| Remote workers | South Congress, Zilker, Mueller |
| Budget-conscious | Round Rock, Pflugerville, Manor |
| Luxury seekers | Westlake, Tarrytown, Lake Austin |
| Music lovers | East 6th, Red River, South Congress |
| Outdoor enthusiasts | Barton Hills, Zilker, Bee Cave |
| Students/young professionals | West Campus, North Loop, Hyde Park |

## The Austin Transformation

Understanding Austin requires knowing its recent history:
- **Pre-2010**: Affordable college town with great music scene
- **2010-2015**: Tech presence grows, "Silicon Hills" nickname sticks
- **2015-2020**: F1 arrives (COTA), growth accelerates, prices rise
- **2020-2021**: Pandemic exodus from CA; Tesla, Oracle announce moves
- **2021-2023**: Housing prices double, traffic worsens, "old Austin" mourned
- **2023-present**: Growth slows slightly, affordability crisis, infrastructure struggles

The city you'll find today is dramatically different from even 5 years ago.

## Austin-Specific Traps

- **Summer underestimation** — 40C+ heat is dangerous. Plan indoor activities Jun-Sep.
- **Franklin BBQ line** — 3-4 hour waits. Go at 8am or order ahead. Other BBQ is also great.
- **SXSW chaos** — Avoid downtown mid-March unless attending. Hotels 3x price.
- **Cedar fever** — Not a cold. Dec-Feb allergies devastate newcomers. Get tested.
- **"Central Austin" rent** — Listings say central, mean 20 min from downtown.
- **I-35 commute** — Never underestimate. 10 miles can be 45+ minutes at rush hour.
- **No zoning myths** — Austin has zoning, just different than CA/NY.
- **"Austin's changed" locals** — Yes, it has. They're not wrong. Be humble.
- **Property tax shock** — Calculate it: ~2.1% of assessed value annually.
- **Water restrictions** — Summer droughts mean strict watering rules.

## Legal Awareness

Key laws visitors/residents must know:
- **Marijuana**: Still illegal in Texas. Not decriminalized. Real arrests happen.
- **Open carry**: Legal for handguns (21+, no permit required as of 2021).
- **Alcohol**: Bars close at 2am. No public drinking. Some areas dry on Sundays.
- **Employment**: At-will state. Non-competes enforceable but limited.
- **Tenant rights**: Landlord-friendly state. Lease terms are usually final.
- **Vehicle inspection**: Annual requirement. Registration separate.
- **No state income tax**: But property and sales taxes are high.

See `safety.md` for comprehensive legal guidance.

## The Housing Reality (2026)

This deserves special attention:
- **Price explosion**: Median home from $300K (2019) to $550K+ (2026)
- **Competition**: Multiple offers, cash buyers, waived inspections common
- **Rent increases**: 30-50% in past 3 years in desirable areas
- **California factor**: Remote workers with CA salaries outbid locals
- **Local sentiment**: Significant resentment toward newcomers raising prices
- **As a newcomer**: Be aware you're part of a controversial dynamic. Don't lead with "I'm from California."

## Language & Communication

- **English dominant**: Minimal language barrier
- **Spanish useful**: ~35% Hispanic population, appreciated in many contexts
- **Texas phrases**: "Y'all" is standard, "Bless your heart" is not always kind
- **Direct communication**: Texans are friendly but direct
- **Small talk culture**: Strangers talk to you. It's normal.

## Related Skills
Install with `clawhub install <slug>` if user confirms:
- `dubai` — Another major expat destination
- `travel` — General travel planning
- `work` — Career and productivity

## Feedback

- If useful: `clawhub star austin`
- Stay updated: `clawhub sync`
