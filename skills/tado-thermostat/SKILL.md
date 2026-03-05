---
name: tado
description: Interact with Tado smart thermostat. Use for reading temperature, setting heating with auto-revert, viewing energy usage, and controlling zones.
---

# Tado Skill

Use the Tado API to control your smart thermostat.

## Authentication

Tado uses OAuth2 device code flow. You'll need:

- **Client ID:** `1bb50063-6b0c-4d11-bd99-387f4a91cc46`
- **Token endpoint:** `https://login.tado.com/oauth2/token`

### Step 1: Get Device Code

```bash
curl -s -X POST "https://login.tado.com/oauth2/device_authorize" \
  -d "client_id=1bb50063-6b0c-4d11-bd99-387f4a91cc46" \
  -d "scope=offline_access"
```

Response:
```json
{
  "device_code": "XXX_code_XXX",
  "expires_in": 300,
  "interval": 5,
  "user_code": "7BQ5ZQ",
  "verification_uri_complete": "https://login.tado.com/oauth2/device?user_code=7BQ5ZQ"
}
```

### Step 2: User Authenticates

Visit the `verification_uri_complete` URL and enter the user code. The user must log into their Tado account.

### Step 3: Poll for Token

```bash
curl -s -X POST "https://login.tado.com/oauth2/token" \
  -d "client_id=1bb50063-6b0c-4d11-bd99-387f4a91cc46" \
  -d "device_code=YOUR_DEVICE_CODE" \
  -d "grant_type=urn:ietf:params:oauth:grant-type:device_code"
```

Response:
```json
{
  "access_token": "...",
  "refresh_token": "...",
  "expires_in": 600,
  "token_type": "Bearer"
}
```

### Step 4: Refresh Token

Access tokens expire in ~10 minutes. Use the refresh token to get a new one:

```bash
curl -s -X POST "https://login.tado.com/oauth2/token" \
  -d "client_id=1bb50063-6b0c-4d11-bd99-387f4a91cc46" \
  -d "grant_type=refresh_token" \
  -d "refresh_token=YOUR_REFRESH_TOKEN"
```

## Environment Variables

Store these securely (not in the skill):
```bash
export TADO_TOKEN="your-access-token"
export TADO_REFRESH_TOKEN="your-refresh-token"
export TADO_HOME_ID="your-home-id"
```

## Get Home ID

```bash
curl -s "https://my.tado.com/api/v2/me" -H "Authorization: Bearer $TADO_TOKEN"
```

Returns: `{"homes":[{"id":123456,...}]}`

## List Zones

```bash
curl -s "https://my.tado.com/api/v2/homes/$TADO_HOME_ID/zones" -H "Authorization: Bearer $TADO_TOKEN"
```

## Get Zone State

```bash
curl -s "https://my.tado.com/api/v2/homes/$TADO_HOME_ID/zones/$ZONE_ID/state" -H "Authorization: Bearer $TADO_TOKEN"
```

## Get All Zones Summary

This script gets the current temperature, target temperature, and heating % for all zones:

```python
#!/usr/bin/env python3
import os
import requests

TOKEN = os.environ.get("TADO_TOKEN")
HOME_ID = os.environ.get("TADO_HOME_ID")

headers = {"Authorization": f"Bearer {TOKEN}"}

# Get zones
zones = requests.get(f"https://my.tado.com/api/v2/homes/{HOME_ID}/zones", headers=headers).json()

print("Zone           | Current | Target | Heating")
print("---------------|---------|--------|-------")

for zone in zones:
    zid = zone["id"]
    name = zone["name"]
    state = requests.get(f"https://my.tado.com/api/v2/homes/{HOME_ID}/zones/{zid}/state", headers=headers).json()
    
    # Current temperature from sensorDataPoints
    current = state.get("sensorDataPoints", {}).get("insideTemperature", {}).get("celsius")
    # Target temperature from setting
    target = state.get("setting", {}).get("temperature", {}).get("celsius")
    # Actual heating % from activityDataPoints (not from setting!)
    heating = state.get("activityDataPoints", {}).get("heatingPower", {}).get("percentage", 0)
    
    c = f"{current:.1f}°C" if current else "N/A"
    t = f"{target:.0f}°C" if target else "-"
    h = f"{heating:.0f}%" if heating else "OFF"
    
    print(f"{name:14} | {c:7} | {t:6} | {h:>6}")
```

Example output:
```
Zone           | Current | Target | Heating
---------------|---------|--------|-------
Kitchen        | 18.2°C  | 18°C   | 45%
Living Room    | 16.8°C  | 17°C   | 0%
Downstairs Off | 15.2°C  | 14°C   | 78%
Master Bedroom | 17.1°C  | 14°C   | 0%
Cora's Room    | 17.7°C  | 16°C   | 23%
Upstairs Office| 19.1°C  | 19°C   | OFF
Spare Bedroom  | 19.6°C  | -      | OFF
```

**Note:** Use `activityDataPoints.heatingPower.percentage` to get actual heating status, not `setting.power` which only shows the target.

## Set Temperature

**Until next schedule change:**
```bash
curl -s -X PUT "https://my.tado.com/api/v2/homes/$TADO_HOME_ID/zones/$ZONE_ID/overlay" \
  -H "Authorization: Bearer $TADO_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"setting":{"type":"HEATING","power":"ON","temperature":{"celsius":21}},"termination":{"type":"UNTIL_NEXT_TIME_BLOCK"}}'
```

**With timer (e.g., 2 hours):**
```bash
curl -s -X PUT "https://my.tado.com/api/v2/homes/$TADO_HOME_ID/zones/$ZONE_ID/overlay" \
  -H "Authorization: Bearer $TADO_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"setting":{"type":"HEATING","power":"ON","temperature":{"celsius":22}},"termination":{"type":"TIMER","durationInSeconds":7200}}'
```

**Permanent:**
```bash
curl -s -X PUT "https://my.tado.com/api/v2/homes/$TADO_HOME_ID/zones/$ZONE_ID/overlay" \
  -H "Authorization: Bearer $TADO_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"setting":{"type":"HEATING","power":"ON","temperature":{"celsius":20}},"termination":{"type":"MANUAL"}}'
```

## Clear Override

```bash
curl -s -X DELETE "https://my.tado.com/api/v2/homes/$TADO_HOME_ID/zones/$ZONE_ID/overlay" \
  -H "Authorization: Bearer $TADO_TOKEN"
```

## Get Energy Usage

```bash
curl -s "https://my.tado.com/api/v2/homes/$TADO_HOME_ID/energyUsage" -H "Authorization: Bearer $TADO_TOKEN"
```

## Termination Types

| Type | Description |
|------|-------------|
| `UNTIL_NEXT_TIME_BLOCK` | Reverts at next scheduled change |
| `TIMER` | Temporary (max 12 hours / 43200 seconds) |
| `MANUAL` | Permanent until cancelled |
