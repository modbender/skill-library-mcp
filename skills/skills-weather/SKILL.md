---
name: skills-weather
description: Get the weather for a specific location or coordinates
version: 1.0.0
entry: index.js
runtime: node
repository: https://github.com/mangonob/skills-weather
tags:
  - weather
  - qwweather
permissions:
  - network:request
author: mangonob
metadata:
  clawbot:
    emoji: "☁️"
    os: ["darwin", "linux", "windows"]
---

# Weather Skill

## Installation

npm

```bash
npm install skills-weather
```

pnpm

```bash
pnpm add skills-weather
```

## Parameters

- `-V, --version`: output the version number
- `-l, --location <string>`: Location to get the weather for
- `-d, --days <number>`: Specify the number of days to get the weather forecast for.
- `-h, --hours <number>`: Specify the number of hours to get the weather forecast for.
- `-f, --config <string>`: Path to the config file
- `-c, --coordinates <string>`: Latitude and longitude to get the weather for (format: lon,lat)
- `--help`: display help for command

Parameter constraints:

- `--location` and `--coordinates` cannot be used together. You must provide at least one of them.
- `--days` and `--hours` cannot be used together. If neither is provided, real-time weather will be returned.

## Environment variables:

- `SKILLS_WEATHER_CONFIG_FILE_PATH`: Optional environment variable to specify the path to the configuration file. If not provided, the skill will look for a default config file in the current directory.

## Examples

Get real-time weather:

- Get real-time weather for New York: `skills-weather -l "New York"`
- Get real-time weather for specific coordinates: `skills-weather -c "-74.0060,40.7128"`
- Get real-time weather for London (with a specified config file): `skills-weather -l "London" -f "/path/to/config.json"`

Get daily weather forecasts:

- Get today's weather forecast for Futian District, Shenzhen: `skills-weather -l "futian" -d 1`
- Get Beijing's weather forecast for the next 3 days: `skills-weather -l "北京" -d 3`
- Get a one-month weather forecast for specific coordinates: `skills-weather -c "116.4074,39.9042" -d 30`
- Get Shanghai's weather forecast for the next 2 days (with a specified config file): `skills-weather -l "上海" -d 2 -f "/path/to/config.json"`

Get hourly weather forecasts:

- Get Guangzhou's weather forecast for the next 12 hours: `skills-weather -l "广州" -h 12`
- Get a 6-hour weather forecast for specific coordinates: `skills-weather -c "121.4737,31.2304" -h 6`
- Get Shenzhen's weather forecast for the next 24 hours (with a specified config file): `skills-weather -l "深圳" -h 24 -f "/path/to/config.json"`

## Supported Weather Data Providers

- [和风天气 (QWeather)](https://dev.qweather.com)

## Configuration File

#### [和风天气](https://dev.qweather.com)

##### Default config file path: `~/.skills-weather-config.json`

##### Example:

```json
{
	"privateKey": "G7refSYx9TWAPADGuOdyGycWVNr0POaebYddeNtDjxSSN01b0165TITV9fA=",
	"appId": "BB9A36BAB1",
	"credentialId": "3207A9092A",
	"apiHost": "0dfe03a7c3.re.qweatherapi.com"
}
```

##### Field Descriptions

- `privateKey`: A private key provided by QWeather for authentication.
- `appId`: The application ID provided by QWeather to identify the app.
- `credentialId`: A credential ID provided by QWeather for authentication.
- `apiHost`: The host address of the QWeather API.
