---
name: weather-nws
description: "US weather forecasts via National Weather Service (NWS) with automatic fallback to global weather for non-US locations. Provides detailed accumulation data, watches/warnings, and actionable timing. Use for: US-based weather queries, winter storm forecasts, precipitation accumulation estimates, severe weather alerts. Automatically falls back to global weather via wttr.in for international locations."
homepage: https://api.weather.gov/
metadata: {"clawdhub":{"emoji":"🌦️"},"clawdis":{"envVars":[{"name":"AIRNOW_API_KEY","required":false,"description":"AirNow API Key for AQI lookup"}]}}
---

# Weather NWS Skill

Get detailed US weather forecasts from the National Weather Service with automatic global fallback, hourly forecasts, air quality data, and structured winter storm accumulations.

## What This Skill Does

This skill operates in **8 modes** to match your query:

| Mode | When It Activates | What You Get |
|------|-------------------|--------------|
| 🌦️ **Standard Forecast** | Default (no time specified) | 12-hour forecast with today/tonight/tomorrow |
| ⏰ **Hourly Forecast** | Time-specific query detected | Hour-by-hour breakdown (~156 periods, 7 days) |
| 🌨️ **Winter Storm** | Keywords like "snow," "storm" | 12-hour + structured accumulation data |
| 💨 **AQI Report** | `--aqi` flag included | Current + forecast air quality index |
| 🌡️ **Observed vs Forecast** | `--current` flag included | Current station readings with comparison |
| ☀️ **Astronomical Times** | `--astro` flag included | Sunrise/sunset, twilight, moon phase |
| ✈️ **Aviation Forecast** | `--taf` flag included | Terminal Aerodrome Forecast (TAF) |
| 🔥 **Fire Weather** | `--fire` flag included | Fire danger, red flag warnings |
| 🌍 **Global Fallback** | Non-US location | wttr.in data (less detailed) |

## AirNow API Key (Optional but Recommended)

The AirNow API **works without a key** but has limitations:

| Without API Key | With API Key |
|-----------------|--------------|
| Rate limited (requests may fail) | Higher rate limits |
| No guaranteed availability | Priority access |
| May return empty results | Reliable AQI data |

### Getting an API Key

1. Visit: https://docs.airnowapi.org/account/request/
2. Fill out the request form (free for personal use)
3. Key arrives via email within 1-2 business days

### Setting the API Key

**Option 1: Environment Variable (Recommended)**
```bash
export AIRNOW_API_KEY="your-api-key-here"
```

**Option 2: OpenClaw Config (Persistent)**
Add to your OpenClaw config under `skills.entries.weather-nws.env`:
```json
{
  "skills": {
    "entries": {
      "weather-nws": {
        "env": {
          "AIRNOW_API_KEY": "your-api-key-here"
        }
      }
    }
  }
}
```

## When to Use

✅ **USE this skill when:**

- "What's the weather in [US city]?"
- "How much snow is expected?"
- "Winter storm forecast for [location]"
- "Will it rain tomorrow in [US city]?"
- "What time will the rain stop?"
- "Air quality in [city] today"
- Any US-based weather query

🔄 **Automatic fallback:**

- Non-US locations → wttr.in
- NWS API unavailable → wttr.in
- Both sources fail → clear error message

## Quick Start

```bash
# Run the unified weather script
python3 ./scripts/get_weather.py "New York, NY"

# Force specific source if needed (normally auto-detected)
python3 ./scripts/get_weather.py "London, UK" --source wttr

# Get hourly forecast (auto-detected or forced)
python3 ./scripts/get_weather.py "Boston at 8 PM"
python3 ./scripts/get_weather.py "Chicago" --hourly

# Include air quality
python3 ./scripts/get_weather.py "Seattle" --aqi
```

## Hourly Auto-Detection

The skill automatically detects time-specific language and switches to hourly forecast:

```
"Boston at 8 PM"        → ⏰ Hourly mode
"Boston tonight"         → ⏰ Hourly mode
"Boston tomorrow morning" → ⏰ Hourly mode
"Boston at 5:30"         → ⏰ Hourly mode
"When will it stop raining?" → ⏰ Hourly mode
```

**Patterns detected:**
- `at 8 PM`, `at 5:30`, etc.
- `tonight`, `this afternoon`
- `tomorrow morning/afternoon/night`
- `when will...`, `how long until...`

## Air Quality (`--aqi`)

Adds AirNow AQI data to any forecast:

```bash
python3 ./scripts/get_weather.py "Boston" --aqi
```

**Output includes:**
- Current AQI with color-coded emoji (🟢 🟡 🟠 🔴 🟣 🔵)
- Primary pollutant (PM2.5, O3, etc.)
- Health recommendation based on category
- 3-day AQI forecast

**AQI Categories:**
| Range | Category | Emoji | Recommendation |
|-------|----------|-------|------------------|
| 0-50 | Good | 🟢 | Enjoy outdoor activities |
| 51-100 | Moderate | 🟡 | Sensitive groups limit exertion |
| 101-150 | Unhealthy for Sensitive Groups | 🟠 | Children/elderly limit outdoor activities |
| 151-200 | Unhealthy | 🔴 | Everyone reduce outdoor exertion |
| 201-300 | Very Unhealthy | 🟣 | Avoid outdoor activities |
| 301-500 | Hazardous | 🔵 | Stay indoors — health alert |

## Output Format

The script provides consistent output regardless of source:

**Header:** Location and current alert status
**Today → Tonight → Tomorrow:** Structured timeline
**Accumulation:** Specific snow/rain amounts when available
**Bottom Line:** Actionable summary with timing

## Implementation

The script handles:
1. Geocoding location to lat/long
2. Detecting if location is in US
3. Calling NWS API for US locations (detailed accumulation)
4. Falling back to wttr.in for non-US (basic forecast)
5. Formatting consistent output with emojis and structure

## Limitations

- **NWS:** US only, requires internet, rate limited
- **wttr.in:** Global, less detail on accumulation, no official watches/warnings
- **AirNow:** US + Canada only, requires API key for reliable access

## Examples

**US winter storm query:**
```bash
python3 ./scripts/get_weather.py "Boston, MA"
```
→ Returns NWS data with accumulation estimates

**International location:**
```bash
python3 ./scripts/get_weather.py "Toronto, Canada"
```
→ Automatically uses wttr.in, notes it's non-US

**With air quality:**
```bash
python3 ./scripts/get_weather.py "Seattle" --aqi
```
→ Weather + AQI data with health recommendations

**Observed vs Forecast:**
```bash
python3 ./scripts/get_weather.py "Boston" --current
```
→ Current station readings with forecast comparison

**Combined features:**
```bash
python3 ./scripts/get_weather.py "Seattle" --aqi --current
```
→ Full weather report with all data sources

**Phase 3 features:**
```bash
python3 ./scripts/get_weather.py "Boston" --astro       # Sunrise/sunset times
python3 ./scripts/get_weather.py "SFO" --taf           # Aviation forecast
python3 ./scripts/get_weather.py "California" --fire    # Fire weather
python3 ./scripts/get_weather.py "Denver" --astro --aqi --current  # Everything!
```

## Observed vs Forecast (`--current`)

Shows actual measured conditions from the nearest NWS observation station alongside the forecast:

```
🌡️ **Observed Conditions**
   **Actually 43°F (3° warmer than 40° forecast)**
   ☁️ Partly Cloudy
   💨 WNW 8 mph • 💧 36% humidity • 🌫️ Dewpoint 18°F • 📊 Pressure 29.86 inHg • 👀 Visibility 10+ mi
```

**Fields shown:**
- Temperature with forecast delta
- Conditions description
- Wind speed and direction
- Humidity percentage
- Dewpoint
- Barometric pressure (inHg)
- Visibility

## Alert Priorities

When alerts are active, they're displayed with enhanced formatting using severity/urgency/certainty weighting:

| Factor | Weights |
|--------|---------|
| **Severity** | Extreme (4) > Severe (3) > Moderate (2) > Minor (1) |
| **Urgency** | Immediate (3) > Expected (2) > Future (1) |
| **Certainty** | Observed (3) > Likely (2) > Possible (1) |

**Severity Styling:**
| Severity | Emoji | Badge |
|----------|-------|-------|
| Extreme | ⚫ | EXTREME |
| Severe | 🔴 | SEVERE |
| Moderate | 🟠 | MODERATE |
| Minor | 🟡 | MINOR |

**Alert display includes:**
- Event name with severity badge
- Urgency tag: ⏰ Immediate / 📅 Expected / 🔮 Future
- Time range (onset → expires)
- First sentence of description
- Recommended response action

**Example:**
```
🟠 [**MODERATE**] **Winter Storm Warning**
   📅 Expected | *Winter Storm Warning from 6 PM to 10 AM EST*
   🕐 6:00 PM → 10:00 AM
   📝 Heavy snow expected with accumulations of 6-10 inches...
   👉 🎒 Prepare now
```

## References

- [references/nws-api.md](references/nws-api.md) — NWS API endpoint details
- [references/airnow-api.md](references/airnow-api.md) — AirNow API documentation

## Phase 3 Features

### Astronomical Times (`--astro`)

Shows sunrise, sunset, civil twilight, and moon phase information:

```bash
python3 ./scripts/get_weather.py "Boston" --astro
```

**Output includes:**
- 🌅 **Sunrise:** Time with countdown/ago
- 🌇 **Sunset:** Time with countdown/ago  
- 💡 **Civil Twilight:** Dawn and dusk times (useful for runners, cyclists)
- ⏱️ **Daylight:** Total hours of daylight
- 🌙 **Moon:** Current phase with illumination percentage

**Example:**
```
☀️ **Astronomical Times — Boston**

🌅 **Sunrise:** 6:22 AM (12h ago)
🌇 **Sunset:** 5:31 PM (in 2h)
💡 **Civil Twilight:** 5:55 AM – 5:58 PM
⏱️ **Daylight:** 11h 9m
🌙 **Moon:** 🌓 First Quarter (50.0%)
```

### Aviation Forecast (`--taf`)

Shows Terminal Aerodrome Forecast (TAF) for the nearest aviation weather station:

```bash
python3 ./scripts/get_weather.py "SFO" --taf
```

**Note:** TAFs are designed for aviation use. The report provides:
- Station identifier
- Wind conditions and direction
- Visibility
- Cloud ceiling information

**Important:** *This is informational only. Always check official sources for flight planning.*

### Fire Weather (`--fire`)

Shows fire danger information for wildfire-prone areas:

```bash
python3 ./scripts/get_weather.py "California" --fire
```

**Output includes:**
- Fire danger level (if elevated)
- 🔥 **Red Flag Warnings** (if active)
- Fire weather zone forecast
- Source attribution

**Red Flag Warnings** indicate critical fire weather conditions (low humidity + high winds).

## Changelog

### v1.3.0 (2026-02-26) - Phase 3
- Added `--astro` flag for sunrise/sunset, twilight, and moon phase
- Added `--taf` flag for Aviation Terminal Aerodrome Forecasts
- Added `--fire` flag for fire weather danger and red flag warnings
- Added moon phase calculation (waxing/waning, illumination %)
- Added daylight hours calculation
- Added civil twilight detection for runners/cyclists

### v1.2.0 (2026-02-26) - Phase 2
- Added `--current` flag for station observations vs forecast comparison
- Enhanced alert formatting with severity/urgency/certainty priority scoring
- Added temperature delta comparison (warmer/cooler than forecast)
- Added full observation details: humidity, dewpoint, pressure, visibility

### v1.1.0 (2026-02-26)
- Added hourly forecast with temporal query auto-detection
- Added AirNow AQI integration (`--aqi` flag)
- Added structured grid data for winter storm accumulations
- Fixed AirNow API endpoint URLs

### v1.0.0 (2026-02-22)
- Initial release: NWS API with wttr.in fallback
- 12-hour forecast periods
- Alert integration
- Accumulation estimates from text parsing
