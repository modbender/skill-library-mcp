---
name: Beijing
slug: beijing
version: 1.0.0
homepage: https://clawic.com/skills/beijing
description: Navigate Beijing as visitor, resident, tech worker, student, or entrepreneur with neighborhoods, transport, costs, visas, and local insights.
metadata: {"clawdbot":{"emoji":"🏯","requires":{"bins":[]},"os":["linux","darwin","win32"]}}
---

## When to Use

User asks about Beijing for any purpose: visiting, moving, working, studying, or starting a business. Agent provides practical guidance with current data.

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
| Chaoyang, CBD, Sanlitun | `neighborhoods-downtown.md` |
| Haidian, Zhongguancun | `neighborhoods-tech.md` |
| Dongcheng, Xicheng (Historic) | `neighborhoods-historic.md` |
| Shunyi, Changping, Tongzhou | `neighborhoods-suburban.md` |
| Choosing guide | `neighborhoods-choosing.md` |
| **Food** | |
| Overview & dining scene | `food-overview.md` |
| Beijing & Northern Chinese | `food-local.md` |
| International & fine dining | `food-international.md` |
| Best areas for dining | `food-areas.md` |
| Dietary, alcohol, practicalities | `food-practical.md` |
| **Practical** | |
| Moving & settling | `resident.md` |
| Transport (subway, DiDi, bikes) | `transport.md` |
| Cost of living | `cost.md` |
| Safety & laws | `safety.md` |
| Weather & AQI tips | `climate.md` |
| Local services (banking, SIM) | `local.md` |
| **Career** | |
| Tech industry & salaries | `tech.md` |
| Business setup & WFOE | `business.md` |
| Visas (Z, X, M, residence permit) | `visas.md` |
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

### 2. The Great Firewall Reality
China operates the world's most sophisticated internet censorship system:
- **Blocked:** Google, YouTube, Facebook, Instagram, Twitter, WhatsApp, most Western news
- **Essential:** VPN before arrival (cannot download inside China)
- **Super Apps:** WeChat (微信) is EVERYTHING — messaging, payments, food, transport, social
- **Alternative Apps:** Baidu (search), Amap/Gaode (maps), Alipay (payments), Taobao (shopping)
See `local.md` for comprehensive app ecosystem.

### 3. Language Barrier
Beijing is NOT English-friendly like Singapore or Hong Kong:
- **Mandarin essential:** 90%+ of daily interactions require Chinese
- **Even expat-heavy areas:** Limited English compared to Shanghai
- **Apps help:** Translation apps, DiDi has English mode, some menus have pictures
- **Pinyin:** Learn basic tones and phrases — it matters
See `culture.md` for language survival guide.

### 4. Weather Reality
Beijing has extreme continental climate:
- **Winter (Nov-Mar):** -10°C to 5°C, bone-dry, occasional snow
- **Summer (Jun-Aug):** 30-40°C+ with high humidity
- **Spring (Mar-May):** Sandstorms possible, pleasant otherwise
- **Autumn (Sep-Nov):** Best season, crisp and clear
- **AQI:** Air quality varies dramatically — check daily, mask recommended
See `climate.md` for monthly breakdown and AQI survival strategies.

### 5. Current Data (Feb 2026)

| Item | Range |
|------|-------|
| 1BR rent (CBD/Chaoyang) | ¥8,000-15,000/month (~$1,100-2,100) |
| 1BR rent (Haidian) | ¥6,000-12,000/month (~$830-1,650) |
| Senior SWE salary (local) | ¥40,000-80,000/month (~$5,500-11,000) |
| Senior SWE salary (foreign) | ¥60,000-120,000/month (~$8,300-16,500) |
| Subway single ride | ¥3-10 (distance-based) |
| Hotpot dinner (mid-range) | ¥100-200/person |
| International school fees | ¥150,000-350,000/year |

### 6. Registration & Compliance
All foreigners must register with police within 24 hours of arrival:
- **Hotels:** Register automatically
- **Private residence:** YOU must register at local PSB (Public Security Bureau)
- **Penalty:** Fines, visa issues, potential deportation
- **Every move:** Re-register if you change address
See `visas.md` and `safety.md` for compliance details.

### 7. Transit Excellence
Beijing has world-class public transport (but traffic is horrific):
- **Subway:** 27 lines, 800+ km — largest network globally
- **Buses:** Extensive but complex for non-Chinese speakers
- **DiDi:** Chinese Uber equivalent — essential for non-subway trips
- **Bikes:** Dockless bikes everywhere (Meituan, Hello, Didi)
- **Driving:** Restricted by license plate lottery, not recommended
Most expats use subway + DiDi. See `transport.md` and `driving.md`.

### 8. Neighborhood Matching

| Profile | Best Areas |
|---------|------------|
| Young professionals | Sanlitun, CBD, Guomao |
| Families (expat) | Shunyi, Chaoyang Park area |
| Tech workers | Zhongguancun, Wudaokou, Haidian |
| Students | Wudaokou, Haidian university area |
| Budget-conscious | Tongzhou, outer Chaoyang |
| History/culture lovers | Dongcheng, Xicheng (hutongs) |
| Luxury seekers | Sanlitun, CBD penthouses, Shunyi villas |

## Hukou & Work Permit Context

Beijing has unique residency restrictions:
- **Hukou (户口):** Chinese household registration system
- **Beijing hukou:** Extremely hard to get even for Chinese citizens
- **Impact:** Access to schools, healthcare, property purchase differs by hukou status
- **Foreigners:** Not affected by hukou directly, but work permits are tier-based
- **Work Permit Tiers:** A (top talent), B (professional), C (temporary/intern)

See `visas.md` for work permit details and `education.md` for school implications.

## Beijing-Specific Traps

- **No VPN = no Western internet** — Must install BEFORE entering China. Cannot download inside.
- **WeChat dependency** — Without WeChat Pay, daily life is extremely difficult. Link bank card ASAP.
- **24-hour registration** — Forgetting to register at PSB is a serious offense. Hotels do it automatically.
- **License plate lottery** — Cannot just buy a car and drive. Beijing plates require years of waiting.
- **AQI underestimation** — Heavy pollution days (200+ AQI) happen. Have N95 masks and air purifier.
- **Cash almost useless** — China is nearly 100% mobile payment. Carry ¥500 max as backup.
- **Taxis without DiDi** — Flagging taxis is hard; most drivers use DiDi exclusively.
- **Saturday/Sunday schools** — Kids often have weekend classes (tutoring culture).
- **Noise levels** — Beijing is LOUD. Traffic, construction, people — expect it.
- **Spitting and smoking** — Common in public, including restaurants. Improving but still present.

## Legal Awareness

Key laws visitors/residents must know:
- **VPN:** Legal gray area. Personal use tolerated, selling/promoting is illegal.
- **Registration:** 24-hour PSB registration MANDATORY for all foreigners.
- **Work permit:** Working without proper Z visa + work permit = deportation + ban.
- **Drugs:** Zero tolerance. Death penalty possible for trafficking. Any amount is serious.
- **Photography:** No photos of military, police, government buildings.
- **Political speech:** Criticizing government/Party is risky. Avoid completely.
- **Social media posts:** WeChat is monitored. Be careful what you share.
- **LGBTQ+:** Not illegal, but no legal recognition. Discretion advised.

See `safety.md` for comprehensive legal guidance.

## Related Skills

Install with `clawhub install <slug>` if user confirms:

*No related skills published yet.*

## Feedback

- If useful: `clawhub star beijing`
- Stay updated: `clawhub sync`
- [Report issues](https://clawhub.com/openclaw/beijing/issues)
