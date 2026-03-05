---
name: nest-sdm
description: Control Nest thermostat, doorbell, and cameras via the Google Smart Device Management (SDM) API.
metadata:
  openclaw:
    emoji: "🏠"
    requires:
      bins: ["curl", "python3"]
---

# Nest SDM Skill

Control and monitor Google Nest devices via the Smart Device Management REST API.

## Setup

### Prerequisites

1. **Device Access Console** — Register at https://console.nest.google.com/device-access ($5 one-time fee)
2. **GCP Project** — Create at https://console.cloud.google.com with SDM API enabled
3. **OAuth Client** — Web application type with `https://www.google.com` as redirect URI
4. **SDM scope** — Add `https://www.googleapis.com/auth/sdm.service` to OAuth consent screen

### First-time Authorization

1. Build the authorization URL:
```
https://nestservices.google.com/partnerconnections/<PROJECT_ID>/auth?redirect_uri=https://www.google.com&access_type=offline&prompt=consent&client_id=<CLIENT_ID>&response_type=code&scope=https://www.googleapis.com/auth/sdm.service
```

2. Open in browser, sign in as the **device owner** Google account
3. Enable ALL device permissions, click Next, then Continue through consent
4. Copy the `code=` parameter from the redirect URL
5. Exchange for tokens:
```bash
curl -s -X POST https://oauth2.googleapis.com/token \
  -d "client_id=<CLIENT_ID>" \
  -d "client_secret=<CLIENT_SECRET>" \
  -d "code=<AUTH_CODE>" \
  -d "grant_type=authorization_code" \
  -d "redirect_uri=https://www.google.com"
```

6. Save tokens to the config file (see Configuration below)

### Configuration

Create `~/.openclaw/workspace/.nest-sdm-tokens.json`:
```json
{
  "client_id": "<your-client-id>",
  "client_secret": "<your-client-secret>",
  "project_id": "<device-access-project-id>",
  "refresh_token": "<your-refresh-token>",
  "token_type": "Bearer",
  "scope": "https://www.googleapis.com/auth/sdm.service"
}
```
Secure it: `chmod 600 ~/.openclaw/workspace/.nest-sdm-tokens.json`

## CLI Usage

```bash
# Alias for convenience
alias nest="<skill-dir>/nest-sdm.sh"
```

### Device Discovery
```bash
nest devices                    # List all devices (JSON)
nest structures                 # List structures/rooms
```

### Thermostat
```bash
nest thermostat                 # Current status (temp, humidity, mode, setpoints)
nest set-cool <°F>              # Set to COOL mode at temperature
nest set-heat <°F>              # Set to HEAT mode at temperature
nest set-range <low°F> <high°F> # Set HEATCOOL range
nest set-mode <MODE>            # HEAT | COOL | HEATCOOL | OFF
nest set-eco <MODE>             # MANUAL_ECO | OFF
nest fan-on [duration_seconds]  # Turn fan on (default: 900s / 15min)
nest fan-off                    # Turn fan off
```

### Doorbell & Cameras
```bash
nest doorbell                   # Doorbell info & capabilities
nest display                    # Kitchen display info
nest camera-stream <DEVICE_ID>  # Generate WebRTC live stream (returns SDP answer)
nest camera-image <EVENT_ID>    # Get event snapshot URL
```

### Raw API
```bash
nest api GET devices                              # Raw device list
nest api GET devices/<DEVICE_ID>                  # Single device
nest api POST devices/<DEVICE_ID>:executeCommand '{"command":"...","params":{...}}'
```

## Supported Devices

| Type | Traits | Control |
|------|--------|---------|
| THERMOSTAT | Temperature, Humidity, Mode, Eco, Fan, HVAC, Setpoint, Connectivity | Full read/write |
| DOORBELL | LiveStream, CameraImage, Person, Motion, Chime, EventImage, ClipPreview | Read + stream |
| DISPLAY | LiveStream, CameraImage, Person, Sound, Motion, EventImage | Read + stream |

## SDM API Commands Reference

### Thermostat Commands
| Command | Params |
|---------|--------|
| `ThermostatMode.SetMode` | `{"mode": "HEAT\|COOL\|HEATCOOL\|OFF"}` |
| `ThermostatTemperatureSetpoint.SetHeat` | `{"heatCelsius": <float>}` |
| `ThermostatTemperatureSetpoint.SetCool` | `{"coolCelsius": <float>}` |
| `ThermostatTemperatureSetpoint.SetRange` | `{"heatCelsius": <float>, "coolCelsius": <float>}` |
| `ThermostatEco.SetMode` | `{"mode": "MANUAL_ECO\|OFF"}` |
| `Fan.SetTimer` | `{"timerMode": "ON", "duration": "<seconds>s"}` |

### Camera Commands
| Command | Params |
|---------|--------|
| `CameraLiveStream.GenerateWebRtcStream` | `{"offerSdp": "<SDP offer>"}` |
| `CameraLiveStream.StopWebRtcStream` | `{"mediaSessionId": "<id>"}` |
| `CameraLiveStream.ExtendWebRtcStream` | `{"mediaSessionId": "<id>"}` |
| `CameraEventImage.GenerateImage` | `{"eventId": "<event-id>"}` |

## Pub/Sub Real-Time Events

Get instant alerts for doorbell presses, motion, person detection, and device state changes.

### CLI: `nest-events`

```bash
nest-events setup-check         # Verify Pub/Sub config is ready
nest-events create-topic        # Create GCP Pub/Sub topic
nest-events grant-permissions   # Grant SDM publisher role
nest-events create-subscription # Create pull subscription
nest-events poll                # Pull events once
nest-events listen              # Poll continuously (daemon)
```

### Setup Steps

1. **OAuth with Pub/Sub scope** — Run OAuth flow as your-email@example.com with `pubsub` + `cloud-platform` scopes. Save tokens to `.nest-pubsub-tokens.json`.
2. **Create topic** — `nest-events create-topic` (creates `projects/YOUR_GCP_PROJECT/topics/nest-sdm-events`)
3. **Grant permissions** — `nest-events grant-permissions` (adds `sdm-publisher@googlegroups.com`)
4. **Create subscription** — `nest-events create-subscription`
5. **Enable in Device Access Console** — https://console.nest.google.com/device-access → Enable Pub/Sub → Enter topic ID
6. **Trigger initial events** — `nest devices` (one-time API call)
7. **Start listener** — `nest-events listen`

### Event Types Supported

| Event | Alert |
|-------|-------|
| `DoorbellChime.Chime` | 🔔 DOORBELL — Someone rang! |
| `CameraPerson.Person` | 👤 Person detected at device |
| `CameraMotion.Motion` | 🏃 Motion at device |
| `CameraSound.Sound` | 🔊 Sound at device |
| `ThermostatHvac` status change | ❄️/🔥 HVAC now COOLING/HEATING |
| `ThermostatTemperatureSetpoint` | 🌡️ Setpoint changed |
| `Temperature` trait | 🌡️ Ambient temperature change |

### Configuration

**Environment Variables:**
| Variable | Description | Default |
|----------|-------------|---------|
| `NEST_PUBSUB_TOKENS` | Path to Pub/Sub OAuth tokens | `~/.openclaw/workspace/.nest-pubsub-tokens.json` |
| `TELEGRAM_BOT_TOKEN` | Bot token for alerts | from `~/.zshenv` |
| `TELEGRAM_CHAT_ID` | User/chat ID for alerts | from `~/.zshenv` |
| `POLL_INTERVAL` | Seconds between polls | 10 |
| `GCP_PROJECT` | GCP project ID | `YOUR_GCP_PROJECT` |
| `PUBSUB_TOPIC` | Topic name | `nest-sdm-events` |
| `PUBSUB_SUBSCRIPTION` | Subscription name | `nest-sdm-events-sub` |

### Event Logs

Raw events are logged to `data/nest-events/events-YYYY-MM-DD.jsonl`.

### Alert Dedup

Same event type won't re-alert within 60 seconds to prevent alert fatigue.

## Important Notes

- **Token expiry:** If the GCP app is in "testing" mode, refresh tokens expire in 7 days. Publish the app to avoid re-auth.
- **Temperature:** API uses Celsius internally. The CLI handles F↔C conversion.
- **Setpoint constraints:** HEATCOOL range must have at least 1.5°C (2.7°F) gap between heat and cool setpoints.
- **Camera streams:** WebRTC only (no RTSP). Requires SDP offer/answer exchange.
- **Rate limits:** 10 queries/min per device, 10 commands/min per device.
- **Events:** Use `nest-events listen` for real-time alerts. Requires Pub/Sub setup (see above).
