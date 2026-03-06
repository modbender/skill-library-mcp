# Home Assistant CLI for OpenClaw

A streamlined Home Assistant CLI for OpenClaw with one-command setup and natural language control.

## Features

- **One-command setup**: `ha-cli setup <url> <token>`
- **Natural commands**: `ha-cli on living room` or `ha-cli living room on`
- **Smart fuzzy matching**: "bed" finds "Bedroom Light", "Bedroom AC"
- **Auto-config save**: Credentials stored in config.json
- **Any device type**: Lights, switches, covers, climate, locks, scenes, scripts

## Quick Start

```bash
# One-command setup
ha-cli setup 192.168.1.100 your_long_lived_token

# Control devices
ha-cli on living room
ha-cli off bedroom light
ha-cli 22 thermostat
ha-cli scene movie

# Check status
ha-cli status
ha-cli list light
```

## Setup

### 1. Get Long-Lived Access Token

1. Open Home Assistant Web UI
2. Click your username (Profile)
3. Scroll to "Long-Lived Access Tokens"
4. Click "Create Token"
5. Copy the token

### 2. Configure

```bash
# Replace with your HA IP and token
ha-cli setup 192.168.1.100 your_token_here
```

That's it! Configuration is saved automatically.

## Commands

### Basic Control

```bash
# Turn on/off (works with any device)
ha-cli on living room
ha-cli off bedroom light
ha-cli open garage
ha-cli close blinds
ha-cli lock front door

# Alternative: name first
ha-cli living room on
ha-cli bedroom light off
```

### Brightness & Color

```bash
ha-cli brightness 75 living room
ha-cli rgb #FF5500 desk lamp
```

### Temperature

```bash
ha-cli 22 thermostat
ha-cli temperature 24 bedroom
```

### Scenes & Scripts

```bash
ha-cli scene movie
ha-cli scene good morning
ha-cli script morning
```

### Status

```bash
ha-cli status           # HA status overview
ha-cli list             # All entities
ha-cli list light       # Only lights
ha-cli list switch      # Only switches
```

## Examples

```bash
# Morning routine
ha-cli scene good morning
ha-cli script morning_routine

# Movie time
ha-cli scene movie
ha-cli brightness 20 living room

# Goodnight
ha-cli off everywhere
ha-cli lock front door
```

## Supported Domains

- `light` - On/off, brightness, RGB
- `switch` - On/off
- `cover` - Open/close/stop
- `climate` - Temperature
- `lock` - Lock/unlock
- `fan` - On/off
- `scene` - Activate
- `script` - Run

## Files

```
homeassistant/
├── SKILL.md      # OpenClaw skill docs
├── ha-cli        # Main CLI (Node.js)
├── ha            # Bash wrapper
└── config.json   # Saved config
```

## License

MIT
