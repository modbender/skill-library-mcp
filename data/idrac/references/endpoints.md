# iDRAC Redfish API Endpoint Reference

All examples use the helper script's `api_get` pattern. For raw curl:
```bash
curl -k -s -u "$(cat "$CREDS_FILE")" "https://${IDRAC_IP}/redfish/v1${ENDPOINT}"
```

## Table of Contents

- [System Information](#system-information)
- [Thermal & Power](#thermal--power)
- [Storage](#storage)
- [Network](#network)
- [Logs & Events](#logs--events)
- [Managers (iDRAC itself)](#managers-idrac-itself)
- [BIOS Settings](#bios-settings)
- [Firmware Inventory](#firmware-inventory)
- [Dell OEM Attributes](#dell-oem-attributes)
- [Session-Based Authentication](#session-based-authentication)
- [Power Operations](#power-operations)

---

## System Information

```bash
# Root service
api_get "/" | jq

# Systems collection
api_get "/Systems" | jq

# Main system
api_get "/Systems/System.Embedded.1" | jq

# Quick summary
api_get "/Systems/System.Embedded.1" | \
  jq '{Model, Manufacturer, SerialNumber, PowerState, ProcessorSummary, MemorySummary}'
```

## Thermal & Power

```bash
# Thermal (temps, fans)
api_get "/Chassis/System.Embedded.1/Thermal" | jq

# Power (supplies, voltage, consumption)
api_get "/Chassis/System.Embedded.1/Power" | jq

# Current power consumption
api_get "/Chassis/System.Embedded.1/Power" | \
  jq '.PowerControl[0].PowerConsumedWatts'
```

## Storage

```bash
# Storage controllers
api_get "/Systems/System.Embedded.1/Storage" | jq

# Specific controller (e.g., RAID.Integrated.1-1)
api_get "/Systems/System.Embedded.1/Storage/RAID.Integrated.1-1" | jq

# Physical disks
api_get "/Systems/System.Embedded.1/Storage/RAID.Integrated.1-1" | \
  jq '.Drives[]'
```

## Network

```bash
# Network adapters
api_get "/Systems/System.Embedded.1/NetworkAdapters" | jq

# Network interfaces
api_get "/Systems/System.Embedded.1/EthernetInterfaces" | jq
```

## Logs & Events

```bash
# System Event Log (SEL)
api_get "/Managers/iDRAC.Embedded.1/Logs/Sel" | jq

# Lifecycle Controller Log (LCLog)
api_get "/Managers/iDRAC.Embedded.1/Logs/Lclog" | jq
```

## Managers (iDRAC itself)

```bash
# iDRAC manager info
api_get "/Managers/iDRAC.Embedded.1" | jq

# iDRAC firmware version
api_get "/Managers/iDRAC.Embedded.1" | \
  jq '{Firmware: .FirmwareVersion, Model: .Model, Status: .Status}'
```

## BIOS Settings

```bash
# BIOS configuration
api_get "/Systems/System.Embedded.1/Bios" | jq

# Pending BIOS changes
api_get "/Systems/System.Embedded.1/Bios/Settings" | jq
```

## Firmware Inventory

```bash
# All firmware versions (BIOS, iDRAC, NICs, RAID, etc.)
api_get "/UpdateService/FirmwareInventory" | jq

# Filter by component name
api_get "/UpdateService/FirmwareInventory" | \
  jq '.Members[] | select(.Name | contains("BIOS"))'
```

## Dell OEM Attributes

```bash
# Dell-specific attributes (boot state, POST codes, etc.)
api_get "/Managers/iDRAC.Embedded.1/Attributes" | jq

# System boot progress
api_get "/Managers/iDRAC.Embedded.1/Attributes" | \
  jq '.Attributes | with_entries(select(.key | contains("ServerBoot")))'
```

## Session-Based Authentication

For multiple API calls, session tokens are more efficient than Basic Auth per-request:

```bash
# Create session (returns X-Auth-Token in headers)
SESSION_RESPONSE=$(curl -k -i -X POST \
  -H "Content-Type: application/json" \
  -d "{\"UserName\":\"${IDRAC_USER}\",\"Password\":\"${IDRAC_PASS}\"}" \
  "https://${IDRAC_IP}/redfish/v1/SessionService/Sessions")

# Extract session token
SESSION_TOKEN=$(echo "$SESSION_RESPONSE" | grep -i "X-Auth-Token:" | awk '{print $2}' | tr -d '\r')

# Use session token for subsequent calls
curl -k -H "X-Auth-Token: $SESSION_TOKEN" \
  "https://${IDRAC_IP}/redfish/v1/Systems/System.Embedded.1" | jq

# Delete session when done
SESSION_URI=$(echo "$SESSION_RESPONSE" | grep -i "Location:" | awk '{print $2}' | tr -d '\r')
curl -k -X DELETE -H "X-Auth-Token: $SESSION_TOKEN" "${SESSION_URI}"
```

## Power Operations

```bash
# Power state
api_get "/Systems/System.Embedded.1" | jq -r '.PowerState'

# Power on (if off)
curl -k -s -u "$(cat "$CREDS_FILE")" \
  -X POST -H "Content-Type: application/json" \
  -d '{"ResetType":"On"}' \
  "https://${IDRAC_IP}/redfish/v1/Systems/System.Embedded.1/Actions/ComputerSystem.Reset"

# Graceful shutdown
curl -k -s -u "$(cat "$CREDS_FILE")" \
  -X POST -H "Content-Type: application/json" \
  -d '{"ResetType":"GracefulShutdown"}' \
  "https://${IDRAC_IP}/redfish/v1/Systems/System.Embedded.1/Actions/ComputerSystem.Reset"

# Force restart
curl -k -s -u "$(cat "$CREDS_FILE")" \
  -X POST -H "Content-Type: application/json" \
  -d '{"ResetType":"ForceRestart"}' \
  "https://${IDRAC_IP}/redfish/v1/Systems/System.Embedded.1/Actions/ComputerSystem.Reset"

# Available reset types
api_get "/Systems/System.Embedded.1" | \
  jq '.Actions."#ComputerSystem.Reset"."ResetType@Redfish.AllowableValues"'
```

## Common Queries

```bash
# Is the server healthy?
api_get "/Systems/System.Embedded.1" | \
  jq '{Health: .Status.Health, State: .Status.State, PowerState}'

# CPU/Memory summary
api_get "/Systems/System.Embedded.1" | \
  jq '{Processors: .ProcessorSummary, Memory: .MemorySummary}'

# Current temperatures
api_get "/Chassis/System.Embedded.1/Thermal" | \
  jq '.Temperatures[] | {Name, ReadingCelsius, Status}'

# Fan speeds
api_get "/Chassis/System.Embedded.1/Thermal" | \
  jq '.Fans[] | {Name, Reading, Units, Status}'
```

## Compatibility

| iDRAC Version | Redfish | Notes |
|---------------|---------|-------|
| iDRAC 8 (v2.40+) | 1.0–1.4 | R630/R730/R930 era. OEM Dell extensions. |
| iDRAC 9 (v3.x+) | 1.6+ | R640/R740/R940 era. Richer Redfish, Telemetry support. |

Most endpoints above work on both. iDRAC 9 adds:
- `/redfish/v1/TelemetryService` — streaming metrics
- Expanded `/Managers/iDRAC.Embedded.1/Oem/Dell/` namespace
- SSE (Server-Sent Events) for real-time alerts

## References

- [DMTF Redfish Specification](https://www.dmtf.org/standards/redfish)
- [Dell iDRAC Redfish Scripting (GitHub)](https://github.com/dell/iDRAC-Redfish-Scripting)
