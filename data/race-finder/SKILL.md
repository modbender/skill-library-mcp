---
name: race-finder
description: Find upcoming races — running, trail, triathlon, cycling, swimming, and obstacle courses. Search by location, distance, sport, and date. Returns race details with registration links.
---

# Race Finder Skill

Search for upcoming races across the US and internationally. Data sourced from RunSignUp, the largest endurance event registration platform.

## API

**Base URL:** `https://api.racefinder.net`

### Search Races

```
GET /api/v1/races
```

All parameters are optional. Returns upcoming races sorted by date.

#### Query Parameters

| Parameter    | Type   | Description                                          | Example            |
|-------------|--------|------------------------------------------------------|--------------------|
| `q`         | string | Search by race name                                  | `q=Austin Marathon` |
| `city`      | string | City name                                            | `city=Austin`      |
| `state`     | string | US state code                                        | `state=TX`         |
| `country`   | string | Two-letter country code (default: US)                | `country=CA`       |
| `sport`     | string | Sport type (see below)                               | `sport=running`    |
| `distance`  | string | Distance category (see below)                        | `distance=marathon` |
| `start_date`| string | Races on or after this date (YYYY-MM-DD, default: today) | `start_date=2026-06-01` |
| `end_date`  | string | Races on or before this date (YYYY-MM-DD)            | `end_date=2026-12-31` |
| `zipcode`   | string | US zipcode (requires `radius`)                       | `zipcode=78701`    |
| `radius`    | string | Miles from zipcode                                   | `radius=25`        |
| `page`      | int    | Page number (default: 1)                             | `page=2`           |
| `per_page`  | int    | Results per page (default: 20, max: 50)              | `per_page=10`      |

#### Sport Values

| Value       | Description              |
|------------|--------------------------|
| `running`  | Road running races       |
| `trail`    | Trail running & ultras   |
| `triathlon`| Triathlons & duathlons   |
| `cycling`  | Bike races & rides       |
| `swimming` | Swimming & open water    |
| `obstacle` | Obstacle courses & mud runs |

#### Distance Values

| Value           | Range         |
|----------------|---------------|
| `5k`           | ~2–4 miles    |
| `10k`          | ~5–8 miles    |
| `half-marathon`| ~12–15 miles  |
| `marathon`     | ~25–28 miles  |
| `ultra`        | 30+ miles     |

#### Response Format

```json
{
  "races": [
    {
      "id": "12345",
      "name": "Austin Marathon",
      "date": "2026-03-15",
      "start_time": "7:00 AM",
      "sport": "running",
      "city": "Austin",
      "region": "Texas",
      "country": "US",
      "distances": [
        {"name": "Marathon", "miles": 26.2, "km": 42.2, "category": "marathon"},
        {"name": "Half Marathon", "miles": 13.1, "km": 21.1, "category": "half-marathon"}
      ],
      "prices": [
        {"name": "Marathon — $120", "price": 120, "currency": "USD", "available": true}
      ],
      "image_url": "https://...",
      "details_url": "https://racefinder.net/race/12345",
      "register_url": "https://runsignup.com/Race/12345?rsu_aff=..."
    }
  ],
  "page": 1,
  "total_results": 20
}
```

**No authentication required.**

## Examples

### Find races in a city

```bash
curl "https://api.racefinder.net/api/v1/races?city=Austin&state=TX"
```

### Find marathons near a zipcode

```bash
curl "https://api.racefinder.net/api/v1/races?zipcode=78701&radius=50&distance=marathon"
```

### Find trail races in Colorado this summer

```bash
curl "https://api.racefinder.net/api/v1/races?state=CO&sport=trail&start_date=2026-06-01&end_date=2026-08-31"
```

### Search by race name

```bash
curl "https://api.racefinder.net/api/v1/races?q=Ironman"
```

### Find 5Ks in California

```bash
curl "https://api.racefinder.net/api/v1/races?state=CA&sport=running&distance=5k"
```

## Tips for Agents

- Use `details_url` when users want to learn more about a race — it links to the full race page on racefinder.net
- Use `register_url` when users are ready to sign up — it links directly to registration
- Default search returns races starting from today, sorted by date
- Combine `zipcode` + `radius` for location-based search (US only)
- Combine `sport` + `distance` to narrow results (e.g., `sport=running&distance=half-marathon`)
- The `total_results` field shows how many results were returned on this page; use `page` to paginate
