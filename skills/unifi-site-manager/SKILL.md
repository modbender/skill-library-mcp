---
name: unifi-site-manager
version: 3.2.1
homepage: https://github.com/odrobnik/unifi-skill
description: Monitor and configure UniFi network infrastructure. Auto-routes between local gateway and cloud connector. Manage hosts, sites, devices, clients, WLANs, radios, firmware, and events.
metadata:
  openclaw:
    requires:
      env: ["UNIFI_API_KEY"]
      optionalEnv: ["UNIFI_BASE_URL", "UNIFI_GATEWAY_IP", "UNIFI_LOCAL_API_KEY"]
---

# UniFi Network API

Monitor and configure UniFi network infrastructure.

**Entry point:** `{baseDir}/scripts/unifi.py`

## Setup

See [SETUP.md](SETUP.md) for prerequisites and setup instructions.

Config (`config.json`):
- `api_key` — UniFi Cloud API key (required)
- `gateway_ip` — Local gateway IP (for faster local access)
- `local_api_key` — Local gateway API key
- `site_id` — Default site UUID (auto-detected if only one site)

Routing is automatic: local gateway when reachable, cloud connector when remote. Use `--local` to force local-only.

## Commands

All commands support `--json` for raw JSON output.

### Infrastructure

```bash
python3 {baseDir}/scripts/unifi.py list-hosts              # Controllers/consoles
python3 {baseDir}/scripts/unifi.py list-sites              # Sites with statistics
python3 {baseDir}/scripts/unifi.py list-devices            # All network devices (summary)
python3 {baseDir}/scripts/unifi.py list-site-devices       # Devices with rich detail (ports, radios, features)
python3 {baseDir}/scripts/unifi.py list-aps                # Access points only
python3 {baseDir}/scripts/unifi.py get-device <device_id>  # Single device details
python3 {baseDir}/scripts/unifi.py firmware-status         # Firmware versions + update availability
```

### Clients

```bash
python3 {baseDir}/scripts/unifi.py list-clients              # Currently connected clients
python3 {baseDir}/scripts/unifi.py list-clients --detailed    # With traffic/signal stats
python3 {baseDir}/scripts/unifi.py list-known-clients         # All known clients (current + historical)
python3 {baseDir}/scripts/unifi.py list-known-clients --named # Only clients with custom names
python3 {baseDir}/scripts/unifi.py list-ap-clients            # Wireless clients grouped by AP
python3 {baseDir}/scripts/unifi.py list-ap-clients --ap Living  # Filter by AP name
python3 {baseDir}/scripts/unifi.py get-client <client_id>     # Single client details
python3 {baseDir}/scripts/unifi.py label-client <mac> "Name"  # Set custom name for a client
```

### Networks & WLANs

```bash
python3 {baseDir}/scripts/unifi.py list-networks             # Configured networks (VLANs)
python3 {baseDir}/scripts/unifi.py get-wlan-config            # WLAN/SSID configurations
python3 {baseDir}/scripts/unifi.py get-wlan-config --ssid Hogwarts  # Specific SSID
python3 {baseDir}/scripts/unifi.py set-wlan --ssid Hogwarts \
  --fast-roaming on \
  --bss-transition on \
  --pmf required \
  --band-steering prefer_5g
```

### Network DNS

```bash
python3 {baseDir}/scripts/unifi.py get-network-dns              # All networks
python3 {baseDir}/scripts/unifi.py get-network-dns Default       # Specific network
python3 {baseDir}/scripts/unifi.py set-network-dns Default \
  --dns1 1.1.1.1 --dns2 1.0.0.1                                 # Set DNS servers
python3 {baseDir}/scripts/unifi.py set-network-dns Default \
  --dns1 auto                                                    # Disable override (use gateway)
```

### Radio Configuration

```bash
python3 {baseDir}/scripts/unifi.py get-radio-config           # Radio config for all APs
python3 {baseDir}/scripts/unifi.py get-radio-config --ap Living  # Specific AP
python3 {baseDir}/scripts/unifi.py set-radio --ap Living --band 5 \
  --channel 36 --width 80 --power high
```

### Events

```bash
python3 {baseDir}/scripts/unifi.py list-events                # All site events
python3 {baseDir}/scripts/unifi.py list-events --filter Roam   # Filter by event type
python3 {baseDir}/scripts/unifi.py list-events --mac aa:bb:cc:dd:ee:ff  # Filter by MAC
```

## Notes

- Site is auto-detected when only one exists; use `--site <siteId>` otherwise
- `--local` forces local gateway access (errors if unreachable)
- Event buffer is limited (~3 weeks of history depending on volume)
- Apple devices use randomized MACs; use `label-client` to track them by their per-network Wi-Fi Address
