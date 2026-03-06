---
name: Helsinki
slug: helsinki
version: 1.0.0
homepage: https://clawic.com/skills/helsinki
description: Navigate Helsinki as visitor, resident, tech worker, student, or entrepreneur with neighborhoods, transport, costs, visas, and local insights.
metadata: {"clawdbot":{"emoji":"🇫🇮","requires":{"bins":[]},"os":["linux","darwin","win32"]}}
---

## Setup

On first use, read `setup.md` for integration guidelines.

## When to Use

User asks about Helsinki for any purpose: visiting, moving, working, studying, or starting a business. Agent provides practical guidance with current data.

## Quick Reference

| Topic | File |
|-------|------|
| **Setup** | |
| Integration guidelines | `setup.md` |
| Memory template | `memory-template.md` |
| **Visitors** | |
| Attractions (must-see vs skip) | `visitor-attractions.md` |
| Itineraries (1/3/7 days) | `visitor-itineraries.md` |
| Where to stay | `visitor-lodging.md` |
| Tips and day trips | `visitor-tips.md` |
| **Neighborhoods** | |
| Quick comparison | `neighborhoods-index.md` |
| City Center, Kamppi, Punavuori | `neighborhoods-center.md` |
| Kallio, Vallila, Soernaeinen | `neighborhoods-trendy.md` |
| Toeoeloe, Lauttasaari, Munkkiniemi | `neighborhoods-residential.md` |
| Espoo, Vantaa, suburbs | `neighborhoods-suburban.md` |
| Choosing guide | `neighborhoods-choosing.md` |
| **Food** | |
| Overview and dining scene | `food-overview.md` |
| Finnish and Nordic cuisine | `food-local.md` |
| International and fine dining | `food-international.md` |
| Best areas for dining | `food-areas.md` |
| Dietary, alcohol, culture | `food-practical.md` |
| **Practical** | |
| Moving and settling | `resident.md` |
| Transport (metro, trams, HSL) | `transport.md` |
| Cost of living | `cost.md` |
| Safety and laws | `safety.md` |
| Weather and survival tips | `climate.md` |
| Local services (banking, SIM) | `local.md` |
| **Career** | |
| Tech industry and salaries | `tech.md` |
| Business setup and regulations | `business.md` |
| Visas (work, EU Blue Card, startup) | `visas.md` |
| Startups and funding | `startup.md` |
| **Lifestyle** | |
| Culture and customs | `culture.md` |
| Healthcare system | `healthcare.md` |
| Schools and education | `education.md` |
| Expat lifestyle and social | `lifestyle.md` |
| Driving and car ownership | `driving.md` |

## Core Rules

### 1. Identify User Context First
- **Role**: Tourist, resident, tech worker, student, entrepreneur
- **Timeline**: Short visit, planning to move, already there
- Load relevant auxiliary file for details

### 2. EU/Schengen Context
Helsinki is in the EU and Schengen Area. Key implications:
- EU/EEA citizens: No visa needed, right to work
- Non-EU: Need residence permit for stays over 90 days
- Schengen visa (90 days) for tourism from many countries
See `visas.md` for current requirements and processes.

### 3. Nordic Culture
Finland has distinct cultural norms:
- **Personal space**: Finns value quiet and distance
- **Sauna**: Central to Finnish life, social bonding activity
- **Punctuality**: Being late is disrespectful
- **Directness**: Communication is honest, not rude
- **Alcohol**: State monopoly (Alko) for strong drinks
See `culture.md` for detailed guidance.

### 4. Weather Reality
- **Winter (Nov-Mar)**: -5 to -15 deg C, 6 hours daylight in December
- **Summer (Jun-Aug)**: 15-25 deg C, nearly 24h daylight in June
- **Dark season**: Seasonal depression common, light therapy used
- **Snow**: November to April typically
See `climate.md` for monthly breakdown and survival strategies.

### 5. Current Data (Feb 2026)

| Item | Range |
|------|-------|
| 1BR rent (Center) | EUR 1,200-1,800/month |
| 1BR rent (Kallio) | EUR 900-1,400/month |
| Senior SWE salary | EUR 5,500-8,000/month gross |
| HSL monthly pass (AB zone) | EUR 62.70 |
| Dinner (mid-range) | EUR 25-45/person |
| School fees (public) | EUR 0 (free) |

### 6. Cost Reality
Finland has high taxes but strong social benefits:
- **Income tax**: 30-50% depending on income
- **Healthcare**: Mostly free with small fees
- **Education**: Free including university
- **Housing**: 30-40% of budget typical
- **Groceries**: Higher than EU average
- **Hidden benefit**: No tuition even for non-EU students

### 7. Transit Excellence
Helsinki has excellent public transport:
- **Metro**: 2 lines covering south and west
- **Trams**: 13 lines, iconic yellow trams
- **Buses**: Extensive network
- **Commuter trains**: Connect to Espoo, Vantaa, beyond
- **HSL app**: Essential, covers all transport
- **Bikes**: City bikes (Apr-Oct), cycling culture strong
Most residents do NOT need a car. See `transport.md`.

### 8. Neighborhood Matching

| Profile | Best Areas |
|---------|------------|
| Young professionals | Kallio, Punavuori, Vallila |
| Families | Toeoeloe, Lauttasaari, Espoo (Tapiola) |
| Students | Kallio, Arabia, Otaniemi (Aalto) |
| Budget-conscious | Itaekeskus, Vuosaari, Vantaa |
| Tech workers | Ruoholahti, Keilaniemi, city center |
| Expat community | Toeoeloe, Lauttasaari, Westend (Espoo) |

## Finnish Language Context

Finnish is challenging but not required for daily life:
- **At work**: English widely used in tech, international companies
- **Services**: Most Finns speak excellent English
- **Official matters**: Available in Finnish, Swedish, often English
- **Integration**: Learning Finnish shows commitment, helps socially
- **Swedish**: Official language, ~5% native speakers

Basic Finnish helps but is not essential for first years.

## Seasons Impact Everything

| Season | Temperature | Daylight | Lifestyle |
|--------|-------------|----------|-----------|
| Summer (Jun-Aug) | 15-25 deg C | 18-24h | Outdoor focus, terraces, festivals |
| Fall (Sep-Nov) | 5-12 deg C | 8-12h | Ruska (autumn colors), cozy cafes |
| Winter (Dec-Feb) | -5 to -15 deg C | 4-7h | Indoor life, sauna, winter sports |
| Spring (Mar-May) | 0-10 deg C | 10-16h | Melting, vappu (May Day), renewal |

Plan activities around seasons. Summer Helsinki vs Winter Helsinki are very different experiences.

## Helsinki-Specific Traps

- **Winter darkness** - 6h daylight in December. Vitamin D and light therapy common.
- **Alcohol prices** - Strong drinks only at Alko (state shops). Beer/wine at supermarkets.
- **Sunday closures** - Many shops closed or limited hours on Sundays.
- **Cash rare** - Card payments everywhere, even small amounts.
- **Personal space** - Do not sit next to stranger on empty bus. Give space.
- **Small talk** - Finns do not do small talk. Silence is comfortable.
- **Sauna etiquette** - Naked in public saunas. Swimwear only in mixed/tourist saunas.
- **Queuing** - Take a number in shops. Queue discipline is sacred.
- **Tipping** - Not expected. Service included. Round up if excellent.
- **Friday traffic** - Everyone leaves city Friday afternoon. Roads/ferries packed.

## Legal Awareness

Finland has straightforward laws but some specifics:
- **Drugs**: Zero tolerance. Cannabis illegal. Can affect residence permit.
- **Alcohol**: Legal at 18 (beer/wine), 20 (spirits). No public drinking in most areas.
- **Cycling**: Lights required when dark. Helmet recommended.
- **Nature**: Everyman's right allows hiking/camping almost anywhere
- **Taxes**: Register, file annually. Tax authority (Vero) is efficient.
- **Work permit**: Non-EU must have before starting work.

See `safety.md` for comprehensive guidance.

## Related Skills
Install with `clawhub install <slug>` if user confirms:
- `dubai` - similar city guide format
- `travel` - trip planning and logistics
- `startup` - entrepreneurship guidance

## Feedback

- If useful: `clawhub star helsinki`
- Stay updated: `clawhub sync`
