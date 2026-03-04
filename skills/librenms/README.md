# LibreNMS Skill for OpenClaw

Monitor your network infrastructure with LibreNMS REST API integration. Read-only monitoring skill for devices, health sensors, ports, and alerts.

## Features

- 📊 **Dashboard Summary** — Quick overview of all devices, up/down counts, active alerts
- 🖥️ **Device Monitoring** — List all devices with status, uptime, and OS info
- 🚨 **Alert Management** — View active/unresolved alerts with severity levels
- 🌡️ **Health Sensors** — Temperature, CPU, memory, disk usage monitoring
- 🔌 **Port Statistics** — Network interface status and traffic rates
- ⚠️ **Down Device Filter** — Instantly see which devices need attention

## Installation

1. Clone or copy this skill to your OpenClaw skills directory:
   ```bash
   cd ~/.openclaw/skills/
   git clone <this-repo> librenms
   # or copy the librenms/ folder
   ```

2. Install dependencies:
   ```bash
   # Most systems already have these
   sudo apt install curl jq bc  # Debian/Ubuntu
   sudo yum install curl jq bc  # RHEL/CentOS
   brew install curl jq         # macOS
   ```

3. Create configuration file:
   ```bash
   mkdir -p ~/.openclaw/credentials/librenms
   cat > ~/.openclaw/credentials/librenms/config.json << EOF
   {
     "url": "https://librenms.example.com",
     "api_token": "your-api-token-here"
   }
   EOF
   chmod 600 ~/.openclaw/credentials/librenms/config.json
   ```

4. Get your API token:
   - Log into LibreNMS web UI
   - Go to Settings → API Settings
   - Click "Create API Token"
   - Copy the token to your config.json

## Usage

### Quick Start

```bash
# Dashboard overview
librenms summary

# List all devices
librenms devices

# Show only devices that are down
librenms down

# Check active alerts
librenms alerts
```

### Device Details

```bash
# Get detailed info for a specific device
librenms device router-core-01

# Check health sensors (temp, CPU, memory, disk)
librenms health router-core-01

# View port/interface statistics
librenms ports router-core-01
```

### Example Output

**Summary:**
```
=== LibreNMS Summary ===

Devices:
  Total: 42
  Up:    40 ●
  Down:  2 ●

Active Alerts: 3
```

**Down Devices:**
```
=== Devices Down ===

STS  HOSTNAME                       IP                   LAST SEEN      
---  --------                       --                   ---------      
●    switch-edge-12                 192.168.1.12         2026-02-14 17:45
●    ap-warehouse-3                 10.20.5.33           2026-02-14 16:22
```

## Commands Reference

| Command | Description |
|---------|-------------|
| `summary` | Dashboard view: devices up/down, alert count |
| `devices` | List all monitored devices |
| `down` | Show only devices that are down |
| `device <hostname>` | Detailed info for a specific device |
| `health <hostname>` | Health sensors (temperature, CPU, RAM, disk) |
| `ports <hostname>` | Network interfaces and traffic statistics |
| `alerts` | Active/unresolved alerts |

## Configuration Options

**Config file** (`~/.openclaw/credentials/librenms/config.json`):
```json
{
  "url": "https://librenms.example.com",
  "api_token": "abc123def456"
}
```

**Environment variables** (override config file):
```bash
export LIBRENMS_URL="https://librenms.example.com"
export LIBRENMS_TOKEN="abc123def456"
librenms summary
```

## Integration Ideas

### Heartbeat Monitoring
Add to your OpenClaw heartbeat script:
```bash
# Check for down devices
if librenms down | grep -q "●"; then
    notify "Infrastructure Alert" "$(librenms down)"
fi

# Check for active alerts
alert_count=$(librenms summary | grep "Active Alerts" | awk '{print $3}')
if [[ $alert_count -gt 0 ]]; then
    notify "LibreNMS Alerts" "$(librenms alerts)"
fi
```

### Daily Reports
```bash
# Morning infrastructure summary
librenms summary > /tmp/daily-infra.txt
librenms down >> /tmp/daily-infra.txt
librenms alerts >> /tmp/daily-infra.txt
```

### Specific Device Monitoring
```bash
# Monitor critical devices
for device in router-core-01 switch-dist-01 fw-perimeter; do
    echo "=== $device ==="
    librenms health $device
    echo
done
```

## Security Notes

- This skill is **read-only** — no device modifications are possible
- API token is stored locally in `~/.openclaw/credentials/`
- The script uses `-k` flag for curl to accept self-signed certificates (common in LibreNMS)
- Restrict file permissions on config.json: `chmod 600 config.json`

## Troubleshooting

**Authentication Failed (HTTP 401)**
- Verify your API token is correct
- Check that the token hasn't expired
- Ensure the user associated with the token has API access

**Connection Failed**
- Verify the LibreNMS URL is correct and reachable
- Check firewall rules allow API access
- Test manually: `curl -k https://your-librenms/api/v0/devices`

**No Data Returned**
- Some devices may not have health sensors configured
- Check that the device is being polled successfully in LibreNMS
- Verify the hostname is exact (case-sensitive)

## API Documentation

Full LibreNMS API documentation: https://docs.librenms.org/API/

## License

MIT License — Free to use, modify, and distribute.

## Author

OpenClaw Community

## Contributing

Contributions welcome! Submit issues or pull requests on GitHub.

---

**Version:** 1.0.0  
**Dependencies:** curl, jq, bc (optional)  
**LibreNMS API:** v0  
**Platform:** Linux, macOS, Windows (WSL)
