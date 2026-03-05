# Itsyhome Webhook API Reference

Base URL: `http://localhost:8423` (default port, configurable in Settings)

All endpoints respond with JSON. Targets are case-insensitive. Use `%20` for spaces.

## Read Endpoints

### Status
```bash
curl http://localhost:8423/status
# → {"rooms": 5, "devices": 23, "accessories": 18, "reachable": 17, "unreachable": 1, "scenes": 4, "groups": 2}
```

### List
```bash
curl http://localhost:8423/list/rooms
curl http://localhost:8423/list/devices
curl http://localhost:8423/list/devices/Kitchen       # filter by room
curl http://localhost:8423/list/scenes
curl http://localhost:8423/list/groups
curl http://localhost:8423/list/groups/Living%20Room  # filter groups by room
```

### Info (device state)
```bash
curl http://localhost:8423/info/Office/Spotlights     # Room/Device
curl http://localhost:8423/info/Living%20Room         # entire room
curl http://localhost:8423/info/Front%20Door          # single device
# → includes: name, type, reachable, room, state (on, brightness, temperature, locked, etc.)
```

### Debug (raw characteristics)
```bash
curl http://localhost:8423/debug/Office/Spotlights    # specific device
curl http://localhost:8423/debug/all                  # all accessories
curl http://localhost:8423/debug/raw                  # raw HomeKit dump
curl http://localhost:8423/debug/cameras              # all cameras
curl http://localhost:8423/debug/cameras/camera.office # specific camera entity
```

## Control Endpoints

### Power
```bash
curl http://localhost:8423/toggle/Office/Spotlights
curl http://localhost:8423/on/Kitchen/Light
curl http://localhost:8423/off/Bedroom/Lamp
```

### Brightness (0–100)
```bash
curl http://localhost:8423/brightness/50/Bedroom/Lamp
curl http://localhost:8423/brightness/100/Kitchen/Light
```

### Color (hue 0–360, saturation 0–100)
```bash
curl http://localhost:8423/color/120/100/Kitchen/Light   # green, full saturation
curl http://localhost:8423/color/0/100/Living%20Room/Lamp # red
```

### Temperature (degrees, e.g. Celsius)
```bash
curl http://localhost:8423/temp/21/Bedroom/Thermostat
curl http://localhost:8423/temp/20/Living%20Room/AC
```

### Fan Speed (0–100)
```bash
curl http://localhost:8423/speed/50/Living%20Room/Fan
curl http://localhost:8423/speed/100/Bedroom/Fan
```

### Position / Blinds (0–100, 0=closed, 100=open)
```bash
curl http://localhost:8423/position/75/Living%20Room/Blinds
curl http://localhost:8423/position/0/Bedroom/Blinds
```

### Locks
```bash
curl http://localhost:8423/lock/Front%20Door
curl http://localhost:8423/unlock/Front%20Door
```

### Garage / Doors
```bash
curl http://localhost:8423/open/Garage
curl http://localhost:8423/close/Garage
```

### Scenes
```bash
curl http://localhost:8423/scene/Goodnight
curl http://localhost:8423/scene/Movie%20Time
```

## SSE Stream (live state changes)

```bash
curl -N http://localhost:8423/events
# Streams Server-Sent Events with characteristic updates in real time
```

## URL Scheme (no server required)

The `itsyhome://` URL scheme triggers actions without the webhook server:

```bash
open "itsyhome://toggle/Office/Spotlights"
open "itsyhome://on/Kitchen/Light"
open "itsyhome://brightness/50/Bedroom/Lamp"
open "itsyhome://position/75/Living%20Room/Blinds"
open "itsyhome://temp/21/Bedroom/Thermostat"
open "itsyhome://color/120/100/Kitchen/Light"
open "itsyhome://speed/50/Living%20Room/Fan"
open "itsyhome://scene/Goodnight"
open "itsyhome://lock/Front%20Door"
open "itsyhome://unlock/Front%20Door"
open "itsyhome://open/Garage"
open "itsyhome://close/Garage"
```

URL scheme has no read/query capability — use webhook server for status and info.

## Target Format

- `Room/Device` → most specific, preferred
- `DeviceName` → matches across all rooms (may be ambiguous)
- `RoomName` → matches all devices in room (for info/list only)
- URL encode spaces: `Living Room` → `Living%20Room`

## Error Responses

| Status | Meaning |
|--------|---------|
| 200 | Success |
| 400 | Bad request / unsupported action |
| 404 | Device or scene not found |
| 500 | Itsyhome internal error / no data |
