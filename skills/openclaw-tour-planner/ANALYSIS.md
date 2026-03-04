# OpenCLAW Tour Planner — Architecture & Roadmap

> **⚠️ This is a design / roadmap document, not a description of current functionality.**
>
> It describes possible future capabilities (Playwright scrapers, flight APIs, hotel search).
> **None of the scraping features described here are implemented in the current release.**
> Playwright is NOT a dependency. No scraping code exists in `src/`.
>
> For the current feature set, see `SKILL.md` and `src/`.

---

## Executive Summary

**Project Name:** OpenCLAW Tour Planner  
**Domain:** openclaw.tours  
**License:** Open Source (MIT)  
**Monetization:** None (future: affiliate links optional)

A universal travel planning skill for OpenClaw agents that combines free APIs, web scraping, and curated knowledge to generate comprehensive itineraries.

---

## Core Philosophy

1. **Agent-First Design** — The skill is built for agents, not humans
2. **Zero-Cost Stack** — All data sources must have generous free tiers or be completely free
3. **Progressive Enhancement** — Start simple, add complexity only when needed
4. **Privacy-First** — No user data storage, ephemeral planning sessions

---

## Data Sources Analysis

### Tier 1: Free APIs (No Auth or Generous Limits)

| Source | Data Type | Free Tier | Auth Required | Rate Limits |
|--------|-----------|-----------|---------------|-------------|
| **Nominatim (OpenStreetMap)** | Geocoding, places, boundaries | Unlimited | No | 1 req/sec |
| **Visual Crossing Weather** | Weather forecasts, historical | 1000 records/day | Yes (free key) | 1000/day |
| **OpenWeatherMap** | Current weather, 5-day forecast | 1000 calls/day | Yes (free key) | 1000/day |
| **Wikivoyage API** | Travel guides, attractions, tips | Unlimited | No | Respectful use |
| **RestCountries** | Country info, currencies, languages | Unlimited | No | None |
| **ExchangeRate-API** | Currency conversion | 1500 requests/month | No (standard) | 1500/month |
| **AirLabs (Aviation)** | Airports, airlines, routes | 1000 calls/month | Yes (free key) | 1000/month |

### Tier 2: Web Scraping (Playwright-Based)

| Site | Data Extractable | Complexity | Legal Considerations |
|------|------------------|------------|---------------------|
| **Google Flights** | Flight prices, routes, times | High | robots.txt allows, but dynamic |
| **Skyscanner** | Flight comparisons | Medium | API preferred, scraping restricted |
| **Rome2Rio** | Multi-modal transport | Medium | Terms restrict scraping |
| **Booking.com** | Hotel prices, availability | High | Aggressive anti-bot |
| **Hostelworld** | Budget accommodations | Medium | Scraping possible |
| **GetYourGuide** | Tours, activities | Medium | API available (paid) |
| **TripAdvisor** | Reviews, attractions | High | Strict anti-scraping |

**Recommendation:** Use scraping only as fallback, prioritize APIs.

### Tier 3: Static Knowledge Bases

| Source | Content | Format | Update Frequency |
|--------|---------|--------|------------------|
| **Wikivoyage Dump** | Full travel guides | XML/JSON | Monthly |
| **OpenStreetMap Data** | POIs, boundaries | PBF/Osmosis | Daily |
| **GeoNames** | Cities, altitudes, timezones | TSV/JSON | Weekly |
| **OurAirports** | Airport database | CSV | Monthly |

---

## Skill Capabilities Matrix

### Phase 1: MVP (Core Planning)

```
┌─────────────────────────────────────────────────────────────┐
│  INPUT: "Plan a 5-day trip to Tokyo in April"              │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│  1. DESTINATION INTELLIGENCE                                │
│     • Geocode Tokyo (Nominatim)                            │
│     • Get country info (RestCountries)                     │
│     • Fetch weather forecast (Visual Crossing)             │
│     • Load Wikivoyage guide snippets                       │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│  2. ITINERARY GENERATION                                    │
│     • Day-by-day structure                                  │
│     • Morning/Afternoon/Evening blocks                      │
│     • Activity categorization (culture, food, nature)       │
│     • Travel time estimates between locations               │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│  3. OUTPUT FORMAT                                           │
│     • Markdown itinerary                                    │
│     • Budget estimate (rough)                               │
│     • Packing suggestions based on weather                  │
│     • Cultural tips from Wikivoyage                         │
└─────────────────────────────────────────────────────────────┘
```

### Phase 2: Enhanced (Transport & Booking)

```
┌─────────────────────────────────────────────────────────────┐
│  4. FLIGHT SEARCH (Amadeus API - free tier)                │
│     • Search routes from user location                      │
│     • Price estimates                                       │
│     • Alternative airports                                  │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│  5. ACCOMMODATION SUGGESTIONS                               │
│     • Neighborhood recommendations                          │
│     • Price ranges by area                                  │
│     • Proximity to attractions                              │
│     • (Future: Booking.com affiliate links)                 │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│  6. LOCAL TRANSPORT                                         │
│     • Airport to city options                               │
│     • Public transport passes                               │
│     • Ride-sharing availability                             │
│     • Walking/biking routes                                 │
└─────────────────────────────────────────────────────────────┘
```

### Phase 3: Advanced (Real-time & Personalization)

```
┌─────────────────────────────────────────────────────────────┐
│  7. REAL-TIME DATA                                          │
│     • Current events/festivals                              │
│     • Attraction opening hours                              │
│     • Restaurant availability (scraping)                    │
│     • Live weather alerts                                   │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│  8. PERSONALIZATION ENGINE                                  │
│     • Interest profiling (foodie, adventure, history, etc.) │
│     • Pace preferences (relaxed vs packed)                  │
│     • Budget constraints                                    │
│     • Accessibility needs                                   │
└─────────────────────────────────────────────────────────────┘
```

---

## Technical Architecture

### Directory Structure

```
openclaw-tour-planner/
├── SKILL.md                    # Skill definition & usage
├── package.json
├── src/
│   ├── index.ts               # Main entry point
│   ├── types.ts               # TypeScript interfaces
│   ├── apis/                  # API clients
│   │   ├── nominatim.ts       # Geocoding
│   │   ├── weather.ts         # Visual Crossing
│   │   ├── wikivoyage.ts      # Travel guides
│   │   ├── amadeus.ts         # Flights (Phase 2)
│   │   └── currency.ts        # Exchange rates
│   ├── scrapers/              # Playwright scrapers
│   │   ├── base-scraper.ts    # Common logic
│   │   ├── flights.ts         # Google Flights
│   │   └── hotels.ts          # Booking.com fallback
│   ├── planners/              # Planning engines
│   │   ├── itinerary.ts       # Day-by-day builder
│   │   ├── budget.ts          # Cost estimation
│   │   └── transport.ts       # Route optimization
│   ├── data/                  # Static data
│   │   ├── countries.json     # Country metadata
│   │   ├── airports.json      # Airport database
│   │   └── attractions/       # Curated POIs by city
│   └── utils/
│       ├── cache.ts           # Simple file cache
│       ├── formatter.ts       # Output formatting
│       └── validator.ts       # Input validation
├── data/
│   └── wikivoyage/            # Downloaded guides
└── tests/
```

### Key Technical Decisions

| Decision | Rationale |
|----------|-----------|
| **TypeScript** | Type safety, better IDE support |
| **SQLite Cache** | Zero-config, file-based persistence |
| **Playwright** | Handles JS-heavy sites, stealth mode |
| **Axios + Retry** | Reliable HTTP with exponential backoff |
| **No External DB** | Keep deployment simple |

---

## API Integration Details

### 1. Nominatim (Geocoding)

```typescript
// Free, no API key, 1 req/sec limit
const geocode = async (query: string) => {
  const url = `https://nominatim.openstreetmap.org/search?q=${encodeURIComponent(query)}&format=json&limit=1`;
  const response = await fetch(url, {
    headers: { 'User-Agent': 'OpenCLAW-TourPlanner/1.0' }
  });
  return response.json();
};
```

**Capabilities:**
- Forward geocoding (city name → coordinates)
- Reverse geocoding (coordinates → address)
- Bounding box for map areas
- Address details (country, state, city)

### 2. Visual Crossing Weather

```typescript
// Free tier: 1000 records/day
const getWeather = async (lat: number, lon: number, days: number) => {
  const url = `https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/${lat},${lon}/next${days}days?unitGroup=metric&key=${API_KEY}&contentType=json`;
  // Returns: daily forecasts with temp, precipitation, conditions
};
```

**Capabilities:**
- 15-day forecast
- Historical weather (for packing advice)
- Hourly breakdowns
- Weather alerts

### 3. Wikivoyage Integration

```typescript
// MediaWiki API - free, no key
const getGuide = async (destination: string) => {
  const url = `https://en.wikivoyage.org/w/api.php?action=query&titles=${destination}&prop=extracts&exintro&explaintext&format=json&origin=*`;
  // Returns: Travel guide content, attractions, tips
};
```

**Capabilities:**
- Destination overviews
- "See" and "Do" sections
- "Eat" and "Drink" recommendations
- "Stay" (accommodation areas)
- "Get around" (transport)
- Cultural tips and warnings

### 4. Amadeus Flight API (Phase 2)

```typescript
// Free tier: Limited calls for testing
const searchFlights = async (origin: string, dest: string, date: string) => {
  // Requires OAuth2 authentication
  // Returns: Flight offers with prices, airlines, times
};
```

**Free Tier Limits:**
- 2,000 API calls/month for Flight Offers Search
- 2,000 API calls/month for Flight Inspiration Search
- No production use without partnership

**Alternative:** Skip real-time flight search, provide general guidance on booking sites.

---

## Web Scraping Strategy (Playwright)

### When to Scrape vs API

| Data Need | Primary Source | Fallback |
|-----------|---------------|----------|
| Flight prices | Amadeus API (limited) | Google Flights scraping |
| Hotel prices | None (no free API) | Booking.com scraping |
| Activity bookings | GetYourGuide API (paid) | Viator scraping |
| Real-time availability | None | Direct site scraping |

### Scraping Architecture

```typescript
// Base scraper with stealth
class TravelScraper {
  protected browser: Browser;
  protected context: BrowserContext;
  
  async init() {
    this.browser = await chromium.launch({ headless: true });
    this.context = await this.browser.newContext({
      userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
      viewport: { width: 1920, height: 1080 }
    });
    // Add stealth plugins
  }
  
  async scrapeWithRetry(url: string, selector: string, maxRetries = 3) {
    // Exponential backoff, screenshot on failure
  }
}
```

### Ethical Scraping Guidelines

1. **Respect robots.txt**
2. **Rate limiting** — Max 1 req/sec per domain
3. **User-Agent identification**
4. **No scraping behind logins**
5. **Cache aggressively** — Minimize repeat requests
6. **Fail gracefully** — Return partial data if scraping fails

---

## Output Formats

### 1. Markdown Itinerary (Default)

```markdown
# 5-Day Tokyo Adventure

## Overview
- **Dates:** April 15-19, 2025
- **Weather:** 18-22°C, partly cloudy, low rain chance
- **Budget Estimate:** $1,200-1,800 (excl. flights)

## Day 1: Arrival & Shibuya
### Morning
- **10:00** Arrive at Narita/Haneda
- **12:00** Airport Express to Shibuya (¥300)
- **Activity:** Shibuya Crossing + Hachiko statue

### Afternoon
- **14:00** Lunch at Genki Sushi (conveyor belt)
- **16:00** Meiji Shrine walk

### Evening
- **19:00** Dinner in Nonbei Yokocho (alley bars)
- **Stay:** Shibuya area hotels (¥8,000-15,000/night)

---

## Cultural Tips
- Bow slightly when greeting
- No tipping required
- Carry cash — many places don't take cards
```

### 2. JSON (For Agent Processing)

```json
{
  "destination": "Tokyo",
  "duration_days": 5,
  "weather_summary": {...},
  "days": [
    {
      "day": 1,
      "theme": "Arrival & Shibuya",
      "activities": [...],
      "meals": {...},
      "transport": [...],
      "estimated_cost": 150
    }
  ],
  "budget_breakdown": {...},
  "packing_list": [...],
  "cultural_notes": [...]
}
```

### 3. PDF Export (Future)

Using Puppeteer or similar to generate printable itineraries.

---

## Skill Commands

### Primary Commands

| Command | Description | Example |
|---------|-------------|---------|
| `plan` | Generate full itinerary | `/tour plan Tokyo 5 days in April` |
| `flights` | Search flight options | `/tour flights NYC to Tokyo April 15` |
| `weather` | Get weather forecast | `/tour weather Tokyo next week` |
| `budget` | Estimate trip costs | `/tour budget Tokyo 5 days mid-range` |
| `activities` | Find things to do | `/tour activities Tokyo family-friendly` |
| `guide` | Get destination guide | `/tour guide Tokyo` |

### Advanced Commands

| Command | Description | Example |
|---------|-------------|---------|
| `compare` | Compare destinations | `/tour compare Tokyo vs Seoul for 5 days` |
| `optimize` | Optimize route | `/tour optimize Tokyo Kyoto Osaka 10 days` |
| `share` | Share itinerary | `/tour share [itinerary-id]` |
| `save` | Save for later | `/tour save "Tokyo Spring 2025"` |

---

## Caching Strategy

### Cache Layers

```
┌─────────────────────────────────────────────────────────────┐
│  L1: Memory Cache (per session)                            │
│     • Active itinerary data                                │
│     • TTL: Session duration                                │
├─────────────────────────────────────────────────────────────┤
│  L2: SQLite Cache (local file)                             │
│     • API responses (weather, geocoding)                   │
│     • Wikivoyage snippets                                  │
│     • TTL: 24 hours for weather, 7 days for static data    │
├─────────────────────────────────────────────────────────────┤
│  L3: Static Data (JSON files)                              │
│     • Country metadata                                     │
│     • Airport database                                     │
│     • Curated attraction lists                             │
│     • Updated monthly                                      │
└─────────────────────────────────────────────────────────────┘
```

### Cache Keys

```typescript
// Geocoding: "geo:tokyo" → {lat, lon, boundingbox}
// Weather: "weather:35.6762:139.6503:2025-04-15" → forecast
// Wikivoyage: "wv:tokyo" → guide content
```

---

## Error Handling & Fallbacks

### Graceful Degradation

| Primary Fails | Fallback | Last Resort |
|---------------|----------|-------------|
| Visual Crossing | OpenWeatherMap | Static climate data |
| Wikivoyage API | Local dump | Generic template |
| Nominatim | Photon API | Manual coordinate lookup |
| Amadeus flights | Scraping | Booking site links |
| Real-time data | Cached data | "Check locally" note |

### User Communication

```
⚠️  Weather data unavailable — using historical averages for April in Tokyo.

⚠️  Real-time flight prices couldn't be retrieved. 
    Recommended booking sites: Google Flights, Skyscanner, Kayak
```

---

## Future Enhancements (Post-MVP)

### Phase 2 (3-6 months)
- [ ] Amadeus flight integration
- [ ] Hotel price scraping
- [ ] Multi-city route optimization
- [ ] PDF export
- [ ] Shareable links

### Phase 3 (6-12 months)
- [ ] Real-time event integration (Eventbrite, Meetup)
- [ ] Restaurant reservation (OpenTable API)
- [ ] Local transport passes (city-specific)
- [ ] Collaborative planning (group trips)
- [ ] Mobile app wrapper

### Phase 4 (Future)
- [ ] AI-generated custom maps
- [ ] Voice itinerary playback
- [ ] Integration with travel insurance APIs
- [ ] Carbon footprint calculation
- [ ] Affiliate partnerships ( Booking.com, GetYourGuide)

---

## Website Structure (openclaw.tours)

### Landing Page
```
┌─────────────────────────────────────────────────────────────┐
│  OpenCLAW Tour Planner                                     │
│  Give your agent the power to plan any trip                │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  [Try Demo]  [Install Skill]  [View on GitHub]             │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  Demo Chat:                                         │   │
│  │  User: Plan a 3-day trip to Lisbon                  │   │
│  │  Agent: Here's your itinerary...                    │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│  Features:                                                  │
│  • 100% Free • Open Source • Privacy-First • Agent-Native  │
└─────────────────────────────────────────────────────────────┘
```

### Documentation Pages
- `/docs` — Full skill documentation
- `/docs/api` — API references
- `/docs/examples` — Sample itineraries
- `/docs/contributing` — How to add destinations

---

## Success Metrics

| Metric | Target |
|--------|--------|
| Itinerary generation time | < 10 seconds |
| API uptime (critical path) | > 95% |
| Cache hit rate | > 70% |
| User satisfaction | > 4.5/5 |
| Destinations covered | 100+ cities |

---

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| API rate limits exceeded | Medium | High | Aggressive caching, fallback chains |
| Scraping blocked | Medium | Medium | Respect robots.txt, rotate UA, cache |
| Amadeus API changes | Low | High | Abstract API layer, easy to swap |
| Data accuracy | Medium | Medium | Wikivoyage + multiple sources |
| Legal (scraping) | Low | High | Only public data, no ToS violations |

---

## Next Steps

1. **Week 1:** Set up project structure, Nominatim + Weather integration
2. **Week 2:** Wikivoyage integration, basic itinerary generation
3. **Week 3:** Markdown output, caching layer
4. **Week 4:** Website, documentation, GitHub release
5. **Month 2:** Playwright scrapers, flight search
6. **Month 3:** Polish, community feedback, iterate

---

*Document Version: 1.0*  
*Last Updated: 2026-02-26*  
*Author: KimiA for Asif*
