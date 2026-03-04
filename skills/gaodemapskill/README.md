# Gaode Map (AMap) Skill for OpenClaw

This is an OpenClaw skill that integrates with the Gaode Map (AMap) API to provide location services.

## Features

- **Place Search**: Search for places/POIs by keywords.
- **Route Planning**: Plan routes for driving, walking, bicycling, and public transit.
- **Geocoding**: Automatically converts addresses to coordinates.

## Installation

1. Clone this repository into your OpenClaw skills directory (e.g., `~/.openclaw/skills/gaode_map`).
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Configuration

You need a Gaode Map API Key. Get one from [AMap Console](https://console.amap.com/).

Set the environment variable `AMAP_API_KEY` in your OpenClaw configuration or environment.

## Usage

This skill exposes a Python script `amap_tool.py` that the agent can use.

### Commands

- **Search**: `python amap_tool.py search --keywords "..." --city "..."`
- **Route**: `python amap_tool.py route --origin "..." --destination "..." --mode "..."`

## Structure

- `SKILL.md`: The skill definition and instructions for OpenClaw.
- `amap_tool.py`: The implementation of the API client.
- `requirements.txt`: Python dependencies.
