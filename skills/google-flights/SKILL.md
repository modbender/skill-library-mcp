---
name: google-flights
description: Search Google Flights for prices and availability. Use when user asks about flight prices, searching for flights, comparing airfares, or planning air travel between cities.
---

# Flights

Two modes: **quick** (prices only, fast) and **full** (airlines/times/stops, browser).

## Quick Mode (Default)

Use `scripts/search.py` for fast price lookups:

```bash
./scripts/search.py YYC LAX "2026-03-15"
./scripts/search.py YYC LAX tomorrow --return "next friday"
./scripts/search.py JFK LHR "Mar 1" --adults 2 --seat business
```

**Output:** Price trend (low/typical/high), price range, flight count, Google Flights link.

**Options:**
- `--return`, `-r` — Return date for round-trip
- `--adults`, `-a` — Number of adults (default: 1)
- `--children`, `-c` — Number of children  
- `--seat`, `-s` — economy, premium-economy, business, first
- `--json` — JSON output

## Full Mode (Browser)

When user needs airlines, times, or specific flight options — use browser automation:

```
1. browser open (profile: clawd, targetUrl: google flights URL)
2. browser snapshot (wait for "results returned" alert)
3. Parse link descriptions for flight data
4. browser close
```

### URL Format

```
# One-way
https://www.google.com/travel/flights?q=Flights%20from%20{FROM}%20to%20{TO}%20on%20{DATE}%20one%20way&hl=en

# Round-trip
https://www.google.com/travel/flights?q=Flights%20from%20{FROM}%20to%20{TO}%20on%20{DATE}%20returning%20{RETURN}&hl=en
```

### Parsing Snapshot

Flight data in link elements:
```
"From 737 Canadian dollars... flight with Air Canada. Leaves... at 6:25 AM... arrives at 11:48 AM... Total duration 6 hr 23 min. 1 stop... Layover 1 hr 30 min at YVR..."
```

### Full Mode Output

```
✈️ YYC → LAX | Fri Feb 20

1. Air Canada | 6:25 AM → 11:48 AM | 6h 23m | 1 stop (YVR) | CA$737
2. United | 6:15 AM → 11:31 AM | 6h 16m | 1 stop (DEN) | CA$744
3. WestJet | 9:00 AM → 11:27 AM | 3h 27m | Nonstop | CA$1,047 ⭐

🔗 Book on Google Flights: [link]
```

## Setup (Quick Mode)

Quick mode requires `fast-flights`. Install once:

```bash
cd skills/google-flights
uv venv && source .venv/bin/activate && uv pip install fast-flights
```

## When to Use Which

| User Request | Mode |
|--------------|------|
| "How much to fly to NYC?" | Quick |
| "Are flights to LA cheap right now?" | Quick |
| "Find me flights on March 5th" | Full |
| "What airlines fly YYC to LAX?" | Full |
| "Best nonstop options to Denver" | Full |
| "Compare morning vs evening flights" | Full |
