---
description: Diagnose Wi-Fi issues with signal analysis, channel scanning, speed tests, and DNS checks.
---

# Wi-Fi Diagnostics

Diagnose Wi-Fi connectivity issues with signal analysis, channel scanning, and speed tests.

## Requirements

- Linux with `nmcli`, `iwconfig`, or `iw`
- `curl` for speed tests
- Optional: `dig` for DNS diagnostics
- Some commands require `sudo` for wireless scanning

## Instructions

### Connection info
```bash
# Current network details
nmcli -t -f active,ssid,signal,chan,freq,bssid dev wifi | grep '^yes'

# Interface details
iwconfig 2>/dev/null | grep -E 'ESSID|Quality|Bit Rate'

# IP and gateway
ip route | grep default
ip addr show | grep 'inet '
```

### Channel scan
```bash
# Nearby networks (may need sudo)
nmcli dev wifi list

# Channel utilization summary
nmcli -t -f chan,signal dev wifi list | sort -t: -k1 -n | \
  awk -F: '{ch[$1]++; sig[$1]+=$2} END{for(c in ch) printf "Ch %s: %d networks, avg signal %d%%\n", c, ch[c], sig[c]/ch[c]}'
```

### Speed test (no dependencies)
```bash
# Download test (~10MB)
curl -o /dev/null -s -w "Download: %{speed_download} bytes/sec (%{time_total}s)\n" https://speed.cloudflare.com/__down?bytes=10000000

# Upload test (~10MB)
dd if=/dev/zero bs=1M count=10 2>/dev/null | curl -X POST -d @- -s -w "Upload: %{speed_upload} bytes/sec\n" https://speed.cloudflare.com/__up
```

### DNS diagnostics
```bash
dig google.com | grep "Query time"
ping -c 5 8.8.8.8 | tail -1
ping -c 5 1.1.1.1 | tail -1
```

### Output format
```
## 📶 Wi-Fi Diagnostics — <timestamp>

**Network**: MyWiFi | **Channel**: 6 (2.4GHz) | **Signal**: 72%

| Test | Result | Status |
|------|--------|--------|
| Signal | -45 dBm (72%) | 🟢 Good |
| Download | 48.2 Mbps | 🟢 Good |
| Upload | 12.1 Mbps | 🟡 Fair |
| DNS Latency | 15ms | 🟢 Good |
| Ping (8.8.8.8) | 22ms avg | 🟢 Good |

**Channel Congestion**: Ch 6 has 8 networks. Consider switching to Ch 1 or 11.

**Thresholds**: Signal: 🟢>60% 🟡30-60% 🔴<30% | Speed: 🟢>25Mbps 🟡>5Mbps 🔴<5Mbps
```

## Edge Cases

- **No Wi-Fi adapter**: Detect with `iw dev`. Report if no wireless interface found.
- **Ethernet only**: Note that diagnostics apply to Wi-Fi only — ethernet has different tools.
- **5GHz vs 2.4GHz**: Report which band is in use. Channel recommendations differ per band.
- **VPN active**: Speed tests may be affected by VPN. Note if a VPN interface is detected.
- **nmcli unavailable**: Fall back to `iwconfig` and `iw`.

## Security

- Speed tests send data to external servers (Cloudflare) — fine for diagnostics.
- Wi-Fi scan reveals nearby network names — don't share in public contexts.
- Never expose Wi-Fi passwords in diagnostic output.
