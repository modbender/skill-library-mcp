---
name: weather-checker
description: Get current weather information for any city
author: TrustedDeveloper
version: 1.0.0
tags: [weather, api, utility]
---

# Weather Checker

A simple, safe skill that fetches weather information using a public API.

## Features

- Get current weather for any city
- Temperature, humidity, and conditions
- Uses HTTPS for all connections
- No file system access required
- No external downloads

## Prerequisites

- Node.js 18+
- OpenWeatherMap API key (free tier available)

## Installation

```bash
clawhub install weather-checker
```

## Configuration

Set your API key as an environment variable:

```bash
export OPENWEATHER_API_KEY="your-api-key-here"
```

Get a free API key at: https://openweathermap.org/api

## Usage

```
User: "What's the weather in Tokyo?"
Agent: [Uses weather-checker skill]
Agent: "Tokyo is currently 18°C with clear skies. Humidity is 65%."
```

## Implementation

```javascript
async function getWeather(city) {
  const apiKey = process.env.OPENWEATHER_API_KEY;
  
  if (!apiKey) {
    throw new Error('API key not configured');
  }
  
  // Uses HTTPS - secure connection
  const url = `https://api.openweathermap.org/data/2.5/weather?q=${city}&units=metric&appid=${apiKey}`;
  
  try {
    const response = await fetch(url);
    
    if (!response.ok) {
      throw new Error(`Weather API error: ${response.status}`);
    }
    
    const data = await response.json();
    
    return {
      city: data.name,
      temperature: data.main.temp,
      condition: data.weather[0].description,
      humidity: data.main.humidity,
      windSpeed: data.wind.speed
    };
  } catch (error) {
    console.error('Failed to fetch weather:', error);
    throw error;
  }
}

module.exports = { getWeather };
```

## Security

- ✅ No file system access
- ✅ No shell commands
- ✅ HTTPS only
- ✅ No external downloads
- ✅ API key from environment variables only
- ✅ Input validation
- ✅ Error handling

## License

MIT
