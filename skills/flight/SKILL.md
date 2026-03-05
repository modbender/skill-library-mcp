---
name: Flight
slug: flight
version: 1.0.1
description: Search, compare, book, and manage flights with price tracking, multi-platform comparison, and loyalty optimization.
changelog: "Preferences now persist across skill updates"
metadata: {"clawdbot":{"emoji":"✈️","requires":{"bins":[]},"os":["linux","darwin","win32"]}}
---

## Quick Reference

| Topic | File |
|-------|------|
| Search, compare, flexible dates | `search.md` |
| Booking, rebooking, disruptions | `booking.md` |
| Price alerts, tracking, predictions | `tracking.md` |
| Miles, points, status, awards | `points.md` |
| APIs, integrations, data sources | `apis.md` |

## User Profile

Preferences persist in `~/flight/memory.md`. Create on first use.

```markdown
## Home Airports
<!-- Primary airports. Format: "IATA, IATA" -->
<!-- Examples: MAD, BCN | JFK, EWR, LGA -->

## Preferred Airlines
<!-- Airlines or alliances. Format: "airline | alliance" -->
<!-- Examples: Iberia, BA | Star Alliance | any -->

## Elite Status
<!-- Loyalty tiers. Format: "program: tier" -->
<!-- Examples: BA Gold, United 1K, Marriott Platinum -->

## Budget Style
<!-- budget | moderate | premium | business-class -->

## Travel Style
<!-- solo | couple | family-with-kids | business-frequent -->

## Carry-On Only
<!-- yes | no | prefer -->
```

*Empty sections = ask when relevant. Fill as you learn.*

## Data Storage

Store flight data in ~/flights/:
- searches — saved route searches with price history
- bookings — active reservations with PNRs
- alerts — price drop thresholds by route
- history — past flights for loyalty tracking

## Core Rules

- Always compare 3+ platforms before recommending (Skyscanner, Google Flights, Kiwi, direct airline)
- Calculate TRUE total cost including baggage, seat selection, and fees — especially for budget carriers
- Check visa requirements before booking international flights
- For families: verify adjacent seat availability before booking, not after
- Set price alerts on flexible dates (±3 days) for better deal coverage
- Track flight status starting 24h before departure — proactive rebooking on delays
- Never book non-refundable for trips >30 days out without asking
- When comparing award bookings: calculate cents-per-point against cash price
- Warn about tight connections (<90min domestic, <2h international)
- For multi-city: check if separate bookings are cheaper than one ticket
