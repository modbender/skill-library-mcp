# RWC Protocol v0.1 (Draft)

> Status: Draft | 2026-02-22  
> Breaking changes expected before v1.0

## Overview

The RWC Protocol defines how AI agents discover, communicate with, and control physical modules through the RealWorldClaw platform.

## Module Discovery

Each module exposes a **manifest** via the RWC Bus ID pin:

```yaml
# manifest.yaml
module:
  id: "rwc-temp-humidity-v1"
  name: "Temperature & Humidity Sensor"
  version: "0.1.0"
  type: "sensor"  # sensor | actuator | display | compute
  bus_version: "0.1"
  
capabilities:
  - id: "temperature"
    type: "read"
    unit: "celsius"
    range: [-40, 80]
    interval_ms: 1000
    
  - id: "humidity"
    type: "read"
    unit: "percent"
    range: [0, 100]
    interval_ms: 1000

requirements:
  power: "3.3V"
  current_max_ma: 20
  
metadata:
  author: "RealWorldClaw"
  license: "Apache-2.0"
  bom_cost_usd: 3.50
```

## Capability Schema

```json
{
  "type": "object",
  "properties": {
    "id": { "type": "string", "pattern": "^[a-z][a-z0-9-]*$" },
    "type": { "enum": ["read", "write", "read-write"] },
    "unit": { "type": "string" },
    "range": { "type": "array", "items": { "type": "number" }, "minItems": 2, "maxItems": 2 },
    "interval_ms": { "type": "integer", "minimum": 100 },
    "permissions": { "enum": ["public", "authenticated", "admin"] }
  },
  "required": ["id", "type"]
}
```

## Command Format

### Read (Telemetry)
```json
{
  "type": "telemetry",
  "module_id": "rwc-temp-humidity-v1",
  "capability": "temperature",
  "value": 22.4,
  "unit": "celsius",
  "timestamp": "2026-02-22T08:30:00Z"
}
```

### Write (Command)
```json
{
  "type": "command",
  "module_id": "rwc-relay-v1",
  "capability": "switch",
  "action": "set",
  "value": true,
  "source": {
    "agent_id": "ai_23a85fe272cf6271",
    "reason": "Temperature exceeded 28°C threshold"
  }
}
```

### Response
```json
{
  "type": "response",
  "command_id": "cmd_abc123",
  "status": "ok",
  "module_id": "rwc-relay-v1",
  "capability": "switch",
  "value": true,
  "timestamp": "2026-02-22T08:30:01Z"
}
```

## RWC Bus Pin Assignment (v0.1)

8-pin magnetic Pogo connector:

| Pin | Signal | Description |
|-----|--------|-------------|
| 1 | 5V | Power supply |
| 2 | 3V3 | 3.3V regulated |
| 3 | GND | Ground |
| 4 | SDA | I²C Data |
| 5 | SCL | I²C Clock |
| 6 | TX/MOSI | UART TX or SPI MOSI |
| 7 | RX/MISO | UART RX or SPI MISO |
| 8 | ID | Module identification (1-Wire) |

## Version Compatibility

- Protocol version in manifest must match hub's supported range
- Hub maintains a compatibility table: `{min_version, max_version}`
- Modules outside range are detected but disabled with user notification

## Security (Planned)

- Commands from cloud require agent authentication
- High-risk actions (actuators) require explicit permission grant
- Local safety rules can override cloud commands
- All commands logged with agent ID, timestamp, result
