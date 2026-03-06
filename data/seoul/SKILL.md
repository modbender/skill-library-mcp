---
name: Seoul
slug: seoul
version: 1.0.0
homepage: https://clawic.com/skills/seoul
description: Navigate Seoul as visitor, resident, tech worker, student, or entrepreneur with neighborhoods, transport, costs, visas, and local insights.
metadata: {"clawdbot":{"emoji":"🏙️","requires":{"bins":[]},"os":["linux","darwin","win32"]}}
---

## When to Use

User asks about Seoul for any purpose: visiting, moving, working, studying, or starting a business. Agent provides practical guidance with current data.

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
| Gangnam, Seocho, Samsung | `neighborhoods-gangnam.md` |
| Hongdae, Mapo, Yeonnam | `neighborhoods-hongdae.md` |
| Itaewon, Hannam, Yongsan | `neighborhoods-itaewon.md` |
| Jongno, Bukchon, Insadong | `neighborhoods-traditional.md` |
| Choosing guide | `neighborhoods-choosing.md` |
| **Food** | |
| Overview & dining scene | `food-overview.md` |
| Korean cuisine essentials | `food-korean.md` |
| International & fine dining | `food-international.md` |
| Best areas for dining | `food-areas.md` |
| Dietary, alcohol, etiquette | `food-practical.md` |
| **Practical** | |
| Moving & settling | `resident.md` |
| Transport (metro, buses, T-money) | `transport.md` |
| Cost of living | `cost.md` |
| Safety & laws | `safety.md` |
| Weather & survival tips | `climate.md` |
| Local services (banking, phone) | `local.md` |
| **Career** | |
| Tech industry & salaries | `tech.md` |
| Business setup & regulations | `business.md` |
| Visas (work, D-10, startup) | `visas.md` |
| Startups & funding | `startup.md` |
| **Lifestyle** | |
| Culture & customs | `culture.md` |
| Healthcare & insurance | `healthcare.md` |
| Schools & education | `education.md` |
| Expat lifestyle & social | `lifestyle.md` |
| Driving & car ownership | `driving.md` |

## Core Rules

### 1. Identify User Context First
- **Role**: Tourist, resident, tech worker, student, entrepreneur
- **Timeline**: Short visit, planning to move, already there
- Load relevant auxiliary file for details

### 2. Housing System (Unique to Korea)
Korean rental system differs fundamentally from Western models:
- **Jeonse (전세)**: Large deposit (50-80% of home value), no monthly rent
- **Wolse (월세)**: Smaller deposit + monthly rent (closer to Western model)
- **Banjiha (반지하)**: Semi-basement units — cheap but humidity issues
- Deposits are refundable but require significant upfront capital
See `cost.md` and `resident.md` for current requirements.

### 3. Cultural Context
Korea has distinct social expectations:
- **Hierarchy**: Age and seniority matter in all interactions
- **Drinking culture**: Refusing drinks from seniors can be awkward
- **Work culture**: Long hours common; "눈치" (nunchi) — reading social cues essential
- **Confucian roots**: Respect for elders, education highly valued
See `culture.md` for detailed guidance.

### 4. Weather Reality
- **Summer (Jun-Aug)**: 25-35°C with monsoon season (장마) — high humidity, heavy rain
- **Winter (Dec-Feb)**: -10 to 5°C — dry, cold, yellow dust (황사) from China
- **Spring/Fall**: Best seasons (April-May, Sep-Oct) — mild and pleasant
See `climate.md` for monthly breakdown and survival strategies.

### 5. Current Data (Feb 2026)

| Item | Range |
|------|-------|
| Studio jeonse (Gangnam) | ₩150-250M (~$110K-185K deposit) |
| Studio wolse (Gangnam) | ₩10M deposit + ₩800K-1.2M/month |
| Studio wolse (Mapo/Hongdae) | ₩5M deposit + ₩600K-900K/month |
| Senior SWE salary | ₩70-120M/year (~$52K-89K) |
| Metro single ride | ₩1,400 (~$1) |
| Dinner (Korean BBQ) | ₩15,000-25,000/person |
| International school | ₩25-40M/year |

### 6. Cost Reality
Seoul is moderately expensive with some surprises:
- **Housing**: Jeonse requires huge capital; wolse more accessible
- **Food**: Cheap Korean food ($5-8), expensive imports/Western
- **Healthcare**: Excellent and affordable (national insurance)
- **Transport**: Very cheap (metro + bus integrated)
- **Hidden costs**: Key money (보증금), maintenance fees (관리비)

### 7. Transit Excellence
Unlike car-centric cities, Seoul has world-class public transit:
- **Metro**: 23 lines, 700+ stations, covers entire metropolitan area
- **Buses**: Comprehensive network, color-coded by distance
- **T-money card**: Essential — works on all transport, convenience stores
- **KTX**: High-speed rail to other cities (Busan: 2.5 hours)
- **Taxis**: Cheap by Western standards, Kakao T app for ride-hailing
Most residents don't need cars. See `transport.md`.

### 8. Neighborhood Matching

| Profile | Best Areas |
|---------|------------|
| Young professionals | Gangnam, Seocho, Yeoksam |
| Creatives & nightlife | Hongdae, Yeonnam-dong, Itaewon |
| Families (Korean schools) | Apgujeong, Bundang, Songpa |
| Families (International schools) | Hannam, Yongsan, Pangyo |
| Budget-conscious | Sinchon, Noryangjin, outer Mapo |
| Traditional vibes | Bukchon, Samcheong-dong, Jongno |
| Tech workers | Pangyo (Korea's Silicon Valley), Gangnam |

## Visa Overview

Korea has multiple pathways for foreigners:
- **E-7**: Skilled worker visa (employer sponsorship required)
- **E-7-1**: IT specialist visa (points-based, easier)
- **D-10**: Job-seeking visa (up to 2 years)
- **D-8**: Corporate investment visa (startup founders)
- **F-2-7**: Points-based residency (long-term)
- **F-5**: Permanent residency (after 5+ years)
- **K-ETA**: Visa-free entry for most Western countries (tourism)

See `visas.md` for current requirements and processes.

## Tech Industry Context

Seoul + Pangyo form Korea's tech hub:
- **Chaebols**: Samsung, LG, SK, Hyundai — stable but rigid
- **Naver/Kakao**: Internet giants, more startup-like culture
- **Startups**: Growing ecosystem, especially fintech and gaming
- **Work culture**: Long hours, hierarchy, but changing in tech
- **English**: Limited outside international companies

Salaries lower than US/Europe but:
- Lower taxes (income tax ~15-20% typical)
- National health insurance (3-4% of salary)
- Lower cost of living for daily expenses

See `tech.md` for detailed comparison and job hunting strategies.

## Seoul-Specific Traps

- **Jeonse scams** — Always use certified real estate agents (공인중개사). Verify ownership.
- **No tipping** — Tipping is not expected and can be awkward.
- **Cash still matters** — Many small shops don't take foreign cards. Get Korean bank account.
- **Apartment numbering** — Buildings count ground floor as 1F. "5th floor" = 6th floor Western.
- **Age calculation** — Korea uses "Korean age" (+1-2 years). Being phased out but still used socially.
- **Sunday closures** — Some traditional markets and restaurants close Sundays.
- **Phone addiction** — Everyone uses KakaoTalk. No Kakao = social isolation.
- **Noise complaints** — Apartments have thin walls. Neighbor conflicts common.
- **Yellow dust season** — March-May, check air quality (미세먼지) before going out.
- **Work dinner expectations** — Declining 회식 (hweshik) can hurt career. Know when it's optional.

## Legal Awareness

Key laws visitors/residents must know:
- **Drugs**: Zero tolerance. Cannabis = prison. Even prior use detected = deportation.
- **Photography**: Illegal to photograph people without consent (strict enforcement)
- **Noise**: Noise after 10 PM can result in fines
- **Alcohol**: Legal at 19 (Korean age). Public drinking is legal.
- **Smoking**: Banned in most public places. Designated areas only.
- **National Service**: Korean male citizens must serve ~18 months military
- **Defamation**: Truth is NOT a defense. Accurate criticism can be prosecuted.

See `safety.md` for comprehensive legal guidance.

## Related Skills
Install with `clawhub install <slug>` if user confirms:
- `dubai` — Similar city guide for Dubai with neighborhoods, visas, and expat life
- `korean` — Learn Korean language with structured lessons and practice
- `travel` — Plan trips with itineraries, packing lists, and logistics
- `food` — Explore cuisines, recipes, and dining recommendations
- `money` — Personal finance, budgeting, and expense tracking

## Feedback

- If useful: `clawhub star seoul`
- Stay updated: `clawhub sync`
