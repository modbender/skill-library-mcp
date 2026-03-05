# AdBlock DNS

Network-wide ad and tracker blocking at the DNS level. A Pi-hole alternative that runs directly on your machine as an OpenClaw skill. No separate hardware needed.

## What It Does

Runs a DNS sinkhole server that blocks ads, trackers, malware, and telemetry domains across your entire network. Any device that uses this machine as its DNS server gets ad-free browsing automatically — phones, tablets, smart TVs, laptops, IoT devices, everything.

Blocks 189,000+ ad and tracker domains using the same blocklists as Pi-hole (Steven Black, AdAway, EasyList, EasyPrivacy, Anti-Malware). Blocks both IPv4 (A) and IPv6 (AAAA) queries.

**Works great for:** Banner ads on websites, tracking pixels, third-party ad networks (Doubleclick, Amazon Ads, Criteo, Rubicon, etc.), in-app ads, telemetry/analytics trackers, malware domains.

**Won't block:** YouTube ads, Twitch ads, or any ads served from the same domain as the content itself. These platforms serve ads from their own CDN (e.g. `googlevideo.com` for YouTube), so blocking the domain would break the entire service. This is a fundamental limitation of ALL DNS-level blockers including Pi-hole. For YouTube ads, use a browser extension like uBlock Origin.

## How It Works

The skill runs a DNS server on this machine. When a device queries a domain:
- If the domain is on the blocklist, it returns 0.0.0.0 (blocked)
- If the domain is clean, it forwards the query to upstream DNS (Cloudflare 1.1.1.1 by default)

All queries are logged with stats (total queries, blocked percentage, top blocked domains).

## Setup

### Step 1: Run the setup script

```bash
cd /path/to/skills/adblock/scripts
bash setup.sh
```

This will:
1. Install dependencies if needed
2. Create a systemd service (runs as root, starts on boot, auto-restarts)
3. Download blocklists (~150K+ domains)
4. Start the DNS server on port 53
5. Start a stats API on port 8053
6. Print your DNS IP and device setup instructions

The user will need to enter their sudo password once during setup.

**Alternative (manual start without systemd):**
```bash
sudo node dns-server.js
```

### Step 2: Change DNS settings on your devices

**This is the critical step.** The DNS server does nothing until devices point to it.

Find this machine's local IP address:
```bash
hostname -I | awk '{print $1}'
```

Then configure devices to use that IP as their DNS server:

**Router (blocks entire network):**
- Log into your router admin panel (usually 192.168.1.1)
- Find DNS settings (usually under DHCP or Internet/WAN settings)
- Set primary DNS to this machine's IP
- Set secondary DNS to 1.1.1.1 (fallback if this machine is off)
- All devices on the network are now protected

**Individual devices:**

- **iPhone/iPad:** Settings > Wi-Fi > tap your network > Configure DNS > Manual > add this machine's IP
- **Android:** Settings > Network > Wi-Fi > your network > Advanced > DNS > set to this machine's IP
- **Mac:** System Settings > Network > Wi-Fi > Details > DNS > add this machine's IP
- **Windows:** Settings > Network > Wi-Fi > Hardware properties > DNS server assignment > Manual > set IPv4 DNS
- **Linux:** Edit /etc/resolv.conf or NetworkManager: `nmcli con mod "Wi-Fi" ipv4.dns "MACHINE_IP"`

### Step 3: Verify it's working

```bash
# Should return 0.0.0.0 (blocked)
nslookup ads.google.com MACHINE_IP

# Should return a real IP (allowed)
nslookup google.com MACHINE_IP
```

Or check the API: `curl http://localhost:8053/stats`

## Agent Commands

When the user asks about ad blocking, use these:

### Check stats
```bash
curl -s http://localhost:8053/stats | python3 -m json.tool
```
Report: total queries, blocked queries, block percentage, top blocked domains.

### Whitelist a domain
If something is broken because it's being blocked:
```bash
curl -s -X POST http://localhost:8053/whitelist/add -H "Content-Type: application/json" -d '{"domain":"example.com"}'
```

### Block a specific domain
```bash
curl -s -X POST http://localhost:8053/blacklist/add -H "Content-Type: application/json" -d '{"domain":"annoying-site.com"}'
```

### Check if a domain is blocked
```bash
curl -s "http://localhost:8053/check?domain=ads.google.com"
```

### Update blocklists
Blocklists auto-update every 24 hours. To force an update:
```bash
curl -s -X POST http://localhost:8053/update
```

### View whitelist
```bash
curl -s http://localhost:8053/whitelist
```

## Running as a Service

The `setup.sh` script handles this automatically. If you need to manage it manually:

```bash
sudo systemctl start adblock-dns     # Start
sudo systemctl stop adblock-dns      # Stop
sudo systemctl restart adblock-dns   # Restart
sudo systemctl status adblock-dns    # Check status
journalctl -u adblock-dns -f         # View logs

# Remove completely
sudo systemctl disable adblock-dns
sudo rm /etc/systemd/system/adblock-dns.service
sudo systemctl daemon-reload
```

## Configuration

Edit `data/config.json`:
```json
{
  "upstream": "1.1.1.1",   // Upstream DNS (Cloudflare, Google 8.8.8.8, etc.)
  "port": 53,              // DNS port (53 = standard, needs sudo)
  "apiPort": 8053           // Stats API port
}
```

## Files

- `data/blocklist.txt` - Compiled blocklist (auto-generated)
- `data/whitelist.txt` - Whitelisted domains (one per line)
- `data/custom-blacklist.txt` - Extra domains to block (one per line)
- `data/stats.json` - Query statistics
- `data/config.json` - Server configuration

## Constraints

- Port 53 requires root/sudo access
- Devices MUST be configured to use this machine's IP as DNS for blocking to work
- If this machine goes offline, devices using it as DNS will lose DNS resolution (set a secondary DNS as fallback)
- Only blocks domains, not in-page ad elements (use a browser ad blocker for that)
- HTTPS/DoH queries that bypass system DNS won't be caught
