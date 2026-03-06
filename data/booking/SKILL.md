---
name: Booking
slug: booking
version: 1.0.0
description: Search, compare, and book accommodation across platforms with real pricing, user preferences, and end-to-end execution.
metadata: {"clawdbot":{"emoji":"🏨","requires":{"bins":[]},"os":["linux","darwin","win32"]}}
---

## Quick Reference

| Topic | File |
|-------|------|
| Search, compare, shortlist | `search.md` |
| Platforms, APIs, data sources | `platforms.md` |
| Total cost calculation | `pricing.md` |

## User Preferences

Store preferences in `~/booking/memory.md`. Load on activation.

```
~/booking/
├── memory.md       # Traveler type, budget, preferences
├── history.md      # Past bookings, liked properties
└── alerts.md       # Active price tracking
```

## Critical Rules — Never Skip

1. **Calculate TOTAL cost always** — base price + cleaning fee + service fee + tourist tax + any extras. Never quote per-night without fees
2. **Compare 3+ platforms** before recommending — Booking.com, Airbnb, direct hotel, local platforms (Hostelworld, HousingAnywhere, etc.)
3. **Verify real-time data** — don't recommend from training data. Check live availability and current prices
4. **Ask about purpose** — tourist, business, family, remote work, budget. Needs differ completely
5. **Surface deal-breakers early** — non-refundable, no A/C, far from center, negative review patterns, wifi issues for workers
6. **Shortlist, don't overwhelm** — 3-5 curated options with trade-offs, not 20 links to review
7. **Execute when asked** — "book this" means book, not "here's how to book"
8. **Check cancellation policy** — state deadline clearly before any booking

## Traveler-Specific Traps

| Type | Common Model Failure |
|------|---------------------|
| Casual | Ignoring stated budget, recommending based on popularity not fit |
| Business | Missing corporate rates, not understanding loyalty program math |
| Family | Treating "2 bedrooms" as sufficient without checking bed config, missing safety issues |
| Backpacker | Recommending mid-range, not calculating fees, missing hostel direct pricing |
| Nomad | Multiplying nightly×30 instead of real monthly rate, trusting "wifi included" |

## Before Recommending Any Property

- [ ] Total price calculated with ALL fees
- [ ] Cancellation policy stated
- [ ] Location context (walking time to center/meeting/beach)
- [ ] Review patterns checked (cleanliness, noise, wifi for workers, family-friendliness)
- [ ] Deal-breakers surfaced if any
