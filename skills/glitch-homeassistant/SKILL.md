# Home Assistant Skill

Control smart home devices via Home Assistant API.

## Skill Metadata

- **Name**: homeassistant
- **Type**: OpenClaw Skill
- **Purpose**: Control lights, switches, covers, climate, scenes, scripts via HA API

## Setup Commands

### Prerequisites

1. Home Assistant running on local network
2. Long-Lived Access Token from HA Profile page

### Configuration (One-Command)

```bash
# Run this to configure
ha-cli setup <HA_URL> <TOKEN>

# Example:
ha-cli setup 192.168.1.100 your_long_lived_token_here
```

Or set environment variables:

```bash
export HA_URL="http://homeassistant.local:8123"
export HA_TOKEN="your_token_here"
```

## Usage Commands

### Basic Control

```bash
# Turn on device (any type)
ha-cli on <device_name>
ha-cli <device_name> on

# Turn off device
ha-cli off <device_name>
ha-cli <device_name> off
```

### Brightness & Color

```bash
# Set brightness (0-100)
ha-cli brightness <0-100> <device_name>
ha-cli <device_name> brightness 75

# Set RGB color
ha-cli rgb #RRGGBB <device_name>
ha-cli rgb #FF5500 "Living Room"
```

### Temperature

```bash
# Set temperature
ha-cli <temperature> <thermostat_name>
ha-cli 22 thermostat
```

### Scenes & Scripts

```bash
# Activate scene
ha-cli scene <scene_name>
ha-cli scene movie

# Run script
ha-cli script <script_name>
ha-cli script morning
```

### Status & Discovery

```bash
# Check HA status
ha-cli status
ha-cli info

# List all entities
ha-cli list
ha-cli list entities

# List by domain
ha-cli list light
ha-cli list switch
ha-cli list climate
```

## Supported Device Types

| Domain | Commands | Examples |
|--------|----------|----------|
| light | on, off, brightness, rgb | `ha-cli on living room` |
| switch | on, off | `ha-cli off tv` |
| cover | open, close, stop | `ha-cli open blinds` |
| climate | temperature, mode | `ha-cli 22 thermostat` |
| lock | lock, unlock | `ha-cli lock front door` |
| scene | activate | `ha-cli scene movie` |
| script | run | `ha-cli script morning` |

## Entity Matching

- Case insensitive
- Partial name matching (bed → Bedroom Light)
- Fuzzy matching enabled

## Error Handling

- Connection error: Shows HA URL and token setup instructions
- Entity not found: Shows similar entity suggestions
- Invalid command: Shows usage help

## Related Skills

- openhue (Philips Hue)
- sonoscli (Sonos speakers)
- eightctl (Eight Sleep)

## Files

```
homeassistant/
├── SKILL.md      # This file
├── README.md     # User documentation
├── ha-cli        # Main CLI executable
├── ha            # Bash wrapper
└── config.json   # Saved configuration
```
