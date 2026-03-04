# Tor Browser Setup Guide

## Prerequisites

### 1. Install Tor

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install tor
sudo systemctl enable tor
sudo systemctl start tor
```

**macOS:**
```bash
brew install tor
brew services start tor
```

**Docker:**
```bash
docker run -d --name tor-proxy \
  -p 9050:9050 \
  -p 9051:9051 \
  peterdavehello/tor-socks-proxy
```

### 2. Verify Tor is Running

```bash
# Check SOCKS5 proxy is listening
curl --socks5-hostname 127.0.0.1:9050 https://check.torproject.org/api/ip
```

Expected output:
```json
{"IsTor":true,"IP":"xxx.xxx.xxx.xxx"}
```

### 3. Install Python Dependencies

```bash
pip install playwright
playwright install chromium
```

## Tor Configuration (Optional)

Edit `/etc/tor/torrc`:

```
# SOCKS5 proxy (default)
SocksPort 9050

# Control port for new identity requests
ControlPort 9051
CookieAuthentication 0
HashedControlPassword 16:YOUR_HASHED_PASSWORD
```

Reload Tor:
```bash
sudo systemctl restart tor
```

## Security Considerations

1. **Isolate circuits**: Each browser context uses a fresh Tor circuit
2. **No JavaScript exploits**: JavaScript is enabled but runs in isolated context
3. **Fingerprinting**: User agent is set to Tor Browser default
4. **DNS leaks**: All DNS queries go through Tor SOCKS5 proxy

## Troubleshooting

### Connection refused
- Ensure Tor service is running: `sudo systemctl status tor`
- Check firewall: `sudo ufw allow 9050`

### Timeout errors
- Some .onion sites are slow; increase timeout: `--timeout 60000`
- Try different Tor exit nodes by restarting Tor

### CAPTCHA challenges
- Some sites detect automation; use `--headed` mode
- Consider using a dedicated Tor Browser profile

## Advanced Usage

### Custom Tor Proxy

```bash
export TOR_PROXY="socks5://192.168.1.100:9050"
tor-browser open http://3g2upl4pq6kufc4m.onion --proxy $TOR_PROXY
```

### Multi-session Browsing

Use separate browser instances for different identities:

```python
from scripts.tor_browser import TorBrowser, Config

config1 = Config(tor_proxy="socks5://127.0.0.1:9050")
browser1 = TorBrowser(config1)

config2 = Config(tor_proxy="socks5://127.0.0.1:9050")  
browser2 = TorBrowser(config2)
```
