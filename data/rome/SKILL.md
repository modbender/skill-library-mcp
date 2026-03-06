---
name: Rome
slug: rome
version: 1.0.0
homepage: https://clawic.com/skills/rome
description: Navigate Rome as visitor, expat, digital nomad, or entrepreneur with neighborhoods, transport, costs, visas, and Italian lifestyle insights.
metadata: {"clawdbot":{"emoji":"🏛️","requires":{"bins":[]},"os":["linux","darwin","win32"]}}
---

## Setup

On first use, read `setup.md` for integration guidelines.

## When to Use

User asks about Rome or Italy for any purpose: visiting, relocating, working remotely, studying, retiring, or starting a business. Agent provides practical guidance with current data.

## Architecture

Memory lives in `~/.rome/`. See `memory-template.md` for structure.

```
~/.rome/
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
| Historic Center (Centro Storico, Trastevere, Campo de' Fiori) | `neighborhoods-historic.md` |
| Trendy & Creative (San Lorenzo, Pigneto, Ostiense) | `neighborhoods-trendy.md` |
| Upscale (Parioli, Prati, Aventino) | `neighborhoods-upscale.md` |
| Residential (Testaccio, San Giovanni, Monteverde) | `neighborhoods-residential.md` |
| Outer & Suburbs (EUR, Garbatella, Ostia) | `neighborhoods-outer.md` |
| Choosing guide | `neighborhoods-choosing.md` |
| **Food** | |
| Overview & dining scene | `food-overview.md` |
| Roman cuisine essentials | `food-roman.md` |
| Traditional Roman dishes | `food-local.md` |
| International cuisine | `food-international.md` |
| Pizza & street food | `food-pizza.md` |
| Coffee & aperitivo culture | `food-coffee.md` |
| Best areas for dining | `food-areas.md` |
| Practical (tipping, hours, reservations) | `food-practical.md` |
| **Practical** | |
| Moving & settling | `resident.md` |
| Transport (metro, buses, trams) | `transport.md` |
| Cost of living | `cost.md` |
| Safety & laws | `safety.md` |
| Weather & seasonal tips | `climate.md` |
| Local services (codice fiscale, healthcare, SIM) | `local.md` |
| **Career** | |
| Tech scene & remote work | `tech.md` |
| Business setup & freelancing | `business.md` |
| Visas (Elective Residence, Digital Nomad, EU) | `visas.md` |
| Startups & innovation | `startup.md` |
| **Lifestyle** | |
| Culture & customs | `culture.md` |
| Healthcare (SSN) | `healthcare.md` |
| Schools & universities | `education.md` |
| Expat lifestyle & social | `lifestyle.md` |
| Driving & car ownership | `driving.md` |
| Parks, beaches & outdoors | `outdoors.md` |

## Core Rules

### 1. Identify User Context First
- **Role**: Tourist, expat, digital nomad, student, retiree, entrepreneur
- **Timeline**: Short visit, planning to move, already there
- Load relevant auxiliary file for details

### 2. The Eternal City Reality
Rome is not a modern efficient city — it's a living museum with ancient infrastructure:
- **Bureaucracy**: Italian bureaucracy is legendary. Patience required.
- **Pace**: Things move slowly. "Piano piano" (slowly, slowly) is the motto.
- **Chaos**: Traffic, noise, crowds are constant. Embrace it.
- **Beauty**: 3,000 years of history at every corner. Worth the chaos.
See `culture.md` for detailed guidance.

### 3. Visa & Residency Options
Key pathways for non-EU citizens:
- **Elective Residence Visa**: Passive income route (no work permitted)
- **Digital Nomad Visa**: New in 2024, remote workers
- **Student Visa**: Universities and language schools
- **Self-Employment Visa**: Freelancers and entrepreneurs
- **EU Citizens**: Free movement, just register with comune
See `visas.md` for current requirements and processes.

### 4. Weather Reality
- **Mediterranean climate**: Hot dry summers, mild wet winters
- **Best seasons**: Spring (Apr-May) and Fall (Sep-Oct) — 18-25C, fewer tourists
- **Summer (Jun-Aug)**: Very hot (35C+), extremely crowded, locals flee
- **Winter (Dec-Feb)**: Mild (8-15C), rainy, but Rome is beautiful
- **August**: Many businesses close. Romans leave for Ferragosto.
See `climate.md` for monthly breakdown.

### 5. Current Data (Feb 2026)

| Item | Range |
|------|-------|
| 1BR rent (center) | EUR 1,200-1,800/month |
| 1BR rent (periphery) | EUR 700-1,000/month |
| Average salary | EUR 1,500-2,000/month net |
| Senior developer salary | EUR 2,500-4,000/month net |
| Metro single ticket | EUR 1.50 |
| 24h transport pass | EUR 7.00 |
| Espresso at bar | EUR 1.20-1.50 |
| Pizza al taglio slice | EUR 2.50-4.00 |
| Restaurant meal | EUR 15-25 |

### 6. Cost Reality
Rome is moderate by Western European standards:
- **Housing**: Expensive in center, reasonable in outer neighborhoods
- **Food**: Eating out affordable, groceries reasonable
- **Transport**: Excellent public transit, cheap
- **Healthcare**: Public (SSN) is free/cheap for residents
- **Hidden costs**: Bureaucracy fees, furniture (unfurnished common), utilities

### 7. Transit Excellence
Rome has good public transport despite the chaos:
- **Metro**: 3 lines (A, B, C), covers main areas
- **Buses**: Extensive ATAC network, can be chaotic
- **Trams**: Several lines, scenic
- **Regional trains**: To Ostia beach, Fiumicino, suburbs
- **Walking**: Historic center is very walkable
See `transport.md` for complete guide.

### 8. Neighborhood Matching

| Profile | Best Areas |
|---------|------------|
| First-time visitor | Centro Storico, Trastevere |
| Budget traveler | Termini area, San Lorenzo |
| Expat families | Parioli, Monteverde, EUR |
| Digital nomads | Trastevere, Testaccio, Pigneto |
| Students | San Lorenzo, Pigneto, Garbatella |
| Retirees | Prati, Aventino, Trastevere |
| Short-term luxury | Campo de' Fiori, Piazza Navona area |

## The Rome Experience

Understanding Rome requires accepting its contradictions:
- **Ancient + Modern**: 3,000 years coexist, often uneasily
- **Beautiful + Chaotic**: Stunning beauty amid traffic and crowds
- **Frustrating + Rewarding**: Bureaucracy is painful, dolce vita is real
- **Touristy + Authentic**: Both exist, sometimes in same street

The city rewards patience and curiosity. Don't try to "optimize" Rome — experience it.

## Rome-Specific Traps

- **August shutdown** — Half the city closes for Ferragosto. Plan around it.
- **Termini area hotels** — Convenient but sketchy at night. Not the best area.
- **Restaurant tourist menus** — Fixed price "menu turistico" is usually bad. Avoid.
- **Gladiator photos** — They'll demand money. Don't engage.
- **Taxi scams** — Use official white taxis only, insist on meter.
- **Pickpockets** — Crowded metro, tourist sites. Keep valuables secure.
- **Siesta hours** — Many shops close 13:00-16:00. Adapt.
- **Sunday closures** — Many things closed, especially outside center.
- **Fountains are drinking water** — The "nasoni" — use them!
- **Dress codes at churches** — Covered shoulders and knees required.

## Legal Awareness

Key laws visitors/residents must know:
- **Drinking**: Legal at 18. Public drinking generally tolerated in piazzas.
- **Smoking**: Banned in enclosed public spaces, some outdoor areas.
- **Monuments**: Sitting on Spanish Steps is fined. Don't eat at fountains.
- **Driving ZTL**: Limited traffic zones — big fines if you enter without permit.
- **Cannabis**: Decriminalized for small amounts, but still illegal.
- **Tax residency**: 183+ days = tax resident. 7% flat tax for retirees available.
- **Receipts**: Businesses must give receipts; you can be fined for not taking one.

See `safety.md` for comprehensive legal guidance.

## The Housing Reality (2026)

Housing in Rome:
- **Center**: Expensive, often old buildings, character but issues
- **Semi-center**: Better value, good transport links
- **Outer areas**: Most affordable, requires car or long commute
- **Furnished vs unfurnished**: Unfurnished very common (you buy everything)
- **Contracts**: Typically 4+4 year standard contracts
- **Deposits**: Usually 2-3 months rent
- **Competition**: Good apartments go fast, especially near center

## Language

- **Italian essential**: Less English than Northern Europe
- **Romanesco**: Local dialect, colorful expressions
- **Gestures**: Italians communicate with hands — learn them
- **Bureaucracy in Italian**: Almost always, bring translator if needed
- **Learning Italian**: Greatly improves quality of life and integration
- **English improving**: Younger generation, tourist areas, but don't assume

## Related Skills
Install with `clawhub install <slug>` if user confirms:
- `dubai` — Expat destination comparison
- `travel` — General travel planning
- `work` — Career and remote work guidance

## Feedback

- If useful: `clawhub star rome`
- Stay updated: `clawhub sync`
