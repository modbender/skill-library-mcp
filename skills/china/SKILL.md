---
name: China
slug: china
version: 1.0.0
homepage: https://clawic.com/skills/china
changelog: "Initial release with expanded mega-region guides, practical logistics, and long-route planning for China travel."
description: Discover China like a local with deep city-region coverage, practical route planning, food context, and execution-ready travel logistics.
metadata: {"clawdbot":{"emoji":"🇨🇳","requires":{"bins":[],"config":["~/china/"]},"os":["linux","darwin","win32"]}}
---

## Setup

If `~/china/` doesn't exist or is empty, read `setup.md` and start naturally.

## When to Use

User planning a trip to China or asking for local insights: where to base, how to split huge distances, what to prioritize by season, and how to handle transport, payments, connectivity, and pace.

## Architecture

Memory lives in `~/china/`. See `memory-template.md` for structure.

```
~/china/
└── memory.md     # Trip context
```

## Quick Reference

| Topic | File |
|-------|------|
| **Major Hubs and Routes** | |
| Beijing complete guide | `beijing.md` |
| Shanghai complete guide | `shanghai.md` |
| Guangzhou and Shenzhen complete guide | `guangzhou-shenzhen.md` |
| Xi'an complete guide | `xian.md` |
| Chengdu and Chongqing complete guide | `chengdu-chongqing.md` |
| Yunnan complete guide | `yunnan.md` |
| Guilin and Yangshuo complete guide | `guilin-yangshuo.md` |
| Zhangjiajie and Hunan complete guide | `zhangjiajie-hunan.md` |
| Silk Road west corridor complete guide | `silk-road-gansu-qinghai.md` |
| Hainan complete guide | `hainan.md` |
| **Planning** | |
| Core itineraries | `itineraries.md` |
| Long-distance route patterns | `long-routes.md` |
| Where to stay by style | `accommodation.md` |
| Entry and documents planning | `entry-and-documents.md` |
| Useful apps | `apps.md` |
| **Food and Drink** | |
| Regional dishes and restaurant strategy | `food-guide.md` |
| Wine, tea, baijiu, and bar strategy | `wine.md` |
| **Experiences** | |
| Signature experiences | `experiences.md` |
| Beaches and island planning | `beaches.md` |
| Hikes and mountain safety | `hiking.md` |
| Nightlife by city type | `nightlife.md` |
| **Reference** | |
| Regions and route differences | `regions.md` |
| Culture, etiquette, expectations | `culture.md` |
| Seasonality and climate strategy | `seasonality.md` |
| Traveling with children | `with-kids.md` |
| High-altitude and permit-sensitive areas | `tibet-and-high-altitude.md` |
| **Practical** | |
| Intercity transport and rail/air tradeoffs | `transport.md` |
| Telecom and SIM/eSIM planning | `telecoms.md` |
| Payments and internet constraints | `payment-and-internet.md` |
| Emergencies and safety | `emergencies.md` |

## Core Rules

### 1. Specific Over Generic
Do not say "visit China highlights." Say "pick 2-3 bases max, anchor each by one high-value district cluster, and protect transfer days as logistics days, not attraction marathons."

### 2. Local Perspective
What locals and repeat travelers actually do, not brochure advice:
- China rewards route logic and punishes over-ambitious city stacking
- Same-day intercity transfers can consume most useful day hours
- Weather and air quality windows can change outdoor planning fast
- Payment and connectivity setup quality affects everything else

### 3. Regional Differences

| Region | Key difference |
|--------|----------------|
| Beijing and North China | Imperial history, museums, colder winters, major landmarks |
| Shanghai and East coast | Global-city pace, neighborhoods, modern food and design |
| Pearl River Delta | Manufacturing-meets-tech region, fast intercity access |
| Southwest (Sichuan, Yunnan, Guizhou) | Food depth, mountain routes, climate variation |
| Northwest (Gansu, Qinghai, Xinjiang corridors) | Long distances, desert-highland logistics |
| South coast and Hainan | Tropical rhythm, beach and water activity planning |

### 4. Timing is Everything
- National holiday windows can massively change transport and crowd patterns
- Summer heat and humidity require daytime pacing control in many regions
- Winter can be excellent for cities and selected landscapes with preparation
- Shoulder periods often deliver best price-crowd balance
- Long routes should always include one buffer day per major transfer block

### 5. Flag Tourist Traps
Be explicit about what to avoid:
- Trying Beijing, Xi'an, Shanghai, and Yunnan in one short trip with no slack
- Booking no-reservation high-demand dining in major hubs on weekends
- Ignoring real transfer time from airports/stations to accommodation
- Overpaying for generic landmark-zone food with no quality signal

### 6. Match Trip Style

| Traveler | Focus on |
|----------|----------|
| Foodie | `food-guide.md`, `chengdu-chongqing.md`, `shanghai.md` |
| Culture and history | `beijing.md`, `xian.md`, `regions.md` |
| Nature and scenery | `yunnan.md`, `guilin-yangshuo.md`, `hiking.md` |
| Family | `with-kids.md`, `accommodation.md`, `itineraries.md` |
| Nightlife and modern city | `nightlife.md`, `shanghai.md`, `guangzhou-shenzhen.md` |
| Long route explorer | `long-routes.md`, `transport.md`, `seasonality.md` |

## Common Traps

- Treating China as one compact destination.
- Choosing too many bases for short trips.
- Skipping payment and app setup before arrival.
- Ignoring seasonality for mountain and southern tropical regions.
- No fallback plans for weather, rail disruption, or crowd spikes.
- Confusing map distance with real travel-time cost.

## Security & Privacy

**Data that stays local:** Trip preferences in `~/china/`

**This skill does NOT:** Access files outside `~/china/` or make network requests.

## Related Skills
Install with `clawhub install <slug>` if user confirms:
- `travel` — General trip planning and itinerary structuring
- `food` — Deeper restaurant and cuisine recommendations
- `chinese` — Language support for local communication and signs
- `english` — Backup communication support for multilingual logistics

## Feedback

- If useful: `clawhub star china`
- Stay updated: `clawhub sync`
