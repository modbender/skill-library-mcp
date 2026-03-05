---
name: bitaxe-monitor
description: Monitor Bitaxe Gamma Bitcoin miner status via HTTP API. Use when the user wants to check the status, hashrate, temperature, power consumption, or statistics of a Bitaxe Gamma miner. Supports config file or environment variable for device IP configuration, fetching system info, and formatting output as human-readable text or JSON.
---

# Bitaxe Monitor

Monitor and retrieve status information from Bitaxe Gamma (and compatible) Bitcoin miners via their HTTP API.

## Overview

Bitaxe Gamma is an open-source Bitcoin miner based on the BM1370 ASIC. It exposes a REST API at `http://<ip>/api/system/info` that returns real-time statistics including:

- Hashrate (current, 1m, 10m, 1h averages)
- Power consumption and voltage
- Temperatures (ASIC, voltage regulator)
- Fan speed and RPM
- Share statistics (accepted/rejected)
- Best difficulty found
- WiFi status and signal strength
- Pool connection info
- Uptime and version info

## Usage

Use the provided script to fetch and display miner status:

```bash
python3 scripts/bitaxe_status.py [ip_address] [--format {json,text}] [--set-ip IP]
```

### IP Configuration

The script looks for the Bitaxe IP in this order:
1. Command line argument
2. Config file (`~/.config/bitaxe-monitor/config.json`)
3. `BITAXE_IP` environment variable
4. Error (if none found)

### Saving IP Configuration

**Option 1: Save to config file (recommended)**
```bash
python3 scripts/bitaxe_status.py --set-ip 192.168.1.100
```
This saves the IP to `~/.config/bitaxe-monitor/config.json`.

The config file is stored in a dedicated directory and does not modify your shell profile files.

**Option 2: Set environment variable**
```bash
export BITAXE_IP=192.168.1.100
python3 scripts/bitaxe_status.py
```

**Option 3: Set for a single command**
```bash
BITAXE_IP=192.168.1.100 python3 scripts/bitaxe_status.py
```

### Checking Status

**With IP configured:**
```bash
python3 scripts/bitaxe_status.py
```

**Override with different IP:**
```bash
python3 scripts/bitaxe_status.py 192.168.1.105
```

**Get raw JSON data:**
```bash
python3 scripts/bitaxe_status.py --format json
```

## API Endpoints

The Bitaxe API provides these main endpoints:

- `GET /api/system/info` - Complete system status (used by default)
- `GET /api/system/asic` - ASIC-specific settings
- `GET /api/system/statistics` - Historical statistics (requires data logging enabled)
- `GET /api/system/statistics/dashboard` - Dashboard-formatted statistics

## Key Status Fields

| Field | Description | Unit |
|-------|-------------|------|
| `hashRate` | Current hashrate | GH/s |
| `hashRate_1m` | 1-minute average | GH/s |
| `hashRate_10m` | 10-minute average | GH/s |
| `power` | Power consumption | Watts |
| `temp` | ASIC temperature | °C |
| `vrTemp` | Voltage regulator temp | °C |
| `fanspeed` | Fan speed percentage | % |
| `fanrpm` | Fan RPM | RPM |
| `sharesAccepted` | Accepted shares | count |
| `sharesRejected` | Rejected shares | count |
| `bestDiff` | Best difficulty found | number |
| `wifiRSSI` | WiFi signal strength | dBm |
| `uptimeSeconds` | System uptime | seconds |

## Resources

### scripts/

- `bitaxe_status.py` - Main script to fetch and display Bitaxe status
  - Supports both text (human-readable) and JSON output formats
  - Handles connection errors gracefully
  - Formats key metrics with emoji indicators
  - Reads IP from config file or `BITAXE_IP` environment variable
  - Saves IP to config file with `--set-ip`

## Configuration

### Config File Location

The script stores configuration in:
```
~/.config/bitaxe-monitor/config.json
```

This directory is created automatically when using `--set-ip`.

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `BITAXE_IP` | IP address of your Bitaxe miner | Alternative to config file |

## Error Handling

The script handles common errors:
- Connection failures (wrong IP, device offline)
- Invalid JSON responses
- Network timeouts
- Missing IP (prompts user to configure IP)

## Command Reference

| Command | Description |
|---------|-------------|
| `bitaxe_status.py` | Check status using saved configuration |
| `bitaxe_status.py <IP>` | Check status of specific IP (one-time) |
| `bitaxe_status.py --set-ip <IP>` | Save IP to config file |
| `bitaxe_status.py --format json` | Output raw JSON |
| `bitaxe_status.py --format text` | Output formatted text (default) |

## Examples

**Quick setup (do once):**
```bash
python3 scripts/bitaxe_status.py --set-ip 192.168.1.100
```

**Daily usage:**
```bash
python3 scripts/bitaxe_status.py
```

**Check multiple miners:**
```bash
python3 scripts/bitaxe_status.py 192.168.1.100
python3 scripts/bitaxe_status.py 192.168.1.101
```

## References

For complete API documentation, see the official Bitaxe wiki:
https://osmu.wiki/bitaxe/api/

The OpenAPI specification is available at:
https://github.com/bitaxeorg/ESP-Miner/blob/master/main/http_server/openapi.yaml
