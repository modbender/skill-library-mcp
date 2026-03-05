---
name: moltflights
description: Search cheap flights via the MoltFlights API. Find deals, compare prices, track routes, and set up price alerts.
homepage: https://moltflights.com
metadata:
  openclaw:
    emoji: "✈️"
    keywords: [travel, flights, cheap-flights, search, booking, price-alerts, digital-nomad]
tools:
  moltflights_search:
    description: Search for flights between two airports. Returns real-time prices with direct booking links.
    url: https://moltflights.com/api/search
    method: GET
    parameters:
      type: object
      properties:
        origin:
          type: string
          description: "IATA airport code for departure (e.g. HEL, JFK, LHR)"
        destination:
          type: string
          description: "IATA airport code for arrival (e.g. BKK, NRT, BCN)"
        date:
          type: string
          description: "Departure date YYYY-MM-DD. Omit for cheapest flights across the month."
        returnDate:
          type: string
          description: "Return date YYYY-MM-DD for round-trips. Omit for one-way."
        adults:
          type: integer
          description: "Number of adults 1-9 (default: 1)"
        children:
          type: integer
          description: "Number of children ages 2-12, 0-8 (default: 0)"
        infants:
          type: integer
          description: "Number of infants under 2, 0-8 (default: 0)"
      required: [origin, destination]
  moltflights_autocomplete:
    description: Look up IATA airport codes by city or airport name.
    url: https://moltflights.com/api/autocomplete
    method: GET
    parameters:
      type: object
      properties:
        term:
          type: string
          description: "City or airport name to search (min 2 characters)"
      required: [term]
---

# MoltFlights — Flight Search Skill

Search cheap flights using the [MoltFlights API](https://moltflights.com/agents). Returns structured JSON with real-time prices and direct booking links.

No API key required. No authentication. Just call the endpoint.

---

## Tools

### `moltflights_search` — Search Flights

```
GET https://moltflights.com/api/search?origin=HEL&destination=BKK&date=2026-03-15
```

| Parameter     | Required | Type    | Description                          |
|---------------|----------|---------|--------------------------------------|
| `origin`      | yes      | string  | IATA airport code (e.g. `HEL`)      |
| `destination` | yes      | string  | IATA airport code (e.g. `NRT`)      |
| `date`        | no       | string  | Departure date `YYYY-MM-DD`          |
| `returnDate`  | no       | string  | Return date `YYYY-MM-DD` (round-trip)|
| `adults`      | no       | integer | Number of adults, 1–9 (default: 1)   |
| `children`    | no       | integer | Children ages 2–12, 0–8 (default: 0) |
| `infants`     | no       | integer | Infants under 2, 0–8 (default: 0)    |

If `date` is omitted, the API returns the cheapest flights for the upcoming month.

### `moltflights_autocomplete` — Look Up Airport Codes

```
GET https://moltflights.com/api/autocomplete?term=bangkok
```

| Parameter | Required | Type   | Description                              |
|-----------|----------|--------|------------------------------------------|
| `term`    | yes      | string | City or airport name (min 2 characters)  |

---

## Example: Search Flights

```bash
curl "https://moltflights.com/api/search?origin=HEL&destination=BKK&date=2026-03-15"
```

### Response

```json
{
  "meta": {
    "source": "MoltFlights",
    "origin": "HEL",
    "destination": "BKK",
    "date": "2026-03-15",
    "adults": 1,
    "children": 0,
    "infants": 0,
    "results": 12
  },
  "data": [
    {
      "airline": "Finnair",
      "flight_number": "809",
      "price": "€432",
      "price_per_person": "€432",
      "departure": "2026-03-15T10:30:00",
      "return_at": "",
      "transfers": 1,
      "origin": "HEL",
      "destination": "BKK",
      "book_link": "https://www.aviasales.com/search/..."
    }
  ]
}
```

Each result includes a `book_link` — a direct booking URL the user can open.

---

## Example: Round-Trip with Passengers

```bash
curl "https://moltflights.com/api/search?origin=JFK&destination=CDG&date=2026-06-01&returnDate=2026-06-15&adults=2&children=1"
```

The `price` field shows the **total** for all seat-occupying passengers. `price_per_person` shows the per-person price.

---

## Common Use Cases

### 1. Find the cheapest flight to a destination

Search without a specific date to get the cheapest options for the whole month:

```bash
curl "https://moltflights.com/api/search?origin=LHR&destination=TYO"
```

### 2. Compare prices across dates

Run multiple searches for different dates and compare:

```bash
for date in 2026-04-01 2026-04-08 2026-04-15; do
  echo "=== $date ==="
  curl -s "https://moltflights.com/api/search?origin=HEL&destination=BKK&date=$date" | head -20
done
```

### 3. Price monitoring / alerts (cron job)

Check a route daily and alert when price drops below a threshold:

```bash
# Run daily via cron: 0 8 * * * /path/to/check-price.sh
PRICE=$(curl -s "https://moltflights.com/api/search?origin=HEL&destination=BKK&date=2026-05-01" \
  | grep -o '"price":"€[0-9]*"' | head -1 | grep -o '[0-9]*')

if [ "$PRICE" -lt 400 ]; then
  echo "Deal found: HEL→BKK for €$PRICE"
fi
```

### 4. Multi-city search

Search several routes and pick the cheapest:

```bash
for dest in BKK TYO BCN LIS; do
  echo "=== HEL → $dest ==="
  curl -s "https://moltflights.com/api/search?origin=HEL&destination=$dest" \
    | grep -o '"price":"€[0-9]*"' | head -1
done
```

---

## Common IATA Codes

| Code | City            | Code | City          |
|------|-----------------|------|---------------|
| HEL  | Helsinki        | LHR  | London        |
| JFK  | New York        | CDG  | Paris         |
| NRT  | Tokyo Narita    | BKK  | Bangkok       |
| BCN  | Barcelona       | FCO  | Rome          |
| SIN  | Singapore       | DXB  | Dubai         |
| LAX  | Los Angeles     | SFO  | San Francisco |
| BER  | Berlin          | AMS  | Amsterdam     |
| IST  | Istanbul        | LIS  | Lisbon        |

Don't know the code? Use the `moltflights_autocomplete` tool:

```bash
curl "https://moltflights.com/api/autocomplete?term=bangkok"
```

---

## Error Handling

- **400** — Missing `origin` or `destination` parameter
- **Empty `data` array** — No flights found for this route/date. Try a different date or omit the date for flexible search.

---

## Tips

- Prices are in EUR (€)
- Results are sorted: exact date matches first, then nearby dates by price
- Omitting `date` gives you the cheapest flights across the whole upcoming month
- The API is free and requires no authentication
- Responses are cached for 5 minutes
