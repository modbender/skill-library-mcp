---
name: itsyhome-control
description: "Control and query HomeKit and Home Assistant smart home devices via the Itsyhome macOS app (https://itsyhome.app). Use when the user asks to turn devices on/off, toggle lights, set brightness/temperature/color/fan speed/blind position, lock/unlock doors, open/close garage doors, run scenes, list rooms or devices, check device state or status. Requires Itsyhome Pro running on the same Mac as the OpenClaw gateway. Trigger on any smart home control intent (lights, thermostat, locks, blinds, fans, cameras, scenes, groups)."
---

# Itsyhome Control

Itsyhome exposes a local HTTP webhook server (default port `8423`) and a URL scheme (`itsyhome://`).

**Prerequisites:** Itsyhome Pro, webhook server enabled in Settings → Webhooks.

## Core Pattern

All control and query happens via `curl http://localhost:8423/<action>/<target>`.

- Targets use `Room/Device` format or just `DeviceName`
- Spaces → `%20` in URLs
- On success: `{"success": true}` or JSON data
- On failure: `{"error": "..."}` with HTTP 4xx

## Workflow

1. **If target is ambiguous** → `curl http://localhost:8423/list/devices` to find exact names
2. **To check current state** → `curl http://localhost:8423/info/<target>`
3. **To control** → appropriate action endpoint (see references/api.md)
4. **Confirm to user** with what was done; include state if queried

## Quick Reference

```bash
# Status
curl http://localhost:8423/status

# List
curl http://localhost:8423/list/rooms
curl http://localhost:8423/list/devices
curl http://localhost:8423/list/devices/Kitchen

# Query
curl http://localhost:8423/info/Office/Spotlights

# Control
curl http://localhost:8423/toggle/Office/Spotlights
curl http://localhost:8423/on/Kitchen/Light
curl http://localhost:8423/brightness/50/Bedroom/Lamp
curl http://localhost:8423/scene/Goodnight
```

For the full endpoint list, all control actions, and URL scheme reference: see [references/api.md](references/api.md).
