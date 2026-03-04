# Snapmaker 2.0 HTTP API Notes

## Sources

- https://forum.snapmaker.com/t/documentation-of-the-web-api/20976
- https://forum.snapmaker.com/t/guide-automatic-start-via-drag-drop/29177

## Available Endpoints (API v1)

All endpoints require `token` header for authentication.

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/connect` | Establish connection (required before other calls) |
| GET | `/api/v1/status` | Current printer status, temperatures, progress |
| POST | `/api/v1/prepare_print` | Upload a gcode file (multipart form) |
| POST | `/api/v1/start_print` | Start the prepared print |
| POST | `/api/v1/pause` | Pause current print |
| POST | `/api/v1/resume` | Resume paused print |
| POST | `/api/v1/stop` | Stop/cancel current print |
| GET | `/api/v1/enclosure` | Enclosure status (if available) |

## Known Limitations

- **No file listing** — Cannot list files stored on the printer's internal storage or SD card
- **No file deletion** — Cannot delete files from the printer remotely
- **No file management** — Files on the printer can only be managed via:
  - Touchscreen UI directly
  - Luban desktop app
  - USB drive
- **Single connection** — Only one client can connect at a time. If Luban or the touchscreen is active, API connection will fail with "Failed to connect, there is someone trying to connect to Touchscreen."
- **No GCode streaming** — Cannot send raw GCode commands via HTTP API
- **No camera** — No API endpoint for camera/video feed

## Authentication

Token is stored by Luban in:
```
~/Library/Application Support/snapmaker-luban/machine.json
```

## Status Response Fields

- `status` — Machine state (RUNNING, IDLE, PAUSED, etc.)
- `x`, `y`, `z` — Current position
- `t0` (nozzle temp), `b` (bed temp) — Current / target temperatures
- `progress` — Print progress percentage
- `elapsedTime`, `remainingTime` — In seconds
- `fileName` — Currently printing file
- `totalLines`, `currentLine` — GCode line progress
