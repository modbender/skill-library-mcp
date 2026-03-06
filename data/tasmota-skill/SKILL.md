---
name: tasmota
description: Discover, monitor, and control Tasmota smart home devices on local networks. Use when tasks involve finding Tasmota devices via network scanning, checking device status and power states, controlling devices (on-off, brightness, color), managing device inventory, or any other Tasmota management operations on ESP8266 or ESP32 devices running Tasmota firmware.
---

# Tasmota Device Management

## Overview

Automated discovery and control of Tasmota-powered smart home devices (ESP8266/ESP32) on local networks. Includes network scanning, status monitoring, power control, dimming, color control, and inventory management.

## Quick Start

**Scan network for Tasmota devices:**
```bash
python3 scripts/tasmota-discovery.py
```

**Check device status:**
```bash
python3 scripts/tasmota-control.py <IP> status 0
```

**Control device:**
```bash
python3 scripts/tasmota-control.py <IP> power on|off|toggle
python3 scripts/tasmota-control.py <IP> brightness 0-100
python3 scripts/tasmota-control.py <IP> color <hex-rgb>
```

## Discovery

### Network Scan

Run a full network scan to find all Tasmota devices:

```bash
python3 scripts/tasmota-discovery.py
```

The script:
1. Performs ping sweep to identify live hosts
2. Scans HTTP (port 80) on live hosts
3. Detects Tasmota via Server header (e.g., "Tasmota/13.1.0")
4. Confirms via JSON API (`/cm?cmnd=status%200`)
5. Retrieves device names, versions, and hardware

Output includes:
- IP address
- Device friendly name
- Tasmota version
- Hardware platform (ESP8266/ESP32)
- Response time

### Identification Signals

Tasmota devices are identified by:
- **Server header:** `Tasmota/<version> (<hardware>)`
- **JSON API response:** `/cm?cmnd=status%200` returns structured status
- **Content keywords:** "Tasmota" in HTML

## Device Control

### Power Control

Toggle or set power state:

```bash
# Toggle
python3 scripts/tasmota-control.py <IP> power toggle

# On/Off
python3 scripts/tasmota-control.py <IP> power on
python3 scripts/tasmota-control.py <IP> power off
```

### Brightness (Dimmers)

Set brightness level (0-100):

```bash
python3 scripts/tasmota-control.py <IP> brightness 50
```

Works on devices with Dimmer support (check StatusSTS).

### Color (RGB Lights)

Set RGB color (hex or comma-separated):

```bash
# Hex format
python3 scripts/tasmota-control.py <IP> color FF0000  # Red
python3 scripts/tasmota-control.py <IP> color 00FF00  # Green

# RGB comma format
python3 scripts/tasmota-control.py <IP> color 255,0,0
```

Works on devices with RGB support (AiYaTo-RGBCW, etc.).

## Status Queries

### Device Status

Retrieve status information:

```bash
# Basic status
python3 scripts/tasmota-control.py <IP> status 0

# All statuses
python3 scripts/tasmota-control.py <IP> status all
```

**Status codes:**
- `0 = Status` - Device info, friendly name, power state
- `1 = StatusPRM` - Parameters, uptime, MAC
- `2 = StatusFWR` - Firmware version, hardware
- `3 = StatusLOG` - Log settings
- `4 = StatusNET` - Network config (IP, gateway, WiFi)
- `5 = StatusMQT` - MQTT configuration
- `9 = StatusTIM` - Time, timezone, sunrise/sunset

### Key Status Fields

**StatusSTS (Status 0):**
- `POWER` - Current state (ON/OFF)
- `Dimmer` - Brightness level (0-100)
- `Wifi.RSSI` - Signal strength
- `Wifi.SSId` - Connected WiFi network

**StatusNET:**
- `IPAddress` - Device IP
- `Hostname` - mDNS hostname
- `Mac` - MAC address

## Bulk Operations

### Get All Device Status

```bash
python3 scripts/tasmota-status.py
```

Iterates through inventory file and shows power state for all devices.

### Managing Inventory

Devices are tracked in a CSV inventory file. Format:

```
IP Address,Device Name,Version,Hardware,Response Time (ms)
192.168.1.116,Office Hall Light,13.1.0,ESP8266EX,53
```

After discovery, save output to inventory file for batch operations.

## Common Tasks

### Finding Labeled Devices

```bash
# Scan and grep for specific device names
python3 scripts/tasmota-discovery.py | grep "Kitchen"
python3 scripts/tasmota-discovery.py | grep "Bulb"
```

### Checking All Lights

```bash
# Get status of all devices
python3 scripts/tasmota-status.py
```

### Power Cycle a Device

```bash
# Off, wait 2s, on
python3 scripts/tasmota-control.py 192.168.1.116 power off
sleep 2
python3 scripts/tasmota-control.py 192.168.1.116 power on
```

## Tasmota API Reference

### Command Format

```
http://<IP>/cm?cmnd=<COMMAND>
```

### Common Commands

| Command | Description |
|---------|-------------|
| `Power` | Toggle power |
| `Power ON` | Turn on |
| `Power OFF` | Turn off |
| `Power TOGGLE` | Toggle state |
| `Status 0` | Device status |
| `Status 4` | Network status |
| `Dimmer <0-100>` | Set brightness |
| `Color <hex>` | Set RGB color |
| `Fade <ON|OFF>` | Enable fade effects |

## Troubleshooting

### Device Not Found

- Verify device is on same subnet
- Check device has HTTP server enabled (Webserver 2 in config)
- Ensure device is powered on and connected to WiFi
- Try direct HTTP request: `curl http://<IP>/cm?cmnd=Status%200`

### Timeout Errors

- Device may be power saving (WiFi sleep)
- Network latency or packet loss
- Check device uptime for recent restarts

### Unknown Power State

Some devices (BLE gateways, sensors) don't have power control. Check capability in StatusSTS.

## Network Configuration

Tasmota devices typically:
- Connect on WiFi channel 1-11
- Use DHCP (check StatusNET for current IP)
- May respond to mDNS (hostname patterns: tasmota-XXXXXX)
- Use HTTP on port 80 (standard)

## Best Practices

- Scan during network maintenance windows (avoid peak usage)
- Cache inventory file to avoid repeated scans
- Use device friendly names for easier identification
- Set static IPs for critical devices (via Tasmota web UI or DHCP reservations)
- Group devices by location/function in inventory comments

## Resources

### scripts/tasmota-discovery.py
Network scanner that finds live hosts and identifies Tasmota devices via HTTP and JSON API.

### scripts/tasmota-control.py
Device controller supporting power, brightness, color, and status queries via Tasmota JSON API.

### scripts/tasmota-status.py
Bulk status checker that queries all devices in inventory and displays power states.