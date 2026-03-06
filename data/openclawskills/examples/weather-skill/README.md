# Weather Skill

Get weather information using OpenWeatherMap API.

## Setup

1. Get a free API key from [OpenWeatherMap](https://openweathermap.org/api)
2. Configure the skill with your API key

## Configuration

```json
{
  "apiKey": "your-api-key-here",
  "defaultLocation": "New York",
  "units": "metric"
}
```

## Tools

- `getCurrentWeather(location?)` - Get current weather
- `getForecast(location?)` - Get 5-day forecast
- `getLastWeather()` - Get cached weather data

## Usage Example

```typescript
const weather = await agent.tools.weather.getCurrentWeather("Tokyo");
// Returns: { location, temperature, feelsLike, humidity, description, windSpeed, timestamp }
```
