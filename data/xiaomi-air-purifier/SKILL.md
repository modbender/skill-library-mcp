---
name: xiaomi-air-purifier
description: Monitor and control Xiaomi Air Purifier 4 Lite via Mi Cloud. Use when asked to check air quality, humidity, purifier status, turn on/off the air purifier, or change fan mode/level. Supports multi-room setups.
---

# Xiaomi Air Purifier Control

Control and monitor Xiaomi Air Purifier 4 Lite (`zhimi.airp.rmb1`) via Xiaomi Cloud API. Supports multiple devices and room-based targeting.

## Setup

1. Install dependencies:
```bash
cd xiaomi-air-purifier && pnpm install
```

2. Login to Mi Cloud (OTP will be sent via SMS/Email):
```bash
pnpm exec xmihome login -u <email/phone> -p <password> -c <country>
```
Supported countries: `sg`, `ru`, `us`, `cn`

3. List devices to verify discovery:
```bash
node scripts/purifier.js devices
```

## Usage

Commands can be targeted by **Room Name**, **Device Name**, or **DID**. If no target is provided, it uses the selected default or the only available device.

```bash
node scripts/purifier.js status [room]      # Check status (e.g., status Bedroom)
node scripts/purifier.js status-full [room] # Show full status (incl. filter)
node scripts/purifier.js on [room]          # Power on
node scripts/purifier.js off [room]         # Power off
node scripts/purifier.js mode <0-2> [room]  # 0=Auto, 1=Sleep, 2=Favorite
node scripts/purifier.js level <0-14> [room]# Fan speed (Favorite mode)
node scripts/purifier.js brightness <0-2> [room]
node scripts/purifier.js buzzer <on|off> [room]
node scripts/purifier.js lock <on|off> [room]
```

## Quick Reference

| Property | siid | piid | Type | Description |
|----------|------|------|------|-------------|
| Power | 2 | 1 | bool | On/Off |
| Mode | 2 | 4 | int | 0=Auto, 1=Sleep, 2=Favorite |
| Humidity | 3 | 1 | int | Relative humidity (%) |
| PM2.5 | 3 | 4 | int | Air quality (μg/m³) |
| Temperature | 3 | 7 | float | Temperature (°C) |
| Filter Life | 4 | 1 | int | Filter remaining (%) |
| Buzzer | 6 | 1 | bool | Notification sound on/off |
| Child Lock | 8 | 1 | bool | Physical button lock |
| Fan Level | 9 | 11 | int | 0-14 (Favorite mode) |
| Brightness | 13 | 2 | int | 0=Off, 1=Dim, 2=On |
