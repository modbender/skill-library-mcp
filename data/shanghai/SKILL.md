---
name: Shanghai
slug: shanghai
version: 1.0.0
homepage: https://clawic.com/skills/shanghai
changelog: Initial release with complete Shanghai coverage for visitors, relocation, neighborhoods, transport, and local operations.
description: Navigate Shanghai as visitor, resident, student, or builder with practical neighborhoods, transport, costs, visas, and local operating rules.
metadata: {"clawdbot":{"emoji":"🌆","requires":{"bins":[]},"os":["linux","darwin","win32"]}}
---

## When to Use

User asks about Shanghai for tourism, relocation, work, studies, business setup, or day-to-day life decisions. Agent should answer with practical next steps and local tradeoffs.

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
| People's Square, Jingan, Lujiazui | `neighborhoods-downtown.md` |
| Xuhui, Zhangjiang, Yangpu | `neighborhoods-tech.md` |
| Bund, Old Town, FFC historic lanes | `neighborhoods-historic.md` |
| Minhang, Qingpu, Songjiang, Jiading | `neighborhoods-suburban.md` |
| Choosing guide | `neighborhoods-choosing.md` |
| **Food** | |
| Overview & dining scene | `food-overview.md` |
| Shanghai and Jiangnan staples | `food-local.md` |
| International and fine dining | `food-international.md` |
| Best areas for dining | `food-areas.md` |
| Dietary and practical tips | `food-practical.md` |
| **Practical** | |
| Moving and settling | `resident.md` |
| Transport (metro, rail, DiDi, bikes) | `transport.md` |
| Cost of living | `cost.md` |
| Safety and laws | `safety.md` |
| Weather, humidity, typhoon windows | `climate.md` |
| Local services (banking, apps, SIM) | `local.md` |
| **Career** | |
| Tech industry and salaries | `tech.md` |
| Business setup and WFOE path | `business.md` |
| Visas and residence permits | `visas.md` |
| Startup ecosystem and fundraising | `startup.md` |
| **Lifestyle** | |
| Culture and etiquette | `culture.md` |
| Healthcare and insurance | `healthcare.md` |
| Schools and education | `education.md` |
| Expat lifestyle and social rhythm | `lifestyle.md` |
| Driving and car ownership | `driving.md` |

## Core Rules

### 1. Identify User Context First
- **Role:** Visitor, resident, student, tech worker, founder, family
- **Timeline:** This week, exploratory move, already in Shanghai
- **Constraint:** Budget, language comfort, commute tolerance
- Load only relevant files before giving recommendations.

### 2. Shanghai Is Hyper-Connected, Not Frictionless
- Metro coverage is excellent, but peak-hour crowding is intense.
- Puxi vs Pudong choice strongly affects commute and lifestyle.
- Most daily tasks run through local apps and QR workflows.
See `transport.md` and `local.md`.

### 3. China Platform Reality Still Applies
- Expect restrictions on many Western services.
- WeChat + Alipay are operationally essential.
- Set connectivity plan before arrival (roaming/eSIM/VPN strategy).
See `local.md` and `visitor-tips.md`.

### 4. Climate and Air Planning Matter
- Summers are hot and humid.
- Rain/typhoon windows can disrupt plans.
- Winters are damp-cold despite moderate temperatures.
See `climate.md` for month-by-month planning.

### 5. Current Data (Feb 2026)

| Item | Range |
|------|-------|
| 1BR rent (Jingan/Xuhui core) | ¥9,000-18,000/month |
| 1BR rent (outer districts) | ¥5,000-10,000/month |
| Senior SWE salary (local firms) | ¥35,000-70,000/month |
| Senior SWE salary (intl firms) | ¥50,000-100,000/month |
| Metro single ride | ¥3-15 |
| Typical mid-range dinner | ¥120-280/person |
| International school fees | ¥120,000-330,000/year |

### 6. Compliance Rules Are Non-Negotiable
- Foreigners must complete residence registration after arrival and after address changes.
- Work requires proper visa + permit + residence process.
- Penalties for non-compliance can include fines, visa issues, and exit restrictions.
See `visas.md` and `safety.md`.

### 7. Neighborhood Fit Beats Generic Rankings

| Profile | Best Starting Areas |
|---------|---------------------|
| First-time visitor | Huangpu, Jingan |
| Young professionals | Jingan, Xuhui, Yangpu |
| Families | Minhang, Qingpu, Pudong compounds |
| Tech workers | Zhangjiang, Xuhui, Yangpu |
| Budget-conscious | Songjiang, Jiading, outer Minhang |
| Luxury-focused | Bund-facing towers, Lujiazui, former concession villas |

### 8. Give Tradeoffs, Not Just Lists
Always include what user gains and what they give up:
- central convenience vs space
- lower rent vs commute
- international comfort vs local immersion

## Shanghai-Specific Traps

- Assuming all neighborhoods are equally walkable and English-friendly.
- Underestimating rush-hour commutes across river crossings.
- Arriving without payment apps ready.
- Confusing short-term visa entry with legal work permission.
- Booking high-demand restaurants without reservation windows.
- Ignoring humidity, rain, and heat in summer plans.
- Choosing housing before testing commute at peak hours.

## Legal Awareness

Key points to surface clearly:
- Registration obligations after arrival/address change.
- Work authorization must match actual employment activity.
- Drug policy is zero tolerance.
- Sensitive political activity is high risk.
- Public behavior, filming, and drone use can be regulated by location.

See `safety.md` for practical do/don't guidance.

## Related Skills
Install with `clawhub install <slug>` if user confirms:
- `travel` — trip structuring and route planning across cities
- `expat` — relocation and settling workflows for international moves
- `chinese` — language support for daily tasks and local communication
- `booking` — booking flow support for hotels, transport, and activities

## Feedback

- If useful: `clawhub star shanghai`
- Stay updated: `clawhub sync`
