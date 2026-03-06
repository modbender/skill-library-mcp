---
name: Car Rental
slug: car-rental
version: 1.0.0
homepage: https://clawic.com/skills/car-rental
description: Find the best car rental deals with price comparison, alerts, and lease vs rent analysis.
changelog: Initial release with monitoring, price tracking, and smart comparison features.
metadata: {"clawdbot":{"emoji":"🚗","requires":{"bins":[]},"os":["linux","darwin","win32"]}}
---

## Setup

On first use, read `setup.md`. Always ask user permission before creating ~/car-rental/ folder or any files.

## When to Use

User needs to rent, lease, or find vehicle deals. Agent handles price comparison across sites, monitors for deals, tracks preferences, and analyzes rent vs lease vs buy decisions.

## Architecture

Memory lives in `~/car-rental/`. See `memory-template.md` for structure.

```
~/car-rental/
├── memory.md        # Preferences, active searches, alerts
├── searches/        # Saved search configurations
└── history/         # Past rentals and price snapshots
```

## Quick Reference

| Topic | File |
|-------|------|
| Setup process | `setup.md` |
| Memory template | `memory-template.md` |
| Sites and sources | `sites.md` |
| Rent vs Lease | `comparison.md` |

## Core Rules

### 1. Always Compare Multiple Sources
Never recommend based on one site. Check at least 3 sources:
- Aggregators: Kayak, Google Flights, Rentalcars.com
- Direct: Hertz, Avis, Enterprise, Sixt, Europcar
- Budget: AutoEurope, DiscoverCars, local options

### 2. Factor Total Cost
Base price is misleading. Always calculate:
- Insurance (CDW, theft, liability)
- Fuel policy (full-to-full vs prepaid)
- Airport fees and taxes
- Mileage limits and overage charges
- One-way drop-off fees
- Young/senior driver surcharges

### 3. Track User Preferences
Save and apply:
- Preferred car class (economy, SUV, luxury)
- Insurance preferences (own coverage vs rental)
- Transmission preference (auto vs manual)
- Fuel type (petrol, diesel, electric, hybrid)
- Loyalty programs (Hertz Gold, Avis Preferred, etc.)

### 4. Monitor With Permission
When user explicitly requests an alert:
- Ask how often they want updates
- Check prices at requested intervals
- Notify on significant drops (>15%)
- Track availability for high-demand dates
- User can disable alerts anytime

### 5. Match Solution to Duration
| Duration | Best Option |
|----------|-------------|
| 1-7 days | Standard rental |
| 1-4 weeks | Long-term rental or subscription |
| 1-6 months | Lease or subscription |
| 6+ months | Lease, finance, or buy |

### 6. Location Intelligence
Prices vary dramatically by:
- Airport vs city center (airport often 30-50% more)
- Country regulations (some require IDP)
- Local vs international companies
- Seasonal demand (holidays, events)

## Car Rental Traps

- **Prepaid fuel trap** → Often overpriced. Full-to-full policy is usually cheaper unless you genuinely cannot refuel before return.
- **Basic insurance trap** → CDW often has high excess (€1000+). Check if your credit card or travel insurance covers this.
- **One-way fee surprise** → Can be €100-500+. Always check before booking if picking up and dropping off in different locations.
- **Manual transmission default** → In Europe, cheapest options are often manual. Filter for automatic if needed.
- **Mileage caps** → Some "cheap" deals have 100km/day limits. Calculate your actual needs.
- **Credit card hold trap** → Some companies block €1000-3000 on your card. Debit cards often refused.

## Comparison Framework

### Rent vs Lease vs Buy

| Factor | Short Rental | Long-term Lease | Buy |
|--------|--------------|-----------------|-----|
| Duration | Days to weeks | Months to years | Permanent |
| Upfront cost | Low | Medium | High |
| Monthly cost | Highest | Medium | Lowest (once paid) |
| Flexibility | Maximum | Medium | Low |
| Maintenance | Included | Usually included | Your responsibility |
| Best for | Travel, occasional use | Temporary relocation, testing | Permanent need |

### When to Consider Leasing
- Relocating 3-12 months
- Testing a car before buying
- Don't want maintenance hassle
- Business use with tax benefits
- Credit score issues (easier than financing)

### When Short-term Rental Beats Leasing
- Less than 2-3 months total use
- Sporadic use (weekends only)
- Different car needs each time
- Peak season (leasing harder to find)

## Alert Configuration

Users can set alerts for:
- **Price drop** — Notify when price falls below threshold
- **Availability** — Notify when specific car becomes available
- **Deal quality** — Notify when total cost is in bottom 20% historically
- **Comparison** — Notify when better option found vs current booking

Alert frequency options:
- Immediate (any change)
- Daily digest
- Weekly summary

## Data Storage

**All data is stored locally in ~/car-rental/ (created only with your permission):**
- memory.md — your preferences and active alerts
- searches/ — saved search configurations
- history/ — past rental price snapshots

**You control everything:**
- View: Read any file in ~/car-rental/
- Delete: Remove files or the entire folder anytime
- No cloud sync, no external storage

## Security & Privacy

**Data that stays local:**
- All preferences and search history in ~/car-rental/
- No telemetry or cloud sync

**When comparing prices:**
- Agent searches rental sites using your specified criteria (location, dates, car type)
- These search parameters are sent to rental sites (Kayak, Hertz, etc.) as part of normal searches
- No account credentials, payment info, or personal identifiers are shared

**This skill does NOT:**
- Store payment information
- Make bookings on your behalf
- Access files outside ~/car-rental/
- Send data to any server we control

## Related Skills
Install with `clawhub install <slug>` if user confirms:
- `travel` — trip planning and logistics
- `expenses` — track rental costs
- `money` — budget decisions

## Feedback

- If useful: `clawhub star car-rental`
- Stay updated: `clawhub sync`
