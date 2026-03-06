# Residential Proxy Setup

## Provider Comparison

| Provider | Pool Size | Pay-as-you-go | Geo-targeting | Best for |
|----------|-----------|--------------|---------------|----------|
| Oxylabs | 100M+ IPs | ✅ | Country/city/state | Difficult targets, highest success rate |
| DataImpulse | 5M+ IPs | ✅ (no minimum) | Country | Budget, high-volume |
| Smartproxy | 55M+ IPs | ✅ | Country/city | Unlimited connections |
| Bright Data | 72M+ IPs | ❌ ($500 min) | Country/city/ASN | Enterprise |

**Recommendation:** Oxylabs for most use cases. DataImpulse if budget is tight.

## Setup

### 1. Get credentials

After signing up with any provider, you'll get:
- **Host** (e.g., `pr.oxylabs.io`)
- **Port** (e.g., `7777`)
- **Username**
- **Password**

### 2. Test connectivity

```bash
curl -x http://USERNAME:PASSWORD@HOST:PORT https://httpbin.org/ip
```

Should return a JSON object with an IP different from your server's IP.

### 3. Verify residential

```bash
curl -x http://USERNAME:PASSWORD@HOST:PORT -s https://ipinfo.io/json
```

Look at `org` field — should be an ISP (Comcast, Verizon, AT&T, BT, Deutsche Telekom), NOT a cloud provider (AWS, Google, DigitalOcean).

### 4. Configure

**Python requests:**
```python
proxies = {
    "http": "http://USER:PASS@HOST:PORT",
    "https": "http://USER:PASS@HOST:PORT"
}
response = requests.get(url, proxies=proxies)
```

**Playwright:**
```python
browser = playwright.chromium.launch(
    proxy={"server": "http://HOST:PORT", "username": "USER", "password": "PASS"}
)
```

**Puppeteer:**
```javascript
const browser = await puppeteer.launch({
    args: ['--proxy-server=http://HOST:PORT']
});
// Authenticate per page:
await page.authenticate({username: 'USER', password: 'PASS'});
```

**Environment variables (curl, wget, most CLI tools):**
```bash
export HTTP_PROXY="http://USER:PASS@HOST:PORT"
export HTTPS_PROXY="http://USER:PASS@HOST:PORT"
```

**OpenClaw browser tool:**
Set env vars before starting the gateway, or configure in the browser launch options.

### 5. Save for reuse

```bash
mkdir -p ~/.config/stealth
cat > ~/.config/stealth/proxy.json << 'EOF'
{
  "host": "HOST",
  "port": "PORT",
  "username": "USER",
  "password": "PASS",
  "provider": "oxylabs"
}
EOF
chmod 600 ~/.config/stealth/proxy.json
```

### 6. IP Rotation

Most providers auto-rotate per request. For sticky sessions (same IP for a session):
- **Oxylabs:** append `-session-RANDOM` to username
- **Smartproxy:** use session port (e.g., `7778`)
- **DataImpulse:** append `-sessid-RANDOM` to username

## Country Targeting

Route through specific countries by modifying the username or endpoint:

- **Oxylabs:** `customer-USER-cc-US:PASS@pr.oxylabs.io:7777`
- **Smartproxy:** `user-USER-country-us:PASS@gate.smartproxy.com:7000`
- **DataImpulse:** `USER-country-us:PASS@gw.dataimpulse.com:823`
