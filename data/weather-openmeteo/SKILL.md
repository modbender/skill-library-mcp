---
name: weather-openmeteo
description: Get current weather and forecasts using Open-Meteo API (no API key required). Optimized for PowerShell environments with Chinese support.
homepage: https://open-meteo.com/en/docs
metadata: {"clawdbot":{"emoji":"🌤️","requires":{"bins":[]}}}
---

# Weather Open-Meteo Skill

A reliable weather skill using Open-Meteo API, specifically optimized for PowerShell environments with full Chinese support.

## Features

- ✅ **No API key required** - Completely free to use
- ✅ **PowerShell optimized** - Works well in PowerShell environments
- ✅ **Chinese support** - Designed for Chinese users
- ✅ **7-day forecast** - Complete weather predictions
- ✅ **Multi-city support** - Built-in Chinese major cities
- ✅ **Weather code translation** - Converts WMO codes to Chinese descriptions

## Quick Start

### Basic Usage

```powershell
# Navigate to skill directory
cd ~/.openclaw/workspace/skills/weather-openmeteo

# Get current weather (English version)
.\weather-en.ps1 -City Shanghai

# Get current weather (Chinese version)
.\weather-cn.ps1 -City Beijing
```

### Supported Cities

- Shanghai (上海)
- Beijing (北京)
- Guangzhou (广州)
- Shenzhen (深圳)
- Chengdu (成都)
- Hangzhou (杭州)
- Nanjing (南京)
- Wuhan (武汉)
- Xian (西安)
- Chongqing (重庆)

## Script Files

### weather-en.ps1 (English Version)
- Displays weather information in English
- Complete weather code descriptions
- Suitable for international users

### weather-cn.ps1 (Chinese Version)
- Displays weather information using Pinyin
- Avoids Chinese character encoding issues
- Suitable for Chinese users

### weather-simple.ps1 (Simplified Version)
- Basic functionality
- Good for learning and modification

## API Reference

### Current Weather API
```
https://api.open-meteo.com/v1/forecast?
  latitude=31.2304&
  longitude=121.4737&
  current_weather=true&
  timezone=Asia/Shanghai
```

### 7-Day Forecast API
```
https://api.open-meteo.com/v1/forecast?
  latitude=31.2304&
  longitude=121.4737&
  daily=weathercode,temperature_2m_max,temperature_2m_min,precipitation_sum&
  timezone=Asia/Shanghai
```

## Weather Code Reference

| Code | English | Chinese |
|------|---------|---------|
| 0 | Clear sky | 晴天 |
| 1 | Mainly clear | 主要晴朗 |
| 2 | Partly cloudy | 部分多云 |
| 3 | Overcast | 多云 |
| 45 | Fog | 雾 |
| 48 | Depositing rime fog | 雾凇 |
| 51-55 | Drizzle | 雨 |
| 61-65 | Rain | 雨 |
| 71-77 | Snow | 雪 |
| 80-86 | Rain showers | 雨 |
| 95-99 | Thunderstorm | 雷暴 |

## Example Output

### Current Weather
```
=== Current Weather - Shanghai ===
Time: 2026-03-03T17:45
Temperature: 8.7C
Wind speed: 12.0 km/h
Wind direction: 16 degrees
Weather: Overcast
```

## Troubleshooting

### 1. Script Execution Error
```powershell
# Set execution policy
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### 2. Network Connection Issues
- Ensure you can access open-meteo.com
- Check firewall settings

### 3. City Not Supported
Edit the `$cityCoords` hash table to add new cities:
```powershell
"CityName" = @{ latitude = 纬度; longitude = 经度; timezone = "Asia/Shanghai" }
```

## Files Included

- `SKILL.md` - Skill description
- `README.md` - Usage instructions
- `USAGE.md` - Detailed usage guide
- `CREATION.md` - Creation process documentation
- `weather.ps1` - Complete script (Chinese)
- `weather-en.ps1` - English version
- `weather-cn.ps1` - Chinese version (Pinyin)
- `weather-simple.ps1` - Simplified version
- `example.ps1` - Usage examples

## Advantages

### vs Original Weather Skill
| Feature | Original | New Skill |
|---------|----------|-----------|
| API Key | Not needed | Not needed |
| PowerShell Support | Problematic | Optimized |
| Chinese Display | Limited | Full support |
| City Database | None | Built-in Chinese cities |
| Error Handling | Basic | Comprehensive |

### vs Other Weather Services
| Service | API Key | PowerShell | Chinese |
|---------|---------|------------|---------|
| Open-Meteo | ❌ | ✅ | ✅ |
| wttr.in | ❌ | ❌ | Limited |
| WeatherAPI | ✅ | ✅ | ✅ |

## License

MIT License - Free to use and modify