---
name: weather-pet-forecast
description: Pet-friendly 3-day weather forecast with caring recommendations for humans and their beloved pets. Use when user asks for weather analysis, pet-friendly weather, dog walking conditions, outdoor pet activities, or weather-based pet care advice. Includes temperature trends, precipitation analysis, UV safety, ground conditions, optimal walking times, and comprehensive care guidance for both humans and pets. Works with any global location. Perfect for pet owners who want to plan outdoor activities with their furry friends.
---

# Weather Pet Forecast 🐕

Get a comprehensive 3-day weather forecast with warm, caring recommendations for both humans and their beloved pets. Perfect for pet owners who want to plan outdoor activities with their furry friends!

## When to Use

✅ **USE this skill when:**

- "Check the weather for the next few days"
- "What's the weather forecast for today, tomorrow, and the day after?"
- "Give me a weather analysis"
- "Should I plan outdoor activities this week?"
- "Will I need an umbrella in the next few days?"
- "Is it safe to walk my dog today?"
- "Pet-friendly weather forecast"

## Workflow

### Step 1: Determine Location

Ask for location if not provided. Accept:
- City names: "Beijing", "London", "New York"
- City + Country: "Paris, France"
- Airport codes: "PEK", "LAX", "JFK"

### Step 2: Fetch 3-Day Weather Data

Use wttr.in to get forecast data:

```bash
# JSON format for parsing (recommended)
curl -s "wttr.in/{LOCATION}?format=j1"

# Human-readable 3-day forecast
curl -s "wttr.in/{LOCATION}"
```

Extract key data for each day:
- **Today** (day 0): Current + today's forecast
- **Tomorrow** (day 1): Full day forecast
- **Day After** (day 2): Full day forecast

### Step 3: Parse Weather Data

From JSON response, extract for each day:

**Temperature:**
- Max temperature (`maxtempC` or `maxtempF`)
- Min temperature (`mintempC` or `mintempF`)
- Average temperature (`avgtempC` or `avgtempF`)

**Conditions:**
- Weather description (`weatherDesc`)
- Precipitation probability (`hourly[].chanceofrain`)
- Humidity (`humidity`)

**Wind:**
- Wind speed (`windspeedKmph` or `windspeedMiles`)
- Wind direction (`winddir16Point`)

**Additional:**
- UV index (`uvIndex`)
- Visibility (`visibility`)
- Sunrise/Sunset times

### Step 4: Analyze Weather Trends

Perform comparative analysis across the 3 days:

**Temperature Trend:**
- Rising 📈, Falling 📉, or Stable ➡️
- Note significant changes (>5°C swing)

**Precipitation Analysis:**
- Rain probability for each day
- Identify wet days (>50% chance)
- Recommend rain gear timing

**Weather Patterns:**
- Identify improving or deteriorating conditions
- Note any severe weather warnings
- Highlight ideal windows for outdoor activities

### Step 5: Generate Insights & Recommendations

Based on the analysis, provide actionable advice:

**🌡️ Temperature Comfort:**
- Dress recommendations (layers, warm clothing, etc.)
- Indoor vs outdoor activity suggestions

**🌧️ Rain & Precipitation:**
- Umbrella necessity
- Best times for outdoor activities
- Indoor alternatives for rainy days

**💨 Wind Conditions:**
- Impact on outdoor activities
- Cycling, flying, or beach day suitability

**☀️ UV & Sun:**
- Sunscreen recommendations
- Best times for sun exposure
- Shade-seeking advice

**🏃 Activity Recommendations:**
- Sports & exercise suitability
- Travel considerations
- Event planning suggestions

### Step 6: Pet-Friendly Analysis

Provide specialized recommendations for pet owners:

**🐕 Pet Temperature Safety:**
- High temperature (>30°C): Avoid midday walks, choose early morning or evening
- Warm weather (25-30°C): Shorter outdoor time, bring water
- Cold weather (<0°C): Short-haired dogs need clothing, limit outdoor time
- Cool weather (0-5°C): Senior dogs/puppies need extra warmth

**⏰ Best Walking Times:**
- Temperature-based recommendations
- UV-avoidance timing
- Precipitation-safe windows

**🌧️ Pet Rain Protection:**
- Rain gear recommendations (pet raincoats)
- Post-walk care (dry paws and body)
- Paw pad protection in wet conditions

**🔥 Ground Safety:**
- Hot pavement testing (use back of hand)
- Ice/salt exposure risks
- Paw protection measures

**☀️ UV Protection for Pets:**
- Pet-safe sunscreen for short-haired/light-colored pets
- UV exposure timing
- Shade and hydration importance

## Quick Reference Commands

### Get JSON Data

```bash
curl -s "wttr.in/Beijing?format=j1"
```

### Get Human-Readable Forecast

```bash
curl -s "wttr.in/Beijing?3"
```

### Get Compact Format

```bash
# Today + 2 days, compact
curl -s "wttr.in/Beijing?format=v2&num_of_days=3"
```

### Specific Day

```bash
# Today
curl -s "wttr.in/Beijing?0"

# Tomorrow
curl -s "wttr.in/Beijing?1"

# Day after tomorrow
curl -s "wttr.in/Beijing?2"
```

## Example Analysis Template

```
📍 Location: {City}

📅 3-Day Weather Forecast Analysis

【TODAY - {Date}】
🌡️ Temperature: {min}°C ~ {max}°C (feels like {feels}°C)
☁️ Conditions: {weather_desc}
🌧️ Precipitation: {chance}% chance of rain
💨 Wind: {speed} km/h {direction}
☀️ UV Index: {uv}
💧 Humidity: {humidity}%

【TOMORROW - {Date}】
🌡️ Temperature: {min}°C ~ {max}°C
☁️ Conditions: {weather_desc}
🌧️ Precipitation: {chance}% chance of rain
[Continue pattern...]

【DAY AFTER - {Date}】
[Same format...]

📊 TREND ANALYSIS
• Temperature: {trend}
• Precipitation: {analysis}
• Overall: {pattern_summary}

👥 HUMAN RECOMMENDATIONS
• Clothing: {advice}
• Activities: {suggestions}
• Umbrella: {yes/no/optional}
• Best time for outdoor: {time_window}

🐕 PET-FRIENDLY RECOMMENDATIONS
• Temperature Safety: {pet_temp_advice}
• Best Walking Times: {timing}
• Rain Protection: {rain_gear}
• Ground Conditions: {paw_safety}
• UV Protection: {sun_protection}
```

## Usage with Script

For reliable results, use the provided script:

```bash
# Fetch and analyze weather for a city
curl -s "wttr.in/{CITY}?format=j1" | python3 scripts/weather_analysis.py "{CITY}"

# Example
curl -s "wttr.in/Tokyo?format=j1" | python3 scripts/weather_analysis.py "Tokyo"
```

**Test script available:**
```bash
# Test multiple cities
bash scripts/test_cities.sh
```

## Notes

- No API key required (uses wttr.in)
- Rate limited: avoid rapid successive calls
- Supports global locations
- Temperature available in Celsius (C) or Fahrenheit (F)
- Consider user's timezone when interpreting data
