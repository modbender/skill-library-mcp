# Duffel API Guide

## Key Concepts

- **Offer Request**: A search query (origin, destination, dates, passengers, cabin class) → returns offers
- **Offer**: A bookable flight option with price. Expires after ~20 minutes
- **Slice**: One leg of a journey (e.g., outbound or return). Contains segments
- **Segment**: A single flight within a slice (e.g., MIA→JFK is one segment of MIA→JFK→LHR)
- **Order**: A confirmed booking with PNR, passengers, and payment
- **Passenger**: Traveler info (name, DOB, nationality, contact)

## API Endpoints

| Action | Method | Endpoint |
|--------|--------|----------|
| Search flights | POST | `/air/offer_requests` |
| Get offer details | GET | `/air/offers/{id}?return_available_services=true` |
| Create booking | POST | `/air/orders` |
| Get order | GET | `/air/orders/{id}` |
| Cancel (quote) | POST | `/air/order_cancellations` |
| Cancel (confirm) | POST | `/air/order_cancellations/{id}/actions/confirm` |
| Seat maps | GET | `/air/seat_maps?offer_id={id}` |
| Places search | GET | `/places/suggestions?query={q}` |

## Authentication

- Header: `Authorization: Bearer <DUFFEL_TOKEN>`
- Header: `Duffel-Version: v2`
- Test tokens start with `duffel_test_`
- Live tokens start with `duffel_live_`

## Payment Types

- `balance`: Duffel account balance (prepaid wallet). Works from CLI. Unlimited in test mode.
- `arc_bsp_cash`: IATA agents only.
- Duffel Payments (card): Requires browser/JS frontend. Not for CLI use.

## Common Gotchas

- Offers expire quickly (~20 min). Always re-search if getting "offer expired" errors.
- Passenger IDs from the offer request must be passed when creating orders.
- Round-trips need two slices in the offer request.
- City codes (e.g., NYC) cover multiple airports; airport codes (e.g., JFK) are specific.
- `max_connections: 0` in offer request = nonstop only.
