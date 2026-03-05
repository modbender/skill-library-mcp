---
name: realworldclaw
description: "Give your AI agent physical world capabilities via RealWorldClaw — control ESP32 modules, read sensors (temperature, humidity, motion), actuate relays/servos/LEDs, and create automation rules. Use when: (1) controlling IoT/ESP32 hardware, (2) reading sensor data, (3) automating physical actions based on conditions, (4) managing RWC-compatible devices, (5) 3D printing related device control. NOT for: pure software tasks, cloud-only APIs unrelated to physical devices."
---

# RealWorldClaw — Physical World for AI Agents

Give any AI agent the ability to sense and act in the physical world.

## Setup

1. Install dependencies:
```bash
pip install httpx paho-mqtt
```

2. Configure device connection in `config.json` (skill directory):
```json
{
  "api_url": "https://realworldclaw-api.fly.dev/api/v1",
  "devices": [
    {
      "name": "my-esp32",
      "ip": "192.168.x.x",
      "access_code": "xxxxxxxx",
      "serial": "xxxxxxxxxxxx",
      "type": "esp32"
    }
  ]
}
```

## Quick Start

### Read sensor data
```bash
python3 scripts/rwc.py sense --device my-esp32
```
Returns temperature, humidity, and other connected sensor values.

### Control actuator
```bash
python3 scripts/rwc.py act --device my-esp32 --action relay_on
python3 scripts/rwc.py act --device my-esp32 --action relay_off
python3 scripts/rwc.py act --device my-esp32 --action led --value '{"r":255,"g":0,"b":0}'
```

### Create automation rule
```bash
python3 scripts/rwc.py rule add --name "cool-down" \
  --condition "temperature > 30" \
  --action "relay_on" \
  --device my-esp32
```

### List devices and status
```bash
python3 scripts/rwc.py status
python3 scripts/rwc.py devices
```

### Platform API (optional, for registered users)
```bash
python3 scripts/rwc.py api health
python3 scripts/rwc.py api modules
python3 scripts/rwc.py api register --username x --email x --password x
```

## Commands Reference

| Command | Description |
|---------|-------------|
| `status` | Show all device status |
| `devices` | List configured devices |
| `sense --device NAME` | Read all sensors from device |
| `act --device NAME --action ACTION` | Execute actuator command |
| `rule add/list/remove` | Manage automation rules |
| `api health/modules/register/login` | Platform API access |
| `monitor --device NAME --interval 5` | Continuous monitoring mode |

## Supported Hardware

- ESP32 / ESP32-C3 / ESP32-S3 with RWC firmware
- Sensors: DHT22 (temp/humidity), PIR (motion), LDR (light), soil moisture
- Actuators: Relay, Servo, LED (RGB), Buzzer
- Communication: WiFi + MQTT (local) or HTTP (cloud API)

## RWC Protocol

Devices expose capabilities via manifest. Read `references/protocol.md` for full spec.

## Architecture

```
AI Agent (OpenClaw)
    ↓ skill command
RWC Skill (this)
    ↓ MQTT (local) or HTTP (cloud)
ESP32 Module
    ↓ GPIO
Physical World (sensors/actuators)
```

Local MQTT is preferred for low latency. Cloud API for remote access.
