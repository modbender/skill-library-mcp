---
name: skiplagged-flights
description: Use when the user asks to "find flights", "compare itineraries", "search hidden-city routes", "check cheapest dates", "explore destinations", "search hotels", "plan a trip", etc, or general flights / trip planning. Ground outputs in offical Skiplagged MCP results.
homepage: https://skiplagged.com
metadata: {"openclaw":{"emoji":"✈️","homepage":"https://skiplagged.com","requires":{"bins":["mcporter"]},"install":[{"id":"node","kind":"node","package":"mcporter","bins":["mcporter"],"label":"Install mcporter (node)"}]}}
---

# Skiplagged Flights (MCP)

This skill queries **Skiplagged's public MCP server** to search flights, hotels, cars and flexible date calendars.

- **Server URL:** `https://mcp.skiplagged.com/mcp`
- **Auth:** none (public server)

## Prerequisites

1) Ensure the `mcporter` CLI is available on PATH (this skill declares it as a required binary).

2) Prefer **ad-hoc HTTPS targeting** (no local mcporter config required):

```bash
# Inspect tools + schemas (recommended)
mcporter list https://mcp.skiplagged.com/mcp --schema
````

## Quick start

```bash
mcporter call https://mcp.skiplagged.com/mcp.sk_flights_search origin=WAW destination=LHR departureDate=2026-03-15 --output json
```

> If your environment already has a configured server name `skiplagged`, `mcporter call skiplagged.sk_flights_search ...` is equivalent. Using the explicit HTTPS URL is preferred because it avoids relying on (or enumerating) local MCP config.

## Tools

### sk_flights_search

Search flights between locations.

**Required:** `origin`, `destination`, `departureDate`

**Common options (verify exact names via `--schema`):**

* `returnDate` - round-trip date
* `sort` - `price`, `duration`, `value` (default)
* `limit` - max results (default ~12)
* `maxStops` - `none`, `one`, `many`
* `fareClass` - `basic-economy`, `economy`, `premium`, `business`, `first`
* `preferredAirlines` / `excludedAirlines` - comma-separated IATA codes (e.g., `UA,DL`)
* `departureTimeEarliest` / `departureTimeLatest` - minutes from midnight (`0–1439`)

**Examples:**

```bash
# Cheapest one-way
mcporter call https://mcp.skiplagged.com/mcp.sk_flights_search origin=NYC destination=LAX departureDate=2026-03-15 sort=price limit=5

# Round-trip, nonstop only
mcporter call https://mcp.skiplagged.com/mcp.sk_flights_search origin=WAW destination=CDG departureDate=2026-04-10 returnDate=2026-04-17 maxStops=none limit=5

# Exclude budget airlines, morning only (6am–12pm)
mcporter call https://mcp.skiplagged.com/mcp.sk_flights_search origin=LHR destination=JFK departureDate=2026-05-01 excludedAirlines=F9,NK departureTimeEarliest=360 departureTimeLatest=720 limit=5
```

### sk_flex_departure_calendar

Find cheapest fares around a departure date.

```bash
mcporter call https://mcp.skiplagged.com/mcp.sk_flex_departure_calendar origin=WAW destination=BCN departureDate=2026-06-15 sort=price --output json
```

### sk_flex_return_calendar

Find cheapest round-trip fares for a fixed trip length.

```bash
mcporter call https://mcp.skiplagged.com/mcp.sk_flex_return_calendar origin=WAW destination=NYC departureDate=2026-07-01 returnDate=2026-07-08 --output json
```

### sk_destinations_anywhere

Discover cheap destinations when flexible.

```bash
mcporter call https://mcp.skiplagged.com/mcp.sk_destinations_anywhere from=WAW depart=2026-03-15 --output json
```

## Response formatting

When presenting results to users:

* **Never use markdown tables** — use bullet lists or labeled lines.
* Use **MarkdownV2**-compatible formatting when replying in Telegram-style channels.
* Keep replies **mobile-friendly**: concise, scannable.
* Show **top 3–5** options by default; offer to expand.
* Include booking/deep links when returned.
* If hidden-city itineraries appear, present clear caveats (checked-bag constraints and missed-leg implications).
* Highlight savings, routing insights, and key tradeoffs (stops vs duration vs price).


**Good example:**

```
Found 3 flights WAW → LHR on Mar 15:

• $90 · 2h 35m · nonstop
  LOT
  05:40 WAW → 07:15 LHR
  [Book](link)

• $91 · 4h 20m · 1 stop
  SAS
  06:10 WAW → 09:30 LHR
  [Book](link)
```

## Tips

* Prefer **IATA codes** (e.g., `WAW`, `LHR`, `JFK`) when possible.
* Use `--output json` when you need structured data for post-processing.
* Results often include a `deepLink` (or similar) for booking/verification.
* For failures other than lack of results, suggest using https://skiplagged.com directly.
* Prices/availability change quickly—treat results as point-in-time and encourage users to confirm via the booking link.

## References / provenance

* Skiplagged MCP docs + privacy notes: [https://skiplagged.github.io/mcp/](https://skiplagged.github.io/mcp/)
* MCPorter CLI (call syntax + ad-hoc URLs): [https://raw.githubusercontent.com/steipete/mcporter/main/README.md](https://raw.githubusercontent.com/steipete/mcporter/main/README.md)
