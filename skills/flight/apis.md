# APIs & Integrations

## Flight Search APIs

### Can Search + Book
- **Amadeus** — 400+ airlines, full booking, ancillaries. Free test tier, usage-based pricing.
- **Duffel** — Modern REST API, NDC support, 300+ airlines. $99/mo + per-booking.
- **Kiwi Tequila** — Virtual interlining, multi-modal. Free to start, revenue share.

### Search Only (Affiliate/Redirect)
- **Skyscanner** — Metasearch, partner access required. Redirects to OTAs.
- **Google Flights** — No public API. Must scrape (legal risk).
- **Travelpayouts** — Affiliate data, cached prices. Good for trends.

## Flight Status APIs
- **FlightAware AeroAPI** — Real-time tracking, delays. Free 500/mo, $100/mo for 10K.
- **FlightRadar24** — Best positioning data. $9-900/mo tiers.
- **AviationStack** — Schedules, status. Free 100/mo, $49/mo for 10K.
- **AeroDataBox** — Budget option via RapidAPI. $5/mo for 3K calls.

## Price Tracking
- No public "prediction" API exists (Hopper is proprietary)
- Build custom: scrape periodically, store in database, analyze trends
- Amadeus Flight Price Analysis: historical data available

## Miles/Points APIs
- **AwardWallet** — Track 700+ programs. Requires user credentials. Enterprise pricing.
- **Seats.aero** — Award availability (legally gray, scraping-based)
- Direct airline APIs: limited, inconsistent, mostly internal-only

## What Doesn't Exist (Gaps)
- Unified award flight search API
- Public Google Flights API
- Hopper-style prediction API
- Cross-airline miles booking API
