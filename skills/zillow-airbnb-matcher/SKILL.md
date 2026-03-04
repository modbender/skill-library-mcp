---
name: zillow-airbnb-matcher
version: 3.1.0
description: Find properties for sale that are already generating Airbnb income. Cross-references Zillow listings with active Airbnb rentals using geo-matching and calculates investment metrics.
author: em8.io
metadata:
  openclaw:
    requires:
      bins: [node]
    install:
      - id: deps
        kind: shell
        command: bash scripts/install.sh
        label: Install dependencies and configure RapidAPI key
    env:
      - name: RAPIDAPI_KEY
        required: true
        description: Free RapidAPI key (rapidapi.com — subscribe to airbnb13 + us-property-market1)
requires:
  - RAPIDAPI_KEY (get free at rapidapi.com — 100+ free requests/month)
commands:
  - trigger: "search airbnb"
    script: scripts/search.js
    description: Search by ZIP code or city
  - trigger: "check properties"
    script: scripts/search.js
    description: Find STR investment properties
  - trigger: "airbnb demo"
    script: scripts/search.js --demo
    description: Run demo with Austin TX sample data (no API needed)
tags:
  - real-estate
  - airbnb
  - investment
  - short-term-rental
  - zillow
---

# Zillow × Airbnb Matcher Skill

This skill finds for-sale properties that **already have an active Airbnb listing** nearby — using GPS-based geo-matching to cross-reference Zillow and Airbnb data.

## How to Use (Chat Commands)

Send any of these messages:

| Message | What Happens |
|---------|-------------|
| `search airbnb 78704` | Search Austin TX zip code |
| `search airbnb Nashville TN` | Search by city |
| `check properties 33139` | Miami Beach STR check |
| `airbnb demo` | Run demo (no API needed) |
| `search airbnb 78704 max 800000` | Filter by max price |
| `search airbnb 78704 min 3 beds` | Filter by bedrooms |

## How It Works

1. **Zillow search** — Finds all for-sale properties in the ZIP code (~2 seconds)
2. **Airbnb search** — Finds all active Airbnb listings in the same area (~3 seconds)
3. **Geo-matching** — Matches properties within 100-200 meters using GPS coordinates
4. **Investment analysis** — Calculates cap rate, cash flow, mortgage, and break-even occupancy

⏱️ **Total runtime: ~5-10 seconds per search** (RapidAPI is fast)

## Important Notes

- **Revenue estimates** are based on nightly rate × 70% occupancy. For precise data, use AirDNA ($100+/mo)
- **Geo-matching** means the Airbnb may be a neighbor's property, not the exact same house — always verify
- **Free tier** gives 100 Airbnb + 600 Zillow searches per month (RapidAPI free plan)
- **Cost per search: $0** on free plan

## Setup

1. Get free RapidAPI key: https://rapidapi.com → Sign up (free, no credit card)
2. Subscribe to these 2 APIs (both free):
   - Airbnb: https://rapidapi.com/3b-data-3b-data-default/api/airbnb13
   - Zillow: https://rapidapi.com/SwongF/api/us-property-market1
3. Add to your .env: `RAPIDAPI_KEY=your_key_here`
4. Test: `airbnb demo` (no API needed)
5. Live test: `search airbnb 78704`

See GUIDE.md for step-by-step setup instructions.

## Investment Metrics

The tool calculates (with 20% down, 7.25% rate, 30yr fixed):
- **Cap Rate** — annual return on full purchase price
- **Cash-on-Cash** — return on your actual cash invested
- **Monthly Cash Flow** — what's left after ALL expenses
- **GRM** — how many years of revenue to pay back purchase price
- **Break-even occupancy** — minimum % booked to not lose money

## Investment Grades

- 🟢 A (Excellent) — Cap ≥6%, CoC ≥10%, occupancy ≥85%
- 🟡 B (Good) — Solid returns, normal market risk
- 🟠 C (Fair) — Works but thin margins
- 🔴 D (Weak) — Avoid unless value-add opportunity
