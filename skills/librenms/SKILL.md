# LibreNMS Skill

Monitor network infrastructure via LibreNMS REST API. Read-only monitoring skill for device status, health sensors, port statistics, and alerts.

## Configuration

Create `~/.openclaw/credentials/librenms/config.json`:
```json
{
  "url": "https://librenms.example.com",
  "api_token": "your-api-token-here"
}
```

Or set environment variables:
- `LIBRENMS_URL` — Base URL of your LibreNMS instance
- `LIBRENMS_TOKEN` — API authentication token

## Commands

### Quick Overview
```bash
librenms summary
```
Dashboard view showing total devices, how many are up/down, and active alert count. Use this first to get a quick status overview.

### Device Management
```bash
librenms devices           # List all devices with status, IP, OS, uptime
librenms down             # Show ONLY devices that are down (critical for alerting)
librenms device <hostname> # Detailed info: hardware, serial, location, OS version
```

### Health Monitoring
```bash
librenms health <hostname> # Temperature, CPU, memory, disk usage sensors
librenms ports <hostname>  # Network interfaces with traffic stats
```

### Alerts
```bash
librenms alerts           # Show active/unresolved alerts with severity and timestamps
```

## Usage Patterns

**Daily health check:**
```bash
librenms summary && librenms down && librenms alerts
```

**Investigate specific device:**
```bash
librenms device switch-core-01
librenms health switch-core-01
librenms ports switch-core-01
```

**Quick down-device triage:**
```bash
librenms down | grep -v "UP"
```

## Important Notes

- All operations are **read-only** — no device modifications possible
- The script accepts self-signed certificates (-sk flag for curl)
- Status indicators: ● green = up, ● red = down
- Uptime is formatted as human-readable (days/hours instead of seconds)
- Traffic stats are formatted as KB/MB/GB per second

## Heartbeat Integration

Check infrastructure health periodically:
```bash
# In heartbeat script
if librenms down | grep -q "Devices Down"; then
    # Alert on down devices
    librenms down
fi

# Check for active alerts
if librenms alerts | grep -q "Active Alerts"; then
    librenms alerts
fi
```

## Dependencies

- `curl` — API calls
- `jq` — JSON parsing
- `bc` — Numeric formatting (optional, for bytes conversion)

## API Coverage

Wrapped endpoints:
- `/api/v0/devices` — All devices
- `/api/v0/devices/{hostname}` — Single device details
- `/api/v0/devices/{hostname}/health` — Health sensors
- `/api/v0/devices/{hostname}/ports` — Network ports
- `/api/v0/alerts?state=1` — Unresolved alerts

Full API docs: https://docs.librenms.org/API/

## Troubleshooting

**"Config file not found"**
Create `~/.openclaw/credentials/librenms/config.json` or set env vars.

**"API returned HTTP 401"**
Check your API token. Generate a new one in LibreNMS under Settings → API.

**"Failed to connect"**
Verify the URL is correct and the LibreNMS instance is reachable. Check firewall rules.

**Self-signed cert warnings**
The script uses `-sk` to ignore cert validation (common in LibreNMS setups). If you need strict validation, edit the script and remove the `-k` flag.
