---
name: starling-home-hub
description: Controls Nest and Google Home smart home devices via the Starling Home Hub's local REST API. Supports thermostats, cameras, Nest Protects, Nest × Yale locks, temperature sensors, home/away control, and Nest weather service. Use this skill when managing Nest/Google Home devices through Starling Home Hub — reading device status, setting temperatures, getting camera snapshots, locking/unlocking doors, checking smoke/CO alerts, and toggling home/away mode.
homepage: https://starlinghome.io
env:
  - name: STARLING_HUB_IP
    required: true
    secret: false
    description: Local IP address of your Starling Home Hub (e.g. 192.168.1.151)
  - name: STARLING_API_KEY
    required: true
    secret: true
    description: API key from the Starling Home Hub app (Developer Connect section)
---

# Starling Home Hub (Nest/Google Home)

> **Community skill — not affiliated with or endorsed by Starling LLC, Google, Nest, or Apple.** Nest is a trademark of Google LLC. Starling Home Hub is a product of Starling LLC. This skill requires a [Starling Home Hub](https://starlinghome.io) with firmware 8.0+ and the Developer Connect API enabled.

## Overview

Control Nest smart home devices through the Starling Home Hub Developer Connect (SDC) local REST API using the `starling.sh` script.

## Required Environment Variables

| Variable | Required | Secret | Description |
|----------|----------|--------|-------------|
| `STARLING_HUB_IP` | **Yes** | No | Local IP address of your Starling Home Hub (e.g. `192.168.1.151`) |
| `STARLING_API_KEY` | **Yes** | **Yes** | API key created in the Starling Home Hub app (Developer Connect section) |

## Setup

Set these environment variables (never hardcode keys in scripts):

```bash
export STARLING_HUB_IP="192.168.1.xxx"
export STARLING_API_KEY="your-api-key"     # From Starling Home Hub app
```

The script is at: `scripts/starling.sh`

Options: `--http` (downgrade to HTTP — not recommended), `--raw` (skip jq formatting)

**HTTPS is the default.** The script uses port 3443 unless `--http` is specified.

## Security

### API Key Management
- **Always use the `STARLING_API_KEY` env var** — never pass keys via `--key` (visible in `ps` output)
- Never store keys in scripts, SKILL.md, or version-controlled files
- Use a `.env` file with restricted permissions: `chmod 600 .env`
- Consider a secrets manager for production/automated setups

### Least Privilege
- Create API keys with minimum required permissions in the Starling Home Hub app
- Use **read-only keys** unless you need to set properties or access camera streams
- Create separate keys for different automation tasks if possible

### TLS Certificate Verification
- HTTPS is the default, but the script uses `curl -k` (skip cert verification) because Starling Home Hub uses a self-signed certificate
- This is acceptable on a **trusted local network** but increases MITM risk on untrusted networks
- To pin the hub's certificate instead: `starling.sh --cacert /path/to/hub-cert.pem status`
- When `--cacert` is provided, `-k` is not used and full certificate verification applies

### API Key in URL
- The Starling Developer Connect API requires the key as a URL query parameter (`?key=...`) — this is the API's design, not a skill choice
- URL query parameters can appear in access logs and browser history — this is mitigated by the API being local-only (no intermediary proxies/CDNs)
- Always use HTTPS to encrypt the key in transit on your local network

### Network Security
- The Starling API is **local network only** by design — no cloud exposure
- **Never port-forward** 3080 or 3443 to the internet
- Always use HTTPS (default) to prevent local network sniffing of API keys and device data

### Snapshot Handling
- Camera snapshots contain sensitive imagery — don't store in world-readable locations
- The script sets snapshot files to `chmod 600` (owner-only) automatically
- Clean up temporary snapshot files when no longer needed

## Best Practices

### Always Check Status First
Before making device calls, verify the hub is ready:
```bash
scripts/starling.sh status
```
Confirm `apiReady: true` and `connectedToNest: true` before proceeding.

### Respect Rate Limits
These limits are enforced by the Nest cloud:
- **POST** (set properties): **max once per second** per device
- **Snapshot**: **max once per 10 seconds** per camera
- **GET** (read properties/device list): no cloud rate limit (local cache)

### Idempotent Operations
Safe to retry without side effects:
- All GET operations (status, devices, device, get, snapshot)
- SET operations with the same values (setting temp to 22 when already 22)
- stream-extend (just resets the keepalive timer)

**Not idempotent:** stream-start (creates a new stream each time)

### Error Handling
The script provides actionable error messages:
- **401**: Check API key and permissions — key is never exposed in error output
- **404**: Verify device ID and property name
- **400**: Check parameter values and types

## Common Workflows

### List All Devices
```bash
scripts/starling.sh devices
```

### Read Device Properties
```bash
scripts/starling.sh device <id>          # All properties
scripts/starling.sh get <id> <property>  # Single property
```

### Set Device Properties
```bash
scripts/starling.sh set <id> key=value [key=value...]
```

### Camera Snapshots
```bash
scripts/starling.sh snapshot <id> --output photo.jpg --width 1280
```

### Camera Streaming (WebRTC)
```bash
scripts/starling.sh stream-start <id> <base64-sdp-offer>
scripts/starling.sh stream-extend <id> <stream-id>   # Every 60s
scripts/starling.sh stream-stop <id> <stream-id>
```

## Common Tasks

**Set thermostat to 22°C:**
```bash
scripts/starling.sh set <thermostat-id> targetTemperature=22
```

**Set HVAC mode:**
```bash
scripts/starling.sh set <thermostat-id> hvacMode=heat
```

**Check for motion on camera:**
```bash
scripts/starling.sh get <camera-id> motionDetected
```

**Lock/unlock a door:**
```bash
scripts/starling.sh set <lock-id> targetState=locked
```

**Get camera snapshot:**
```bash
scripts/starling.sh snapshot <camera-id> --output front-door.jpg
```

**Check smoke/CO status:**
```bash
scripts/starling.sh get <protect-id> smokeDetected
scripts/starling.sh get <protect-id> coDetected
```

**Set home/away:**
```bash
scripts/starling.sh set <home-away-id> homeState=away
```

## API Reference

See `references/api-reference.md` for full device property details, writable properties, error codes, and endpoint documentation.
