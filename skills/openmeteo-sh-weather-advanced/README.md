# openmeteo-sh-weather-advanced

An OpenClaw skill for advanced weather queries using [openmeteo-sh](https://github.com/lstpsche/openmeteo-sh).

## What this skill does

Teaches the agent how to perform advanced weather queries: historical weather data (from 1940), detailed variable selection, weather model choice, and fine-grained forecast control.

This is the **advanced** variant — use it when you need historical data, niche variables (pressure, dew point, snow depth, visibility, etc.), or specific weather models (ERA5, CERRA, ECMWF IFS). For everyday weather queries, see [openmeteo-sh-weather-simple](../openmeteo-sh-weather-simple/).

## About openmeteo-sh

[openmeteo-sh](https://github.com/lstpsche/openmeteo-sh) is a fast, lightweight Bash CLI for the [Open-Meteo](https://open-meteo.com) weather API. It has near-zero dependencies — only `bash`, `curl`, and `jq` — with no Python, Node, or compiled binaries required.

Key features relevant to this skill:
- **`--llm` output format** — compact TSV designed for AI agents, reduces token usage by ~90% compared to key=value formats
- **City name resolution** — `--city=London` instead of lat/lon coordinates
- **Weather code resolution** — WMO codes are automatically converted to text (e.g. "Light rain" instead of code 61)
- **Built-in variable help** — `openmeteo weather help --daily-params` lists all available variables with descriptions
- **Historical data** — reanalysis data from 1940 via ERA5, CERRA, ECMWF IFS
- **No API key required** — uses the free Open-Meteo API

Data is provided by [Open-Meteo](https://open-meteo.com), which is free for non-commercial use.

## Prerequisites

- `bash` 3.2+ (pre-installed on macOS and Linux)
- `curl` (pre-installed on macOS and Linux)
- `jq` — install if missing: `brew install jq` (macOS) or `sudo apt install jq` (Debian/Ubuntu)

## Installation

### openmeteo-sh CLI

#### macOS / Linux (Homebrew)

```sh
brew tap lstpsche/tap
brew install openmeteo-sh
```

#### Debian / Ubuntu (APT)

```sh
# Import the signing key
curl -fsSL https://lstpsche.github.io/apt-repo/pubkey.gpg \
  | sudo gpg --dearmor -o /usr/share/keyrings/openmeteo-sh.gpg

# Add the repository
echo "deb [signed-by=/usr/share/keyrings/openmeteo-sh.gpg] https://lstpsche.github.io/apt-repo stable main" \
  | sudo tee /etc/apt/sources.list.d/openmeteo-sh.list

# Install
sudo apt update
sudo apt install openmeteo-sh
```

#### From source

```sh
git clone https://github.com/lstpsche/openmeteo-sh.git
cd openmeteo-sh
sudo make install
```

## What the agent can do with this skill

- Everything from [openmeteo-sh-weather-simple](../openmeteo-sh-weather-simple/), plus:
- Historical weather data from 1940 to present (`openmeteo history`)
- Weather model selection (best_match, ERA5, ERA5-Land, CERRA, ECMWF IFS, etc.)
- Past-days lookback (up to 92 days before today)
- Extended variable set (pressure, dew point, humidity, visibility, snow depth, etc.)
- Built-in variable discovery via `openmeteo weather help --daily-params --llm`

## Network access

This skill invokes the `openmeteo` CLI, which makes HTTPS requests to:
- `https://api.open-meteo.com` — weather forecast API
- `https://archive-api.open-meteo.com` — historical weather API
- `https://geocoding-api.open-meteo.com` — city name resolution

No other network access is made. No data is sent to any third-party service. No API key or authentication is needed.

## License

This skill is MIT licensed. [openmeteo-sh](https://github.com/lstpsche/openmeteo-sh) is MIT licensed. Weather data is provided by [Open-Meteo](https://open-meteo.com).
