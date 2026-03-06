---
name: farmos-weather
description: Query weather data and forecasts for farm fields via the Agronomy module.
tags: [farming, weather, forecast]
---

# FarmOS Weather

Current conditions and forecasts for farm fields, sourced from the Agronomy module.

## When to Use This

**What this skill handles:** Current weather conditions, forecasts, growing degree days (GDD), spray condition evaluation, and historical weather data for farm fields.

**Trigger phrases:** "what's the weather", "can we spray", "GDD for field X", "forecast", "will it rain this week?", "temperature and wind right now", "field conditions?"

**What this does NOT handle:** Field observations about weather damage like hail, flooding, or frost injury (use farmos-observations with weather_damage type -- that logs the damage for tracking). This skill tells you what the weather IS; observations logs what the weather DID.

**Minimum viable input:** "Weather" or a field reference. If no field is specified, any nearby field ID works since all 69 fields are in central Indiana.

## API Base

http://100.102.77.110:8012

## Endpoints

### Health Check
GET /api/weather/health

Returns: Weather service health status.

### Current Weather
GET /api/weather/field/{field_id}/current

Returns: Current conditions for a specific field (temperature, precipitation, wind).

### Forecast
GET /api/weather/field/{field_id}/forecast?days=7

Returns: Daily and hourly forecast data (up to 14 days).

### Historical
GET /api/weather/field/{field_id}/historical?days=30

Returns: Historical weather records for a field.

### Growing Degree Days
GET /api/weather/field/{field_id}/gdd?startDate=YYYY-MM-DD&endDate=YYYY-MM-DD&baseTemp=10

Returns: GDD accumulation for a field over a date range.

### Spray Conditions
GET /api/weather/field/{field_id}/spray-conditions

Returns: Spray condition evaluation (wind, rain probability, temperature checks).

### Weather by Coordinates
GET /api/weather/coordinates?latitude={lat}&longitude={lon}&type=current

Returns: Weather by coordinates (no field ID required). Use type=forecast for forecast data.

### Integration Dashboard
GET /api/integration/dashboard

Returns: Agronomy summary including weather data if available.

## Data Completeness

1. **The `/api/integration/dashboard` returns agronomy summary data** — use it for a quick overview only, not as the primary weather source.
2. **If a weather endpoint fails or returns empty**, say so: "The weather service isn't responding right now." Don't guess the weather.
3. **For GDD queries**, always include the date range in your response so the user knows the scope: "GDD from April 1 to today: 1,142."

## Cross-Module Context

When answering weather questions, think about what else on the farm is affected:

**Weather → Tasks:**
- Before answering "can we spray?" or "should we get in the field?", check farmos-tasks for what's on the board. Connect the forecast to specific scheduled work: "Rain Thursday through Saturday — if you're planning to spray field 14, today's your window."
- When reporting the forecast, flag weather-sensitive tasks that conflict: "You've got 3 spray tasks this week but wind picks up Wednesday. Today and tomorrow are your best shot."
- GDD milestones trigger agronomic actions. When GDD data crosses key thresholds (V6 ~450 GDD, VT ~1,100 GDD, R1 ~1,400 GDD for corn), connect to tasks: "Field 12 just hit 1,100 GDD — that's your V6 marker. Side-dress window is now. Want me to create a task?"

**Weather → Observations:**
- After extended rain + warm temps, flag disease pressure: "We've had 3 days of rain and highs in the 80s — conditions are ripe for gray leaf spot and tar spot. Worth scouting the corn this week."
- After frost or severe weather, suggest damage checks: "First frost was last night. Might be worth checking the late-planted fields for damage."
- Connect recent weather to existing observation patterns: if there are recent disease observations, note the weather connection.

**Weather → Equipment:**
- If rain is coming and there are field operations scheduled, note the equipment implication: "Rain starts Thursday — anything that needs to be in the field should get there before then."

Query farmos-tasks and farmos-observations alongside weather for any field operation question. You don't need to cross-reference on every simple "what's the temperature?" question — use judgment. Cross-reference when the weather materially affects the plan.

## Units — Already Imperial, Display Directly

The weather API returns all values in US imperial units. **Display them as-is — no conversion needed.**

| API field | Unit | Example display |
|-----------|------|-----------------|
| `temperature_max` / `temperature_min` | °F | "high of 55°F" |
| `precipitation_sum` | inches | "about a quarter inch of rain" |
| `wind_speed_10m_max` / `wind_gusts_10m_max` | mph | "winds up to 21 mph" |

**Do not convert, do not relabel.** `0.25` means 0.25 inches. `55` means 55°F. `16` means 16 mph.

## Date Handling — Anchor to Today

The API returns dates as `YYYY-MM-DD` strings starting from today. The first entry is **today**, not tomorrow.

- Use your system date to label each day correctly: "Today (Feb 28)", "Tomorrow (Mar 1)", "Wednesday (Mar 2)"
- Do not assume the first forecast entry is tomorrow — it is today
- If you're unsure of today's date, say so rather than guess

## Usage Notes

- Farm is located in central Indiana. If specific field weather isn't available, general local weather is fine.
- Spray conditions matter: wind speed under 10mph, no rain in forecast for 24hrs, temperature ranges.
- "Can we spray?" is a common question -- check wind, rain probability, and temperature via the spray-conditions endpoint.
- Field IDs are integers -- 69 fields across the operation. Most weather queries can use any nearby field ID since they are all in the same area.
- For coordinates-based queries without a field ID, use the /coordinates endpoint with the farm's approximate location (latitude ~40.25, longitude ~-85.67).
