---
name: ryanair-fare-finder
description: >
  Build and interpret Ryanair fare-finder URLs for cheap flight searches.
  Use when the user wants to find budget flights from a specific UK airport,
  configure departure/return time windows, set overnight or multi-night trip
  parameters, filter by day of week, or constrain results by price and currency.
  Handles all fare-finder query parameters including passenger counts, date ranges,
  flexible dates, and promo codes.
compatibility: Requires network access to reach ryanair.com fare-finder pages.
metadata:
  author: Callum Kemp
  version: "1.0"
  base-url: "https://www.ryanair.com/gb/en/fare-finder"
---

# Ryanair Fare Finder

Generate, modify, and explain Ryanair fare-finder URLs from user requirements.

## Base URL

```
https://www.ryanair.com/gb/en/fare-finder
```

All parameters below are appended as query-string key-value pairs.

## Parameter Reference

### Route

| Parameter            | Type    | Example | Description                                                                 |
|----------------------|---------|---------|-----------------------------------------------------------------------------|
| `originIata`         | string  | `MAN`   | IATA code of the departure airport (e.g. MAN, STN, LTN, EDI, BHX, LPL).   |
| `destinationIata`    | string  | `ANY`   | IATA code of the arrival airport, or `ANY` for all destinations.            |
| `isMacDestination`   | boolean | `false` | When `true`, filters to multi-airport city destinations only.               |

### Trip type

| Parameter   | Type    | Example | Description                                          |
|-------------|---------|---------|------------------------------------------------------|
| `isReturn`  | boolean | `true`  | `true` for return (round-trip), `false` for one-way. |

### Passengers

| Parameter | Type | Example | Description              |
|-----------|------|---------|--------------------------|
| `adults`  | int  | `1`     | Number of adults (16+).  |
| `teens`   | int  | `0`     | Number of teens (12-15). |
| `children`| int  | `0`     | Number of children (2-11).|
| `infants` | int  | `0`     | Number of infants (< 2). |

### Date range

| Parameter     | Type    | Example      | Description                                                                 |
|---------------|---------|--------------|-----------------------------------------------------------------------------|
| `dateOut`     | date    | `2026-02-01` | Start of the search window (YYYY-MM-DD).                                    |
| `dateIn`      | date    | `2027-01-31` | End of the search window (YYYY-MM-DD).                                      |
| `isExactDate` | boolean | `false`      | `true` to search a specific date only; `false` to scan the full date range. |

### Day and flexibility

| Parameter        | Type    | Example    | Description                                                        |
|------------------|---------|------------|--------------------------------------------------------------------|
| `dayOfWeek`      | enum    | `SATURDAY` | Restrict outbound to a specific day. Values: `MONDAY`..`SUNDAY`.   |
| `isFlexibleDay`  | boolean | `false`    | When `true`, Ryanair widens the day-of-week filter by +/- 1 day.  |

### Stay duration

| Parameter    | Type | Example | Description                                            |
|--------------|------|---------|--------------------------------------------------------|
| `daysTrip`   | int  | `1`     | Total trip length in days (outbound day counts as 1).  |
| `nightsFrom` | int  | `0`     | Minimum number of nights at the destination.           |
| `nightsTo`   | int  | `1`     | Maximum number of nights at the destination.           |

### Time windows

| Parameter          | Type   | Example | Description                                      |
|--------------------|--------|---------|--------------------------------------------------|
| `outboundFromHour` | string | `00:00` | Earliest acceptable outbound departure time.     |
| `outboundToHour`   | string | `11:00` | Latest acceptable outbound departure time.       |
| `inboundFromHour`  | string | `13:00` | Earliest acceptable return departure time.       |
| `inboundToHour`    | string | `23:59` | Latest acceptable return departure time.         |

### Pricing

| Parameter      | Type   | Example | Description                                                        |
|----------------|--------|---------|--------------------------------------------------------------------|
| `currency`     | string | `GBP`   | ISO 4217 currency code (GBP, EUR, etc.).                           |
| `priceValueTo` | int    | `80`    | Maximum total return price. Leave empty for no cap.                |
| `promoCode`    | string | *(empty)* | Ryanair promotional code, if applicable.                         |

## Example: Overnight Saturday getaway from Manchester

The following URL searches for return flights from Manchester to anywhere,
departing on a Saturday morning, returning the same day or next day in the
afternoon/evening, across the full year, under GBP 80 return:

```
https://www.ryanair.com/gb/en/fare-finder?originIata=MAN&destinationIata=ANY&isReturn=true&isMacDestination=false&promoCode=&adults=1&teens=0&children=0&infants=0&dateOut=2026-02-01&dateIn=2027-01-31&daysTrip=1&nightsFrom=0&nightsTo=1&dayOfWeek=SATURDAY&isExactDate=false&outboundFromHour=00:00&outboundToHour=11:00&inboundFromHour=13:00&inboundToHour=23:59&priceValueTo=80&currency=GBP&isFlexibleDay=false
```

### Why these time windows work for overnights

- **Outbound 00:00-11:00** — arrive by early afternoon, giving a full day/evening at the destination.
- **Inbound 13:00-23:59** — depart after checkout / lunch the next day, home by late evening.

## Step-by-step: building a URL from scratch

1. Start with the base URL.
2. Set `originIata` to the user's departure airport IATA code.
3. Set `destinationIata` to a specific IATA code or `ANY`.
4. Choose `isReturn=true` for returns or `false` for one-way.
5. Set passenger counts (`adults`, `teens`, `children`, `infants`).
6. Define the date search window with `dateOut` and `dateIn`.
7. Pick `dayOfWeek` and set `isExactDate=false` to scan all matching days.
8. Configure stay duration with `daysTrip`, `nightsFrom`, `nightsTo`.
9. Set outbound/inbound time windows to taste.
10. Set `currency` and optionally `priceValueTo` for a price cap.
11. Add `promoCode` if the user has one.

## Common UK origin airports

| IATA | Airport             |
|------|---------------------|
| MAN  | Manchester          |
| STN  | London Stansted     |
| LTN  | London Luton        |
| LGW  | London Gatwick      |
| EDI  | Edinburgh           |
| BHX  | Birmingham          |
| LPL  | Liverpool           |
| BRS  | Bristol             |
| EMA  | East Midlands       |
| GLA  | Glasgow             |
| BFS  | Belfast Intl        |
| LBA  | Leeds Bradford      |
| NCL  | Newcastle           |
| ABZ  | Aberdeen            |
