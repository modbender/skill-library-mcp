# openmeteo-sh-weather-simple

An OpenClaw skill for getting current weather and forecasts using [openmeteo-sh](https://github.com/lstpsche/openmeteo-sh).

## What this skill does

Teaches the agent how to fetch current weather conditions and forecasts (up to 16 days) for any city or coordinates worldwide. The agent summarizes results in natural language — it never pastes raw CLI output to the user.

This is the **simple** variant: it covers everyday weather queries (temperature, rain, wind, snow, UV, sunrise/sunset) and is optimized for speed and minimal token usage. For historical weather, detailed variable selection, or model choice, see [openmeteo-sh-weather-advanced](../openmeteo-sh-weather-advanced/).

## About openmeteo-sh

[openmeteo-sh](https://github.com/lstpsche/openmeteo-sh) is a fast, lightweight Bash CLI for the [Open-Meteo](https://open-meteo.com) weather API. It has near-zero dependencies — only `bash`, `curl`, and `jq` — with no Python, Node, or compiled binaries required.

Key features relevant to this skill:
- **`--llm` output format** — compact TSV designed for AI agents, reduces token usage by ~90% compared to key=value formats
- **City name resolution** — `--city=London` instead of lat/lon coordinates
- **Weather code resolution** — WMO codes are automatically converted to text (e.g. "Light rain" instead of code 61)
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

- Current conditions for any city or coordinates
- Hourly and daily forecasts up to 16 days
- Targeted queries (e.g. "when will the rain stop?" fetches only precipitation data)
- Unit conversion (Celsius/Fahrenheit, km/h/mph, mm/inch)
- Smart forecast windowing via `--forecast-since` (skip to a specific day)

## Network access

This skill invokes the `openmeteo` CLI, which makes HTTPS requests to:
- `https://api.open-meteo.com` — weather forecast API
- `https://geocoding-api.open-meteo.com` — city name resolution

No other network access is made. No data is sent to any third-party service. No API key or authentication is needed.

## License

This skill is MIT licensed. [openmeteo-sh](https://github.com/lstpsche/openmeteo-sh) is MIT licensed. Weather data is provided by [Open-Meteo](https://open-meteo.com).
