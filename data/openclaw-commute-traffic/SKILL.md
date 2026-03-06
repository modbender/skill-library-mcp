---
name: commute-traffic
description: Check real-time traffic conditions for a route between two locations using TomTom. Use when the user asks about traffic, commute time, best time to leave, driving conditions, or road congestion. The user provides origin and destination conversationally — extract them from context.
version: 2.0.0
user-invocable: true
metadata:
  {"openclaw": {"emoji": "🚗", "requires": {"bins": ["python3"], "env": ["TOMTOM_API_KEY"]}, "primaryEnv": "TOMTOM_API_KEY"}}
---

# Commute Traffic Checker (TomTom)

## Purpose

Query real-time traffic data from TomTom for any route and provide the user with actionable travel advice. The script handles geocoding (resolving place names to coordinates) and routing (calculating travel time with live traffic) — all via the same TomTom API key.

## Determining Origin and Destination

The origin and destination are **not static** — you must determine them from what the user tells you. Examples:

- "How's traffic from the office to home?" → You must know (or ask) where their office and home are.
- "Check traffic Basel to Zurich" → origin=Basel, destination=Zurich.
- "Should I leave now?" → Use previously discussed or known origin/destination. If unknown, ask.
- "What's the commute like?" → If you know the user's regular commute, use that. Otherwise, ask.

**Rules:**
1. If both origin and destination are clear from context, proceed immediately.
2. If only one is clear, ask for the missing one.
3. If neither is clear and you have no prior context, ask the user for both.
4. Accept any format: addresses, city names, landmarks, coordinates — the script geocodes automatically.

## Running the Traffic Check

Execute the script with origin and destination as arguments:

```bash
python3 {baseDir}/scripts/check_traffic.py --origin "<ORIGIN>" --destination "<DESTINATION>"
```

**Examples:**

```bash
python3 {baseDir}/scripts/check_traffic.py --origin "Basel, Switzerland" --destination "Zurich, Switzerland"
python3 {baseDir}/scripts/check_traffic.py --origin "Basel SBB" --destination "Paradeplatz, Zürich"
python3 {baseDir}/scripts/check_traffic.py --origin "Aeschenplatz, Basel" --destination "ETH Zürich"
```

## Interpreting the Output

The script returns JSON with one or more route alternatives. For each route:

| Field | Meaning |
|-------|---------|
| `travel_time_min` | Total travel time **with current live traffic** |
| `no_traffic_time_min` | Travel time with zero traffic (free-flow) |
| `historic_traffic_time_min` | Typical travel time based on historical patterns |
| `live_traffic_time_min` | Time including live incident data |
| `traffic_delay_min` | Extra delay caused by current traffic |
| `traffic_delay_pct` | Delay as percentage of free-flow time |
| `congestion` | Derived level: `light`, `moderate`, or `heavy` |
| `distance_km` | Route distance in kilometers |
| `departure_time` / `arrival_time` | Departure and estimated arrival timestamps |

### Congestion classification:
- **Light**: traffic delay adds less than 20% to free-flow time
- **Moderate**: 20–50% above free-flow
- **Heavy**: more than 50% above free-flow

## Presenting Results to the User

When presenting traffic data, always include:

1. **The fastest route** and its estimated travel time.
2. **Traffic delay** in plain language (e.g., "Currently 8 minutes delay due to traffic on the A2, adding about 15% to the normal drive time").
3. **Comparison of alternatives** if multiple routes are returned.
4. **A recommendation**: whether to leave now or wait, based on congestion level.

Keep it concise and practical. The user wants to know: *"How long will it take and should I go now?"*

## Error Handling

- If the script returns `{"status": "error"}`, relay the error message to the user.
- If `TOMTOM_API_KEY` is not configured, tell the user to set it up in `~/.openclaw/openclaw.json`.
- If geocoding fails (no coordinates found), the location may be too vague — ask the user to be more specific.
- If no routes are returned, suggest trying different location descriptions.
