# Starling Home Hub Developer Connect API Reference

## Base URL

- HTTP: `http://<HUB_IP>:3080/api/connect/v1/`
- HTTPS: `https://<HUB_IP>:3443/api/connect/v1/`

Authentication: `?key=<API_KEY>` query parameter on all requests.

All successful responses include `"status": "OK"`.

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/status` | Hub status, API version, connection state, app permissions |
| GET | `/devices` | List all Nest devices |
| GET | `/devices/{id}` | All properties of a device |
| GET | `/devices/{id}/{property}` | Single property value |
| GET | `/devices/{id}/snapshot?width=N` | Camera snapshot (JPEG). Width max 1280, default 640. Rate limit: 1/10s |
| POST | `/devices/{id}` | Set device properties (JSON body). Rate limit: 1/s |
| POST | `/devices/{id}/stream` | Start WebRTC stream. Body: `{"offer": "<base64 SDP>"}`. Returns `answer` + `streamId` |
| POST | `/devices/{id}/stream/{sid}/extend` | Keep stream alive (call every 60s, timeout 2min) |
| POST | `/devices/{id}/stream/{sid}/stop` | Stop camera stream |

## Device Types

All devices share: `type`, `id`, `where`, `name`, `serialNumber`, `structureName`

### Thermostat

| Property | Type | Writable | Notes |
|----------|------|----------|-------|
| currentTemperature | float (°C) | No | |
| backplateTemperature | float (°C) | No | |
| humidityPercent | int | No | |
| targetTemperature | float (°C) | **Yes** | |
| hvacMode | string | **Yes** | "off", "heat", "cool", "heatCool" |
| targetHeatingThresholdTemperature | float (°C) | **Yes** | For heatCool mode |
| targetCoolingThresholdTemperature | float (°C) | **Yes** | For heatCool mode |
| displayTemperatureUnits | string | **Yes** | "C" or "F" |
| ecoMode | bool | **Yes** | |
| fanRunning | bool | **Yes** | |
| hotWaterEnabled | bool | **Yes** | |
| humidifierActive | bool | **Yes** | |
| targetHumidity | int (%) | **Yes** | |
| hvacState | string | No | "off", "heating", "cooling" |
| canHeat | bool | No | |
| canCool | bool | No | |
| batteryStatus | string | No | |
| sensorSelected | string | **Yes** | |
| presetSelected | string | **Yes** | |
| tempHoldMode | string | **Yes** | |
| currentHumidifierState | string | No | "off", "idle", "humidifying", "dehumidifying" |

### Temperature Sensor

| Property | Type | Writable |
|----------|------|----------|
| batteryStatus | string | No |
| currentTemperature | float (°C) | No |

### Protect (Smoke/CO Detector)

| Property | Type | Writable | Notes |
|----------|------|----------|-------|
| batteryStatus | string | No | |
| coDetected | bool | No | |
| coStateDetail | string | No | "ok", "warn", "emergency" |
| smokeDetected | bool | No | |
| smokeStateDetail | string | No | "ok", "warn", "emergency" |
| manualTestActive | bool | No | |
| occupancyDetected | bool | No | |

### Camera

| Property | Type | Writable | Notes |
|----------|------|----------|-------|
| cameraEnabled | bool | **Yes** | |
| chimeEnabled | bool | **Yes** | Doorbell only |
| floodlightOn | bool | **Yes** | Floodlight cams only |
| motionDetected | bool | No | |
| personDetected | bool | No | |
| animalDetected | bool | No | |
| vehicleDetected | bool | No | |
| doorbellPushed | bool | No | |
| soundDetected | bool | No | |
| packageDelivered | bool | No | |
| packageRetrieved | bool | No | |
| faceDetected:name | string | No | |
| zoneActivityDetected:name | string | No | |
| garageDoorState | string | No | |
| batteryLevel | int | No | |
| batteryStatus | string | No | |
| batteryIsCharging | bool | No | |
| runningOnBattery | bool | No | |
| trickleCharging | bool | No | |
| cameraModel | string | No | |
| supportsStreaming | bool | No | |

### Nest × Yale Lock

| Property | Type | Writable | Notes |
|----------|------|----------|-------|
| targetState | string | **Yes** | "unlocked", "locked" |
| autoRelockEnabled | bool | **Yes** | |
| oneTouchLockEnabled | bool | **Yes** | |
| privacyModeEnabled | bool | **Yes** | |
| currentState | string | No | "unlocked", "locked", "jammed" |
| batteryStatus | string | No | |
| isTampered | bool | No | |
| lastLockUnlockMethod | string | No | |

### Home/Away Control

| Property | Type | Writable |
|----------|------|----------|
| homeState | string | **Yes** |

### Weather

| Property | Type | Writable |
|----------|------|----------|
| currentTemperature | float (°C) | No |
| humidityPercent | int | No |

## Error Responses

| Code | Meaning |
|------|---------|
| 400 | Bad request — missing or invalid parameters |
| 401 | Unauthorized — bad/missing API key or insufficient permissions |
| 404 | Device or property not found |
