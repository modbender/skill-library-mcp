# Loxone - Setup Instructions

## Prerequisites

### Required Software

- **Python 3** — For running the Loxone control scripts

No additional Python packages required. Uses only Python standard library (WebSocket, HTTP).

### Loxone Miniserver

- **Loxone Miniserver** — Must be accessible on your network or via Loxone Cloud DNS
- **User credentials** — Username and password for API access

## Configuration

### Config File

Create `~/Developer/Skills/loxone/config.json` (gitignored):

Start from the example:
```bash
cp ~/Developer/Skills/loxone/config.json.example \
   ~/Developer/Skills/loxone/config.json
```

Edit `config.json`:
```json
{
  "host": "192.168.0.222",
  "username": "your-username",
  "password": "your-password",
  "use_https": false
}
```

### Host Configuration

The `host` value can be configured in multiple ways:

#### 1. Local IP/Hostname (LAN)
```json
{
  "host": "192.168.0.222",
  "use_https": false
}
```

Good for local network access. No SSL required.

#### 2. Custom Hostname with SSL
```json
{
  "host": "loxone.example.com",
  "use_https": true
}
```

Requires valid SSL certificate for the hostname.

#### 3. Loxone Cloud DNS (Recommended for Remote Access)
```json
{
  "host": "dns.loxonecloud.com/504F94A22C29",
  "use_https": true
}
```

Or shorthand:
```json
{
  "host": "504F94A22C29",
  "use_https": true
}
```

The skill resolves the serial number via Loxone Cloud DNS at runtime and uses the appropriate `*.dyndns.loxonecloud.com` hostname with SSL certificate verification.

### Security

- **HTTPS + certificate verification** is enabled by default when `use_https: true`
- For LAN access without SSL, set `"use_https": false`
- When `use_https` is true, SSL certificates are **always verified**
  - Install a proper certificate on your Miniserver, or
  - Use the Loxone Cloud DNS tunnel (recommended)

### File Permissions

Config file should be readable only by you:
```bash
chmod 600 ~/Developer/Skills/loxone/config.json
```

## Loxone Cloud DNS Setup

To use Cloud DNS (`dns.loxonecloud.com/<SERIAL>`):

1. Find your Miniserver serial number:
   - Loxone Config → Miniserver → Properties → Serial Number
   - Example: `504F94A22C29`

2. Enable Cloud DNS in Loxone Config:
   - Miniserver → Network → Cloud DNS → Enable

3. Use in config:
   ```json
   {
     "host": "504F94A22C29",
     "use_https": true
   }
   ```

The skill automatically:
- Queries `https://dns.loxonecloud.com/?getip&snr=<SERIAL>&json=true`
- Resolves to current IP + port
- Uses certificate-matching `*.dyndns.loxonecloud.com` hostname
- Connects with SSL verification

## Verification

Test your configuration:

```bash
# List all rooms
python3 ~/Developer/Skills/loxone/scripts/loxone.py rooms

# Get structure map
python3 ~/Developer/Skills/loxone/scripts/loxone.py map

# Check room status
python3 ~/Developer/Skills/loxone/scripts/loxone.py status "Living Room"
```

If WebSocket fails, the skill falls back to HTTP for status queries.

## WebSocket vs HTTP

- **WebSocket** — Real-time event monitoring, live updates
- **HTTP** — Status queries, control commands

The skill uses both protocols:
- `loxone.py` — HTTP API for queries and control
- `loxone_watch.py` — WebSocket for real-time monitoring

WebSocket authentication can be finicky. If WebSocket fails, HTTP queries still work.

## Safety Note

**Treat as read-only by default.** Only use control commands when explicitly requested by the user. Smart home automation can have real-world consequences.
