# 🔍 network-scanner

Discover devices and scan ports on your local network — powered by nmap.

## Features

- LAN device discovery (ping sweep)
- Quick or full port scanning
- Service and version detection
- OS fingerprinting
- Clean formatted results with security highlights

## Usage

Ask the agent to scan your network or a specific host.

```
"Scan my local network for devices"
"Check open ports on 192.168.1.100"
"What services are running on my NAS?"
```

## Requirements

- `nmap` installed (`apt install nmap` / `brew install nmap`)
- Root/sudo for advanced scans (OS detection, SYN scan)

## Author

REY ([@REY_MoltWorker](https://x.com/REY_MoltWorker))
