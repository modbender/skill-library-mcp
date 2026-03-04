---
name: iqair
description: Get real-time air quality data from IQAir API for any location worldwide. Returns AQI (Air Quality Index) with visual indicators and quality levels. Use when asked about air quality, pollution levels, or AQI in specific cities/locations (e.g., "How is the air in Riga?", "Is it safe to go outside in Beijing?", "What's the air quality like?"). Also use when asked about general weather to supplement weather data with air quality information (e.g., "What's the weather in Budapest?", "How's the weather today?").
metadata:
  openclaw:
    homepage: https://github.com/atesluks/openclaw-skill-iqair
    requires:
      env: ["IQAIR_API_KEY"]
---

# IQAir Air Quality Checker

Get real-time air quality data from the IQAir API with formatted output including AQI score, emoji indicator, and quality level.

## Prerequisites

**API Key Required**: User must have a free IQAir API key stored in the `IQAIR_API_KEY` environment variable.

If the key is not set, guide the user:
1. Visit https://dashboard.iqair.com/personal/api-keys
2. Sign up/sign in and subscribe to the free Community plan
3. Copy the API key
4. Set it: `export IQAIR_API_KEY="your_key_here"`

## Quick Usage

**By city name:**
```bash
python scripts/get_aqi.py Riga Latvia
python scripts/get_aqi.py London "United Kingdom"
python scripts/get_aqi.py Budapest Hungary
```

**By coordinates (most reliable):**
```bash
python scripts/get_aqi.py --lat 56.9496 --lon 24.1052
```

**Nearest city (based on IP):**
```bash
python scripts/get_aqi.py --nearest
```

## How to Respond to User Queries

When a user asks about air quality:

1. **Determine the location** - Extract city/country from their query
2. **Run the script** - Use `scripts/get_aqi.py` with appropriate arguments
3. **Return formatted output** - The script provides emoji, AQI value, level, and location

**Example interaction:**

User: "How good is air in Riga?"

Response process:
- Location: Riga, Latvia
- Run: `python scripts/get_aqi.py Riga Latvia`
- Output: `🟢 19 - Good\nRiga, Latvia`
- Reply: "Air quality in Riga is currently excellent! 🟢 19 (Good)"

## Handling Location Names

**City/country names**:
- Use exact names as they appear in IQAir's database
- Capital cities: Often the state/province matches the city name
- If city lookup fails, try coordinates instead

**Common location patterns**:
- Riga, Latvia → `Riga Latvia` (state defaults to city)
- London, UK → `London "United Kingdom"` (quote if spaces)
- New York, USA → `"New York" "United States" "New York"` (city, country, state)

**When in doubt**: Use coordinate-based lookup with `--lat` and `--lon` (more reliable).

## Output Format

The script returns a concise, formatted string:
```
🟢 45 - Good
Riga, Latvia
```

Customize your response based on the AQI level:
- **0-50 (🟢 Good)**: "Excellent", "Perfect for outdoor activities"
- **51-100 (🟡 Moderate)**: "Acceptable", "Sensitive people should limit prolonged outdoor exertion"
- **101-150 (🟠 USG)**: "Unhealthy for sensitive groups", "Children and people with respiratory issues should reduce outdoor exertion"
- **151-200 (🔴 Unhealthy)**: "Everyone may experience health effects", "Reduce outdoor activities"
- **201-300 (🟣 Very Unhealthy)**: "Health alert", "Avoid outdoor activities"
- **301+ (🟤 Hazardous)**: "Emergency conditions", "Stay indoors"

## Technical Details

For API specifications, endpoints, and error handling, see `references/api.md`.

## Rate Limits

Free Community plan limits:
- 5 calls/minute
- 500 calls/day
- 10,000 calls/month

Avoid making repeated calls for the same location within short time periods.
