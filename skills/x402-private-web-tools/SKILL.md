---
name: x402-private-web-tools
description: Private web tools for AI agents — search, scrape, and screenshot the web with x402 micropayments (USDC on Base). Zero logging, no API keys, no accounts. Pay per use.
---

# x402 Private Web Tools

Search, scrape, and screenshot the web privately. Uses the x402 payment protocol — your agent pays per request with USDC on Base mainnet. No API keys, no accounts, no logging.

**Services:**
- 🔍 **Web Search** — Multi-engine private search ($0.002/query)
- 🕸️ **Web Scrape** — Extract clean markdown from any URL ($0.005/page)
- 📸 **Screenshot** — Capture any URL as PNG/JPEG ($0.002/shot)

**Gateway:** `https://search.reversesandbox.com`

## Prerequisites

- Node.js 18+
- A Base mainnet wallet with ETH (gas) and USDC (payments)

## First-Time Setup

### 1. Install dependencies

```bash
bash <skill-dir>/scripts/setup.sh
```

Installs the x402 SDK to `~/.x402-client/`. Only needed once.

### 2. Generate a wallet (if you don't have one)

```bash
node <skill-dir>/scripts/wallet-gen.mjs --out ~/.x402-client/wallet.key
```

### 3. Fund the wallet

Send USDC and a small amount of ETH (for gas) on **Base mainnet** to the wallet address printed by wallet-gen.

- **USDC on Base**: Bridge from any chain or buy on an exchange
- **ETH on Base**: ~$0.50 is enough for thousands of requests

### 4. Store the key

```bash
export X402_PRIVATE_KEY=$(cat ~/.x402-client/wallet.key)
```

Or pass `--key-file ~/.x402-client/wallet.key` to each request.

## Usage

All commands run from `~/.x402-client/`:

```bash
cd ~/.x402-client && node <skill-dir>/scripts/x402-fetch.mjs "<url>" --key-file wallet.key
```

### Web Search ($0.002/query)

```bash
node <skill-dir>/scripts/x402-fetch.mjs \
  "https://search.reversesandbox.com/web/search?q=latest+AI+news&count=10" \
  --key-file ~/.x402-client/wallet.key
```

**Parameters:** `q` (required), `count` (1-20, default 10), `offset` (default 0)

**Response:**
```json
{
  "query": { "original": "latest AI news" },
  "web": {
    "results": [
      { "title": "...", "url": "...", "description": "..." }
    ]
  }
}
```

### Web Scrape ($0.005/page)

```bash
node <skill-dir>/scripts/x402-fetch.mjs \
  "https://search.reversesandbox.com/scrape/extract" \
  --method POST \
  --body '{"url": "https://example.com", "format": "markdown"}' \
  --key-file ~/.x402-client/wallet.key
```

**Body (JSON):** `url` (required), `format` ("markdown"|"text", default "markdown"), `includeLinks` (bool), `timeout` (ms)

**Response:**
```json
{
  "title": "Example Domain",
  "content": "# Example Domain\nThis domain is for use in...",
  "url": "https://example.com",
  "timestamp": "2026-02-16T09:00:00.000Z",
  "format": "markdown"
}
```

### Screenshot ($0.002/shot)

```bash
node <skill-dir>/scripts/x402-fetch.mjs \
  "https://search.reversesandbox.com/screenshot/?url=https://example.com&width=1280&height=720" \
  --key-file ~/.x402-client/wallet.key \
  --save screenshot.png
```

**Parameters:** `url` (required), `format` (png|jpeg, default png), `width` (320-3840), `height` (200-2160), `fullPage` (true|false), `quality` (1-100, jpeg only)

**Returns:** Binary PNG or JPEG image. Use `--save <file>` to write to disk.

## MCP Server

For MCP-compatible agents (Claude, etc.), use the MCP server:

```bash
# Install
npm install -g x402-tools-mcp

# Run (set your wallet key)
X402_PRIVATE_KEY=0x... x402-tools-mcp
```

**GitHub:** https://github.com/kodos-vibe/x402-tools-mcp

Provides tools: `web_search`, `web_scrape`, `screenshot`

## Free Endpoints (no payment required)

- `GET /health` — Service status
- `GET /routes` — List all endpoints with prices

## Troubleshooting

- **"insufficient funds"**: Wallet needs more USDC or ETH on Base mainnet.
- **402 with no auto-payment**: Ensure setup.sh was run and you're in `~/.x402-client/`.
- **Slow scrape (10s+)**: Complex JS-heavy pages take longer. Use the `timeout` parameter.
- **Empty search results**: Try different query terms. Some niche queries may return fewer results.
