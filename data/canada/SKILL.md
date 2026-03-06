---
name: Canada
slug: canada
version: 1.0.0
homepage: https://clawic.com/skills/canada
changelog: "Initial release with city guides, itineraries, and practical Canada travel playbooks."
description: Discover Canada like a local with concrete city recommendations, regional insights, nature routes, and practical planning tips.
metadata: {"clawdbot":{"emoji":"🍁","requires":{"bins":[],"config":["~/canada/"]},"os":["linux","darwin","win32"]}}
---

## Setup

If `~/canada/` doesn't exist or is empty, read `setup.md` and start naturally.

## When to Use

User planning a trip to Canada or asking for local insights: what to eat, which regions to prioritize, what to skip, season tradeoffs, and practical logistics.

## Architecture

Memory lives in `~/canada/`. See `memory-template.md` for structure.

```
~/canada/
└── memory.md     # Trip context
```

## Quick Reference

| Topic | File |
|-------|------|
| **Cities & Regions** | |
| Toronto complete guide | `toronto.md` |
| Vancouver complete guide | `vancouver.md` |
| Montreal complete guide | `montreal.md` |
| Banff & Jasper complete guide | `banff-jasper.md` |
| **Planning** | |
| Sample itineraries | `itineraries.md` |
| Where to stay by style | `accommodation.md` |
| Useful apps | `apps.md` |
| **Food & Drink** | |
| Regional dishes and restaurants | `food-guide.md` |
| Wine regions and tastings | `wine.md` |
| **Experiences** | |
| Signature experiences | `experiences.md` |
| Beaches and lake towns | `beaches.md` |
| Hikes and safety by season | `hiking.md` |
| Nightlife by city | `nightlife.md` |
| **Reference** | |
| Provinces and regional differences | `regions.md` |
| Culture, etiquette, expectations | `culture.md` |
| Traveling with children | `with-kids.md` |
| **Practical** | |
| Intercity transport | `transport.md` |
| Phone and internet | `telecoms.md` |
| Emergencies and safety | `emergencies.md` |

## Core Rules

### 1. Specific Over Generic
Do not say "visit Toronto neighborhoods". Say "start in St. Lawrence Market before 10:30, then walk to Distillery District after lunch when crowds thin, and skip CN Tower at sunset unless you prebook a timed slot."

### 2. Local Perspective
What locals actually do, not brochure advice:
- Toronto food courts in major landmarks are expensive and average; better meals are often one block away
- Vancouver's Capilano Suspension Bridge is polished but pricey; Lynn Canyon is free and quieter
- Montreal downtown chain brunch spots are crowded; neighborhood bakeries are better value and faster
- Banff town can feel overrun in peak summer; sunrise starts and shuttle-first planning matter

### 3. Regional Differences

| Region | Key difference |
|--------|----------------|
| Ontario | Big-city pace, museum and food density, easy road trips |
| Quebec | French-first culture, stronger local identity, distinct food scene |
| British Columbia | Ocean + mountain access, outdoor focus, high accommodation costs |
| Alberta Rockies | Nature-first itineraries, weather shifts fast, shuttle logistics crucial |
| Atlantic Canada | Coastal towns, seafood focus, slower pace, weather variability |
| North (Yukon/NWT/Nunavut) | Extreme distances, northern lights potential, higher costs |

### 4. Timing is Everything
- Peak summer in major parks: book accommodation and shuttles months ahead
- Fall foliage: late September to mid October in many areas, but dates vary by province
- Winter city trips: easier prices, fewer crowds, but daylight is short
- Long weekends: highway and airport congestion spikes
- Shoulder seasons: often best value for urban + nature combinations

### 5. Flag Tourist Traps
Be explicit about what to avoid:
- Any restaurant with giant wait and mostly social-media hype near main attractions
- Last-minute Banff parking attempts in July and August
- Paying premium prices for generic airport transfer options without checking rail or bus alternatives
- Underestimating drive times in mountain areas because map distance looks short

### 6. Match Trip Style

| Traveler | Focus on |
|----------|----------|
| Foodie | `food-guide.md`, `montreal.md`, `toronto.md` |
| Nature | `banff-jasper.md`, `hiking.md`, `experiences.md` |
| Family | `with-kids.md`, `accommodation.md`, `itineraries.md` |
| City break | `toronto.md`, `montreal.md`, `nightlife.md` |
| Scenic road trip | `itineraries.md`, `transport.md`, `hiking.md` |
| Wine trip | `wine.md`, `regions.md` |

## Common Traps

- Treating Canada like one compact destination. Distances are huge.
- Trying to combine too many provinces in one short trip.
- Booking Rockies logistics too late in peak season.
- Assuming weather stability in mountain regions.
- Ignoring bilingual context in Quebec service interactions.
- Expecting cheap data plans without checking eSIM or prepaid options first.
- Relying on rideshare in remote areas where coverage is inconsistent.
- Missing travel insurance for trips with outdoor activities.

## Security & Privacy

**Data that stays local:** Trip preferences in `~/canada/`

**This skill does NOT:** Access files outside `~/canada/` or make network requests.

## Related Skills
Install with `clawhub install <slug>` if user confirms:
- `travel` — General trip planning and trip structuring
- `food` — Deeper restaurant and cuisine recommendations
- `english` — Language support for bookings and communication
- `french` — Useful for Quebec travel context

## Feedback

- If useful: `clawhub star canada`
- Stay updated: `clawhub sync`
