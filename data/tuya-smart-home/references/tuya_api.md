# Tuya Smart Home API Reference

## Tuya IoT Platform Setup

1. Register at https://iot.tuya.com
2. Create Cloud Project → choose **Smart Home** industry
3. Select Data Center matching your Smart Life app region
4. Subscribe free API services: **IoT Core**, **Smart Home Device Control**
5. Link your Smart Life app account: **Devices** → **Link Tuya App Account** → scan QR code

## API Endpoints

| Region | Endpoint |
|--------|----------|
| China | `https://openapi.tuyacn.com` |
| Western Americas / SEA | `https://openapi.tuyaus.com` |
| Europe | `https://openapi.tuyaeu.com` |
| India | `https://openapi.tuyain.com` |

## Authentication

```python
from tuya_connector import TuyaOpenAPI

api = TuyaOpenAPI(endpoint, access_id, access_secret)
api.connect()  # Returns access_token (valid 2h, auto-refreshed)
```

## Common API Calls

### Get Device Info (includes local_key)

```
GET /v1.0/devices/{device_id}
```

Response fields: `id`, `name`, `local_key`, `ip`, `online`, `status[]`, `model`, `product_name`

### Get Device Status

```
GET /v1.0/devices/{device_id}/status
```

Returns array of `{code, value}` pairs.

### Send Command

```
POST /v1.0/devices/{device_id}/commands
Body: {"commands": [{"code": "manual_feed", "value": 1}]}
```

### List User Devices

```
GET /v1.0/iot-01/associated-users/devices?last_row_key=
```

## Device DP Code Reference

### Pet Feeder (cwwsq)

| DP ID | Code | Type | Values | Description |
|-------|------|------|--------|-------------|
| - | meal_plan | Raw | Base64 | Feeding schedule (5 bytes per meal: 0x7f, hour, minute, portions, enabled) |
| - | quick_feed | Boolean | true/false | One-tap feed |
| 3 | manual_feed | Integer | 1-12 | Feed N portions |
| 4 | feed_state | Enum | standby/feeding | Current state |
| 10 | battery_percentage | Integer | 0-100 | Battery level |
| - | charge_state | Boolean | true/false | Charging status |
| - | feed_report | Integer | - | Last feed portion count |
| 17 | light | Boolean | true/false | Night light |
| - | factory_reset | Boolean | true/false | Factory reset |

#### Meal Plan Decoding

```python
import base64

data = base64.b64decode(meal_plan_value)
# Each meal is 5 bytes: [0x7f, hour, minute, portions, enabled]
meals = []
for i in range(0, len(data), 5):
    if i + 4 < len(data) and data[i] == 0x7f:
        meals.append({
            'hour': data[i+1],
            'minute': data[i+2],
            'portions': data[i+3],
            'enabled': bool(data[i+4])
        })
```

### Smart Light Bulb (dj / light)

| Code | Type | Values | Description |
|------|------|--------|-------------|
| switch_led | Boolean | true/false | On/off |
| work_mode | Enum | white/colour/scene/music | Mode |
| bright_value | Integer | 10-1000 | Brightness |
| temp_value | Integer | 0-1000 | Color temperature (warm→cool) |
| colour_data | String | HSV JSON | Color in HSV format |

### Smart Plug (cz / plug)

| Code | Type | Values | Description |
|------|------|--------|-------------|
| switch_1 | Boolean | true/false | On/off (main) |
| switch_2 | Boolean | true/false | On/off (if multi-gang) |
| countdown_1 | Integer | 0-86400 | Auto-off timer (seconds) |
| cur_current | Integer | mA | Current draw |
| cur_power | Integer | W×10 | Power consumption |
| cur_voltage | Integer | V×10 | Voltage |

### Smart Curtain Motor (cl / curtain)

| Code | Type | Values | Description |
|------|------|--------|-------------|
| control | Enum | open/stop/close | Movement control |
| percent_control | Integer | 0-100 | Position percentage |
| percent_state | Integer | 0-100 | Current position |
| work_state | Enum | opening/closing/stop | Current state |

## Local Control with tinytuya

### Requirements

- Device ID (from Tuya cloud or device scan)
- Local Key (from cloud API `GET /v1.0/devices/{id}` → `local_key`)
- Device IP (from network scan)
- Protocol version (usually 3.4)

### Usage

```python
import tinytuya

# Connect
d = tinytuya.Device(device_id, ip, local_key, version=3.4)
d.set_socketTimeout(5)

# Read status
status = d.status()  # {'dps': {'3': 1, '4': 'standby', '10': 100, '17': true}}

# Send command (use DP ID numbers, not code names)
d.set_value(3, 1)      # manual_feed = 1 portion
d.set_value(17, False)  # light off
```

### Network Scan

```python
import tinytuya
devices = tinytuya.deviceScan(verbose=True)
# Returns dict: {ip: {gwId, productKey, version, ...}}
```

## China Region Cross-Region Access

China data center blocks non-China IP addresses by default.

**Solution 1: IP Whitelist**
1. Go to Tuya IoT Platform → Project → Overview
2. Find "IP Whitelist" / "云授权 IP 白名单"
3. Add your server's public IP

**Solution 2: Local Control (Recommended)**
Use tinytuya with Local Key — bypasses cloud entirely:
- No region restrictions
- No API quotas
- Works offline
- Zero latency
- Free forever

**Obtaining Local Key:**
1. Set up cloud project (any region that works)
2. Link Smart Life app account
3. Call `GET /v1.0/devices/{device_id}` → extract `local_key`
4. Use local_key with tinytuya for all future control
