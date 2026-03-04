---
name: weather-query
description: Use when users ask about weather conditions, forecasts, or climate information for locations in China.
---

# Weather Query Skill

This skill enables AI agents to fetch real-time weather information and forecasts for locations in China using the provided shell scripts.

## When to Use This Skill

Use this skill when users:
- Ask about current weather conditions
- Want weather forecasts
- Need temperature, humidity, wind information
- Request air quality data
- Plan outdoor activities and need weather info

## How to Use

### Get Real-time Weather
Use the `realtime.sh` script to get current conditions, air quality, daily life indices, and weather alerts.
```bash
./scripts/realtime.sh <query> [--encoding <text|json|markdown>]
```

### Get Weather Forecast
Use the `forecast.sh` script to get hourly and daily forecast data, along with sunrise/sunset times.
```bash
./scripts/forecast.sh <query> [--encoding <text|json|markdown>] [--days <0-8>]
```
- `query` (Required): The name of the city, district, or area in Chinese (e.g., `雨花台`, `北京`). Can be provided as a positional argument or with `--query`.
- `encoding` (Optional): Used to specify the returned data format. Can be `text`, `json`, or `markdown`.
- `days` (Optional, forecast only): Used to specify the weather forecast date range. An integer between 0 and 8.

## Response Format

To balance information depth with token consumption, you **MUST** use the following rules for the `encoding` parameter:

1. **Default Strategy (`--encoding markdown`)**
   - **When to use:** By default for standard weather inquiries.
   - **Why:** Provides well-structured, easy-to-read information with moderate token usage.

2. **Brief Information (`--encoding text`)**
   - **When to use:** When the user explicitly requests brief or summarized weather information.
   - **Why:** Returns only essential details in plain text, saving maximum tokens.

3. **Complete Information (`--encoding json`)**
   - **When to use:** Only when the user explicitly asks for raw data, detailed fields, or comprehensive data (all indices, timestamps).
   - **Why:** Returns the complete API payload, which is highly token-heavy.

## Best Practices

1. **Location Names**: Always use Chinese characters for location names
2. **Error Handling**: Check if the location is valid before displaying results
3. **Context**: Provide relevant context based on weather conditions
   - Rain: Suggest bringing umbrella
   - Hot: Recommend staying hydrated
   - Cold: Advise wearing warm clothes
   - Poor AQI: Suggest wearing mask

4. **Fallbacks**: If a specific district doesn't work, try the city name

## Troubleshooting

### Issue: Location not found
- **Solution**: Try using the main city name instead of district
- Example: Use "北京" instead of "朝阳区"

### Issue: No forecast data
- **Solution**: Verify the location name is correct
- Try standard city names: 北京, 上海, 广州, 深圳, etc.

### Issue: Data seems outdated
- **Solution**: The API updates regularly, but weather can change quickly
- Check the `updated` timestamp in the response

## Supported Locations

The weather API supports most cities and districts in China, including:
- Provincial capitals: 北京, 上海, 广州, 深圳, 成都, 杭州, 南京, 武汉, etc.
- Major cities: 苏州, 青岛, 大连, 厦门, etc.
- Districts: 海淀区, 朝阳区, 浦东新区, etc.
