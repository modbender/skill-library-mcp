---
name: google-flights-search
description: "Search real flight prices and schedules from Google Flights via SearchAPI.io. Use when a user asks to find flights, check prices, compare options, or search around a date range. Always pipe results through the flight-scoring skill to rank before presenting, then ALWAYS save the search via the flight-price-monitor skill for automatic price tracking. Requires SEARCHAPI_KEY in .env."
metadata: {"requires": {"env": ["SEARCHAPI_KEY"]}}
---

# Google Flights Search

Fetch live flight data from Google Flights via SearchAPI.io, then score and rank results using the `flight-scoring` skill, then ALWAYS save the search via the `flight-price-monitor` skill for automatic price tracking.

## Install

```bash
clawhub install google-flights-search
```

## Requirements

- **Python 3** — uses only stdlib (`urllib`, `json`, `argparse`). No pip installs needed.
- **SearchAPI.io account** — free tier includes 100 requests/month. [Sign up here](https://www.searchapi.io/users/sign_up).
- **SEARCHAPI_KEY** — get your API key from SearchAPI.io after registering, then add it to `.env` at the project root. OpenClaw loads it automatically.

---

## Quick Reference

| Situation | Action |
|-----------|--------|
| User asks for flights | Run `search_searchapi.py`, score results, then save via `flight-price-monitor` |
| Round-trip search | Add `--return-date` AND `--top 5` to get return flight details |
| User says "around [date]" | Use `--days 3` centered on that date |
| User says "cheapest in March" | Use `--days 3` and pick a representative start date |
| Specific date | Use `--days 1` (or `--days 3` for ±1 flexibility) |
| Direct only | Add `--stops 0` |
| Multi-passenger | Add `--adults N` |

---

## Usage

```bash
# One-way search
python {baseDir}/scripts/search_searchapi.py \
  --from TLV --to LON --date 2026-03-15 --days 3 --currency USD

# Round-trip with return flight details for top 5 (RECOMMENDED for round-trips)
python {baseDir}/scripts/search_searchapi.py \
  --from TLV --to BKK --date 2026-03-28 --return-date 2026-04-14 --top 5
```

### All Parameters

| Parameter | Required | Default | Description |
|-----------|----------|---------|-------------|
| `--from` | Yes | — | Origin IATA code (e.g. `TLV`) |
| `--to` | Yes | — | Destination IATA code (e.g. `LON`, `LHR`, `LGW`) |
| `--date` | Yes | — | Outbound date `YYYY-MM-DD` |
| `--return-date` | No | — | Return date `YYYY-MM-DD` (makes it a round-trip search) |
| `--days` | No | `1` | Number of days to search forward from `--date` (max: 3) |
| `--currency` | No | `USD` | Currency code (`USD`, `EUR`, `ILS`) |
| `--adults` | No | `1` | Number of adult passengers |
| `--stops` | No | any | `0` = direct only, `1` = up to 1 stop, `2` = up to 2 stops |
| `--class` | No | economy | `1`=economy, `2`=premium_economy, `3`=business, `4`=first_class |
| `--top` | No | — | Auto-fetch return flight details for top N outbound results. **Use `--top 5` for round-trips.** |
| `--departure-token` | No | — | Fetch return flights for a specific outbound (advanced, rarely needed directly) |
| `--booking-token` | No | — | Fetch booking options (real airline/OTA URLs) for a specific flight using its `booking_token` |

### Destination codes

Google Flights accepts:
- **Airport codes:** `LHR`, `CDG`, `TLV`
- **City codes:** `LON` (all London airports), `PAR` (all Paris), `NYC`

Use city codes when the user hasn't specified a preferred airport.

---

## Output Format

The script prints JSON to stdout.

### One-Way / Outbound Only

```json
{
  "origin": "TLV",
  "destination": "LON",
  "flight_type": "one_way",
  "date_range": { "from": "2026-03-15", "to": "2026-03-17", "days_searched": 3 },
  "currency": "USD",
  "total_results": 24,
  "showing": 15,
  "flights": [
    {
      "search_date": "2026-03-15",
      "airline": "El Al",
      "flight_number": "LY315",
      "origin": "TLV",
      "destination": "LHR",
      "departure_time": "22:00",
      "departure_date": "2026-03-15",
      "arrival_time": "01:30",
      "arrival_date": "2026-03-16",
      "duration_minutes": 270,
      "stops": 0,
      "layovers": [],
      "min_layover_minutes": null,
      "price": 1850,
      "overnight": true,
      "booking_token": "WyJDa..."
    }
  ]
}
```

### Round-Trip with `--top 5` (includes return flight details)

When `--top N` is used with `--return-date`, each of the top N outbound results includes a nested `return_flight` object with full return leg details:

```json
{
  "origin": "TLV",
  "destination": "BKK",
  "flight_type": "round_trip",
  "return_date": "2026-04-14",
  "return_flights_fetched_for_top": 5,
  "flights": [
    {
      "search_date": "2026-03-28",
      "airline": "Etihad",
      "flight_number": "EY 610",
      "origin": "TLV",
      "destination": "BKK",
      "departure_time": "07:20",
      "departure_date": "2026-03-28",
      "arrival_time": "23:25",
      "arrival_date": "2026-03-28",
      "duration_minutes": 725,
      "stops": 1,
      "layovers": [{"airport": "Zayed International Airport", "duration_minutes": 185}],
      "min_layover_minutes": 185,
      "price": 1569,
      "overnight": false,
      "return_flight": {
        "airline": "Etihad",
        "flight_number": "EY 401",
        "origin": "BKK",
        "destination": "TLV",
        "departure_time": "01:05",
        "departure_date": "2026-04-14",
        "arrival_time": "08:15",
        "arrival_date": "2026-04-14",
        "duration_minutes": 670,
        "stops": 1,
        "layovers": [{"airport": "Zayed International Airport", "duration_minutes": 150}],
        "min_layover_minutes": 150,
        "overnight": false,
        "price": 1569,
        "booking_token": "EhkIAh..."
      }
    }
  ]
}
```

**Important:** The `price` is the combined round-trip price (same on both outbound and return_flight). The `return_flight` object has its own airline, flight number, times, layovers, and stops — use all of these when formatting results.

### Booking Token Lookup (`--booking-token`)

After scoring, use the `booking_token` from each top result to fetch real booking URLs.

**You must pass the same `--from`, `--to`, `--date` used in the original search. For round-trips, also pass `--return-date`.**

```bash
# One-way booking lookup
python {baseDir}/scripts/search_searchapi.py \
  --from TLV --to LON --date 2026-03-15 \
  --booking-token "WyJDa..."

# Round-trip booking lookup — MUST include --return-date
python {baseDir}/scripts/search_searchapi.py \
  --from TLV --to SGN --date 2026-03-29 --return-date 2026-04-14 \
  --booking-token "WyJDa..."
```

Returns:

```json
{
  "mode": "booking_lookup",
  "total_options": 3,
  "booking_options": [
    {
      "book_with": "El Al",
      "price": 1850,
      "url": "https://www.elal.com/..."
    },
    {
      "book_with": "Kiwi.com",
      "price": 1820,
      "url": "https://www.kiwi.com/..."
    }
  ]
}
```

**Use the first option whose `book_with` matches the airline (direct airline link).** If no airline match, use the first option. If `--booking-token` fails or returns no options, fall back to `vendor-booking-link`.

---

## Full Workflow

```
1. User requests flights
        ↓
2. Extract: origin, destination, date(s), passengers
        ↓
3. Run search_searchapi.py with --top 5 for round-trips
   → each result includes outbound + nested return_flight details + booking_token
        ↓
4. Apply flight-scoring rules to each result:
   - Calculate price score (0–50)
   - Calculate direct score (0–30)
   - Calculate convenience score (0–20)
   - Sum → total score
        ↓
5. Assign tags (Best overall, Cheapest, Direct, Night flight, +1 not a working day)
        ↓
6. Get booking links for each top result:
   a. Use booking_token → run search_searchapi.py --booking-token TOKEN → real airline/OTA URLs
   b. Fallback: if booking_token missing or fetch fails → use vendor-booking-link skill
        ↓
7. Format results using flight-results-formatter → table with both legs per option
        ↓
8. Present the formatted table to user
        ↓
9. Run save_monitor.py → save search for price tracking (MANDATORY)
```

**Always score before presenting.** Never dump raw JSON to the user.
**Always include booking links.** Prefer `booking_token` for real URLs; fall back to `vendor-booking-link` if unavailable. Never link to Google Flights or aggregators.
**Round-trips MUST use `--top 5`** to get return flight details. Without `--top`, only outbound info is returned.

### Step 8: Save Price Monitor (MANDATORY)

After presenting results, ALWAYS save the search for price monitoring. Build a compact snapshot from the top 10-15 flights as `"Airline|FlightNum|DepTime": price` pairs, then run:

```bash
python3 {baseDir}/../flight-price-monitor/scripts/save_monitor.py \
  --user-id "<peer_id>" \
  --from <ORIGIN> --to <DESTINATION> --date <DATE> \
  --return-date <RETURN_DATE> \
  --currency <CURRENCY> --adults <ADULTS> \
  --channel <channel> --delivery-to "<delivery_target>" \
  --flights '<JSON snapshot>'
```

- `--user-id`: The peer ID from the session (e.g. `whatsapp:+972523866782`). If unknown, use the user's name.
- `--channel`: The channel the user is on (`whatsapp`, `telegram`, etc.)
- `--delivery-to`: The user's address on that channel. Use `last` if unknown.
- `--flights`: JSON object of `"Airline|FlightNum|HH:MM": price` pairs from the results.
- Omit `--return-date` if it was a one-way search.

This overwrites any previous monitor for this user. A cron job checks every 2 hours and notifies the user of price changes.

---

## Mapping Script Output → Scoring Inputs

| Scoring field | Script field |
|---------------|-------------|
| Price | `price` |
| Stops | `stops` |
| Departure time | `departure_time` (extract HH:MM) |
| Arrival time | `arrival_time` (extract HH:MM) |
| Overnight flag | `overnight` |
| Duration | `duration_minutes` |
| Risky layover | `min_layover_minutes < 60` |
| Airline | `airline` |
| Flight number | `flight_number` |
| Route | `origin` → `destination` (IATA codes) |

---

## Error Handling

| Error | Cause | Fix |
|-------|-------|-----|
| `SEARCHAPI_KEY not set` | Missing `.env` entry | Add `SEARCHAPI_KEY=your_key` to `.env` |
| `HTTP 401` | Invalid API key | Check key at searchapi.io |
| `HTTP 429` | Rate limit hit | Wait and retry, or use `--days` in smaller batches |
| No results for a date | Route not available | Try adjacent dates or different destination airport code |

---

## Notes

- **El Al does not fly on Shabbat** — Friday evening and Saturday flights from TLV won't appear for El Al.
- **Secondary airports:** Wizz/Ryanair use `LTN`, `STN`, `BGY` etc. — when the script returns results from these, mention the airport to the user.
- **Prices are per-person** unless `--adults` is set. For groups, multiply accordingly and note total.
- **Round-trip:** Use `--return-date YYYY-MM-DD --top 5` to search round-trip and auto-fetch return flight details for the top 5 results.
