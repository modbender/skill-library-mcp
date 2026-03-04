---
name: shulian-weather
description: "Get current weather and forecasts via WeatherAPI.com. Use when: user asks about weather, temperature, or forecasts for any location. IMPORTANT: You must configure your own API key in OpenClaw settings or config file before using this skill."
homepage: https://www.weatherapi.com/
author: tanluzhe
license: MIT
version: "1.0.0"
metadata:
  {
    "openclaw":
      { "emoji": "🌦️", "requires": { "bins": ["curl"] }, "primaryEnv": "WEATHER_API_KEY" },
  }
---

# WeatherAPI.com Skill

Get current weather conditions and forecasts using WeatherAPI.com.

## ⚠️ IMPORTANT: Configure Your API Key First

**This skill will NOT work until you configure your own API key.**

### Where to Get API Key

1. Visit [WeatherAPI.com](https://www.weatherapi.com/)
2. Sign up for a free account
3. Copy your API key from the dashboard
4. Configure it using one of the methods below

**Free tier: 1,000,000 calls/month**

## Configuration

### Option 1: OpenClaw UI (Recommended)

1. Open OpenClaw Control UI: http://127.0.0.1:18789
2. Go to **Skills** section
3. Find **shulian-weather** skill
4. Click **Configure** button
5. Enter your API key
6. Save

### Option 2: Config File

Edit `~/.openclaw/openclaw.json`:

```json
{
  "skills": {
    "entries": {
      "shulian-weather": {
        "enabled": true,
        "apiKey": "YOUR-API-KEY-HERE"
      }
    }
  }
}
```

### Option 3: Environment Variable

Add to `~/.zshrc`:

```bash
export WEATHER_API_KEY="YOUR-API-KEY-HERE"
```

Then restart Gateway.

## Usage

After configuring your API key, you can ask:

- "What's the weather in Shanghai?"
- "Will it rain in Beijing tomorrow?"
- "Weather forecast for New York this week"

## Commands

### Current Weather

```bash
API_KEY="${WEATHER_API_KEY}"
curl -s "https://api.weatherapi.com/v1/current.json?key=${API_KEY}&q=London"
```

### Forecast

```bash
API_KEY="${WEATHER_API_KEY}"
curl -s "https://api.weatherapi.com/v1/forecast.json?key=${API_KEY}&q=London&days=7"
```

### Search

```bash
API_KEY="${WEATHER_API_KEY}"
curl -s "https://api.weatherapi.com/v1/search.json?key=${API_KEY}&q=London"
```

## Troubleshooting

### "API key not configured" error

1. Make sure you've configured your API key in OpenClaw UI or config
2. Restart Gateway after configuration
3. Check logs: `tail -f ~/.openclaw/logs/gateway.log`

### Verify configuration

```bash
cat ~/.openclaw/openclaw.json | jq '.skills.entries."shulian-weather"'
```

## Notes

- API key is required - no default key provided
- Supports worldwide locations
- Returns JSON format
- Free tier: 1,000,000 calls/month
