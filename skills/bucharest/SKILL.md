---
name: Bucharest
slug: bucharest
version: 1.0.0
homepage: https://clawic.com/skills/bucharest
description: Navigate Bucharest as visitor, resident, tech worker, student, or entrepreneur with neighborhoods, transport, costs, visas, and local insights.
metadata: {"clawdbot":{"emoji":"🏛️","requires":{"bins":[]},"os":["linux","darwin","win32"]}}
---

## When to Use

User asks about Bucharest for any purpose: visiting, moving, working, studying, or starting a business. Agent provides practical guidance with current data.

## Quick Reference

| Topic | File |
|-------|------|
| **Setup** | |
| Memory template | `memory-template.md` |
| **Visitors** | |
| Attractions (must-see vs skip) | `visitor-attractions.md` |
| Itineraries (1/3/7 days) | `visitor-itineraries.md` |
| Where to stay | `visitor-lodging.md` |
| Tips & day trips | `visitor-tips.md` |
| **Neighborhoods** | |
| Quick comparison | `neighborhoods-index.md` |
| Old Town & Center | `neighborhoods-center.md` |
| Floreasca & Dorobanți | `neighborhoods-north.md` |
| Pipera & Băneasa | `neighborhoods-expat.md` |
| Emerging & budget areas | `neighborhoods-emerging.md` |
| Choosing guide | `neighborhoods-choosing.md` |
| **Food** | |
| Overview & dining scene | `food-overview.md` |
| Romanian cuisine | `food-local.md` |
| International & fine dining | `food-international.md` |
| Best areas for dining | `food-areas.md` |
| Practical (markets, delivery) | `food-practical.md` |
| **Practical** | |
| Moving & settling | `resident.md` |
| Transport (metro, buses, taxis) | `transport.md` |
| Cost of living | `cost.md` |
| Safety & laws | `safety.md` |
| Weather & seasonal tips | `climate.md` |
| Local services (banking, SIM) | `local.md` |
| **Career** | |
| Tech industry & salaries | `tech.md` |
| Business setup & taxes | `business.md` |
| Visas & residency | `visas.md` |
| Startups & funding | `startup.md` |
| **Lifestyle** | |
| Culture & customs | `culture.md` |
| Healthcare | `healthcare.md` |
| Schools & education | `education.md` |
| Expat lifestyle & social | `lifestyle.md` |
| Driving & car ownership | `driving.md` |

## Core Rules

### 1. Identify User Context First
- **Role**: Tourist, resident, tech worker, student, entrepreneur
- **Timeline**: Short visit, planning to move, already there
- Load relevant auxiliary file for details

### 2. EU Member Advantage
Romania joined EU in 2007. Key implications:
- **EU/EEA citizens**: No visa needed, free movement
- **Non-EU**: Schengen visa for short stays, work permit for employment
- **Euro not adopted**: Uses Romanian Leu (RON), but EUR widely accepted in tourist areas
- **Digital nomads**: Growing infrastructure, no specific visa yet but tourist visa allows 90 days
See `visas.md` for current requirements and processes.

### 3. Cultural Context
Bucharest blends Eastern European traditions with rapid modernization:
- **Language**: Romanian (Latin-based), English widely spoken by young people
- **Religion**: Orthodox Christian majority, churches everywhere
- **Tipping**: 10% standard, often not included in bill
- **Smoking**: Banned indoors since 2016, but terraces common
See `culture.md` for detailed guidance.

### 4. Weather Reality
- **Summer (Jun-Aug)**: 30-35°C, can reach 40°C in heatwaves
- **Winter (Dec-Feb)**: -5 to 5°C, snow common, can drop to -15°C
- **Spring/Autumn**: Pleasant 15-25°C, ideal for visiting
- **Indoor heating**: Universal, winters are comfortable indoors
See `climate.md` for monthly breakdown and seasonal tips.

### 5. Current Data (Feb 2026)

| Item | Range |
|------|-------|
| 1BR rent (Center) | €500-800/month |
| 1BR rent (Floreasca) | €600-1,000/month |
| Senior SWE salary | €3,500-6,000/month net |
| Metro monthly pass | 80 RON (~€16) |
| Dinner for two (mid-range) | 200-350 RON (~€40-70) |
| International school fees | €8,000-20,000/year |

### 6. Cost Reality
Bucharest is very affordable compared to Western Europe:
- **Housing**: 30-40% of budget, still cheap by EU standards
- **Food**: Excellent value, local restaurants very affordable
- **Healthcare**: Public free for residents, private affordable (~€50/consultation)
- **Transport**: Extremely cheap, metro/bus passes under €20/month
- **Utilities**: Low compared to Western Europe (~€100-150/month total)

### 7. Transit Options
Bucharest has decent public transit:
- **Metro**: 4 lines, covers main areas, fast and reliable
- **Buses/Trams/Trolleys**: Extensive network, can be crowded
- **Ride-hailing**: Bolt, Uber — very popular and cheap (~€3-5 most rides)
- **Driving**: Possible but traffic is notorious, parking difficult in center
Many residents use a combination. See `transport.md` and `driving.md`.

### 8. Neighborhood Matching

| Profile | Best Areas |
|---------|------------|
| Young professionals | Floreasca, Dorobanți, Aviatorilor |
| Families (expat) | Pipera, Băneasa, Corbeanca |
| Students | Regie, Politehnica area, Cotroceni |
| Budget-conscious | Titan, Berceni, Drumul Taberei |
| Nightlife lovers | Old Town (Centru Vechi), Lipscani |
| Quiet residential | Primăverii, Herăstrău area |

## Tech Hub Context

Bucharest is Romania's Silicon Valley:
- **Major employers**: UiPath (unicorn), Bitdefender, eMag, local offices of Google, Amazon, Microsoft
- **Tech parks**: Pipera area has most tech offices
- **Outsourcing hub**: Many Western companies have dev centers
- **Startup scene**: Growing fast, several incubators and VCs
- **Salaries**: High for Romania, competitive for Eastern Europe

See `tech.md` and `startup.md` for detailed industry information.

## Bucharest-Specific Traps

- **Traffic underestimation** — Rush hours (7-10am, 5-8pm) are brutal. Metro is faster.
- **Street numbering** — Often confusing, use Google Maps pin not address.
- **Taxi scams** — ONLY use apps (Bolt, Uber). Never hail on street.
- **ATM fees** — Use Revolut or withdraw from BRD/BCR ATMs to avoid fees.
- **Card acceptance** — Improving but always carry some cash for small shops.
- **Stray dogs** — Reduced dramatically but still present in suburbs.
- **Winter potholes** — Streets deteriorate in winter, watch your step.
- **Heating schedule** — Central heating in old buildings is on city schedule.
- **Romanian time** — "5 minutes" can mean 20. Factor in flexibility.
- **Sunday closures** — Many shops close or reduce hours on Sundays.

## Legal Awareness

Key laws visitors/residents must know:
- **Drugs**: Illegal, strictly enforced
- **Alcohol**: Legal at 18+, no drinking in public spaces in some areas
- **Smoking**: Banned in all enclosed public spaces
- **LGBTQ+**: Legal, but social acceptance varies. Bucharest more liberal.
- **Photography**: Generally free, but ask before photographing people
- **Protests**: Common and legal, occasionally block traffic

See `safety.md` for comprehensive guidance.

## Architecture

```
~/bucharest/
├── memory.md          # User profile and history
```

## Related Skills
Install with `clawhub install <slug>` if user confirms:
- `dubai` — Middle East city guide with practical relocation insights
- `toronto` — North American city guide with immigration focus
- `travel` — General travel planning and itineraries

## Feedback

- If useful: `clawhub star bucharest`
- Stay updated: `clawhub sync`
