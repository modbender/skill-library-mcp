---
name: ns-trains
description: Check Dutch train schedules, departures, disruptions, and plan journeys using the NS API. Perfect for daily commute checks.
metadata: {"openclaw":{"emoji":"🚆","requires":{"bins":["node"],"env":["NS_SUBSCRIPTION_KEY"]},"primaryEnv":"NS_SUBSCRIPTION_KEY"}}
---

# NS Trains Skill

Check Dutch train schedules, departures, disruptions, and plan journeys using the official NS (Nederlandse Spoorwegen) API.

## Setup

### 1. Get an NS subscription key

1. Go to [NS API Portal](https://apiportal.ns.nl/)
2. Create an account and subscribe to the **Ns-App** product (free tier available)
3. Copy your **Primary Key**

### 2. Set Environment Variables

```bash
export NS_SUBSCRIPTION_KEY="your-subscription-key-here"   # preferred
# Back-compat:
export NS_API_KEY="$NS_SUBSCRIPTION_KEY"                   # legacy name still supported

# Optional: Configure commute stations for quick shortcuts
export NS_HOME_STATION="Utrecht Centraal"
export NS_WORK_STATION="Amsterdam Zuid"
```

For security, prefer injecting these env vars via your runtime secret mechanism rather than committing them anywhere. Avoid printing or sharing your subscription key.

## Quick Usage

### 🚆 Commute shortcuts
```bash
node {baseDir}/scripts/commute.mjs --to-work   # Morning: Home → Work
node {baseDir}/scripts/commute.mjs --to-home   # Evening: Work → Home
```

### Plan any journey
```bash
node {baseDir}/scripts/journey.mjs --from "Utrecht Centraal" --to "Amsterdam Zuid"
```

### Check departures from a station
```bash
node {baseDir}/scripts/departures.mjs --station "Amsterdam Centraal"
```

### Check arrivals at a station
```bash
node {baseDir}/scripts/arrivals.mjs --station "Rotterdam Centraal"
```

### Search for stations
```bash
node {baseDir}/scripts/stations.mjs amsterdam
node {baseDir}/scripts/stations.mjs --search "den haag"
```

### Check current disruptions
```bash
node {baseDir}/scripts/disruptions.mjs
node {baseDir}/scripts/disruptions.mjs --from "Utrecht" --to "Amsterdam"
```

## Natural Language

Just ask:
- "When is the next train to Amsterdam?"
- "Check trains from Utrecht to Rotterdam"
- "Any train disruptions today?"
- "Plan my commute to work"
- "What time does the train arrive?"

## Output

Returns journey options with:
- Departure/arrival times
- Real-time delays
- Duration
- Transfers
- Platform numbers
- Disruption warnings
- Crowdedness forecast (🟢 low / 🟡 medium / 🔴 high)

## Commands Reference

| Command | Description |
|---------|-------------|
| `commute.mjs [work\|home]` | Quick commute check (requires NS_HOME_STATION & NS_WORK_STATION) |
| `journey.mjs --from X --to Y` | Plan a journey between any stations |
| `departures.mjs --station X` | List departures from a station |
| `arrivals.mjs --station X` | List arrivals at a station |
| `stations.mjs [query]` | Search for station names |
| `disruptions.mjs` | Check current disruptions |

## API Endpoints Used

- `/reisinformatie-api/api/v3/trips` - Journey planning
- `/reisinformatie-api/api/v2/arrivals` - Arrivals
- `/reisinformatie-api/api/v2/departures` - Departures  
- `/reisinformatie-api/api/v3/disruptions` - Disruptions
- `/reisinformatie-api/api/v2/stations` - Station search

## Reference

- NS API Portal: https://apiportal.ns.nl/
- Documentation: https://apiportal.ns.nl/startersguide
- Free tier: 5000 requests/day
