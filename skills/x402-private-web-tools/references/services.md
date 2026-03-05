# x402 Private Web Tools — Service Reference

**Gateway:** `https://search.reversesandbox.com`
**Network:** Base mainnet (`eip155:8453`)
**Payment:** USDC

## Endpoints

### Web Search
- **Method:** `GET /web/search`
- **Price:** $0.002 USDC per query
- **Params:** `q` (required), `count` (1-20), `offset`
- **Response:** JSON — Brave Search API compatible format

### Web Scrape
- **Method:** `POST /scrape/extract`
- **Price:** $0.005 USDC per page
- **Body:** `{ url, format?, includeLinks?, timeout? }`
- **Response:** JSON — `{ title, content, url, timestamp, format }`

### Screenshot
- **Method:** `GET /screenshot/`
- **Price:** $0.002 USDC per shot
- **Params:** `url` (required), `format` (png|jpeg), `width`, `height`, `fullPage`, `quality`
- **Response:** Binary image (PNG or JPEG)

## Free Endpoints
- `GET /health` — `{ status: "ok", providers: [...] }`
- `GET /routes` — List all paid endpoints with prices and descriptions

## Discovery
Any x402 service returns payment requirements (HTTP 402) when you hit a paid endpoint without payment. The response includes price, network, and payment address. The x402 SDK handles this automatically.
