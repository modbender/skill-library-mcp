# Bright Data — Setup & Reference

## Sign Up
- Registration: https://brightdata.com/
- After signup, go to: https://brightdata.com/cp/zones

## Create Zones

### Web Unlocker Zone (for regular proxying)
1. Dashboard → Proxies & Scraping → Add Zone
2. Type: **Web Unlocker**
3. Name: `mcp_unlocker` (or any name)
4. Country: Romania (or leave "All" for auto-rotation)
5. Copy credentials from zone settings

### Scraping Browser Zone (for Playwright CDP)
1. Dashboard → Proxies & Scraping → Add Zone
2. Type: **Scraping Browser**
3. Name: `mcp_browser`
4. Used for: `wss://brd.superproxy.io:9222` CDP endpoint

## Billing & Top-Up
- Top up balance: https://brightdata.com/cp/billing
- Minimum deposit: $10
- Pay-as-you-go pricing:
  - Web Unlocker: ~$3/GB
  - Scraping Browser: ~$9/hour

## Proxy Credentials Format

```
# HTTP Proxy (for Playwright context)
server: http://brd.superproxy.io:22225
username: brd-customer-<CUSTOMER_ID>-zone-<ZONE_NAME>-country-ro
password: <ZONE_PASSWORD>

# CDP WebSocket (Scraping Browser only)
wss://brd-customer-<CUSTOMER_ID>-zone-<ZONE_NAME>-country-ro:<PASSWORD>@brd.superproxy.io:9222
```

## Where to Find Credentials
- Dashboard: https://brightdata.com/cp/zones
- Click on your zone → **Access Parameters** tab
- Copy: Customer ID, Zone name, Password

## Country Codes
- `ro` — Romania (DIGI / WS Telecom residential IPs)
- `us` — United States
- `de` — Germany
- Remove `-country-XX` for global rotation

## Node.js Dependency

```bash
npm install playwright
npx playwright install chromium --with-deps
```
