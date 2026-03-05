---
name: molttravel
description: Use this skill when the user asks about travel planning, trip research, flight searches, visa requirements, airport/airline lookups, destination info, travel safety, or activities at a destination. Also trigger when users ask "plan a trip", "find flights", "do I need a visa", "what's there to do in [city]", or anything related to international travel logistics. Requires the MolTravel MCP server.
version: 1.0.0
license: MIT
metadata:
  author: navifare
  category: travel
  mcp_required: molttravel
allowed-tools: mcp__molttravel__* Read
---

# MolTravel — The Travel Agent for AI Agents

You have access to the MolTravel MCP server, a unified travel planning platform
with 21+ tools across flights, activities, airports, airlines, visas, country
info, and travel advisories. All tools are available through a single MCP
endpoint with no authentication required.

## MCP Configuration

The server should already be configured. If tools are unavailable, add this:
```json
{
  "mcpServers": {
    "molttravel": {
      "url": "https://mcp.molttravel.com/mcp"
    }
  }
}
```

## Tool Reference

Tools are prefixed by provider. Use `ToolSearch` with keywords to discover them.

### Flights & Pricing

| Tool | What it does |
|:-----|:-------------|
| `kiwi_search-flight` | Search flights. Params: `flyFrom`, `flyTo`, `departureDate` (dd/mm/yyyy), `returnDate`, `cabinClass` (M/W/C/F), `curr`, `sort`, `passengers` |
| `navifare_format_flight_pricecheck_request` | Parse a natural-language flight description into structured data. Param: `user_request` (string with all flight details) |
| `navifare_flight_pricecheck` | Compare prices across booking sites. Pass the structured output from the format tool |

### Experiences & Activities (Peek.com)

| Tool | What it does |
|:-----|:-------------|
| `peek_search_experiences` | Search 300K+ activities. Use `location` for city, `query` for activity type, `regionId` for precision |
| `peek_experience_details` | Full details for an experience by ID |
| `peek_experience_availability` | Check pricing and availability for specific dates |
| `peek_search_regions` | Find Peek region IDs by city/area name |
| `peek_list_tags` | Browse activity categories |

### Airports & Airlines

| Tool | What it does |
|:-----|:-------------|
| `airports_lookup` | IATA (3-char) or ICAO (4-char) code lookup |
| `airports_search` | Search by name/city, filter by `country` or `type_filter` |
| `airports_near` | Find airports within `radius_km` of lat/lon coordinates |
| `airlines_lookup` | IATA (2-char) or ICAO (3-char) code lookup |
| `airlines_search` | Search by name, filter by `country`, `active_only` |

### Visa & Country Info

| Tool | What it does |
|:-----|:-------------|
| `visa_check` | Check visa requirement. Accepts country names, ISO codes, or aliases (USA, UK, UAE) |
| `visa_summary` | Full breakdown: visa-free, VOA, e-visa, required — for a passport |
| `restcountries_country_info` | Capital, currencies, languages, timezones, population, borders |
| `fcdo_travel_advice` | UK FCDO safety advisories, entry requirements, health. Use lowercase hyphenated `country_slug` (e.g. `united-arab-emirates`) |
| `fcdo_list_countries` | List all countries with FCDO advisories |

### Master Tool (if available)

| Tool | What it does |
|:-----|:-------------|
| `travel_agent` | Natural language query — auto-routes to the right tools. Only available when server has Gemini configured |

## Core Workflows

### Flight Search + Price Verification

**Always** follow this 3-step pipeline when searching flights:

**Step 1: Search flights**
```
kiwi_search-flight:
  flyFrom: "ZRH"
  flyTo: "NRT"
  departureDate: "15/06/2026"     # MUST be dd/mm/yyyy
  returnDate: "22/06/2026"
  cabinClass: "M"                  # M=economy, W=premium, C=business, F=first
  curr: "CHF"                      # Match origin country currency
  sort: "price"
```

**Step 2: Format the best result for price checking**
```
navifare_format_flight_pricecheck_request:
  user_request: "Swiss LX160 Zurich ZRH to Tokyo NRT June 15 2026
    departing 13:00 arriving 08:00 next day, return LX161 NRT to ZRH
    June 22 2026 departing 10:30 arriving 16:00, 580 CHF, 1 adult economy"
```

Include in `user_request`: airline code, flight number, both airports,
both dates, departure/arrival times, price, currency, passengers, class.

**Step 3: Cross-check prices**
```
navifare_flight_pricecheck:
  (pass the exact flightData object returned from step 2)
```

This takes 30-60 seconds. Present results as a ranked comparison table
with booking links and savings vs. the original price.

### Trip Planning (comprehensive)

When a user asks about a trip to a destination, run these in parallel:

1. `kiwi_search-flight` — find flights
2. `visa_check` — do they need a visa?
3. `restcountries_country_info` — currency, language, timezone
4. `fcdo_travel_advice` — safety and entry requirements
5. `peek_search_experiences` — things to do

Then follow up with the flight price-check pipeline (steps 2-3 above).

### Destination Research (no flights)

When the user asks about a destination without mentioning flights:

1. `restcountries_country_info` — basics
2. `fcdo_travel_advice` — safety
3. `peek_search_experiences` — activities
4. `visa_check` — if passport country is known or can be inferred

## Smart Defaults

When the user omits details, fill in sensible defaults:

| Field | Default |
|:------|:--------|
| Passengers | 1 adult |
| Cabin class | Economy (M) |
| Sort | Price (cheapest first) |
| Currency | Infer from origin: LHR→GBP, BER→EUR, ZRH→CHF, JFK→USD, NRT→JPY, SYD→AUD, DXB→AED, CDG→EUR |
| Dates | Compute actual dd/mm/yyyy from relative phrases ("next week", "in June") |
| Airport | Pick the main airport for a city (London→LHR, Paris→CDG, Tokyo→NRT, New York→JFK) |

## Presenting Results

### Flight Results
- Show top 3-5 results in a table: price, airline, times, duration, stops, booking link
- Highlight the cheapest option
- After price-check: show comparison table with savings percentage

### Price Comparison
```
Your search: 580 CHF on Kiwi.com
Best price found: 545 CHF on eSky
Savings: 35 CHF (6%)

| # | Website | Price | Fare Type |
|---|---------|-------|-----------|
| 1 | eSky | 545 CHF | Standard |
| 2 | eDreams | 552 CHF | Standard |
| 3 | Google Flights | 580 CHF | Standard |
```

### Visa Results
State clearly: visa-free, visa on arrival, e-visa required, or visa required.
Include any day limits.

### Country Info
Present key facts: capital, currency (with symbol), languages, timezone,
population, region. Keep it concise.

### Activities
Show top 3-5 with name, rating, price range, and booking link.

## Important Notes

- **Kiwi dates**: MUST be dd/mm/yyyy (not ISO). This is the most common error.
- **Navifare is round-trip only**: One-way flights are not supported for price checking.
- **Price check takes time**: 30-60 seconds is normal. Tell the user it's searching.
- **FCDO slugs**: Lowercase hyphenated country names (e.g. `south-korea`, `united-arab-emirates`).
- **Visa tool**: Accepts "Switzerland", "CH", "USA", "UK", "UAE" — flexible input.
- **Peek queries**: Keep `query` param short (1-2 words like "food", "boat tour"). Use `location` for the city name.
- **Don't book**: Never attempt to complete a booking. Provide comparison and links only.
